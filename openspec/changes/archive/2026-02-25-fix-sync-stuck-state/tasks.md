## 1. Staleness timeout in DB queries

- [x] 1.1 Update `is_sync_in_progress()` in `backend/app/db/queries/sync_status.py` to add a 10-minute staleness check: `WHERE completed_at IS NULL AND started_at > NOW() - INTERVAL '10 minutes'`
- [x] 1.2 Update `get_latest_sync_status()` in `backend/app/db/queries/sync_status.py` to return a `timed_out` flag when a record has `completed_at IS NULL` and `started_at` older than 10 minutes

## 2. Schema status derivation

- [x] 2.1 Update `SyncStatusResponse.compute_derived_fields()` in `backend/app/modules/sync/schemas.py` to handle the `timed_out` flag — map it to `status: "failed"` with error message `"Sync timed out after 10 minutes"`

## 3. Schedule adjustment

- [x] 3.1 Change daily sync cron in `infrastructure/terraform/scheduler.tf` from `0 1 * * *` (08:00 WIB) to `0 2 * * *` (09:00 WIB), update comment and description

## 4. Tests

- [x] 4.1 Add test for `is_sync_in_progress()` returning `False` when sync record is older than 10 minutes
- [x] 4.2 Add test for `get_latest_sync_status()` returning timed-out status for stale records
- [x] 4.3 Add test for `SyncStatusResponse` mapping timed-out records to `status: "failed"`
