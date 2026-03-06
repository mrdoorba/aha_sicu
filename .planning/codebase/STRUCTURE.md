# Codebase Structure

**Analysis Date:** 2026-03-06

## Directory Layout

```
aha_sicu/
├── .github/workflows/        # CI/CD pipeline
├── .planning/codebase/       # GSD analysis documents
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── main.py           # Application entry point
│   │   ├── config.py         # Pydantic Settings (env vars)
│   │   ├── calculators/      # Pure computation engines
│   │   ├── core/             # Auth, exceptions, middleware, deps
│   │   ├── db/
│   │   │   ├── connection.py # asyncpg pool singleton
│   │   │   ├── migrations/   # Alembic migrations
│   │   │   └── queries/      # Raw SQL query functions
│   │   ├── modules/          # Domain feature modules
│   │   │   ├── accounts/     # User account management
│   │   │   ├── auth/         # Auth endpoint (/me)
│   │   │   ├── brands/       # Brand data endpoints
│   │   │   ├── evaluations/  # Core evaluation logic
│   │   │   ├── rules/        # Scoring rules management
│   │   │   ├── sync/         # Google Sheets sync
│   │   │   └── upload/       # File upload + parsing
│   │   └── services/         # (Currently empty __init__.py)
│   ├── tests/                # Backend test suite
│   │   ├── unit/             # Unit tests by domain
│   │   └── integration/      # Integration/API tests
│   └── pyproject.toml        # Python project config
├── frontend/                 # React TypeScript SPA
│   ├── src/
│   │   ├── App.tsx           # Root component + routing
│   │   ├── main.tsx          # DOM entry point
│   │   ├── config.ts         # Runtime config (API URL)
│   │   ├── components/       # UI components by feature
│   │   │   ├── auth/         # ProtectedRoute, RoleProtectedRoute
│   │   │   ├── brands/       # BrandTable
│   │   │   ├── dashboard/    # Dashboard presentation components
│   │   │   ├── evaluation/   # Evaluation page components
│   │   │   │   ├── calculators/  # Calculator result displays
│   │   │   │   ├── forms/        # Manual input forms
│   │   │   │   └── scoring/      # Score display + email output
│   │   │   ├── evaluations/  # History table + dialogs
│   │   │   ├── layout/       # MainLayout, Header, Sidebar
│   │   │   ├── rules/        # Rules editing UI
│   │   │   ├── sync/         # Sync status display
│   │   │   └── ui/           # Primitive UI components (Radix-based)
│   │   ├── context/          # React contexts (AuthContext)
│   │   ├── firebase/         # Firebase config + auth helpers
│   │   ├── hooks/            # Custom React hooks (data fetching)
│   │   ├── lib/              # Utility functions
│   │   ├── locales/          # i18n translation files
│   │   ├── pages/            # Route-level page components
│   │   ├── services/         # API client
│   │   └── test/             # Test setup/utilities
│   ├── package.json          # Node dependencies
│   └── tsconfig.json         # TypeScript config
├── scripts/                  # Utility scripts (SQL, Python)
├── smoke-tests/              # Playwright smoke tests
├── docs/                     # Documentation
├── infrastructure/           # Terraform configs
├── firebase.json             # Firebase Hosting config
├── .firebaserc               # Firebase project aliases
├── CLAUDE.md                 # AI assistant instructions
└── GEMINI.md                 # AI assistant instructions
```

## Directory Purposes

**`backend/app/calculators/`:**
- Purpose: Pure computation logic for evaluation metrics
- Contains: Individual calculator modules + orchestration engine
- Key files: `engine.py` (readiness checks, auto-execute orchestration), `scoring.py` (final score calculator), `ads_keyword.py`, `discount.py`, `top_sku.py`

**`backend/app/core/`:**
- Purpose: Framework-level cross-cutting concerns
- Contains: Auth verification, exception classes, middleware, dependency injection
- Key files: `dependencies.py` (get_current_user, require_role), `exceptions.py` (AppException hierarchy), `security.py` (Firebase token verification), `middleware.py` (error handler), `oidc.py` (OIDC verification)

