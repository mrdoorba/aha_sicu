## ADDED Requirements

### Requirement: Cloud SQL Auth Proxy in CI/CD
The backend deploy workflow SHALL start Cloud SQL Auth Proxy before running Alembic migrations. The proxy SHALL listen on `127.0.0.1:5432` and connect to the Cloud SQL instance specified by the `CLOUD_SQL_INSTANCE_CONNECTION` GitHub Actions variable.

#### Scenario: Auth Proxy starts before migrations
- **WHEN** the deploy workflow runs the migration step
- **THEN** Cloud SQL Auth Proxy is running and listening on `127.0.0.1:5432`

#### Scenario: Auth Proxy authenticates via Workload Identity
- **WHEN** Cloud SQL Auth Proxy starts in GitHub Actions
- **THEN** it authenticates using the Deploy SA credentials already established by the GCP auth step

### Requirement: CI/CD migration URL construction
The deploy workflow SHALL construct the `DATABASE_URL` for migrations using the database credentials and the Auth Proxy's localhost address, in the format `postgresql://{user}:{password}@127.0.0.1:5432/{database}`.

#### Scenario: Migration connects via Auth Proxy
- **WHEN** Alembic migrations run in CI/CD
- **THEN** they connect to `127.0.0.1:5432` (Auth Proxy) instead of a remote database URL

### Requirement: CI/CD fetches database password from Secret Manager
The deploy workflow SHALL fetch the database password from Secret Manager secret `aha_sicu_{env}_db_password` instead of fetching the full `DATABASE_URL` from `aha_sicu_{env}_db_url`.

#### Scenario: Password fetched for dev deployment
- **WHEN** the dev deploy workflow runs
- **THEN** it fetches the password from `aha_sicu_dev_db_password` secret

#### Scenario: Password fetched for prod deployment
- **WHEN** the prod deploy workflow runs
- **THEN** it fetches the password from `aha_sicu_prod_db_password` secret

### Requirement: New GitHub Actions variables
The deploy workflow SHALL require the following new GitHub Actions environment variables:
- `CLOUD_SQL_INSTANCE_CONNECTION`: Full instance connection name (format: `project:region:instance`)
- `DB_USER`: Database username
- `DB_NAME`: Database name

The existing `DB_SECRET_NAME` variable SHALL reference the new password-only secret name.

#### Scenario: All required variables available
- **WHEN** the deploy workflow starts
- **THEN** it can access `CLOUD_SQL_INSTANCE_CONNECTION`, `DB_USER`, `DB_NAME`, and `DB_SECRET_NAME` from the environment configuration

### Requirement: Auth Proxy cleanup after migrations
The deploy workflow SHALL stop the Cloud SQL Auth Proxy after migrations complete (whether successful or failed) to avoid blocking subsequent workflow steps.

#### Scenario: Proxy stopped after successful migration
- **WHEN** Alembic migrations complete successfully
- **THEN** the Cloud SQL Auth Proxy process is terminated

#### Scenario: Proxy stopped after failed migration
- **WHEN** Alembic migrations fail
- **THEN** the Cloud SQL Auth Proxy process is still terminated before the step exits
