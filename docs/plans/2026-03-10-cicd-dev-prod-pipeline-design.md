# CI/CD Pipeline: Dev → Prod with Regression Prevention

**Date:** 2026-03-10
**Status:** Approved
**Team:** 1 Dev + 1 Domain Expert

## Problem

Single `develop` branch deploys directly to the only live environment. Feature work and bug fixes disrupt active users. No separation between development and production.

## Solution

Two-environment, branch-based promotion with additive-only migration safety.

## 1. Environment & Branch Strategy

```
develop branch → auto-deploy → DEV environment (developer playground)
main branch    → auto-deploy → PROD environment (user-facing)
```

### Resource Naming (`aha-coms-sicu` prefix)

| Resource | DEV | PROD |
|----------|-----|------|
| Cloud Run | `aha-coms-sicu-dev-api` | `aha-coms-sicu-prod-api` |
| Database | `aha_coms_sicu_dev` | `aha_coms_sicu_prod` |
| Firebase Hosting | `aha-coms-sicu-dev` | `aha-coms-sicu-prod` |
| Secrets | `aha_coms_sicu_dev_*` | `aha_coms_sicu_prod_*` |
| GCS Bucket | `aha-coms-sicu-dev-uploads` | `aha-coms-sicu-prod-uploads` |

### Promotion Flow

1. Develop on `develop` branch → auto-deploys to DEV
2. Domain expert tests on DEV URL
3. When approved → create PR from `develop` → `main`
4. Merge → auto-deploys to PROD

### Firebase

Same Firebase project for both environments. User authentication is shared; app-level authorization is per-database.

## 2. CI/CD Pipeline

### Workflow 1: CI Gate (`ci.yml` — already exists)

Triggers on every PR to `develop` or `main`:

- Backend: ruff lint + pytest
- Frontend: eslint + tsc typecheck + vitest
- Blocks merge on failure

No changes needed.

### Workflow 2: Deploy to DEV (existing — needs resource rename)

Triggers on push to `develop`:

1. Build Docker image
2. Push to Artifact Registry
3. Run Alembic migrations on DEV DB
4. Deploy Cloud Run revision
5. Deploy Firebase Hosting
6. Run smoke tests

### Workflow 3: Deploy to PROD (needs activation)

Triggers on push to `main`:

1. Build Docker image
2. Push to Artifact Registry
3. **Create Cloud SQL backup** (safety net before migration)
4. Run Alembic migrations on PROD DB
5. Deploy Cloud Run revision
6. Deploy Firebase Hosting
7. Run smoke tests
8. **Cleanup:** delete pre-deploy backups older than the last 5

### Rollback Strategy

| Method | Speed | When to use |
|--------|-------|-------------|
| Cloud Run revision rollback (`gcloud run services update-traffic`) | ~10 seconds | Code bug, UI issue — DB is fine |
| `git revert` on `main` → auto-redeploy | ~3 minutes | Need a permanent code fix in git history |
| Cloud SQL point-in-time recovery | ~10 minutes | Last resort — catastrophic data corruption (causes data loss after recovery point) |

## 3. Database Safety

### Hard Rules

1. **All migrations MUST be additive** — `CREATE TABLE`, `ADD COLUMN`, `ADD INDEX`, `INSERT` only
2. **Destructive changes require two-step release:**
   - Release 1: Add new structure, backfill data, code reads/writes both old and new
   - Release 2: Remove old structure, code uses only new
3. **No exceptions.** Violating this risks prod data loss.

### Protection Layers

| Layer | Mechanism |
|-------|-----------|
| Isolation | Separate databases per environment — dev code cannot reach prod DB |
| Order | Migrations run before Cloud Run revision swap |
| Backup | Pre-migration backup on every prod deploy |
| Automatic backups | Cloud SQL daily backups, 7-day retention (GCP default) |
| Retention | Keep last 5 pre-deploy backups, auto-delete older ones |

## 4. One-Time Bootstrap (Dev → Prod)

### Step 1: Terraform — Rename Dev + Create Prod

Update Terraform `variables.tf` to use `aha-coms-sicu` prefix:
- Rename/recreate dev resources with new names
- Create prod Cloud Run, Firebase Hosting, GCS bucket, secrets

Database rename (cannot rename in-place):
- Create `aha_coms_sicu_dev` database
- `pg_dump` from `aha_sicu_dev` → `pg_restore` into `aha_coms_sicu_dev`
- Verify data integrity (row counts on key tables)
- Drop old `aha_sicu_dev` + `aha_sicu_prod` once confirmed

### Step 2: Clone Dev DB → Prod DB

```
pg_dump aha_coms_sicu_dev → pg_restore into aha_coms_sicu_prod
```

Verify row counts match on: users, brands, evaluations, brand_uploads, calculator_results.

### Step 3: Populate Prod Secrets

Add values to Secret Manager:
- `aha_coms_sicu_prod_db_password` — **new password**, different from dev
- `aha_coms_sicu_prod_firebase_admin` — same Firebase project credentials
- `aha_coms_sicu_prod_gsheets_credentials` — same credentials
- `aha_coms_sicu_prod_smtp_password` — same SMTP credentials

### Step 4: GitHub Environment Variables

Create `production` environment in GitHub repo settings:
- `GCP_PROJECT_ID`, `GCP_REGION`
- `WORKLOAD_IDENTITY_PROVIDER`, `DEPLOY_SERVICE_ACCOUNT`
- `CLOUD_RUN_SERVICE` = `aha-coms-sicu-prod-api`
- `ARTIFACT_REGISTRY_URL`
- `DB_SECRET_NAME`, `CLOUD_SQL_INSTANCE_CONNECTION`, `DB_USER`, `DB_NAME`
- `FIREBASE_HOSTING_SITE` = `aha-coms-sicu-prod`
- `VITE_API_BASE_URL` = prod Cloud Run URL
- `VITE_FIREBASE_*` = same Firebase config

### Step 5: Initial Prod Deploy

Merge `develop` → `main` → triggers first prod deploy.

### Step 6: Verify

- Smoke tests pass against prod URLs
- Domain expert confirms prod works identically to dev
- Bookmark rollback command: `gcloud run services update-traffic aha-coms-sicu-prod-api --to-revisions=REVISION=100`

## 5. Secret Management

All secrets in GCP Secret Manager, accessed via IAM (no keys in code):

| Secret | Dev | Prod |
|--------|-----|------|
| DB password | `aha_coms_sicu_dev_db_password` | `aha_coms_sicu_prod_db_password` (different value) |
| Firebase admin | `aha_coms_sicu_dev_firebase_admin` | `aha_coms_sicu_prod_firebase_admin` |
| GSheets credentials | `aha_coms_sicu_dev_gsheets_credentials` | `aha_coms_sicu_prod_gsheets_credentials` |
| SMTP password | `aha_coms_sicu_dev_smtp_password` | `aha_coms_sicu_prod_smtp_password` |

Authentication: Workload Identity Federation (GitHub Actions → GCP) — zero service account keys.