**`backend/app/db/queries/`:**
- Purpose: All database access via raw parameterized SQL (no ORM)
- Contains: One file per domain entity
- Key files: `brands.py`, `evaluations.py`, `calculator_results.py`, `uploads.py`, `users.py`, `rules.py`, `sync_status.py`, `utils.py` (shared SQL helpers like `escape_like`)

**`backend/app/modules/`:**
- Purpose: Feature modules organized by domain
- Contains: Each module has `router.py`, `schemas.py`, and optionally `service.py` + specialized clients
- Pattern: `router.py` (FastAPI endpoints) -> `service.py` (business logic) -> `db/queries/*.py` (SQL)

**`frontend/src/components/ui/`:**
- Purpose: Primitive/reusable UI components based on Radix UI + shadcn/ui pattern
- Contains: `button.tsx`, `card.tsx`, `dialog.tsx`, `input.tsx`, `label.tsx`, `select.tsx`, `table.tsx`, `tabs.tsx`, `badge.tsx`, `calendar.tsx`, `collapsible.tsx`, `popover.tsx`, `progress.tsx`, `radio-group.tsx`, `sonner.tsx` (toast)

**`frontend/src/components/evaluation/`:**
- Purpose: All components for the evaluation workflow page
- Contains: Three sub-directories for distinct concerns
- Subdirs: `forms/` (manual data input forms), `calculators/` (calculator result displays), `scoring/` (score display, email output, verdict selection)

**`frontend/src/hooks/`:**
- Purpose: Data fetching and mutation hooks wrapping API calls
- Contains: One hook file per domain concern
- Key files: `useEvaluation.ts`, `useCalculator.ts`, `useScoring.ts`, `useUpload.ts`, `useBrands.ts`, `useSync.ts`, `useRules.ts`, `useAccounts.ts`, `useAutoSaveForm.ts`

**`frontend/src/services/`:**
- Purpose: HTTP client configuration
- Contains: Single file with typed API client
- Key file: `apiClient.ts` (openapi-fetch client with manually defined paths interface, auth + error middleware)

## Key File Locations

**Entry Points:**
- `backend/app/main.py`: FastAPI application factory (CORS, lifespan, router registration)
- `frontend/src/main.tsx`: React DOM root
- `frontend/src/App.tsx`: Route definitions and providers

**Configuration:**
- `backend/app/config.py`: Pydantic `Settings` class loading from env vars
- `frontend/src/config.ts`: Runtime config (API base URL)
- `frontend/src/firebase/config.ts`: Firebase client SDK config
- `firebase.json`: Firebase Hosting rewrite rules
- `.github/workflows/ci.yml`: CI pipeline definition

**Core Logic:**
- `backend/app/calculators/scoring.py`: Final score calculation (pure function)
- `backend/app/calculators/engine.py`: Calculator orchestration (readiness, auto-execute)
- `backend/app/modules/evaluations/service.py`: Evaluation business logic
- `backend/app/modules/upload/service.py`: File upload pipeline (signed URL, parse, store, auto-calc)
- `backend/app/modules/sync/service.py`: Google Sheets sync orchestration

**Auth:**
- `backend/app/core/dependencies.py`: `get_current_user` + `require_role`
- `backend/app/core/security.py`: Firebase token verification
- `frontend/src/context/AuthContext.tsx`: Client-side auth state
- `frontend/src/firebase/auth.ts`: Firebase auth operations
- `frontend/src/components/auth/ProtectedRoute.tsx`: Route guard
- `frontend/src/components/auth/RoleProtectedRoute.tsx`: Role-based route guard

**Database:**
- `backend/app/db/connection.py`: asyncpg pool singleton
- `backend/app/db/queries/*.py`: All SQL queries
- `backend/app/db/migrations/versions/`: Schema migrations (001-020)

**Testing:**
- `backend/tests/unit/`: Backend unit tests
- `backend/tests/integration/api/`: Backend API integration tests
- `frontend/src/**/*.test.{ts,tsx}`: Frontend tests (co-located)
- `smoke-tests/`: Playwright E2E smoke tests (separate package)

