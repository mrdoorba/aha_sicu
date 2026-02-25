## ADDED Requirements

### Requirement: Cloud SQL instance provisioning
Terraform SHALL provision a single Cloud SQL PostgreSQL instance in `asia-southeast2` (Jakarta) with tier `db-f1-micro`, 10 GB SSD storage, public IP enabled, SSL required, and automated backups disabled. The instance SHALL have `deletion_protection` enabled for the `prod` environment and disabled for `dev`.

#### Scenario: Instance created with correct configuration
- **WHEN** Terraform applies the Cloud SQL configuration
- **THEN** a `google_sql_database_instance` is created in `asia-southeast2` with tier `db-f1-micro`, 10 GB SSD, public IP, SSL required, no automated backups

#### Scenario: Prod instance has deletion protection
- **WHEN** `var.environment` is `prod`
- **THEN** the Cloud SQL instance has `deletion_protection = true`

#### Scenario: Dev instance allows deletion
- **WHEN** `var.environment` is `dev`
- **THEN** the Cloud SQL instance has `deletion_protection = false`

### Requirement: Dual database provisioning
Terraform SHALL create two databases on the single Cloud SQL instance: `aha_sicu_dev` and `aha_sicu_prod`. A single database user SHALL be created for application access.

#### Scenario: Both databases exist on one instance
- **WHEN** Terraform applies the configuration
- **THEN** `google_sql_database` resources for `aha_sicu_dev` and `aha_sicu_prod` exist on the same instance

#### Scenario: Database user created
- **WHEN** Terraform applies the configuration
- **THEN** a `google_sql_user` exists with access to the instance

### Requirement: Cloud Run Cloud SQL connector
Cloud Run SHALL be configured with `cloud_sql_instances` annotation referencing the Cloud SQL instance connection name. The application SHALL connect via Unix socket at `/cloudsql/<instance-connection-name>`.

#### Scenario: Cloud Run template includes Cloud SQL connection
- **WHEN** the Cloud Run service is deployed
- **THEN** the template includes a `volumes` and `volume_mounts` configuration for the Cloud SQL instance (or `cloud_sql_instance_connection` annotation depending on Cloud Run v2 API)

#### Scenario: Application connects via Unix socket
- **WHEN** the backend starts in Cloud Run
- **THEN** asyncpg connects using the DSN `postgresql://{user}:{pass}@/{db}?host=/cloudsql/{instance}`

### Requirement: Connection pool sizing
The application SHALL use a connection pool with `min_size=1` and `max_size=5` as defaults, configurable via `DATABASE_POOL_MIN` and `DATABASE_POOL_MAX` environment variables.

#### Scenario: Default pool size
- **WHEN** the application starts without custom pool size environment variables
- **THEN** the asyncpg pool is created with `min_size=1` and `max_size=5`

#### Scenario: Custom pool size
- **WHEN** `DATABASE_POOL_MIN=2` and `DATABASE_POOL_MAX=10` are set
- **THEN** the asyncpg pool is created with `min_size=2` and `max_size=10`

### Requirement: Database connection URL construction
The application SHALL construct the database connection URL from individual components (`DB_USER`, `DB_PASSWORD`, `DB_NAME`, `CLOUD_SQL_INSTANCE`) when `DATABASE_URL` is not explicitly set. When `DATABASE_URL` is set, it SHALL take precedence (for local development and backward compatibility).

#### Scenario: URL constructed from components in Cloud Run
- **WHEN** `DATABASE_URL` is not set and `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `CLOUD_SQL_INSTANCE` are all set
- **THEN** the effective database URL is `postgresql://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?host=/cloudsql/{CLOUD_SQL_INSTANCE}`

#### Scenario: Explicit DATABASE_URL takes precedence
- **WHEN** `DATABASE_URL` is set (e.g., local dev with `postgresql://user:pass@localhost:5432/db`)
- **THEN** the application uses `DATABASE_URL` directly, ignoring individual components

