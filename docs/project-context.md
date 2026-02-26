---
project_name: 'aha_sicu'
user_name: 'Mr. Door'
date: '2026-02-16'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow_rules', 'critical_rules']
status: 'complete'
rule_count: 95
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

### Frontend
- React 19 + TypeScript ~5.9 (tilde-pinned, patch-only updates) + Vite 7.2
- ES Modules throughout (`"type": "module"` — no `require()`)
- Tailwind CSS 4.1 via `@tailwindcss/vite` plugin (NOT PostCSS, NO `tailwind.config.js`)
  - CSS-first config with `@theme` directives (NOT JS config)
- Radix UI + shadcn/ui pattern with CVA for component variants
- TanStack React Query 5 for server state, React Hook Form 7 for forms
- React Router DOM 7 (v7 API, not v6 patterns)
- openapi-fetch 0.15 — typed API client (types manually maintained, no OpenAPI spec file)
- Firebase 12 for client-side authentication
- Vitest 4 + Testing Library (globals enabled — do NOT import `describe`/`it`/`expect`)

### Backend
- Python 3.14 + FastAPI 0.115+ + Uvicorn
- **Package manager: `uv`** (NOT pip/poetry) — use `uv run`, `uv sync`
- asyncpg for PostgreSQL — raw SQL with `$1`, `$2` params (NOT `%s` or `:name`)
- No ORM — all queries in `app/db/queries/` as explicit SQL
- Alembic for migrations — run via `uv run alembic upgrade head`
- Polars + fastexcel for Excel/data processing
- Firebase Admin for token verification
- Ruff for linting, Pytest + pytest-asyncio (`asyncio_mode = "auto"`, no `@pytest.mark.asyncio` needed)

### Infrastructure
- PostgreSQL on Cloud SQL (managed)
- GCP: Cloud Run (backend), Cloud SQL (database), Firebase Hosting (frontend), Cloud Storage (uploads)
- Terraform for IaC, GitHub Actions for CI/CD
- Playwright for production smoke tests

## Critical Implementation Rules

### Language-Specific Rules

#### TypeScript (Frontend)
- Path alias `@/` maps to `./src/` — always use it for non-relative imports
- Strict mode enabled with `erasableSyntaxOnly: true` — **no `enum` or `namespace`**
  - Use `as const` objects or union string literals instead of enums
- Use `type` imports for type-only usage: `import type { Foo } from '...'`
- No barrel re-exports in `src/components/ui/` — import each UI component directly
- Barrel exports (`index.ts`) used in nested feature subdirectories (e.g., `calculators/`, `scoring/`)
- Environment variables prefixed with `VITE_` — access via `import.meta.env.VITE_*`
- **Component function style**: Use `function` keyword for components, arrow functions for hooks/utilities
- **Named exports only** — no default exports anywhere. Use `// eslint-disable-next-line react-refresh/only-export-components` when co-exporting hooks with context
- **Double casting for API responses**: Use `as unknown as Type` (not `as Type`) when handling openapi-fetch data
- **`as const` for configuration maps** and discriminated union keys

#### Python (Backend)
- Type hints required on all function signatures — use `dict | None` not `Optional[dict]` (PEP 604, no `Optional` anywhere)
- Async/await for all I/O operations — no synchronous DB calls or HTTP requests
- Pydantic `BaseModel` for request/response schemas at HTTP boundary only
  - **Dataclasses for internal return types** (calculators use `@dataclass`, NOT Pydantic)
  - Pydantic `Field()` for string length constraints (`Field(default="", max_length=200)`)
- **JSONB field validators required**: Every JSONB field needs `@field_validator("field", mode="before")` with `_parse_json` helper — asyncpg may return JSONB as str or dict
- **asyncpg Record conversion**: Always convert with `dict(row)` or `[dict(r) for r in rows]` — never pass raw Records to Pydantic
- **`Literal` types for SQL identifiers**: Use `Literal["col_a", "col_b"]` + f-string for column/table names in SQL — don't parameterize identifiers with `$1`
- Use `asynccontextmanager` pattern for database connections: `async with db.connection() as conn:`
- Snake_case everywhere: files, functions, variables, module names
- No `print()` — use `logging.getLogger(__name__)` with f-string messages
- String formatting: f-strings preferred, never `%` or `.format()`
- Exception subclasses override `__init__` with pre-set `status_code` — follow existing hierarchy in `core/exceptions.py`

### Framework-Specific Rules

