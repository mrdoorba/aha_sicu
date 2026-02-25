## Context

The sync system uses a `sync_status` table to track sync operations. When `POST /sync` is called, a record is created with `success=NULL, completed_at=NULL`, and a FastAPI `BackgroundTask` runs the actual sync. On completion (or failure), the record is updated.

The problem: if the database becomes unreachable while a sync is running (e.g., Cloud SQL scheduled shutdown), both the sync write AND the error handler's status update fail. The record stays stuck with `success=NULL` forever, which:
1. Makes `is_sync_in_progress()` return `True` → blocks all future syncs (409)
2. Makes `get_latest_sync_status()` return `status: "in_progress"` → UI stuck on "Menyinkronkan..."

Additionally, the daily sync cron (`0 1 * * *` = 08:00 WIB) runs 30 minutes before Cloud SQL starts (`30 1 * * *` = 08:30 WIB).

## Goals / Non-Goals

**Goals:**
- Auto-recover from stuck sync records without manual DB intervention
- Ensure the daily sync schedule has adequate buffer after Cloud SQL starts
- Keep the fix minimal and localized to the sync module

**Non-Goals:**
- Changing the sync from background task to synchronous (separate concern)
- Adding a manual "cancel sync" UI button
- Changing Cloud SQL start/stop times

## Decisions

### 1. Staleness timeout at query level (not application level)

Add a 10-minute timeout directly in the SQL queries (`is_sync_in_progress` and `get_latest_sync_status`). Any sync record with `completed_at IS NULL` AND `started_at` older than 10 minutes is treated as failed.

**Why 10 minutes**: A normal sync takes 1-5 minutes (Google Sheets fetch + DB upsert). 10 minutes is generous enough to never false-positive, but short enough to auto-recover within a reasonable window.

**Why query-level**: Simpler than a background cleanup job or startup hook. No new infrastructure needed. The staleness check happens naturally every time the status is read.

**Alternative considered**: Application-level cleanup on startup or periodic task. Rejected because it adds complexity and a new failure mode. Query-level is self-healing on every read.

### 2. `get_latest_sync_status` marks expired records with derived `failed` status

The `SyncStatusResponse` model validator already derives `status` from the `success` field. We extend this: if `success IS NULL` AND `started_at` is older than 10 minutes, the query returns the record with a synthetic `timed_out` flag. The schema validator then maps this to `status: "failed"` with an appropriate error message.

**Alternative considered**: Update the actual DB record (set `success=False`). Rejected because it requires a separate write operation that could itself fail (the same catch-22 we're fixing).

### 3. Daily sync schedule: 09:00 WIB (`0 2 * * *` UTC)

Move from `0 1 * * *` (08:00 WIB) to `0 2 * * *` (09:00 WIB). Cloud SQL starts at 08:30 WIB, giving a 30-minute buffer for the instance to fully start and accept connections.

## Risks / Trade-offs

- **[10-min window]** A sync that legitimately takes >10 minutes would be incorrectly marked as failed. → Mitigation: Current syncs take 1-5 minutes. If data grows, the timeout constant can be increased. It's a single constant in one query.
- **[No DB update]** Stale records are never actually cleaned up in the DB, just treated as failed at read time. → Mitigation: Acceptable for now. The table grows slowly (one record per sync). A future cleanup job could archive old records.
