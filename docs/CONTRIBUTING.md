# Contributing

## Prerequisites

- **Python** 3.14+ with [uv](https://docs.astral.sh/uv/)
- **Node.js** 20+ with npm
- **Docker** & Docker Compose (for local dev stack)
- **Lefthook** (`brew install lefthook && lefthook install`)

## Development Setup

### Option 1: Docker Compose (recommended)

```bash
# Start all services (PostgreSQL, Firebase Emulator, MailHog, Backend, Frontend)
docker compose up

# Access points:
#   Frontend:          http://localhost:5173
#   Backend API:       http://localhost:8000
#   API docs:          http://localhost:8000/docs
#   MailHog UI:        http://localhost:8025
#   Firebase Emulator: http://localhost:4000
```

### Option 2: Manual setup

```bash
# Backend
cd backend
cp .env.example .env        # Edit with your DATABASE_URL, Firebase creds
uv sync                     # Install dependencies
uv run alembic upgrade head # Run database migrations
uv run uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
cp .env.example .env        # Set VITE_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```

See [docs/ENV.md](ENV.md) for all environment variables.

---

<!-- AUTO-GENERATED from package.json and pyproject.toml — do not edit manually -->

## Available Commands

### Frontend (`frontend/`)

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server with hot reload |
| `npm run build` | Type-check and production build |
| `npm run lint` | Run ESLint |
| `npm run preview` | Preview production build locally |
| `npm test` | Run Vitest in watch mode |
| `npm run test:run` | Run Vitest once (CI) |
| `npm run generate:api` | Generate TypeScript types from backend OpenAPI spec (requires backend running) |

### Backend (`backend/`)

| Command | Description |
|---------|-------------|
| `uv run uvicorn app.main:app --reload` | Start FastAPI dev server with hot reload |
| `uv run alembic upgrade head` | Run all pending database migrations |
| `uv run alembic revision --autogenerate -m "desc"` | Create new migration from model changes |
| `uv run ruff check .` | Lint Python code |
| `uv run ruff format .` | Format Python code |
| `uv run pytest tests/ -v` | Run all tests with verbose output |
| `uv run pytest tests/ --cov=app --cov-report=term-missing` | Run tests with coverage report |

### Smoke Tests (`smoke-tests/`)

| Command | Description |
|---------|-------------|
| `npm test` | Run all smoke tests |
| `npm run test:health` | Backend health check only |
| `npm run test:auth` | Auth enforcement only |
| `npm run test:frontend` | Frontend SPA only |
| `npm run test:db` | Database connectivity only |

### Git Hooks (Lefthook)

| Hook | What runs |
|------|-----------|
| `pre-push` | Backend lint + tests, Frontend lint + typecheck + tests (all in parallel) |

<!-- END AUTO-GENERATED -->

## Release Promotion

- Release from `develop` to `production` with a fast-forward only:

```bash
./scripts/promote-production.sh
```

- The script fetches `origin`, verifies the working tree is clean, fast-forwards
  `production` to `origin/develop`, and pushes `production`.
- If the script stops on `--ff-only`, `production` has drifted and should be
  reconciled back into `develop` before retrying.

---

## Testing

### Backend

- Framework: **pytest** with pytest-asyncio
- Coverage minimum: **28%** (tracked in `pyproject.toml`)
- Run: `uv run pytest tests/ -v`

### Frontend

- Framework: **Vitest** with React Testing Library
- Run: `npm run test:run`

### Smoke Tests

- Framework: **Playwright** (API-only, no browser)
- Target: deployed environments (staging/prod)
- See: [`smoke-tests/README.md`](../smoke-tests/README.md)

## Code Style

### Backend

- **Linter/formatter**: Ruff (`uv run ruff check .` / `uv run ruff format .`)
- Type hints required on all function signatures
- Follow existing patterns in `backend/app/`

### Frontend

- **Linter**: ESLint (`npm run lint`)
- TypeScript strict mode enabled
- Use existing component patterns in `frontend/src/components/`

## PR Checklist

- [ ] Code follows existing patterns
- [ ] Tests added/updated for changes
- [ ] `uv run ruff check .` passes (backend)
- [ ] `npm run lint` passes (frontend)
- [ ] `tsc --noEmit` passes (frontend)
- [ ] All tests pass locally
- [ ] Environment variables documented if added