#### React (Frontend)
- **State management hierarchy**: React Query (server state) → Context (auth only) → useState (local UI)
  - Never use Redux, MobX, Zustand, or other external state libraries
  - Never cache server data in useState — always use React Query
- **Component organization**: Feature-based directories under `src/components/`
  - Pages in `src/pages/` — one file per route
  - Shared UI primitives in `src/components/ui/` (shadcn/ui pattern)
  - Feature components grouped by domain: `auth/`, `brands/`, `evaluation/`, `rules/`
- **Custom hooks**: All data-fetching logic lives in `src/hooks/use*.ts`
  - Hooks wrap React Query calls — components never call `apiClient` directly
  - Naming: `useEvaluation.ts`, `useBrands.ts`, `useSync.ts`
- **API client**: Single instance in `src/services/apiClient.ts`
  - Auth middleware auto-injects Firebase Bearer token — never add `Authorization` headers manually
  - Env vars centralized in `src/config/index.ts` — import from `@/config`, don't use `import.meta.env` directly
- **Import order convention**: React → external libs → `@/` absolute → relative imports
- **Forms**: React Hook Form for all form state
  - Auto-save pattern via `useAutoSaveForm` hook (500ms debounce)
- **Auth guard**: Wrap protected routes with `<ProtectedRoute>` / `<RoleProtectedRoute>`
- **Styling**: Tailwind utility classes + `cn()` helper (clsx + tailwind-merge)
  - Component variants via CVA (`class-variance-authority`)
  - Never use CSS modules, styled-components, or inline style objects
- **Toasts**: Use `sonner` (`toast.success()`, `toast.error()`) — not alert/window.confirm

#### FastAPI (Backend)
- **Module structure**: Each domain gets its own directory under `app/modules/`
  - `router.py` — thin HTTP layer, delegates to service
  - `service.py` — business logic, database calls
  - `schemas.py` — Pydantic request/response models
  - Optional: `calculator_service.py`, `handlers.py` for specialized logic
- **Three-layer call chain**: Router → Service → Query function (never skip layers)
  - SQL queries live in `app/db/queries/*.py` — never write inline SQL in services or routers
  - Services acquire connection via `async with db.connection() as conn:` then pass `conn` to query functions
- **Calculators are pure functions** (`app/calculators/`): NO database calls, NO I/O
  - Service layer (`calculator_service.py`) handles I/O and passes data to pure calculators
  - This separation is critical for testability
- **Router registration**: All routers registered in `app/main.py` via `app.include_router()`
- **Endpoint pattern**: Prefix all routes with `/api/v1/`
- **Auth dependency injection**: `Depends(get_current_user)` for authenticated endpoints
  - Role-based: `Depends(require_role("leader", "admin"))`
- **Lifespan pattern**: DB pool init/cleanup in `@asynccontextmanager async def lifespan()`
- **Account management**: `accounts` module — admin-only CRUD via Firebase Admin SDK

#### Cross-Stack Rules
- **Evaluation data flow**: Form sections map 1:1 to `manual_data` JSONB keys — adding a field requires updating `formConfig.ts` (frontend) AND backend schema
- **Immutable snapshots**: Saved evaluations are frozen records with versioned scoring rules — never update, only create new

### Testing Rules

#### Frontend (Vitest + Testing Library)
- **Globals enabled** — `describe`, `it`, `expect`, `vi` available without imports
- **Test files co-located** with source: `Component.tsx` → `Component.test.tsx` (same directory)
- **Setup file**: `src/test/setup.ts` — mocks Firebase, IntersectionObserver, Radix scroll APIs
  - Never re-mock Firebase in individual test files — global setup handles it
- **Render with providers**: Tests need `QueryClientProvider` + `MemoryRouter` wrappers
  - Create a fresh `QueryClient` per test file with `retry: false` to prevent slow retries
- **Mock hooks, not API calls**: Mock `useEvaluationHistory`, `useBrands`, etc. — not `apiClient`
  - Use **relative paths** in `vi.mock()` — matches codebase convention
- **No snapshot tests** — use explicit assertions with Testing Library queries
- **Pre-commit checks**: Run `npx tsc --noEmit` + `npm run lint` — CI runs both and will fail
- **Run**: `npm run test:run` (single pass) or `npm run test` (watch mode)

