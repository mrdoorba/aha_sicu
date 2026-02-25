## Why

The Brand page shows "Menyinkronkan..." forever because a sync record is permanently stuck with `success=NULL, completed_at=NULL`. On Feb 24, sync was triggered at 18:57 WIB — 3 minutes before Cloud SQL scheduled shutdown at 18:30+delay. By 19:01 WIB the DB was off, so both the Meeting sync write and the error handler's status update failed with `[Errno 111] Connection refused`. The record is now stuck, blocking all future syncs (409 Conflict). Additionally, the daily scheduled sync runs at 08:00 WIB — 30 minutes before Cloud SQL even starts at 08:30 WIB.

## What Changes

- Add a staleness timeout to `is_sync_in_progress()` — auto-expire sync records older than 10 minutes so stuck records can't block future syncs forever
- Add the same staleness check to `get_latest_sync_status()` — return `failed` instead of `in_progress` for expired records so the UI stops showing "Menyinkronkan..."
- Change daily sync schedule from 08:00 WIB (`0 1 * * *`) to 09:00 WIB (`0 2 * * *`) — giving 30 minutes buffer after Cloud SQL starts at 08:30 WIB

## Capabilities

### New Capabilities

_(none — this is a fix to existing sync behavior)_

### Modified Capabilities

_(no spec-level requirement changes — these are implementation-level fixes and schedule adjustments)_

## Impact

- **Backend**: `backend/app/db/queries/sync_status.py` — modify `is_sync_in_progress()` and `get_latest_sync_status()` queries
- **Backend**: `backend/app/modules/sync/schemas.py` — adjust status derivation in `SyncStatusResponse` for timed-out records
- **Infrastructure**: `infrastructure/terraform/scheduler.tf` — change daily sync cron from `0 1 * * *` to `0 2 * * *`
- **Existing tests**: May need updates for new staleness timeout behavior
