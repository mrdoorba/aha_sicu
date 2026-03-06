# Technology Stack

**Analysis Date:** 2026-03-06

## Languages

**Primary:**
- Python 3.14 - Backend API (`backend/`)
- TypeScript ~5.9.3 - Frontend SPA (`frontend/`)

**Secondary:**
- HCL (Terraform) - Infrastructure as code (`infrastructure/terraform/`)
- SQL - Database migrations (`backend/app/db/migrations/versions/`)

## Runtime

**Backend:**
- Python 3.14 (via `uv` package manager)
- Docker container: `python:3.14-slim` (`backend/Dockerfile`)
- ASGI server: Uvicorn (bound to `0.0.0.0:8080` in production)

**Frontend:**
- Node.js 20 (per CI workflow `.github/workflows/deploy-frontend.yml`)
- Vite 7.x dev server on port 5173

**Package Managers:**
- Backend: `uv` (lockfile: `backend/uv.lock` present)
- Frontend: `npm` (lockfile: `frontend/package-lock.json` present)

## Frameworks

**Core:**
- FastAPI 0.115+ - Backend REST API (`backend/app/main.py`)
- React 19.2 - Frontend UI (`frontend/package.json`)
- React Router 7.13 - Client-side routing (`frontend/package.json`)

**State & Data:**
- TanStack React Query 5.x - Server state management (`frontend/package.json`)
- TanStack React Table 8.x - Data tables (`frontend/package.json`)
- openapi-fetch 0.15 - Type-safe API client (`frontend/src/services/apiClient.ts`)
- react-hook-form 7.x - Form handling (`frontend/package.json`)

**UI:**
- Tailwind CSS 4.x (via `@tailwindcss/vite` plugin) (`frontend/vite.config.ts`)
- Radix UI 1.4 - Headless component primitives (`frontend/package.json`)
- Lucide React - Icons (`frontend/package.json`)
- class-variance-authority + clsx + tailwind-merge - Variant styling utilities
- Recharts 3.x - Data visualization charts (`frontend/package.json`)
- Sonner 2.x - Toast notifications (`frontend/package.json`)
- next-themes 0.4 - Theme switching (`frontend/package.json`)
- tw-animate-css - Tailwind animations (`frontend/package.json`)
- react-day-picker 9.x - Date picker (`frontend/package.json`)

**Internationalization:**
- i18next 25.x + react-i18next 16.x - Indonesian locale (`frontend/src/i18n.ts`)
- Single language: Indonesian (`id`) with translations in `frontend/src/locales/id.json`

**Testing:**
- Vitest 4.x - Frontend test runner (config in `frontend/vite.config.ts` test section)
- Testing Library (React 16.x, user-event 14.x, jest-dom 6.x) - Component testing
- jsdom 28.x - DOM environment for tests
- pytest 8.x + pytest-asyncio 0.24 - Backend test runner (`backend/pyproject.toml`)
- httpx 0.27 - Backend test HTTP client

**Build/Dev:**
- Vite 7.x - Frontend bundler and dev server (`frontend/vite.config.ts`)
- `@vitejs/plugin-react` 5.x - React Fast Refresh
- ESLint 9.x + typescript-eslint 8.x - Frontend linting (`frontend/eslint.config.js`)
- Ruff 0.11+ - Backend linting (`backend/pyproject.toml`)
- Hatchling - Backend Python build system (`backend/pyproject.toml`)

## Key Dependencies

**Critical (Backend):**
- `fastapi` 0.115+ - REST API framework (`backend/pyproject.toml`)
- `asyncpg` 0.30+ - Async PostgreSQL driver (`backend/app/db/connection.py`)
- `firebase-admin` 6.0+ - Firebase Auth token verification (`backend/app/core/security.py`)
- `pydantic-settings` 2.6+ - Configuration management (`backend/app/config.py`)
- `alembic` 1.13+ - Database schema migrations (`backend/app/db/migrations/`)
- `polars` 1.0+ - High-performance data processing (used in calculators)
- `fastexcel` 0.12+ - Excel file parsing for uploads
- `google-api-python-client` 2.150+ - Google Sheets API access (`backend/app/modules/sync/sheets_client.py`)
- `google-cloud-storage` 2.18+ - GCS file uploads (`backend/app/modules/upload/gcs_client.py`)
- `python-multipart` 0.0.9+ - Multipart form data support

**Critical (Frontend):**
- `firebase` 12.8+ - Firebase Auth client SDK (`frontend/src/firebase/config.ts`)
- `openapi-fetch` 0.15 - Type-safe HTTP client with inline path types (`frontend/src/services/apiClient.ts`)
- `@tanstack/react-query` 5.x - Async state management with caching
- `date-fns` 4.x - Date formatting utilities

**Infrastructure:**
- `psycopg2-binary` 2.9+ - Used by Alembic for sync migrations
- `xlsxwriter` 3.2+ - Dev dependency for generating test Excel files

## Configuration

**Backend Environment (via pydantic-settings):**
- Config file: `backend/app/config.py` (Settings class)
- Loads from `.env` file or environment variables
- `.env.example` present at `backend/.env.example`
- Key config groups: database, Firebase credentials, Google Sheets credentials, GCS bucket, Cloud Run URL, scheduler emails

**Frontend Environment (via Vite env vars):**
- All prefixed with `VITE_` for Vite injection
- `.env.example` present at `frontend/.env.example`
- Required vars: `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, `VITE_API_BASE_URL`

**Build:**
- `frontend/vite.config.ts` - Vite build config with `@` path alias to `./src`
- `frontend/tsconfig.json` - TypeScript project references (app, node, test configs)
- `backend/pyproject.toml` - Python project config with hatchling build system

## Platform Requirements

**Development:**
- Python 3.14+ (via `uv python install 3.14`)
- Node.js 20+ with npm
- PostgreSQL (local instance or Cloud SQL proxy)
- Firebase project with Auth enabled
- Google Sheets service account (for sync feature)

**Production:**
- Google Cloud Platform (asia-southeast2 region)
- Cloud Run (backend container)
- Cloud SQL PostgreSQL (database)
- Firebase Hosting (frontend SPA)
- Google Cloud Storage (file uploads)
- Cloud Scheduler (daily sync cron)
- Secret Manager (credentials storage)
- Artifact Registry (Docker images)
- Workload Identity Federation (CI/CD auth)

---

*Stack analysis: 2026-03-06*