#### Backend (Pytest + pytest-asyncio)
- **`asyncio_mode = "auto"`** — all async tests run automatically, no decorator needed
- **Test directory**: `backend/tests/unit/` with domain subdirectories (`calculators/`, `core/`)
- **Fixtures in `conftest.py`** — shared fixtures like `make_excel_bytes` for test data
- **Inline test data** — define data constants at top of test files, not separate JSON fixtures
- **Calculator tests are extensive** — 22-88KB per file with thorough edge case coverage
- **No database in unit tests** — calculators are pure functions, test with direct data input
- **Integration tests**: Use `httpx.AsyncClient` with FastAPI test client pattern (not `requests`)
- **Pre-commit check**: Run `uv run ruff check .` — CI will fail on lint errors
- **Run**: `uv run pytest -v` (all tests) or `uv run pytest tests/unit/calculators/ -v` (specific)

#### Smoke Tests (Playwright)
- **Separate package**: `smoke-tests/` with independent `package.json`
- **Production verification only** — tests run against deployed environments
- **Test suites**: health, auth, frontend SPA, database connectivity, signed URLs
- **Run**: `npx playwright test` (from `smoke-tests/` directory)

#### CI Pipeline Checklist
- **Frontend CI**: lint → tsc --noEmit → vitest run → build (all must pass)
- **Backend CI**: ruff check → pytest (all must pass)
- **No coverage thresholds** — but all new code should include tests

### Code Quality & Style Rules

#### File & Folder Naming
- **Frontend files**: PascalCase for components (`BrandTable.tsx`), camelCase for hooks/utils (`useSync.ts`, `apiClient.ts`)
- **Backend files**: snake_case everywhere (`calculator_service.py`, `sync_status.py`)
- **Test files**: `Component.test.tsx` (frontend), `test_module.py` (backend)
- **Directories**: lowercase, feature-grouped (`components/evaluation/`, `modules/auth/`)

#### Frontend Code Style
- ESLint 9 flat config with `typescript-eslint` + `react-hooks` + `react-refresh` plugins
- **No Prettier** — do NOT install prettier or prettier plugins
- Named exports everywhere — no default exports
- Props: Destructure in function signature, not in body
- No JSDoc on React components — component name + props interface is sufficient
- Comment business logic only (scoring formulas, etc.), not code mechanics

#### Backend Code Style
- **Ruff** for linting and formatting (no flake8, black, isort)
- Docstrings: One-liner on public service functions, optional on query helpers — no `@param` blocks
- Constants: SCREAMING_SNAKE_CASE (`CALCULATOR_REQUIRED_FILES`, `FILE_TO_CALCULATORS`)
- Classes: PascalCase (`AppException`, `DatabasePool`, `Settings`)
- Query functions: Always accept `conn` as first parameter
- `app/core/` is for cross-cutting concerns ONLY (auth, exceptions, middleware) — never domain logic

#### Function Size Guidelines
- **Router functions**: 5-15 lines — extract params, call service, return response
- **Service functions**: 20-50 lines — one business operation per function
- **Query functions**: Single SQL query per function — transactions belong in service layer

#### Error Response Contract
- Backend errors use `AppException` → `{ "code": "ERROR_CODE", "detail": "message", "timestamp": "ISO" }`
- Error codes are SCREAMING_SNAKE_CASE — reuse existing codes from `core/exceptions.py`
- Frontend checks `error.code` for conditional logic — don't invent ad-hoc error shapes

#### General Rules
- No commented-out code — delete it, git has history
- No TODO comments without a linked issue
- Error messages should be user-facing quality (they reach the frontend)

### Development Workflow Rules

#### Git Branching Strategy
- **`main`** — Production. NO commits unless explicitly requested
- **`develop`** — Integration + deployment trigger. Merge from feature only when feature is complete and tested
  - Pushing to develop deploys to dev environment automatically
- **Feature branches** — All active work goes here first
  - Naming: `feat/`, `fix/`, `update/`, `refactor/`, `docs/`, `chore/` prefixes — lowercase, hyphen-separated
- **Flow**: Create feature branch → atomic commits → merge to `develop` (merge commit, NOT squash/rebase) → delete feature branch
- Delete feature branches immediately after merge — no stale branches

#### Commit Standards
- Atomic commits — one logical change per commit
- Commit immediately after completing a logical unit of work
- Commit message: concise, describes the "what" and "why"
- Author line: `Author: Mr. Door`

#### Local Development
- **Frontend**: `cd frontend && npm install && npm run dev` (Vite dev server)
- **Backend**: `cd backend && uv sync && uv run uvicorn app.main:app --reload`
  - Requires `.env` file — copy from `.env.example` and fill in values
  - `DATABASE_URL` is mandatory for startup
