# Deployment Guide

This document covers the full CI/CD pipeline, infrastructure bootstrap, secret management, and post-deploy verification for the AHA SICU project.

---

## Table of Contents

1. [CI Pipeline](#ci-pipeline)
2. [Deployment Flow](#deployment-flow)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Terraform Bootstrap](#terraform-bootstrap)
6. [Secret Management](#secret-management)
7. [Smoke Tests](#smoke-tests)
8. [Manual Verification Checklist](#manual-verification-checklist)

---

## CI Pipeline

Every pull request targeting `develop` or `main` triggers two parallel CI jobs defined in `.github/workflows/ci.yml`.

### Backend Tests & Lint

Runs in the `backend/` directory using Python 3.14 via `uv`:

| Step               | Command              |
|--------------------|----------------------|
| Install deps       | `uv sync --all-extras` |
| Lint               | `uv run ruff check .`  |
| Tests              | `uv run pytest -v`     |

### Frontend Tests & Lint

Runs in the `frontend/` directory using Node.js 20:

| Step               | Command              |
|--------------------|----------------------|
| Install deps       | `npm ci`             |
| Lint               | `npm run lint`       |
| Type check         | `npx tsc --noEmit`   |
| Tests              | `npx vitest run`     |
| Build              | `npm run build`      |

Both jobs must pass before a PR can be merged (enforced via branch protection rules on `develop` and `main`).

---

## Deployment Flow

```
                    Pull Request
                        |
               CI checks (lint + test)
                        |
                    PR approved
                        |
           +------------+------------+
           |                         |
     merge to develop          merge to main
           |                         |
     auto-deploy DEV         deploy PRODUCTION
     (backend + frontend)    (backend + frontend)
```

Deployments are triggered by pushes to `develop` or `main`, scoped to changed paths:

- **Backend** (`backend/**` changed) -- `.github/workflows/deploy-backend.yml`
- **Frontend** (`frontend/**` changed) -- `.github/workflows/deploy-frontend.yml`

Both workflows also support `workflow_dispatch` for manual triggering. Concurrency groups prevent overlapping deploys on the same branch.

### Environment Mapping

| Branch    | GitHub Environment | Backend Target          | Frontend Target           |
|-----------|--------------------|-------------------------|---------------------------|
| `develop` | `dev`              | Cloud Run (dev service) | Firebase Hosting (dev)    |
| `main`    | `production`       | Cloud Run (prod service)| Firebase Hosting (prod)   |

---

## Backend Deployment

Defined in `.github/workflows/deploy-backend.yml`. Both dev and prod follow the same step sequence.

### Step-by-Step Pipeline

```
 1. Checkout code
 2. Authenticate to GCP (Workload Identity Federation)
 3. Ensure Cloud SQL is running (start if stopped)
 4. Create pre-migration backup (prod only)
 5. Start Cloud SQL Auth Proxy (port 5432)
 6. Run Alembic migrations against Cloud SQL
 7. Stop Cloud SQL Auth Proxy
 8. Build Docker image (Buildx with GHA cache)
 9. Push to Artifact Registry (sha + latest tags)
10. Deploy to Cloud Run
11. Health check via /docs
12. Cleanup old revisions (keep 2)
13. Cleanup old pre-deploy backups (prod only, keep 5)
```

### Required GitHub Actions Variables

Set these per environment (`dev` / `production`) in the repository settings:

| Variable                          | Description                                              |
|-----------------------------------|----------------------------------------------------------|
| `GCP_PROJECT_ID`                  | GCP project ID                                           |
| `GCP_REGION`                      | GCP region (e.g., `asia-southeast2`)                     |
| `WORKLOAD_IDENTITY_PROVIDER`      | Full WIF provider path (from Terraform output)           |
| `DEPLOY_SERVICE_ACCOUNT`          | Deploy service account email (from Terraform output)     |
| `CLOUD_RUN_SERVICE`               | Cloud Run service name (e.g., `aha-coms-sicu-dev-api`)   |
| `ARTIFACT_REGISTRY_URL`           | Docker push URL (from Terraform output)                  |
| `DB_SECRET_NAME`                  | Secret Manager secret name for the database password     |
| `CLOUD_SQL_INSTANCE_CONNECTION`   | Cloud SQL connection name (`project:region:instance`)    |
| `CLOUD_SQL_INSTANCE_NAME`         | Cloud SQL instance name (for backups and start/stop API) |
| `DB_USER`                         | Database username                                        |
| `DB_NAME`                         | Database name                                            |

### Authentication

Uses Workload Identity Federation -- no service account keys are stored in GitHub. The workflow requests an OIDC token and exchanges it for GCP credentials:

```yaml
- name: Authenticate to GCP
  uses: google-github-actions/auth@v3
  with:
    workload_identity_provider: ${{ vars.WORKLOAD_IDENTITY_PROVIDER }}
    service_account: ${{ vars.DEPLOY_SERVICE_ACCOUNT }}
```

### Database Migrations

A Cloud SQL Auth Proxy is started in the background to establish a secure tunnel. Alembic then runs migrations through it:

```bash
# Proxy runs on localhost:5432
./cloud-sql-proxy <INSTANCE_CONNECTION> --port 5432 &

# Migrations
export DB_PASSWORD=$(gcloud secrets versions access latest \
  --secret=<DB_SECRET_NAME> --project=<PROJECT_ID>)
export DATABASE_URL="postgresql://<DB_USER>:${DB_PASSWORD}@127.0.0.1:5432/<DB_NAME>"
uv run alembic -c app/db/migrations/alembic.ini upgrade head
```

The proxy is stopped with `kill $(pgrep -f cloud-sql-proxy)` in an `if: always()` step to guarantee cleanup.

### Docker Build and Push

Images are tagged with both the commit SHA and `latest`:

```
<ARTIFACT_REGISTRY_URL>/<CLOUD_RUN_SERVICE>:<commit-sha>
<ARTIFACT_REGISTRY_URL>/<CLOUD_RUN_SERVICE>:latest
```

Build caching uses GitHub Actions cache (`type=gha`).

### Cloud Run Deployment

The service is deployed using `google-github-actions/deploy-cloudrun@v3`. Dev deploys include the `--cpu-throttling` flag; production does not.

### Health Check

After deployment, the workflow curls the `/docs` endpoint (FastAPI Swagger UI) and expects an HTTP 2xx or 3xx response:

```bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "<SERVICE_URL>/docs" --max-time 30 || true)
```

A non-success status emits a GitHub Actions warning but does not fail the workflow.

### Revision Cleanup

Old Cloud Run revisions are pruned after each deploy, keeping only the 2 most recent:

```bash
gcloud run revisions list \
  --service=<SERVICE> --region=<REGION> \
  --format="value(name)" --sort-by="~createTime"
# Deletes all revisions beyond the first 2
```

---

## Frontend Deployment

Defined in `.github/workflows/deploy-frontend.yml`. Both dev and prod follow the same step sequence.

### Step-by-Step Pipeline

```
1. Checkout code
2. Setup Node.js 20
3. Install dependencies (npm ci)
4. Vite build with Firebase env vars
5. Authenticate to GCP (Workload Identity Federation)
6. Configure Firebase deploy target
7. Deploy to Firebase Hosting
8. Health check (GET root URL)
```

### Required GitHub Actions Variables

| Variable                     | Description                                      |
|------------------------------|--------------------------------------------------|
| `GCP_PROJECT_ID`             | GCP project ID                                   |
| `WORKLOAD_IDENTITY_PROVIDER` | Full WIF provider path (from Terraform output)   |
| `DEPLOY_SERVICE_ACCOUNT`     | Deploy service account email                     |
| `FIREBASE_HOSTING_SITE`      | Firebase Hosting site ID (e.g., `aha-coms-sicu-dev`)  |
| `VITE_FIREBASE_API_KEY`      | Firebase Web API key                             |
| `VITE_FIREBASE_AUTH_DOMAIN`  | Firebase Auth domain                             |
| `VITE_FIREBASE_PROJECT_ID`   | Firebase project ID                              |
| `VITE_API_BASE_URL`          | Backend API URL (Cloud Run service URL)          |

### Build

The Vite build injects Firebase configuration via environment variables:

```bash
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_API_BASE_URL=...
npm run build
```

### Firebase Deploy

The deploy target is configured dynamically, then deployed:

```bash
npx firebase-tools target:apply hosting <SITE_ID> <SITE_ID> --project <PROJECT_ID>
npx firebase-tools deploy --only hosting:<SITE_ID> --project <PROJECT_ID>
```

### Health Check

After deployment, the workflow checks the site root URL:

```bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://<SITE_ID>.web.app" --max-time 30 || true)
```

---

## Terraform Bootstrap

Infrastructure is provisioned via Terraform, with a guided bootstrap script at `infrastructure/terraform/setup.sh`.

### Prerequisites

| Tool        | Install Link                                      |
|-------------|---------------------------------------------------|
| `terraform` | https://www.terraform.io/downloads                |
| `gcloud`    | https://cloud.google.com/sdk/docs/install         |

You must also be authenticated:

```bash
gcloud auth login
gcloud auth application-default login
```

### Running the Bootstrap

```bash
cd infrastructure/terraform
./setup.sh
```

The script walks through the following steps:

1. **Check prerequisites** -- verifies `terraform` and `gcloud` are installed and authenticated.
2. **Select environment** -- prompts for `dev` or `prod` (reads from `environments/dev.tfvars` or `environments/prod.tfvars`).
3. **Terraform init** -- runs `terraform init -upgrade -input=false`.
4. **Terraform plan** -- generates a plan with the selected `.tfvars` file and asks for confirmation.
5. **Terraform apply** -- applies the plan.
6. **Inject secret placeholders** -- for each secret that has no versions, injects a `"placeholder"` value so downstream services can start. The secrets checked are:
   - `aha_coms_sicu_<env>_db_url`
   - `aha_coms_sicu_<env>_gsheets_credentials`
   - `aha_coms_sicu_<env>_firebase_admin`
7. **Show outputs** -- prints Terraform outputs (WIF provider, service account, Artifact Registry URL, etc.).

### Post-Bootstrap: Inject Real Secrets

After the bootstrap, replace placeholder secrets with real values:

```bash
# Example: update the database URL secret for dev
echo -n "postgresql://user:pass@host:5432/dbname" > /tmp/db_url.txt
gcloud secrets versions add aha_coms_sicu_dev_db_url \
  --data-file /tmp/db_url.txt \
  --project <PROJECT_ID>
rm /tmp/db_url.txt
```

Repeat for each secret listed by the script.

---

## Secret Management

Secrets are stored in Google Cloud Secret Manager. The deploy workflows access them at runtime.

### View a Secret's Current Value

```bash
gcloud secrets versions access latest \
  --secret=<SECRET_NAME> \
  --project=<PROJECT_ID>
```

### Update a Secret

```bash
# Write the new value to a temporary file
echo -n "<new-value>" > /tmp/secret_value.txt

# Add a new version
gcloud secrets versions add <SECRET_NAME> \
  --data-file /tmp/secret_value.txt \
  --project=<PROJECT_ID>

# Clean up
rm /tmp/secret_value.txt
```

The latest version is always used by deploy workflows (`gcloud secrets versions access latest`). Previous versions remain available for rollback.

### List All Secrets

```bash
gcloud secrets list --project=<PROJECT_ID>
```

### List Versions of a Secret

```bash
gcloud secrets versions list <SECRET_NAME> --project=<PROJECT_ID>
```

---

## Smoke Tests

Post-deploy smoke tests live in `smoke-tests/` and use Playwright's API testing (no browser needed).

### Running Smoke Tests

```bash
cd smoke-tests
npm install
npm test
```

### Environment Variables

| Variable              | Required | Description                                    |
|-----------------------|----------|------------------------------------------------|
| `SMOKE_BACKEND_URL`   | No       | Backend base URL (default: `http://localhost:8000`) |
| `SMOKE_FRONTEND_URL`  | No       | Frontend base URL (used by frontend SPA tests) |
| `SMOKE_AUTH_TOKEN`     | No       | Firebase Auth Bearer token for authenticated tests |

Example with all variables set:

```bash
SMOKE_BACKEND_URL=https://aha-coms-sicu-dev-api-xxxxx.run.app \
SMOKE_FRONTEND_URL=https://aha-coms-sicu-dev.web.app \
SMOKE_AUTH_TOKEN=eyJhbGciOi... \
npm test
```

### Test Suite Overview

There are **19 test cases** across 6 spec files: **14 unauthenticated** and **5 authenticated** (skipped when `SMOKE_AUTH_TOKEN` is not set).

| Spec File                        | Tests | Auth Required | What It Covers                                     |
|----------------------------------|-------|---------------|----------------------------------------------------|
| `backend-health.spec.ts`         | 2     | No            | `/health` and `/docs` endpoints return 200         |
| `auth-enforcement.spec.ts`       | 4     | No            | Protected endpoints return 401/403 without a token |
| `frontend-spa.spec.ts`           | 5     | No            | Root, HTML content, and SPA deep-link rewrites     |
| `signed-url.spec.ts` (unauth)    | 1     | No            | Signed URL endpoint rejects unauthenticated calls  |
| `signed-url.spec.ts` (auth)      | 2     | Yes           | Returns `upload_url`, `upload_id`, `expires_at`; URL points to GCS |
| `sse-endpoint.spec.ts` (unauth)  | 2     | No            | SSE endpoint returns 422 (no token) / 401 (bad token) |
| `sse-endpoint.spec.ts` (auth)    | 1     | Yes           | SSE endpoint returns `text/event-stream` with valid token |
| `database-connectivity.spec.ts`  | 2     | Yes           | Brands listing and sync status return valid JSON   |

### Running Specific Test Groups

```bash
# Health checks only
npm run test:health

# Auth enforcement only
npm run test:auth

# Frontend SPA only
npm run test:frontend

# Database connectivity only
npm run test:db

# Signed URL tests only
npm run test:signed-url

# SSE endpoint tests only
npm run test:sse
```

### Configuration

Playwright is configured in `smoke-tests/playwright.config.ts`:

- Timeout: 30 seconds per test
- Retries: 1
- Parallel execution: enabled
- Reporters: `list` (console) + `json` (writes `smoke-results.json`)

---

## Manual Verification Checklist

After a deploy, walk through this 10-step end-to-end evaluation cycle to confirm the system is fully operational.

1. **Backend health** -- `GET /health` returns `200` with `{"status": "healthy"}`.
2. **API docs** -- `GET /docs` loads the FastAPI Swagger UI.
3. **Auth gate** -- unauthenticated requests to `/api/v1/brands` return `401` or `403`.
4. **Login flow** -- sign in through the frontend; verify Firebase Auth token is issued.
5. **Brand listing** -- after login, the brands page loads and displays data from Cloud SQL.
6. **Sync status** -- `/api/v1/sync/status` returns a valid `status` and `last_sync` timestamp.
7. **File upload** -- request a signed URL, upload a test CSV, confirm it lands in GCS.
8. **SSE events** -- open `/api/v1/events?token=<valid>` and confirm `text/event-stream` response.
9. **Frontend routing** -- navigate to `/brands`, `/history`, `/evaluation/1` and confirm SPA renders correctly (no 404).
10. **Smoke suite green** -- run the full smoke test suite and confirm all 19 tests pass.

---

## Database Migration Safety Rules

1. **All migrations MUST be additive** -- `CREATE TABLE`, `ADD COLUMN`, `ADD INDEX` only.
2. **Destructive changes require two-step release:**
   - Release 1: Add new structure, backfill data, code reads/writes both old and new.
   - Release 2: Remove old structure, code uses only new.
3. **No exceptions.** Violating this risks prod data loss.

---

## Rollback Procedures

### Cloud Run Revision Rollback (~10 seconds)

```bash
gcloud run services update-traffic aha-coms-sicu-prod-api \
  --region=asia-southeast2 --to-revisions=PREVIOUS_REVISION=100
```

### Code-Level Rollback (~3 minutes)

```bash
git revert HEAD    # on main branch
git push origin main   # triggers auto-redeploy
```

### Pre-deploy Backups

Every prod deploy creates a Cloud SQL backup before running migrations. The last 5 pre-deploy backups are retained; older ones are automatically cleaned up.

To list backups:

```bash
gcloud sql backups list --instance=aha-sicu-db --filter="description~'^pre-deploy-'"
```

To restore from a backup:

```bash
gcloud sql backups restore BACKUP_ID --restore-instance=aha-sicu-db
```
