## Why

Users who access the app outside database operating hours see raw error states (failed API calls, empty screens) with no explanation of what's happening. Additionally, the current DB schedule (07:30–19:00 WIB) needs adjustment: active hours should be 08:00–18:30 WIB and the scheduler start job should fire at 08:30 WIB to align with actual usage patterns.

## What Changes

- Add a modal dialog (center popup with overlay) that appears when API calls fail due to database unavailability, informing users of operating hours (08:00–18:30 WIB) with a "Mengerti" dismiss button
- Update Cloud SQL scheduler START job from 07:30 WIB to 08:30 WIB
- Update Cloud SQL scheduler STOP job from 19:00 WIB to 18:30 WIB

## Capabilities

### New Capabilities
- `db-downtime-warning`: Frontend modal dialog that detects API failures caused by database downtime and displays a user-friendly warning with operating hours information

### Modified Capabilities
- `cloud-sql-hosting`: Scheduled start/stop times are changing — START from 07:30 to 08:30 WIB, STOP from 19:00 to 18:30 WIB

## Impact

- **Frontend**: New modal component, API error detection logic in API client or React Query error handling
- **Infrastructure**: `cloud_sql.tf` — updated cron schedules for `google_cloud_scheduler_job.cloud_sql_start` and `google_cloud_scheduler_job.cloud_sql_stop`
- **No backend changes required** — the backend behavior (returning 500 when DB is down) stays the same; the frontend handles the UX
