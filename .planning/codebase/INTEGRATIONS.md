# External Integrations

**Analysis Date:** 2026-03-06

## APIs & External Services

**Google Sheets API:**
- Purpose: Sync brand data (VP data and 1st Meeting data) from external spreadsheets into the database
- SDK/Client: `google-api-python-client` via `googleapiclient.discovery.build("sheets", "v4")`
- Implementation: `backend/app/modules/sync/sheets_client.py` (GoogleSheetsClient class)
- Auth: Service account credentials via `GSHEETS_CREDENTIALS_PATH` (dev) or `GSHEETS_CREDENTIALS_JSON` (prod, from Secret Manager)
- Scopes: `https://www.googleapis.com/auth/spreadsheets.readonly`
- Config vars: `GSHEETS_VP_SPREADSHEET_ID`, `GSHEETS_VP_RANGE`, `GSHEETS_MEETING_SPREADSHEET_ID`, `GSHEETS_MEETING_RANGE`
- Retry: Exponential backoff (3 retries) on rate limits (HTTP 429)
- Sync trigger: Cloud Scheduler daily at 09:00 WIB or manual POST to `/api/v1/sync`

**Google Cloud Storage:**
- Purpose: Store uploaded Excel files (brand sales data, ads keyword data, etc.)
- SDK/Client: `google-cloud-storage` via `google.cloud.storage.Client`
- Implementation: `backend/app/modules/upload/gcs_client.py` (GCSClient / LocalStorageClient)
- Auth: Application Default Credentials (Cloud Run service account)
- Config var: `GCS_UPLOAD_BUCKET` (empty = local filesystem fallback for dev)
- Features: Signed upload URLs (v4, 15-min expiry), download, delete
- Local dev fallback: `LocalStorageClient` stores to temp dir, returns `localhost:8000` URLs

**Firebase Authentication (Admin SDK - Backend):**
- Purpose: Verify Firebase ID tokens from frontend users
- SDK/Client: `firebase-admin` via `firebase_admin.auth.verify_id_token()`
- Implementation: `backend/app/core/security.py` (init_firebase, verify_firebase_token)
- Auth: Service account via `FIREBASE_CREDENTIALS_PATH` (dev) or `FIREBASE_CREDENTIALS_JSON` (prod)
- Initialization: On app startup in lifespan handler (`backend/app/main.py`)

**Firebase Authentication (Client SDK - Frontend):**
- Purpose: User login/logout, token management
- SDK/Client: `firebase` npm package (v12.8+)
- Implementation: `frontend/src/firebase/config.ts` (app init), `frontend/src/firebase/auth.ts` (auth operations)
- Auth method: Email/password authentication only (`signInWithEmailAndPassword`)
- Config vars: `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`
- Token flow: Frontend gets Firebase ID token -> sends as Bearer token -> backend verifies with Admin SDK

**Google OIDC (Service-to-Service Auth):**
- Purpose: Authenticate Cloud Scheduler requests to the backend API
- SDK/Client: `google-auth` via `google.oauth2.id_token.verify_oauth2_token()`
- Implementation: `backend/app/core/oidc.py` (verify_oidc_token)
- Auth flow: Cloud Scheduler sends OIDC token -> backend verifies against `CLOUD_RUN_URL` audience
- Config vars: `CLOUD_RUN_URL` (audience), `ALLOWED_SCHEDULER_EMAILS` (allowlist)
- Fallback: In `backend/app/core/dependencies.py`, Firebase auth is tried first, then OIDC on failure

## Data Storage

**Database:**
- Type: PostgreSQL (Cloud SQL on GCP)
- Region: asia-southeast2
- Client: asyncpg (async driver, connection pool)
- Connection pool: `backend/app/db/connection.py` (DatabasePool class, min 1 / max 5 connections)
- Connection config: `DATABASE_URL` (local dev) or constructed from `DB_USER` + `DB_PASSWORD` + `DB_NAME` + `CLOUD_SQL_INSTANCE` (Cloud Run)
- Cloud SQL socket: `postgresql://{user}:{pass}@/{db}?host=/cloudsql/{instance}` format
- Migrations: Alembic with 20 migration files in `backend/app/db/migrations/versions/`
- Query layer: Raw SQL in `backend/app/db/queries/` (brands.py, users.py, evaluations.py, rules.py, uploads.py, etc.)
- JSONB support: Custom codec for automatic dict serialization/deserialization

