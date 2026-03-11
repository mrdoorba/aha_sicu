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

See the [Development Guide](docs/engineer/development-guide.md) for full setup instructions.

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

See the [Deployment Guide](docs/engineer/deployment-guide.md) for details.

## Documentation

### For Engineers

| Document | Description |
|----------|------------|
| [Project Overview](docs/engineer/project-overview.md) | Domain, workflow, tech stack, environments |
| [Architecture - Backend](docs/engineer/architecture-backend.md) | FastAPI modules, patterns, auth, DB |
| [Architecture - Frontend](docs/engineer/architecture-frontend.md) | React SPA, components, state, API client |
| [Architecture - Infrastructure](docs/engineer/architecture-infrastructure.md) | GCP resources, Terraform, CI/CD |
| [API Reference](docs/engineer/api-reference.md) | All REST endpoints with schemas |
| [Data Models](docs/engineer/data-models.md) | Database tables, relationships, migrations |
| [Scoring Engine](docs/engineer/scoring-engine.md) | Calculators, rules, verdict logic |
| [Development Guide](docs/engineer/development-guide.md) | Setup, testing, commands |
| [Deployment Guide](docs/engineer/deployment-guide.md) | CI/CD, environments, secrets |
| [Onboarding Guide](docs/engineer/onboarding-guide.md) | BD team walkthrough |

### For AI Agents

| Document | Description |
|----------|------------|
| [Codebase Map](docs/agent/CODEBASE.md) | File map, entry points, module boundaries |
| [Conventions](docs/agent/CONVENTIONS.md) | Naming, patterns, style guidelines |
| [Change Patterns](docs/agent/PATTERNS.md) | Step-by-step recipes for common changes |
