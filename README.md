# Store ICU (AHA SICU)

Brand health evaluation system for Shopee e-commerce stores. Enables Business Development teams to evaluate brand performance across operational, business, content, and advertising dimensions using a structured scoring framework.

## Live Environments

| Environment | Frontend | Backend |
|-------------|----------|---------|
| **Production** | [aha-sicu-prod.web.app](https://aha-sicu-prod.web.app) | Cloud Run (asia-southeast2) |
| **Staging** | [aha-sicu-dev.web.app](https://aha-sicu-dev.web.app) | Cloud Run (asia-southeast2) |

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

See the [Development Guide](docs/development-guide.md) for full setup instructions.

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

See the [Deployment Guide](docs/deployment-guide.md) for details.

## Documentation

| Document | Description |
|----------|------------|
| [Project Overview](docs/project-overview.md) | Executive summary, workflow, tech stack |
| [Architecture - Backend](docs/architecture-backend.md) | FastAPI modules, scoring engine, auth |
| [Architecture - Frontend](docs/architecture-frontend.md) | React SPA, state management, components |
| [Architecture - Infrastructure](docs/architecture-infrastructure.md) | Terraform resources, CI/CD pipelines |
| [API Contracts](docs/api-contracts.md) | All REST endpoints with schemas |
| [Data Models](docs/data-models.md) | Database schema, 9 tables, migrations |
| [Component Inventory](docs/component-inventory.md) | React components, hooks, UI primitives |
| [Integration Architecture](docs/integration-architecture.md) | System communication, data flow diagrams |
| [Development Guide](docs/development-guide.md) | Setup, commands, workflows |
| [Deployment Guide](docs/deployment-guide.md) | GCP deployment instructions |
| [Onboarding Guide](docs/onboarding-guide.md) | BD team walkthrough |
| [Calculator Logic Reference](docs/calculator-logic-reference.md) | 75-row scoring system guide |
