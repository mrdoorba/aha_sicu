# Development Guide

Local development setup for the Store ICU (AHA SICU) project.

---

## Prerequisites

| Tool       | Version   | Install                                      |
|------------|-----------|----------------------------------------------|
| Python     | 3.14+     | https://www.python.org/downloads/             |
| Node.js    | 20+       | https://nodejs.org/                           |
| uv         | latest    | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| npm        | (bundled) | Comes with Node.js                           |
| PostgreSQL | 18        | https://www.postgresql.org/download/          |

---

## Backend Setup

```bash
cd backend
uv sync
cp .env.example .env
```

Edit `.env` with your local values (see [Environment Variables -- Backend](#backend-environment-variables) below). At minimum set `DATABASE_URL` and `FIREBASE_CREDENTIALS_PATH`.

Run database migrations and start the server:

```bash
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

The API runs on **http://localhost:8000**.

---

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
```

Edit `.env` -- set the Firebase client keys and API URL:

```dotenv
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_API_BASE_URL=http://localhost:8000
```

Start the dev server:

```bash
npm run dev
```

The frontend runs on **http://localhost:5173** by default (Vite).

---

## Environment Variables

### Backend Environment Variables

All variables are loaded via `pydantic-settings` in `backend/app/config.py`. The `.env` file is read automatically.

#### Application

| Variable    | Default          | Description                  |
|-------------|------------------|------------------------------|
| `APP_NAME`  | `Store ICU API`  | Application display name     |
| `DEBUG`     | `false`          | Enable debug mode            |

#### Database (PostgreSQL)

Use **Option 1** for local development. Option 2 is for Cloud Run deployments.

| Variable             | Default | Description                                               |
|----------------------|---------|-----------------------------------------------------------|
| `DATABASE_URL`       | (empty) | Full connection string (takes precedence when set)        |
| `DB_USER`            | (empty) | PostgreSQL user (Cloud Run)                               |
| `DB_PASSWORD`        | (empty) | PostgreSQL password (Cloud Run)                           |
| `DB_NAME`            | (empty) | Database name (Cloud Run)                                 |
| `CLOUD_SQL_INSTANCE` | (empty) | Cloud SQL instance connection name (Cloud Run)            |
| `DATABASE_POOL_MIN`  | `1`     | Minimum connection pool size                              |
| `DATABASE_POOL_MAX`  | `5`     | Maximum connection pool size                              |

Local development example:

```dotenv
DATABASE_URL=postgresql://aha_sicu:password@localhost:5432/aha_sicu_dev
```

#### Firebase Admin SDK

| Variable                     | Default | Description                                       |
|------------------------------|---------|---------------------------------------------------|
| `FIREBASE_CREDENTIALS_PATH`  | (none)  | Path to service account JSON file (development)   |
| `FIREBASE_CREDENTIALS_JSON`  | (none)  | Raw JSON string from Secret Manager (production)  |

#### Cloud Run / OIDC

| Variable                     | Default | Description                                                |
|------------------------------|---------|------------------------------------------------------------|
| `CLOUD_RUN_URL`              | (empty) | Service URL for OIDC audience validation (empty = disabled)|
| `ALLOWED_SCHEDULER_EMAILS`   | (empty) | Comma-separated service account emails for scheduler auth  |

#### GCS Upload

| Variable            | Default | Description                                              |
|---------------------|---------|----------------------------------------------------------|
| `GCS_UPLOAD_BUCKET` | (empty) | GCS bucket name. When empty, uploads fall back to local filesystem. |

#### Email / SMTP

| Variable          | Default          | Description                       |
|-------------------|------------------|-----------------------------------|
| `SMTP_HOST`       | `smtp.gmail.com` | SMTP server hostname              |
| `SMTP_PORT`       | `587`            | SMTP server port                  |
| `SMTP_USER`       | (empty)          | SMTP username (Gmail address)     |
| `SMTP_PASSWORD`   | (empty)          | SMTP password (Gmail App Password)|
| `SMTP_FROM_NAME`  | `AHA Commerce`   | Display name on outgoing email    |
| `SMTP_FROM_EMAIL` | (empty)          | Sender email address              |
| `EMAIL_ENABLED`   | `false`          | Master switch for sending emails  |

#### Google Sheets API

| Variable                          | Default                  | Description                                    |
|-----------------------------------|--------------------------|------------------------------------------------|
| `GSHEETS_CREDENTIALS_PATH`       | (none)                   | Path to service account JSON (development)     |
| `GSHEETS_CREDENTIALS_JSON`       | (none)                   | Raw JSON string from Secret Manager (prod)     |
| `GSHEETS_VP_SPREADSHEET_ID`      | (none)                   | Spreadsheet ID for VP brand data               |
| `GSHEETS_VP_RANGE`               | `VP!A:Y`                 | Sheet range for VP data                        |
| `GSHEETS_VP_BRAND_COLUMN`        | `Nama Brand`             | Column header for brand name in VP sheet       |
| `GSHEETS_MEETING_SPREADSHEET_ID` | (none)                   | Spreadsheet ID for 1st Meeting data            |
| `GSHEETS_MEETING_RANGE`          | `ZAP: 1st Meeting!A:D`  | Sheet range for meeting data                   |
| `GSHEETS_MEETING_BRAND_COLUMN`   | `Brand`                  | Column header for brand name in meeting sheet  |

### Frontend Environment Variables

All `VITE_` prefixed variables are exposed to client code at build time.

| Variable                     | Description                              |
|------------------------------|------------------------------------------|
| `VITE_FIREBASE_API_KEY`      | Firebase client API key                  |
| `VITE_FIREBASE_AUTH_DOMAIN`  | Firebase auth domain                     |
| `VITE_FIREBASE_PROJECT_ID`   | Firebase project ID                      |
| `VITE_API_BASE_URL`          | Backend API URL (`http://localhost:8000`) |

---

## Running Tests

### Backend

```bash
cd backend

# Run all tests with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_example.py -v

# Run tests matching a keyword
uv run pytest -k "test_name" -v
```

Pytest is configured with `asyncio_mode = "auto"` and `testpaths = ["tests"]`.

### Frontend

```bash
cd frontend

# Watch mode (re-runs on file changes)
npm run test

# Single run (CI / one-shot)
npm run test:run
```

Tests use Vitest with jsdom environment. Test files are colocated with source as `*.test.tsx`.

---

## Linting

### Backend

```bash
cd backend
uv run ruff check .
```

### Frontend

```bash
cd frontend
npm run lint
```

Uses ESLint 9 with TypeScript and React plugins.

---

## Type Checking

### Frontend

```bash
cd frontend
npx tsc --noEmit
```

This is also run as part of `npm run build` (`tsc -b && vite build`).

---

## Database Migrations

Alembic manages PostgreSQL schema migrations.

```bash
cd backend

# Create a new migration from model changes
uv run alembic revision --autogenerate -m "description of change"

# Apply all pending migrations
uv run alembic upgrade head

# Roll back the last migration
uv run alembic downgrade -1
```

---

## Local File Uploads

When `GCS_UPLOAD_BUCKET` is **not set** (empty string, the default), file uploads fall back to local filesystem storage. Uploaded files are served via:

```
PUT /api/v1/upload/local/
```

In production, set `GCS_UPLOAD_BUCKET` to use Google Cloud Storage instead.

---

## Quick Reference

| Task                        | Command                                                 |
|-----------------------------|---------------------------------------------------------|
| Install backend deps        | `cd backend && uv sync`                                 |
| Install frontend deps       | `cd frontend && npm install`                            |
| Start backend               | `cd backend && uv run uvicorn app.main:app --reload`    |
| Start frontend              | `cd frontend && npm run dev`                            |
| Run backend tests           | `cd backend && uv run pytest -v`                        |
| Run frontend tests (watch)  | `cd frontend && npm run test`                           |
| Run frontend tests (single) | `cd frontend && npm run test:run`                       |
| Lint backend                | `cd backend && uv run ruff check .`                     |
| Lint frontend               | `cd frontend && npm run lint`                           |
| Type check frontend         | `cd frontend && npx tsc --noEmit`                       |
| New DB migration            | `cd backend && uv run alembic revision --autogenerate -m "msg"` |
| Apply DB migrations         | `cd backend && uv run alembic upgrade head`             |
| Rollback last migration     | `cd backend && uv run alembic downgrade -1`             |
| Build frontend              | `cd frontend && npm run build`                          |
| Preview frontend build      | `cd frontend && npm run preview`                        |
