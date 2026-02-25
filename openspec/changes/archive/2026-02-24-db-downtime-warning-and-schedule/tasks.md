## 1. Frontend — Downtime Warning Modal

- [x] 1.1 Create `DowntimeWarningDialog` component using existing Radix Dialog primitive — centered modal with overlay, warning icon, operating hours message (08:00–18:30 WIB), and "Mengerti" dismiss button
- [x] 1.2 Add downtime state management: create a context or state in App.tsx to track whether the modal has been shown and dismissed in the current session
- [x] 1.3 Wire global error detection into React Query — add `onError` callbacks to `QueryCache` and `MutationCache` in the `QueryClient` config to detect HTTP 500 errors and trigger the downtime modal

## 2. Infrastructure — Update Cloud SQL Schedule

- [x] 2.1 Update `cloud_sql.tf` START job: change cron from `30 0 * * *` to `30 1 * * *` (08:30 WIB) and update description
- [x] 2.2 Update `cloud_sql.tf` STOP job: change cron from `0 12 * * *` to `30 11 * * *` (18:30 WIB) and update description