## Naming Conventions

**Files (Backend):**
- Snake_case for all Python files: `calculator_results.py`, `sync_status.py`
- Module structure: `router.py`, `schemas.py`, `service.py` per module
- Migration files: `NNN_description.py` (e.g., `001_create_users_table.py`)

**Files (Frontend):**
- PascalCase for React components: `BrandTable.tsx`, `EvaluationPage.tsx`
- camelCase for hooks: `useBrands.ts`, `useEvaluation.ts`
- camelCase for utilities: `apiClient.ts`, `categoryMap.ts`
- Test files co-located with source: `*.test.tsx` / `*.test.ts`

**Directories:**
- Lowercase with underscores (backend): `calculator_results`, `sync_status`
- Lowercase with hyphens or plain words (frontend): `evaluation`, `auth`, `ui`

## Where to Add New Code

**New Backend Module:**
1. Create directory: `backend/app/modules/{module_name}/`
2. Add files: `__init__.py`, `router.py`, `schemas.py`, `service.py`
3. Add query file: `backend/app/db/queries/{module_name}.py`
4. Register router in `backend/app/main.py` via `app.include_router()`
5. Add migration if new tables needed: `backend/app/db/migrations/versions/0XX_description.py`

**New Backend Calculator:**
1. Create calculator: `backend/app/calculators/{name}.py`
2. Register in engine maps: `CALCULATOR_REQUIRED_FILES`, `FILE_TO_CALCULATORS`, `_CALCULATOR_RUNNERS` in `backend/app/calculators/engine.py`
3. Add service wrapper in `backend/app/modules/evaluations/calculator_service.py`
4. Add router endpoint in `backend/app/modules/evaluations/router.py`

**New Frontend Page:**
1. Create page component: `frontend/src/pages/{Name}Page.tsx`
2. Add route in `frontend/src/App.tsx`
3. Create hook(s) in `frontend/src/hooks/use{Feature}.ts`
4. Add API path types in `frontend/src/services/apiClient.ts` (`paths` interface)

**New Frontend Component:**
1. Feature component: `frontend/src/components/{feature}/{ComponentName}.tsx`
2. Test file (co-located): `frontend/src/components/{feature}/{ComponentName}.test.tsx`
3. UI primitive: `frontend/src/components/ui/{name}.tsx` (lowercase, following shadcn/ui convention)

**New Frontend Hook:**
1. Create: `frontend/src/hooks/use{Feature}.ts`
2. Add API path types to `frontend/src/services/apiClient.ts` if new endpoints involved
3. Test file (co-located): `frontend/src/hooks/use{Feature}.test.ts`

**New Database Migration:**
1. Create: `backend/app/db/migrations/versions/0XX_description.py`
2. Follow existing pattern: `upgrade()` and `downgrade()` functions with raw SQL

**Utility Functions:**
- Backend: `backend/app/core/utils.py` (or create new core module)
- Frontend: `frontend/src/lib/` directory

## Special Directories

**`backend/app/services/`:**
- Purpose: Intended for shared services
- Generated: No
- Status: Currently empty (only `__init__.py`). Domain services live in modules instead.

**`backend/app/db/migrations/versions/`:**
- Purpose: Sequential Alembic schema migrations
- Generated: Manually authored
- Committed: Yes

**`frontend/src/components/ui/`:**
- Purpose: shadcn/ui-style primitive components (Radix UI wrappers)
- Generated: Initially generated via CLI, then customized
- Committed: Yes

**`smoke-tests/`:**
- Purpose: Playwright E2E smoke tests (separate npm package)
- Contains: Playwright config + test files
- Committed: Yes

**`infrastructure/terraform/`:**
- Purpose: Infrastructure as code
- Contains: Terraform configurations
- Committed: Yes

**`scripts/`:**
- Purpose: One-off operational scripts
- Contains: `assign-roles.sql`, `provision-users.py`, `users-config.example.yaml`
- Committed: Yes

---

*Structure analysis: 2026-03-06*
