## Why

The project currently uses Neon (external SaaS) for PostgreSQL, creating a separate billing line outside of GCP. The client wants consolidated billing under one GCP account. Migrating to Cloud SQL PostgreSQL brings the database into GCP alongside Cloud Run, Artifact Registry, and all other infrastructure — reducing cost (~Rp 204,186/month for Jakarta) and simplifying operations. Additionally, all infrastructure is being relocated from Singapore (asia-southeast1) to Jakarta (asia-southeast2) for lower Cloud SQL pricing and closer proximity to Indonesian users.

## What Changes

- **BREAKING**: Replace Neon PostgreSQL with Cloud SQL PostgreSQL (db-f1-micro, 10 GB SSD, single instance with two databases: `aha_sicu_dev` and `aha_sicu_prod`)
- **BREAKING**: Migrate all GCP resources from `asia-southeast1` (Singapore) to `asia-southeast2` (Jakarta) — Cloud Run, Artifact Registry, Cloud Scheduler, GCS bucket, Cloud SQL
- Add Cloud SQL built-in connector to Cloud Run (free Unix socket, no VPC needed)
- Add scheduled start/stop for Cloud SQL instance via Cloud Scheduler (07:30–19:00 WIB) to save cost
- Update CI/CD deploy workflow to use Cloud SQL Auth Proxy for database migrations
- Change secret pattern from full `DATABASE_URL` to individual credentials (`db_password`), constructing connection URLs per context
- Reduce connection pool from min=5/max=20 to min=1/max=5 (sufficient for 2-5 users)
- Move daily sync schedule from 06:00 to 08:00 WIB (after DB starts at 07:30)
- Update Terraform `required_version` from `>= 1.0` to `>= 1.5`

## Capabilities

### New Capabilities

- `cloud-sql-hosting`: Cloud SQL PostgreSQL instance provisioning, IAM, Cloud Run integration, and scheduled start/stop
- `cloud-sql-cicd`: CI/CD pipeline changes for database migrations via Cloud SQL Auth Proxy

### Modified Capabilities

- `sync-polling`: Daily sync schedule changes from 06:00 to 08:00 WIB to accommodate Cloud SQL start time

## Impact

- **Infrastructure (Terraform)**: All regional resources recreated in Jakarta — Cloud Run, Artifact Registry, GCS bucket, Cloud Scheduler. New Cloud SQL resources added. Secrets updated.
- **Backend code**: `config.py`, `connection.py`, `.env.example`, `migrations/env.py` updated for new connection pattern
- **CI/CD**: `deploy-backend.yml` updated with Cloud SQL Auth Proxy step and new variable requirements
- **Cloud Run URLs**: Will change after region migration (new deployment URLs)
- **GitHub Actions variables**: New variables needed (`CLOUD_SQL_INSTANCE_CONNECTION`), existing `DB_SECRET_NAME` changes meaning
- **Data**: One-time pg_dump/pg_restore from Neon to Cloud SQL (manual step with downtime)
- **Neon**: Decommissioned after successful migration
