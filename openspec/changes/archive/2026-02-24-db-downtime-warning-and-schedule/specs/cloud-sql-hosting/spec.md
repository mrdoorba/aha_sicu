## MODIFIED Requirements

### Requirement: Cloud SQL scheduled start and stop
Two Cloud Scheduler jobs SHALL control the Cloud SQL instance activation:
- A START job at 08:30 WIB (cron: `30 1 * * *` UTC) setting `activationPolicy` to `ALWAYS`
- A STOP job at 18:30 WIB (cron: `30 11 * * *` UTC) setting `activationPolicy` to `NEVER`

A dedicated service account with `roles/cloudsql.admin` SHALL be used for the scheduler jobs.

#### Scenario: Instance starts in the morning
- **WHEN** the clock reaches 08:30 WIB
- **THEN** Cloud Scheduler sends an HTTP PATCH to the SQL Admin API setting `activationPolicy: ALWAYS`

#### Scenario: Instance stops in the evening
- **WHEN** the clock reaches 18:30 WIB
- **THEN** Cloud Scheduler sends an HTTP PATCH to the SQL Admin API setting `activationPolicy: NEVER`

#### Scenario: Requests during downtime
- **WHEN** a user sends a request to the API between 18:30 and 08:30 WIB
- **THEN** the API returns an error (database connection fails) but no data is lost
