## Context

The backend currently connects to Neon PostgreSQL (external SaaS) via asyncpg with a TCP connection string stored in GCP Secret Manager. All GCP infrastructure (Cloud Run, Artifact Registry, Cloud Scheduler, GCS) lives in `asia-southeast1` (Singapore). The CI/CD pipeline runs Alembic migrations by fetching `DATABASE_URL` from Secret Manager and connecting directly to Neon's public endpoint.

The project serves 2-5 users in Indonesia. There are 9 tables with heavy JSONB usage, no Neon-specific features, and raw parameterized SQL queries (no ORM).

## Goals / Non-Goals

**Goals:**
- Consolidate database billing into GCP (single invoice)
- Provision Cloud SQL PostgreSQL via Terraform with cost optimization (scheduled start/stop, shared instance)
- Migrate all regional infrastructure from Singapore to Jakarta
- Maintain zero application-level behavior changes (same queries, same schema)
- Update CI/CD pipeline for Cloud SQL Auth Proxy-based migrations

**Non-Goals:**
- Changing the database schema or query patterns
- Adding an ORM or changing from asyncpg
- Setting up read replicas or high availability
- Implementing VPC (using built-in Cloud SQL connector instead)
- Migrating data (manual one-time step, not automated in Terraform/CI)

## Decisions

### 1. Single Cloud SQL instance with two databases

**Decision**: One `db-f1-micro` instance hosting both `aha_sicu_dev` and `aha_sicu_prod` databases.

**Why**: At ~Rp 204,186/month for one instance, running two would double the cost for no benefit at this scale (2-5 users). The risk of shared-instance failures affecting both environments is acceptable — this is not a high-availability requirement.

**Alternative considered**: Separate instances per environment — rejected due to cost doubling with minimal benefit.

### 2. Cloud Run built-in Cloud SQL connector (Unix socket)

**Decision**: Use Cloud Run's native `cloud_sql_instances` annotation which runs Cloud SQL Auth Proxy as an automatic sidecar, creating a Unix socket at `/cloudsql/<instance-connection-name>`.

**Why**: Free, secure (IAM-authenticated), no VPC connector needed ($6-7/month saved). asyncpg natively supports Unix socket connections via the `host` parameter in the DSN.

**Alternative considered**:
- VPC + Serverless VPC connector — rejected, adds $6-7/month and complexity.
- Public IP with direct TCP — rejected, less secure and requires SSL configuration.

### 3. Separate credential storage with per-context URL construction

**Decision**: Store `db_password` in Secret Manager (replacing the full `DATABASE_URL`). Each context constructs its own connection URL:
- **Cloud Run**: `postgresql://{user}:{pass}@/{db}?host=/cloudsql/{instance}` (Unix socket)
- **CI/CD**: `postgresql://{user}:{pass}@127.0.0.1:5432/{db}` (Auth Proxy TCP)
- **Local dev**: `postgresql://{user}:{pass}@localhost:5432/{db}` (direct TCP)

The Python `Settings` class gains `db_user`, `db_password`, `db_name`, `cloud_sql_instance` fields. A `database_url` field remains as an override for local development.

**Why**: Cloud Run (Unix socket) and CI/CD (TCP via Auth Proxy) need different URL formats. Storing a full URL in Secret Manager only works for one context. Splitting credentials lets each context construct the appropriate format.

**Alternative considered**: Two separate secrets (one per URL format) — rejected, duplicates the password and adds maintenance burden.

### 4. Connection pool sizing: min=1, max=5

**Decision**: Reduce asyncpg pool from min=5/max=20 to min=1/max=5.

**Why**: `db-f1-micro` has ~25 max connections and only 0.6 GB RAM. With 2-5 users, 5 max connections is sufficient. min=1 avoids holding idle connections on a resource-constrained instance.

### 5. Scheduled start/stop via Cloud Scheduler → SQL Admin API

