# External Integrations

**Analysis Date:** 2026-03-16

## APIs & External Services

**Google Sheets API:**
- What it's used for: Reading brand data from Google Sheets (VP sheet, Meeting sheet) and writing evaluation results to evaluation sheet
- SDK/Client: `google-api-python-client` 2.150.0+, `google-auth` 2.38.0+
- Auth: Service account credentials (via `GSHEETS_CREDENTIALS_PATH` or `GSHEETS_CREDENTIALS_JSON`)
- Implementation: `app/modules/sync/sheets_client.py` (GoogleSheetsClient)
- Endpoints:
  - VP sheet: `GSHEETS_VP_SPREADSHEET_ID` with range `GSHEETS_VP_RANGE` (default: `VP!A:Y`)
  - Meeting sheet: `GSHEETS_MEETING_SPREADSHEET_ID` with range `GSHEETS_MEETING_RANGE` (default: `ZAP: 1st Meeting!A:D`)
  - Evaluation sheet (write-only): `GSHEETS_EVAL_SPREADSHEET_ID` tab `GSHEETS_EVAL_TAB` (default: `SICU`)
- Error handling: Exponential backoff retry for rate limits; distinct error codes for 404, 403, 429 scenarios

**Gmail SMTP:**
- What it's used for: Sending evaluation emails with branded header/footer and optional chart images
- Configuration:
  - Host: `SMTP_HOST` (default: `smtp.gmail.com`)
  - Port: `SMTP_PORT` (default: 587)
  - Auth: `SMTP_USER` and `SMTP_PASSWORD` (Gmail App Password required)
  - TLS: `SMTP_USE_TLS` (default: true)
  - From: `SMTP_FROM_NAME` and `SMTP_FROM_EMAIL`
- Implementation: `app/modules/email/service.py` (build_email_message, smtp_send)
- Fallback: Email preview written to `/tmp/email_preview_{evaluation_id}.html` when `EMAIL_ENABLED=false`
- Features: Multipart emails with CID inline images (header, footer, optional chart)

## Data Storage

**Databases:**
- PostgreSQL 18 (Cloud SQL in production)
  - Connection: Via `DATABASE_URL` env var or constructed from `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `CLOUD_SQL_INSTANCE`
  - Cloud SQL Unix socket syntax: `postgresql://{user}:{password}@/{db}?host=/cloudsql/{instance}`
  - Client: `asyncpg` 0.30.0
  - Connection pooling: `DATABASE_POOL_MIN` (default: 1) to `DATABASE_POOL_MAX` (default: 5)
  - Migrations: Alembic 1.13.0+

**File Storage:**
- Google Cloud Storage (production): Via `google-cloud-storage` 2.18.0+
  - Bucket: `GCS_UPLOAD_BUCKET` env var
  - Signed URLs: 15-minute expiry for upload/download
  - Auth: Application Default Credentials (ADC) on Cloud Run, or service account credentials
  - Implementation: `app/modules/upload/gcs_client.py` (GCSClient)
- Local filesystem (development): Fallback when `GCS_UPLOAD_BUCKET` is empty
  - Path: `/tmp/aha_sicu_uploads` (temporary directory)
  - Implementation: `app/modules/upload/gcs_client.py` (LocalStorageClient)
  - Serves via: `http://localhost:8000/api/v1/upload/local/{upload_id}/{filename}`

**Caching:**
- Not detected — uses database and in-memory state

## Authentication & Identity

**Auth Provider:**
- Firebase Authentication (combined frontend + backend)
  - Implementation:
    - Backend: `app/core/security.py` (init_firebase, verify_firebase_token)
    - Frontend: `src/firebase/config.ts`, `src/firebase/auth.ts`
  - Frontend SDK: `firebase` 12.8.0+
  - Backend SDK: `firebase-admin` 6.0.0+
  - Emulator support: `FIREBASE_AUTH_EMULATOR_HOST` (local dev via Docker)
  - Credentials: `FIREBASE_CREDENTIALS_PATH` (file) or Application Default Credentials (Cloud Run)
  - Token validation: Async verification with expired/invalid token error handling
  - Project ID (dev): `fbi-dev-484410`

