# Environment Variables

<!-- AUTO-GENERATED from .env.example files — do not edit manually -->

## Backend (`backend/.env`)

### Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_NAME` | No | `Store ICU API` | Application display name |
| `DEBUG` | No | `false` | Enable debug mode |

### Database (Cloud SQL PostgreSQL)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes* | — | Full PostgreSQL connection string (local dev). Takes precedence over individual components. Example: `postgresql://aha_sicu:password@localhost:5432/aha_coms_sicu_dev` |
| `DB_USER` | Yes* | — | Database username (Cloud Run / CI) |
| `DB_PASSWORD` | Yes* | — | Database password (Cloud Run / CI) |
| `DB_NAME` | Yes* | — | Database name (Cloud Run / CI) |
| `CLOUD_SQL_INSTANCE` | Yes* | — | Cloud SQL instance connection name. Example: `project:asia-southeast2:aha-sicu-db` |
| `DATABASE_POOL_MIN` | No | `1` | Minimum connection pool size |
| `DATABASE_POOL_MAX` | No | `5` | Maximum connection pool size |

> \* Use **either** `DATABASE_URL` (local dev) **or** the individual `DB_*` + `CLOUD_SQL_INSTANCE` components (Cloud Run). Not both.

### Firebase Admin SDK

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FIREBASE_CREDENTIALS_PATH` | Yes* | — | Path to Firebase service account JSON (local dev). Cloud Run uses ADC automatically. |

### Email — rich report (`POST /api/v1/email/send`, own SMTP account)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_FROM_NAME` | No | `AHA Commerce` | Sender display name |
| `EMAIL_FROM_EMAIL` | No | — | Verified sender email address |
| `EMAIL_ENABLED` | No | `false` | Gates the rich `/send` path. When `false`, `/send` writes a `/tmp` HTML preview instead of dialing SMTP. |
| `EMAIL_ALLOWED_DOMAINS` | No | `ahacommerce.co.id` | Comma-separated allowed recipient domains |
| `EMAIL_SMTP_HOST` | No | `smtp.gmail.com` | SMTP host for the rich `/send` account |
| `EMAIL_SMTP_PORT` | No | `587` | SMTP port |
| `EMAIL_SMTP_USER` | No | — | SMTP username (defaults to `EMAIL_FROM_EMAIL` when blank) |
| `EMAIL_SMTP_APP_PASSWORD` | No | — | 16-char Google App Password (no spaces) |

### Email — plain-text "Send Mail" dialog (`POST /api/v1/email/send-plain`, Gmail SMTP)

Independent of `EMAIL_ENABLED`; gated only by `GMAIL_SMTP_ENABLED`.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GMAIL_SMTP_ENABLED` | No | `false` | When `false`, `/send-plain` writes a `/tmp` preview instead of dialing SMTP |
| `GMAIL_SMTP_USER` | No | — | Google Workspace account with 2-Step Verification |
| `GMAIL_SMTP_APP_PASSWORD` | No | — | 16-char Google App Password (no spaces) |
| `GMAIL_SMTP_HOST` | No | `smtp.gmail.com` | SMTP host |
| `GMAIL_SMTP_PORT` | No | `587` | SMTP port |

### Google Sheets API

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GSHEETS_CREDENTIALS_PATH` | No* | — | Path to GSheets service account JSON (development) |
| `GSHEETS_CREDENTIALS_JSON` | No* | — | Raw JSON string from Secret Manager (production) |
| `GSHEETS_VP_SPREADSHEET_ID` | No | — | VP data spreadsheet ID (ID marketplace) |
| `GSHEETS_VP_RANGE` | No | `Brands Data!A:Z` | VP sheet range (ID) |
| `GSHEETS_VP_BRAND_COLUMN` | No | `Brand` | VP sheet brand column header (ID) |
| `GSHEETS_VP_SPREADSHEET_ID_TH` | No | — | VP data spreadsheet ID (TH marketplace) |
| `GSHEETS_VP_RANGE_TH` | No | `Brands Data!A:Z` | VP sheet range (TH) |
| `GSHEETS_VP_BRAND_COLUMN_TH` | No | `Brand` | VP sheet brand column header (TH) |
| `GSHEETS_MEETING_SPREADSHEET_ID` | No | — | 1st Meeting spreadsheet ID (ID marketplace) |
| `GSHEETS_MEETING_RANGE` | No | `1st Meeting!A:M` | Meeting sheet range (ID) |
| `GSHEETS_MEETING_BRAND_COLUMN` | No | `Brand` | Meeting sheet brand column header (ID) |
| `GSHEETS_MEETING_SPREADSHEET_ID_TH` | No | — | 1st Meeting spreadsheet ID (TH marketplace) |
| `GSHEETS_MEETING_RANGE_TH` | No | `1st Meeting!A:M` | Meeting sheet range (TH) |
| `GSHEETS_MEETING_BRAND_COLUMN_TH` | No | `Brand` | Meeting sheet brand column header (TH) |
| `GSHEETS_EVAL_SPREADSHEET_ID` | No | — | Evaluation status spreadsheet ID (write-only) |
| `GSHEETS_EVAL_TAB` | No | `SICU` | Evaluation status tab name |

---

## Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_FIREBASE_API_KEY` | Yes | — | Firebase Web API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | Yes | — | Firebase auth domain. Example: `your-project.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | Yes | — | Firebase project ID |
| `VITE_FIREBASE_AUTH_EMULATOR_URL` | No | — | Firebase Auth Emulator URL for local dev. Example: `http://localhost:9099` |
| `VITE_API_BASE_URL` | Yes | — | Backend API base URL. Example: `http://localhost:8000` |

---

## Docker Compose (Local Dev)

When using `docker compose up`, most backend env vars are already wired in `docker-compose.yml`. Email sending is disabled by default; if you want to exercise real outbound email locally, provide the same SMTP-backed variables used by the backend:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_ENABLED` | No | `false` | Enable the rich `/send` path (otherwise a `/tmp` preview is written) |
| `EMAIL_FROM_EMAIL` | No | — | Verified sender email address |
| `EMAIL_SMTP_USER` | No | — | SMTP username (defaults to `EMAIL_FROM_EMAIL`) |
| `EMAIL_SMTP_APP_PASSWORD` | No | — | 16-char Google App Password |
| `GMAIL_SMTP_ENABLED` | No | `false` | Enable the plain-text `/send-plain` dialog path |
| `GMAIL_SMTP_USER` | No | — | Gmail/Workspace account for `/send-plain` |
| `GMAIL_SMTP_APP_PASSWORD` | No | — | 16-char Google App Password |

---

## CI/CD (GitHub Environments)

See [`infrastructure/GITHUB_ENVIRONMENT_VARS.md`](../infrastructure/GITHUB_ENVIRONMENT_VARS.md) for the full list of GitHub Actions environment variables per deployment target.

<!-- END AUTO-GENERATED -->
