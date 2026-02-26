# Development Guide

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Frontend build |
| Python | 3.14+ | Backend runtime |
| UV | latest | Python package manager |
| Git | 2.x | Version control |
| Firebase CLI | latest | Frontend deployment |
| gcloud CLI | latest | GCP operations |
| Terraform | >= 1.5 | Infrastructure management |

## Quick Start

### Backend

```bash
# Navigate to backend
cd backend

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env
# Edit .env with your database URL, Firebase credentials, etc.

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.
Health check: `GET http://localhost:8000/health`

### Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`.

## Environment Variables

### Backend (.env)

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql://user:pass@host/db` | PostgreSQL connection string |
| `FIREBASE_CREDENTIALS_PATH` | One of | `./firebase-sa.json` | Firebase Admin SA file path |
| `FIREBASE_CREDENTIALS_JSON` | One of | `{"type":"service_account",...}` | Firebase Admin SA as JSON string |
| `GSHEETS_CREDENTIALS_PATH` | One of | `./sheets-sa.json` | Google Sheets SA file path |
| `GSHEETS_CREDENTIALS_JSON` | One of | `{"type":"service_account",...}` | Google Sheets SA as JSON string |
| `GSHEETS_VP_SPREADSHEET_ID` | Yes | `1abc...xyz` | VP data Google Sheet ID |
| `GSHEETS_MEETING_SPREADSHEET_ID` | Yes | `1def...uvw` | Meeting data Google Sheet ID |
| `GCS_UPLOAD_BUCKET` | No | `aha-sicu-dev-uploads` | GCS bucket (empty = local storage) |
| `CLOUD_RUN_URL` | No | `https://...run.app` | OIDC audience (empty = skip check) |
| `DATABASE_POOL_MIN` | No | `1` | Min DB connections |
| `DATABASE_POOL_MAX` | No | `5` | Max DB connections |
| `DEBUG` | No | `true` | Enable debug mode |

### Frontend (.env)

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | Yes | `http://localhost:8000` | Backend API URL |
| `VITE_FIREBASE_API_KEY` | Yes | `AIza...` | Firebase API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | Yes | `project.firebaseapp.com` | Firebase auth domain |
| `VITE_FIREBASE_PROJECT_ID` | Yes | `your-project-id` | Firebase project ID |

## Development Commands

### Backend

```bash
uv run uvicorn app.main:app --reload     # Start dev server
uv run pytest                             # Run all tests
uv run pytest tests/unit/                 # Run unit tests only
uv run pytest tests/integration/          # Run integration tests only
uv run pytest -x -v                       # Stop on first failure, verbose
uv run ruff check .                       # Lint check
uv run ruff format .                      # Auto-format
uv run alembic upgrade head               # Run migrations
uv run alembic revision -m "description"  # Create new migration
```

### Frontend

```bash
npm run dev          # Start Vite dev server (port 5173)
npm run build        # TypeScript check + production build
npm run test         # Run Vitest in watch mode
npm run test:run     # Run Vitest once
npm run lint         # ESLint check
npm run preview      # Preview production build
```

## Testing

### Backend Tests

- **Framework:** Pytest with pytest-asyncio
- **Mode:** `asyncio_mode = "auto"`
- **Test directory:** `backend/tests/`
- **Integration tests:** Mock database and Firebase auth
- **Unit tests:** Pure function tests for calculators
- **37 test files** covering all modules

### Frontend Tests

- **Framework:** Vitest with Testing Library
- **Environment:** jsdom
- **Setup:** `src/test/setup.ts`
- **Run:** `npm run test:run`

### Smoke Tests

```bash
cd smoke-tests
npm install
# Set env vars: SMOKE_BACKEND_URL, SMOKE_FRONTEND_URL, SMOKE_AUTH_TOKEN
npx playwright test
```

## Git Workflow

Per `CLAUDE.md` project rules:

| Branch | Purpose | Policy |
|--------|---------|--------|
| `main` | Production | PR-only, CI required |
| `develop` | Staging/integration | CI required |
| `feat/*`, `fix/*`, `update/*`, etc. | Active work | ALL commits go here first |

**Flow:**
1. Create feature branch from `develop` (`feat/`, `fix/`, `update/`, `refactor/`, `docs/`, `chore/`)
2. Make atomic commits on feature branch
3. Merge feature → develop at milestones
4. Delete feature branch after merge
5. Only touch `main` for production deployment

## Project Structure

```
aha_sicu/
├── frontend/          # React SPA
├── backend/           # FastAPI API
├── infrastructure/    # Terraform IaC
├── smoke-tests/       # Playwright smoke tests
├── scripts/           # Utility scripts
├── docs/              # Documentation
├── .github/workflows/ # CI/CD pipelines
└── CLAUDE.md          # Project rules
```

## Common Development Tasks

### Adding a New API Endpoint

1. Create/update schema in `backend/app/modules/{module}/schemas.py`
2. Add query function in `backend/app/db/queries/{module}.py`
3. Add service function in `backend/app/modules/{module}/service.py`
4. Add route in `backend/app/modules/{module}/router.py`
5. Write tests in `backend/tests/`
6. Update frontend hook in `frontend/src/hooks/`

### Adding a New Frontend Page

1. Create page component in `frontend/src/pages/`
2. Add route in `frontend/src/App.tsx`
3. Create hooks in `frontend/src/hooks/` for data fetching
4. Add navigation link in `frontend/src/components/layout/Header.tsx`

### Adding a Database Migration

```bash
cd backend
# Create migration file
uv run alembic revision -m "add_new_table"
# Edit the generated file in app/db/migrations/
# Apply migration
uv run alembic upgrade head
```

### User Provisioning

1. Copy `scripts/users-config.example.yaml` → `scripts/users-config.yaml`
2. Fill in user details (email, password, role)
3. Run: `python scripts/provision-users.py`
4. Have users log in once (auto-creates DB record)
5. Run: `psql $DATABASE_URL -f scripts/assign-roles.sql`

## Deployment

See [Deployment Guide](./deployment-guide.md) for production deployment instructions.

**Quick deploy (dev):**
- Push to `develop` branch triggers automatic deployment
- Backend → Cloud Run
- Frontend → Firebase Hosting

**Production deploy:**
- Push to `main` branch requires manual approval in GitHub Actions
