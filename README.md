# Store ICU (AHA SICU)

Brand health evaluation system for Shopee e-commerce stores. Enables Business Development teams to evaluate brand performance across operational, business, content, and advertising dimensions using a structured scoring framework.

## Live Environments

| Environment | Frontend | Backend |
|-------------|----------|---------|
| **Production** | [aha-coms-sicu-prod.web.app](https://aha-coms-sicu-prod.web.app) | Cloud Run (asia-southeast2) |
| **Staging** | [aha-coms-sicu-dev.web.app](https://aha-coms-sicu-dev.web.app) | Cloud Run (asia-southeast2) |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, TypeScript 5.9, Vite 7.2, Tailwind CSS 4.1 |
| **Backend** | Python 3.14, FastAPI, asyncpg, Alembic |
| **Database** | Cloud SQL PostgreSQL 18 |
| **Auth** | Firebase Authentication |
| **Infrastructure** | Terraform, GCP (Cloud Run, Cloud SQL, Firebase Hosting, Cloud Storage, Secret Manager, Cloud Scheduler) |
| **CI/CD** | GitHub Actions |

## Project Structure

```
aha_sicu/
├── backend/           # FastAPI REST API (Python 3.14)
├── frontend/          # React SPA (TypeScript)
├── infrastructure/    # Terraform IaC (GCP)
├── scripts/           # Utility scripts (user provisioning, role assignment)
├── smoke-tests/       # Playwright production smoke tests
├── docs/              # Project documentation
├── .github/workflows/ # CI/CD pipelines
└── CLAUDE.md          # AI agent instructions
```

## Getting Started

See [Contributing](docs/CONTRIBUTING.md) for full setup instructions.

**Quick start:**

```bash
# Backend
cd backend && uv sync && cp .env.example .env
# Edit .env with your DATABASE_URL, Firebase credentials, etc.
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

## CI/CD

Runs on every PR to `develop` or `main`:

- **Backend**: `ruff check .` → `pytest -v`
- **Frontend**: `npm run lint` → `tsc --noEmit` → `vitest run` → `npm run build`

Deployment triggers on push:
- `develop` → auto-deploy to dev environment
- `main` → deploy to production (manual approval)

See the [Runbook](docs/RUNBOOK.md) for deployment details.

## Documentation

| Document | Description |
|----------|------------|
| [Contributing](docs/CONTRIBUTING.md) | Setup, commands, testing, code style, PR checklist |
| [Environment Variables](docs/ENV.md) | All env vars for backend, frontend, Docker, and CI/CD |
| [Runbook](docs/RUNBOOK.md) | Deployment, health checks, troubleshooting, rollback |
| [GitHub Environment Vars](infrastructure/GITHUB_ENVIRONMENT_VARS.md) | CI/CD variables per deployment target |
| [Smoke Tests](smoke-tests/README.md) | Playwright API smoke tests for deployed environments |