- **Frontend needs backend running** — without it, API calls fail silently (React Query shows loading)
- **Migrations**: `cd backend && uv run alembic upgrade head`

#### Dependency Management
- Frontend: `npm install` — commits `package-lock.json`
- Backend: `uv add <package>` — commits BOTH `pyproject.toml` AND `uv.lock` together
  - Docker build uses `uv sync --frozen` — stale lockfile breaks deployment

#### Pre-Push Checklist
- Frontend: `npm run lint && npx tsc --noEmit && npm run test:run && npm run build`
- Backend: `uv run ruff check . && uv run pytest -v`

#### CI/CD Pipeline
- **CI** (`ci.yml`): Runs on PRs to `develop`/`main` — lint + test + build must pass
- **Deploy Frontend** (`deploy-frontend.yml`): Push to `develop` → dev env, push to `main` → prod env
- **Deploy Backend** (`deploy-backend.yml`): Push to `develop` → dev Cloud Run, push to `main` → prod Cloud Run
- Smoke tests run post-deployment against live environment

#### Protected Directories (NEVER delete)
- `_bmad/`, `_bmad-output/`, `.agent/`, `.claude/`, `.cursor/`, `.gemini/`

### Critical Don't-Miss Rules

#### Anti-Patterns to Avoid
- **Never use an ORM** — no SQLAlchemy, no Tortoise, no Prisma. Raw asyncpg SQL only
- **Never use Pandas** — data processing uses **Polars** (`import polars as pl`). Different API entirely
- **Never install new state management** — no Redux, Zustand, MobX. React Query + Context is the stack
- **Never add `tailwind.config.js`** — Tailwind v4 uses CSS-first config via `@theme`
- **Never put domain logic in `app/core/`** — it's for auth, exceptions, middleware only
- **Never write inline SQL in routers or services** — all SQL lives in `app/db/queries/`
- **Never add I/O to calculator functions** — `app/calculators/` must remain pure
- **Never mutate saved evaluations** — they are immutable snapshots
- **Never skip the service layer** — routers don't call query functions directly
- **Never nest `db.connection()` calls** — acquire once in outermost service, pass `conn` down. Nesting risks pool deadlock (pool is only 1-5 connections)
- **Never add a Vite proxy** — frontend calls backend directly via `VITE_API_BASE_URL`, CORS handled server-side

#### Security Rules
- All endpoints require authentication via `Depends(get_current_user)` — no public endpoints except health check
- Role checks via `Depends(require_role(...))` — never check roles manually in service logic
- Never log tokens, passwords, or PII
- SQL parameterization is mandatory (`$1`, `$2`) — never use string concatenation or f-strings in SQL
- File uploads use signed URLs (GCS) — backend never handles raw file bytes in memory
- Firebase credentials and service account keys must stay in `.env` / Secret Manager — never commit them

#### Edge Cases Agents Must Handle
- **Dual auth**: `get_current_user` returns either a database user (Firebase) or a synthetic scheduler user (OIDC) — always check `user["id"]` which is `None` for scheduler
- **Two evaluation tables**: `evaluation_inputs` = mutable working draft (one per brand+user, upserted). `evaluations` = immutable saved snapshot (INSERT only). Don't confuse them
- **Calculator results persist**: Stored per brand+user in `calculator_results` table — not ephemeral, not per-evaluation
- **Scoring rules versioning**: When rules change, `version` auto-increments — saved evaluations store the `rule_version` at save time
- **Scoring structure**: 75 rows across 11 categories with 3 rule sections (`categories`, `interpretation`, `marketing`) — changes to one affect final score
- **Brand data split**: Brand info comes from TWO tables — `brand_vp_data` and `brand_meeting_data` — joined by `brand_name`
- **Calculator readiness**: Not all calculators can run — `check_calculator_readiness()` in `engine.py` determines which have sufficient data
- **Cloud SQL scheduling**: Instance auto-stops at 18:30 WIB, auto-starts at 08:30 WIB — dev/test connections will fail outside these hours
- **React Query cache keys**: Use structured keys — resource name first, params after (e.g., `['evaluations', page, limit]`). Inconsistent keys break invalidation
- **Migration numbering**: Sequential prefix convention (`014_description.py`) — don't use random Alembic hex IDs
- **date-fns v4**: Direct imports only (`import { format } from 'date-fns'`) — no subpath imports

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge

**For Humans:**
- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time

Last Updated: 2026-02-16