**OIDC Service Account Auth (Cloud Scheduler):**
- Alternative authentication for scheduled tasks
- Implementation: `app/core/oidc.py`
- Configuration: `CLOUD_RUN_URL` for audience validation
- Allowlist: `ALLOWED_SCHEDULER_EMAILS` (comma-separated email addresses)

**Database User Auth:**
- Separate accounts table in PostgreSQL
- Roles: `member`, `leader`, `admin`
- Password reset capability via `POST /api/v1/accounts/{user_id}/reset-password`

## Monitoring & Observability

**Error Tracking:**
- Not detected — no Sentry, DataDog, or similar configured

**Logs:**
- Python logging: Standard library with logger instances in each module
- Firebase Admin SDK logs: Standard to stdout
- Docker: Log collection via `docker logs` or similar container runtime tools
- Frontend: Console logging via standard browser DevTools

## CI/CD & Deployment

**Hosting:**
- Frontend: Firebase Hosting
  - Targets: `aha-coms-sicu-dev` (development), `aha-coms-sicu-prod` (production)
  - Configuration: `firebase.json` with rewrites to `/index.html`
  - Build output: `frontend/dist`
- Backend: Google Cloud Run
  - Project configuration: GCP project ID (customizable)
  - Dockerfile: `backend/Dockerfile` (production), `backend/Dockerfile.dev` (local)
  - Docker image: Builds from `backend/` directory

**CI Pipeline:**
- GitHub Actions (configuration in `.github/`)
- Firebase CLI integration for hosting deployment
- Smoke tests: Playwright (production health checks)
  - Location: `smoke-tests/` directory
  - Tests: backend health, auth enforcement, frontend SPA, database connectivity, signed URLs, SSE endpoint

**Local Development:**
- docker-compose.yml orchestrates full stack:
  - PostgreSQL 18
  - Firebase Auth Emulator (port 9099)
  - MailHog SMTP mock (ports 1025 SMTP, 8025 UI)
  - Backend FastAPI (port 8000)
  - Frontend Vite dev server (port 5173)

## Environment Configuration

**Required env vars:**

Backend critical:
- `DATABASE_URL` OR (`DB_USER`, `DB_PASSWORD`, `DB_NAME`, `CLOUD_SQL_INSTANCE`)
- `FIREBASE_CREDENTIALS_PATH` (file path, optional if using ADC or emulator)
- `FIREBASE_AUTH_EMULATOR_HOST` (local dev only)
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` (for email)
- `GSHEETS_CREDENTIALS_PATH` OR `GSHEETS_CREDENTIALS_JSON` (for sync)
- `GSHEETS_VP_SPREADSHEET_ID`, `GSHEETS_MEETING_SPREADSHEET_ID` (for sync)

Frontend critical:
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_API_BASE_URL` (backend API endpoint)

Optional/feature-dependent:
- `GCS_UPLOAD_BUCKET` (empty = local filesystem)
- `GSHEETS_EVAL_SPREADSHEET_ID` (for writing evaluation results)
- `EMAIL_ENABLED` (default: false; if true, requires SMTP config)
- `CLOUD_RUN_URL` (production audience validation)
- `ALLOWED_SCHEDULER_EMAILS` (comma-separated for OIDC scheduler auth)

**Secrets location:**
- `.env` files (not committed, listed in `.gitignore`)
- Cloud Secret Manager (production on GCP)
- Firebase service account JSON (development, path-based or inline JSON)

## Webhooks & Callbacks

**Incoming:**
- Not detected — no webhook handlers in API

**Outgoing:**
- Google Sheets API write operations: Evaluation results written to evaluation sheet via batch update
- Email sending: SMTP to Gmail and recipient addresses (no webhook callbacks from email service)

---

*Integration audit: 2026-03-16*
