# Technology Stack

**Analysis Date:** 2026-03-16

## Languages

**Primary:**
- Python 3.14+ - Backend API (FastAPI)
- TypeScript 5.9 - Frontend (React) and smoke tests

**Secondary:**
- JavaScript - Browser runtime for frontend
- Shell (Bash) - Docker entrypoints and scripts
- Dockerfile - Containerization

## Runtime

**Environment:**
- Python 3.14+ (backend)
- Node.js (frontend dev, build, and smoke tests)
- PostgreSQL 18 (database)

**Package Manager:**
- Backend: `uv` (Python package manager)
  - Lockfile: `uv.lock` (present at `/Users/mac/HT/Project/aha_sicu/backend/uv.lock`)
- Frontend: `npm`
  - Lockfile: `package-lock.json` (present at `/Users/mac/HT/Project/aha_sicu/frontend/package-lock.json`)
- Smoke tests: `npm`
  - Lockfile: `package-lock.json` (present at `/Users/mac/HT/Project/aha_sicu/smoke-tests/package-lock.json`)

## Frameworks

**Core:**
- FastAPI 0.115.0+ - Web framework for Python backend
- React 19.2.0 - Frontend UI library
- Vite 7.2.4 - Frontend build tool and dev server

**Testing:**
- pytest 8.0.0+ (backend) - Python test runner with asyncio support
- Vitest 4.0.18 (frontend) - Frontend unit/integration tests
- Playwright 1.58 (smoke tests) - E2E testing framework

**Build/Dev:**
- Vite 7.2.4 - Frontend bundler and dev server
- TypeScript 5.9 - Type checking for frontend and tests
- Tailwind CSS 4.1.18 - Utility-first CSS framework
- PostCSS 8.5.6 - CSS transformation tool

**ORM/Database:**
- SQLAlchemy (implicit via asyncpg) - ORM for Python backend
- asyncpg 0.30.0 - PostgreSQL async driver
- Alembic 1.13.0 - Database migration tool

## Key Dependencies

**Backend - Critical:**
- `fastapi` - HTTP framework
- `firebase-admin` 6.0.0+ - Firebase authentication and admin operations
- `asyncpg` 0.30.0 - PostgreSQL async client
- `uvicorn[standard]` 0.32.0+ - ASGI server
- `pydantic-settings` 2.6.0+ - Environment configuration management

**Backend - Infrastructure:**
- `google-cloud-storage` 2.18.0+ - Google Cloud Storage client for file uploads
- `google-api-python-client` 2.150.0+ - Google Sheets API client
- `google-auth` 2.38.0+ - Google authentication library
- `alembic` 1.13.0+ - Database migration framework
- `polars` 1.0.0+ - Data manipulation for analytics
- `fastexcel` 0.12.0+ - Excel file generation
- `python-multipart` 0.0.9+ - Multipart form data parsing
- `email-validator` 2.3.0+ - Email validation
- `psycopg2-binary` 2.9.11+ - PostgreSQL adapter (binary)

**Frontend - UI:**
- `@tanstack/react-query` 5.90.20+ - Server state management
- `@tanstack/react-table` 8.21.3+ - Table component library
- `react-router-dom` 7.13.0+ - Client-side routing
- `react-hook-form` 7.71.1+ - Form state and validation
- `lucide-react` 0.563.0+ - Icon library
- `recharts` 3.7.0+ - Chart library
- `radix-ui` 1.4.3+ - Headless UI components
- `sonner` 2.0.7+ - Toast notifications
- `clsx` 2.1.1+ - CSS class composition
- `class-variance-authority` 0.7.1+ - Variant utilities for components
- `tailwind-merge` 3.4.0+ - Tailwind CSS class merging

**Frontend - API & Auth:**
- `firebase` 12.8.0+ - Firebase SDK for authentication
- `openapi-fetch` 0.15.0+ - Typed OpenAPI client generation

**Frontend - Internationalization:**
- `i18next` 25.8.13+ - i18n framework
- `react-i18next` 16.5.4+ - React binding for i18next

**Frontend - Utilities:**
- `date-fns` 4.1.0+ - Date manipulation
- `react-day-picker` 9.13.2+ - Date picker component
- `next-themes` 0.4.6+ - Theme management (dark/light)

**Dev Only:**
- Backend: `pytest-asyncio`, `pytest-xdist`, `httpx`, `xlsxwriter`, `ruff`
- Frontend: `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`, `@vitejs/plugin-react`, `eslint`

## Configuration

**Environment:**
- Backend configuration: `app/config.py` - Pydantic BaseSettings
- Frontend config: Environment variables prefixed with `VITE_`
- Database URL construction: Via `DATABASE_URL` env var (local) or individual components (Cloud SQL)
- `.env` files present for both backend and frontend (not committed)
- `.env.example` files provided as templates

**Build:**
- Frontend: `vite.config.ts` - Vite build configuration
- Frontend: `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `tsconfig.test.json` - TypeScript configurations
- Backend: `pyproject.toml` - Poetry/uv project config with build system specification
- Frontend: `components.json` - Shadcn/ui component configuration
- Frontend: `eslint.config.js` - ESLint configuration

## Platform Requirements

**Development:**
- Python 3.14+
- Node.js (recent LTS)
- Docker & Docker Compose (for local dev services)
- PostgreSQL 18 (or use docker-compose service)
- Firebase Auth Emulator (or use docker-compose service)
- MailHog or SMTP service (or use docker-compose service)

**Production:**
- Google Cloud Run (backend deployment target)
- Firebase Hosting (frontend deployment target)
- Cloud SQL PostgreSQL (managed database)
- Google Cloud Storage (file uploads)
- Gmail SMTP or equivalent email service

---

*Stack analysis: 2026-03-16*