**Decision**: Two Cloud Scheduler jobs directly calling the Cloud SQL Admin REST API via HTTP PATCH:
- START at 07:30 WIB (`30 0 * * *` UTC): `{"settings": {"activationPolicy": "ALWAYS"}}`
- STOP at 19:00 WIB (`0 12 * * *` UTC): `{"settings": {"activationPolicy": "NEVER"}}`

A dedicated service account with `roles/cloudsql.admin` is used for the scheduler.

**Why**: Cloud Scheduler can call Google APIs directly with OAuth — no Cloud Functions needed. Saves compute cost (~52% of daily compute hours eliminated).

**Alternative considered**: Cloud Functions triggered by Scheduler — rejected, adds unnecessary infrastructure and cost.

### 6. Region migration: asia-southeast1 → asia-southeast2

**Decision**: Change `var.region` default and both tfvars to `asia-southeast2` (Jakarta).

**Why**: Cloud SQL is ~7% cheaper in Jakarta (Rp 204,186 vs Rp 219,236/month). Users are in Indonesia, so latency improves marginally (~20ms → ~5ms). All other services (Cloud Run, Artifact Registry, etc.) have identical pricing between regions.

**Impact**: All regional Terraform resources reference `var.region`, so the change propagates cleanly. Existing Singapore resources will be destroyed and recreated in Jakarta. Cloud Run URLs will change.

### 7. CI/CD migration flow with Cloud SQL Auth Proxy

**Decision**: In `deploy-backend.yml`, add a step to download and start Cloud SQL Auth Proxy before running Alembic migrations. The proxy listens on `127.0.0.1:5432` and the migration step constructs a TCP-based `DATABASE_URL`.

**Why**: GitHub Actions cannot use Unix sockets to reach Cloud SQL. The Auth Proxy provides authenticated, encrypted TCP access. The Deploy SA already has GCP auth via Workload Identity Federation.

## Risks / Trade-offs

- **Shared instance downtime**: If the Cloud SQL instance restarts or has maintenance, both dev and prod are affected → Acceptable for 2-5 users; no SLA requirement.
- **Scheduled stop window**: Any requests between 19:00-07:30 WIB will fail with database connection errors → Acceptable; team only works during business hours. Cloud Run will return 500s but no data loss.
- **Region migration destroys resources**: Terraform will destroy Singapore resources and create Jakarta ones → Plan during low-usage window. Cloud Run URLs change, update any hardcoded references (CORS in storage.tf, GitHub Actions vars).
- **No automated backups**: Data could be lost if instance is accidentally deleted → Mitigation: `deletion_protection = true` for prod, and data can be re-synced from Google Sheets (source of truth).
- **Auth Proxy in CI adds ~10s to deploy**: Download and startup of Cloud SQL Auth Proxy adds latency to CI/CD pipeline → Acceptable tradeoff for secure database access.

## Migration Plan

1. **Terraform apply** (Jakarta): Provision Cloud SQL instance, databases, user, IAM, scheduler jobs. Update Cloud Run config, secrets, region.
2. **Update GitHub Actions variables**: New `CLOUD_SQL_INSTANCE_CONNECTION`, update `DB_SECRET_NAME`, update `ARTIFACT_REGISTRY_URL` (region changed).
3. **Set secret values**: Add `db_password` secret version in Secret Manager.
4. **Deploy backend code**: Push changes to connection.py, config.py, env.py, deploy-backend.yml.
5. **Run Alembic migrations**: Against Cloud SQL (via CI/CD or manual).
6. **Data migration**: `pg_dump` from Neon → `pg_restore` to Cloud SQL (manual, with downtime).
7. **Verify**: Confirm app works end-to-end with Cloud SQL.
8. **Decommission Neon**: Cancel Neon account/project.

**Rollback**: If Cloud SQL fails, revert `DATABASE_URL` secret to Neon connection string and redeploy. Neon should remain active until full verification.

## Open Questions

- None — all decisions resolved during exploration phase.
