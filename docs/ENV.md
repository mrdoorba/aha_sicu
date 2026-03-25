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

### Email (Brevo Transactional API)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BREVO_API_KEY` | No | — | Brevo API key ([get one here](https://app.brevo.com/settings/keys/api)). Free tier: 300 emails/day. |
| `BREVO_SENDER_NAME` | No | `AHA Commerce` | Sender display name |
| `BREVO_SENDER_EMAIL` | No | — | Verified sender email ([verify here](https://app.brevo.com/senders/list)) |
| `EMAIL_ENABLED` | No | `false` | Enable email sending |
| `EMAIL_ALLOWED_DOMAINS` | No | `ahacommerce.co.id` | Comma-separated allowed recipient domains |

### Google Sheets API

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GSHEETS_CREDENTIALS_PATH` | No* | — | Path to GSheets service account JSON (development) |
| `GSHEETS_CREDENTIALS_JSON` | No* | — | Raw JSON string from Secret Manager (production) |
| `GSHEETS_VP_SPREADSHEET_ID` | No | — | VP data spreadsheet ID |
| `GSHEETS_VP_RANGE` | No | `VP!A:Y` | VP sheet range |
| `GSHEETS_VP_BRAND_COLUMN` | No | `Nama Brand` | VP sheet brand column header |
| `GSHEETS_MEETING_SPREADSHEET_ID` | No | — | 1st Meeting data spreadsheet ID |
| `GSHEETS_MEETING_RANGE` | No | `ZAP: 1st Meeting!A:D` | Meeting sheet range |
| `GSHEETS_MEETING_BRAND_COLUMN` | No | `Brand` | Meeting sheet brand column header |
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

When using `docker compose up`, environment variables are pre-configured in `docker-compose.yml`. You only need a root `.env` file for SMTP credentials if you want email sending:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SMTP_USER` | No | — | Gmail SMTP username |
| `SMTP_PASSWORD` | No | — | Gmail SMTP app password |
| `SMTP_FROM_EMAIL` | No | `noreply@ahacommerce.local` | Sender email |
| `EMAIL_ENABLED` | No | `false` | Enable real email sending (otherwise caught by MailHog) |

---

## CI/CD (GitHub Environments)

See [`infrastructure/GITHUB_ENVIRONMENT_VARS.md`](../infrastructure/GITHUB_ENVIRONMENT_VARS.md) for the full list of GitHub Actions environment variables per deployment target.

<!-- END AUTO-GENERATED -->