**File Storage:**
- Production: Google Cloud Storage bucket (configured via `GCS_UPLOAD_BUCKET`)
- Development: Local filesystem at `{tempdir}/aha_sicu_uploads/`
- Abstraction: `StorageClient` ABC in `backend/app/modules/upload/gcs_client.py`

**Caching:**
- None (no Redis/Memcached)

## Authentication & Identity

**Auth Provider:** Firebase Authentication
- Frontend: Email/password sign-in via Firebase Client SDK
- Backend: Token verification via Firebase Admin SDK
- User creation: Auto-created in database on first login (`backend/app/core/dependencies.py`)
- Roles: `member`, `leader`, `admin`, `scheduler` (scheduler is synthetic for OIDC service accounts)
- RBAC: `require_role()` dependency factory in `backend/app/core/dependencies.py`
- Account management: Admin-only endpoints at `/api/v1/accounts` for creating users, role changes, password resets, deletion

**Service Auth:** Google OIDC
- Used by Cloud Scheduler for automated sync triggers
- Allowlist-based authorization via `ALLOWED_SCHEDULER_EMAILS`

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry or equivalent detected)

**Logs:**
- Python `logging` module with `INFO` level (`backend/app/main.py`)
- Format: `%(levelname)s: %(name)s: %(message)s`
- Cloud Run captures stdout/stderr to Cloud Logging automatically

**Health Check:**
- `GET /health` endpoint returns `{"status": "healthy"}` (`backend/app/main.py`)
- Deploy workflow verifies `GET /docs` returns 2xx/3xx after deployment

## CI/CD & Deployment

**Hosting:**
- Backend: Google Cloud Run (containerized, asia-southeast2)
- Frontend: Firebase Hosting (SPA with catch-all rewrite to `index.html`)
- Sites: `aha-sicu-dev` (develop branch), `aha-sicu-prod` (main branch)

**CI Pipeline:** GitHub Actions
- `.github/workflows/ci.yml` - PR checks (lint, typecheck, test, build)
- `.github/workflows/deploy-backend.yml` - Backend deploy (build Docker, push to Artifact Registry, deploy Cloud Run, run Alembic migrations)
- `.github/workflows/deploy-frontend.yml` - Frontend deploy (npm build, deploy to Firebase Hosting)
- Auth: Workload Identity Federation (no service account keys in CI)

**Infrastructure:**
- Terraform >= 1.5 (`infrastructure/terraform/`)
- Google provider ~> 7.0
- State: Local backend (comment notes GCS migration for team use)
- Resources managed: Cloud Run, Cloud SQL, Artifact Registry, IAM, Firebase Hosting, Cloud Scheduler, Secret Manager, GCS bucket, Workload Identity

## Environment Configuration

**Required env vars (Backend):**
- `DATABASE_URL` or (`DB_USER` + `DB_PASSWORD` + `DB_NAME` + `CLOUD_SQL_INSTANCE`)
- `FIREBASE_CREDENTIALS_PATH` or `FIREBASE_CREDENTIALS_JSON`
- `GSHEETS_CREDENTIALS_PATH` or `GSHEETS_CREDENTIALS_JSON`
- `GSHEETS_VP_SPREADSHEET_ID`
- `GSHEETS_MEETING_SPREADSHEET_ID`

**Required env vars (Frontend):**
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_API_BASE_URL`

**Optional env vars (Backend):**
- `GCS_UPLOAD_BUCKET` (empty = local storage fallback)
- `CLOUD_RUN_URL` (empty = skip OIDC audience validation)
- `ALLOWED_SCHEDULER_EMAILS` (empty = accept any valid OIDC token)
- `DATABASE_POOL_MIN` (default: 1), `DATABASE_POOL_MAX` (default: 5)
- `DEBUG` (default: false)

**Secrets location:**
- Production: Google Secret Manager (referenced in Terraform at `infrastructure/terraform/secrets.tf`)
- Development: Local `.env` files and service account JSON files
- CI/CD: GitHub Actions environment variables

## Webhooks & Callbacks

**Incoming:**
- `POST /api/v1/sync` - Triggered daily by Cloud Scheduler (OIDC-authenticated) to sync brand data from Google Sheets
- Configured in `infrastructure/terraform/scheduler.tf` (09:00 WIB / 02:00 UTC daily)

**Outgoing:**
- None

---

*Integration audit: 2026-03-06*