#### Scenario: No connection configured
- **WHEN** neither `DATABASE_URL` nor the individual components are set
- **THEN** the application starts without a database pool (existing behavior for tests)

### Requirement: Cloud SQL IAM permissions
The Cloud Run service account SHALL have `roles/cloudsql.client` to connect via the built-in connector. The Deploy service account SHALL have `roles/cloudsql.client` for CI/CD migrations.

#### Scenario: Cloud Run SA can connect to Cloud SQL
- **WHEN** the Cloud Run service attempts to connect to Cloud SQL
- **THEN** the connection succeeds because the service account has `roles/cloudsql.client`

#### Scenario: Deploy SA can connect to Cloud SQL
- **WHEN** the CI/CD pipeline starts Cloud SQL Auth Proxy
- **THEN** the proxy authenticates successfully because the deploy SA has `roles/cloudsql.client`

### Requirement: Cloud SQL scheduled start and stop
Two Cloud Scheduler jobs SHALL control the Cloud SQL instance activation:
- A START job at 07:30 WIB (cron: `30 0 * * *` UTC) setting `activationPolicy` to `ALWAYS`
- A STOP job at 19:00 WIB (cron: `0 12 * * *` UTC) setting `activationPolicy` to `NEVER`

A dedicated service account with `roles/cloudsql.admin` SHALL be used for the scheduler jobs.

#### Scenario: Instance starts in the morning
- **WHEN** the clock reaches 07:30 WIB
- **THEN** Cloud Scheduler sends an HTTP PATCH to the SQL Admin API setting `activationPolicy: ALWAYS`

#### Scenario: Instance stops in the evening
- **WHEN** the clock reaches 19:00 WIB
- **THEN** Cloud Scheduler sends an HTTP PATCH to the SQL Admin API setting `activationPolicy: NEVER`

#### Scenario: Requests during downtime
- **WHEN** a user sends a request to the API between 19:00 and 07:30 WIB
- **THEN** the API returns an error (database connection fails) but no data is lost

### Requirement: Secret Manager pattern update
The Secret Manager secret SHALL store only the database password (secret ID: `aha_sicu_{env}_db_password`) instead of the full database URL. The old `aha_sicu_{env}_db_url` secret resource SHALL be removed from Terraform.

#### Scenario: Password secret exists
- **WHEN** Terraform applies the configuration
- **THEN** a Secret Manager secret `aha_sicu_{env}_db_password` exists

#### Scenario: Old db_url secret removed from Terraform
- **WHEN** Terraform applies the configuration
- **THEN** the `aha_sicu_{env}_db_url` secret resource is no longer managed by Terraform

### Requirement: Region migration to Jakarta
All regional Terraform resources SHALL use `asia-southeast2` (Jakarta) as the region. This includes Cloud Run, Artifact Registry, Cloud Scheduler, GCS bucket, and Cloud SQL.

#### Scenario: Default region is Jakarta
- **WHEN** Terraform is initialized with default variables
- **THEN** `var.region` defaults to `asia-southeast2`

#### Scenario: All regional resources in Jakarta
- **WHEN** Terraform applies the configuration
- **THEN** Cloud Run, Artifact Registry, Cloud Scheduler, GCS bucket, and Cloud SQL are all in `asia-southeast2`

### Requirement: Terraform version constraint update
The Terraform configuration SHALL require version `>= 1.5` (updated from `>= 1.0`).

#### Scenario: Terraform version constraint
- **WHEN** Terraform initializes the configuration
- **THEN** it requires Terraform CLI version `>= 1.5`

### Requirement: Cloud SQL Admin API enablement
Terraform SHALL enable the `sqladmin.googleapis.com` API on the project.

#### Scenario: SQL Admin API enabled
- **WHEN** Terraform applies the configuration
- **THEN** the `sqladmin.googleapis.com` service is enabled on the project
