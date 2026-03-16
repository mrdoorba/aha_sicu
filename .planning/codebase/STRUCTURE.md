# Codebase Structure

**Analysis Date:** 2026-03-16

## Directory Layout

```
aha_sicu/
├── backend/                    # FastAPI REST API (Python 3.14)
│   ├── app/
│   │   ├── main.py            # Entry point: FastAPI app initialization
│   │   ├── config.py          # Settings from environment
│   │   ├── core/              # Cross-cutting concerns
│   │   ├── db/                # Database connection, migrations, queries
│   │   ├── modules/           # Domain modules (routers, services, schemas)
│   │   └── calculators/       # Calculator plugins and engine
│   ├── tests/                 # Test files
│   ├── scripts/               # Utility scripts (e.g., seed_local.py)
│   ├── pyproject.toml         # Dependencies and project metadata
│   └── .env.example           # Environment config template
│
├── frontend/                   # React SPA (TypeScript)
│   ├── src/
│   │   ├── main.tsx           # Entry point
│   │   ├── App.tsx            # Router configuration
│   │   ├── components/        # React components (UI, layout, feature-specific)
│   │   ├── pages/             # Route-bound page components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API client and auth services
│   │   ├── context/           # React Context providers
│   │   ├── utils/             # Utility functions
│   │   ├── lib/               # External integrations (Firebase)
│   │   ├── locales/           # i18n translation files
│   │   ├── test/              # Test setup and fixtures
│   │   └── index.css          # Tailwind + theme globals
│   ├── public/                # Static assets
│   ├── package.json           # Dependencies
│   ├── vite.config.ts         # Build and test configuration
│   ├── tsconfig.json          # TypeScript configuration
│   └── .env.example           # Environment config template
│
├── infrastructure/            # Terraform IaC (GCP)
├── docs/                      # Project documentation
├── smoke-tests/               # Playwright E2E tests
├── scripts/                   # Utility scripts (provisioning, etc.)
├── docker/                    # Docker configurations
└── docker-compose.yml         # Local development orchestration
```

## Directory Purposes

**Backend - `app/` Root:**
- Purpose: Application code root
- Contains: Python modules with domain logic, infrastructure, database access
- Key entry: `main.py` (FastAPI app factory)

**Backend - `app/core/`:**
- Purpose: Infrastructure and cross-cutting concerns
- Key files:
  - `security.py` - Firebase token verification
  - `oidc.py` - Google OIDC verification for Cloud Scheduler
  - `dependencies.py` - Dependency injection (auth, RBAC, connection)
  - `exceptions.py` - Custom exception hierarchy
  - `middleware.py` - Exception handler middleware
  - `utils.py` - Shared utilities

**Backend - `app/db/`:**
- Purpose: Database access layer
- Structure:
  - `connection.py` - asyncpg connection pool lifecycle
  - `migrations/` - Alembic migration files (DDL)
  - `queries/` - Domain-specific query files (users, brands, evaluations, etc.)
- Pattern: Each query file contains async functions returning raw results

**Backend - `app/modules/`:**
- Purpose: Domain modules with HTTP contract, business logic, and schemas
- Modules:
  - `accounts/` - User account management (admin-only)
  - `auth/` - Authentication endpoints
  - `brands/` - Brand list and detail endpoints
  - `evaluations/` - Evaluation state and scoring
  - `rules/` - Scoring rule management (leader/admin)
  - `sync/` - Google Sheets synchronization
  - `config/` - App configuration endpoints
  - `email/` - Email sending (template-based)
  - `upload/` - File upload to GCS
- Each module has:
  - `router.py` - FastAPI endpoints
  - `service.py` - Business logic
  - `schemas.py` - Pydantic models
  - `queries.py` (optional) - Domain-specific DB access

**Backend - `app/calculators/`:**
- Purpose: Calculator plugin system and scoring engine
- Structure:
  - `engine.py` - Orchestration logic and `CALCULATOR_REGISTRY`
  - `scoring/` - Scoring calculator and rules
  - `top_sku.py`, `discount.py`, `ads_keyword.py` - Individual calculators
- Pattern: Registry-based plugin system; new calculators register in `CALCULATOR_REGISTRY`

**Frontend - `src/components/`:**
- Purpose: React components organized by feature and type
- Structure:
  - `ui/` - Radix UI primitive wrappers (button, input, dialog, etc.)
  - `layout/` - Header, Sidebar, MainLayout (shared across all pages)
  - `auth/` - ProtectedRoute, RoleProtectedRoute guards
  - `evaluation/` - Evaluation form sections, calculators, scoring
  - `evaluations/` - Evaluation history and detail tables
  - `brands/` - Brand list and search
  - `dashboard/` - Dashboard cards and metrics
  - `rules/` - Scoring rule management
  - `sync/` - Sync status display
  - `admin/` - Admin panels (if any)
- Naming: Feature-driven (e.g., `EvaluationPage.tsx`, `RulesCategoryCard.tsx`)
- Co-located tests: `*.test.tsx` files live alongside components

**Frontend - `src/pages/`:**
- Purpose: Route-bound page components that compose layout and feature components
- Files correspond to routes:
  - `LoginPage.tsx` - `/login`
  - `DashboardPage.tsx` - `/dashboard`
  - `BrandsPage.tsx` - `/brands`
  - `EvaluationPage.tsx` - `/evaluation/:brandId`
  - `EvaluationDetailPage.tsx` - `/history/:id`
  - `HistoryPage.tsx` - `/history`
  - `RulesPage.tsx` - `/rules`
  - `AccountsPage.tsx` - `/accounts`
- Each page uses hooks and components to render UI and handle data flows

**Frontend - `src/hooks/`:**
- Purpose: Encapsulate business logic, API calls, state management
- Key hooks:
  - `useEvaluationOrchestrator` - Coordinates evaluation page data and state
  - `useAutoSaveForm` - Auto-saves form fields at intervals
  - `useCalculator` - Fetches calculator status and results
  - `useScoring` - Generates scores via API
  - `useUpload` - Handles file uploads
  - `useRules` - Fetches and updates scoring rules
  - Data hooks: `useBrands`, `useEvaluationDetail`, `useCurrentUser`
- Pattern: Custom hooks return `{ data, error, isLoading, ...handlers }`

**Frontend - `src/services/`:**
- Purpose: API client and authentication services
- Files:
  - `apiClient.ts` - openapi-fetch client with typed `paths` interface
  - `firebaseAuthService.ts` - Firebase Authentication wrapper
  - `authService.ts` - Auth service interface definition

**Frontend - `src/context/`:**
- Purpose: React Context providers for global state
- Files:
  - `AuthContext.tsx` - User authentication state + login/logout

**Frontend - `src/lib/`:**
- Purpose: External SDK initialization
- Files: Firebase, i18n setup if needed

**Frontend - `src/locales/`:**
- Purpose: Translation files for i18n (id, en, th)
- Structure: JSON files per language

**Frontend - `src/utils/`:**
- Purpose: Shared utility functions
- Examples: `renderTranslatable.ts` - Renders multilingual text

**Frontend - `src/test/`:**
- Purpose: Shared test utilities and setup
- Files:
  - `setup.ts` - Vitest/JSDOM configuration

## Key File Locations

**Entry Points:**

- `backend/app/main.py` - FastAPI app initialization, router registration, lifespan management
- `frontend/src/main.tsx` - React DOM mount, theme provider
- `frontend/src/App.tsx` - React Router configuration with all route definitions

**Configuration:**

- `backend/app/config.py` - Pydantic settings from environment
- `backend/pyproject.toml` - Python dependencies and build config
- `frontend/package.json` - Node dependencies and scripts
- `frontend/vite.config.ts` - Vite build and test configuration
- `frontend/tsconfig.json` - TypeScript compilation options

**Core Logic:**

- `backend/app/calculators/engine.py` - Calculator registry and orchestration
- `backend/app/calculators/scoring/_calculator.py` - Scoring computation
- `backend/app/core/dependencies.py` - Dependency injection and RBAC
- `frontend/src/hooks/useEvaluationOrchestrator.ts` - Evaluation page orchestration
- `frontend/src/services/apiClient.ts` - API communication

**Testing:**

- `backend/tests/` - pytest tests for backend modules
- `frontend/src/**/*.test.tsx` - Vitest tests colocated with components
- `smoke-tests/` - Playwright end-to-end tests

**Database:**

- `backend/app/db/migrations/versions/` - Alembic migration files (001_*.py, 002_*.py, etc.)
- `backend/app/db/queries/` - Domain-specific query functions
- `backend/app/db/connection.py` - Connection pool management

**Domain Modules (Backend):**

- `backend/app/modules/accounts/` - User account CRUD (admin-only)
- `backend/app/modules/brands/` - Brand master data
- `backend/app/modules/evaluations/` - Evaluation inputs and scoring
- `backend/app/modules/rules/` - Scoring rule templates
- `backend/app/modules/sync/` - Google Sheets sync
- `backend/app/modules/upload/` - File upload to GCS
- `backend/app/modules/email/` - Email sending

## Naming Conventions

**Backend Files:**

- `router.py` - HTTP endpoints (FastAPI APIRouter)
- `service.py` - Business logic functions
- `schemas.py` - Pydantic request/response models
- `queries.py` - Database access functions
- `_calculator.py` - Internal implementation (leading underscore)
- `*.py` files: snake_case

**Backend Classes/Functions:**

- Exception classes: `PascalCase` (e.g., `AppException`, `AuthException`)
- Functions: `snake_case` (e.g., `get_user_by_firebase_uid`, `create_account`)
- Type hints: All function signatures include type hints

**Frontend Files:**

- Pages: `PascalCase` with `Page` suffix (e.g., `EvaluationPage.tsx`)
- Components: `PascalCase` (e.g., `RulesCategoryCard.tsx`, `MainLayout.tsx`)
- Hooks: `use` prefix + `PascalCase` (e.g., `useAutoSaveForm.ts`)
- Services: `camelCase` or `PascalCase` depending on export pattern
- Tests: Colocated as `*.test.tsx` or `*.test.ts`
- Utilities: `camelCase` (e.g., `renderTranslatable.ts`)

**Frontend Naming Conventions:**

- React components: PascalCase
- Component props interfaces: `${ComponentName}Props`
- Custom hooks: `use${HookName}`
- Constants: `UPPER_SNAKE_CASE`
- Variables/functions: `camelCase`
- CSS classes: Generated by Tailwind, not manual

**Directory Naming:**

- Backend: `snake_case` (e.g., `app/modules/evaluations/`)
- Frontend: `lowercase` (e.g., `src/components/evaluation/`)

## Where to Add New Code

**New Feature:**

1. **Backend API:**
   - Create module: `backend/app/modules/{feature_name}/`
   - Add `router.py` with endpoints
   - Add `service.py` with business logic
   - Add `schemas.py` with Pydantic models
   - Register router in `backend/app/main.py` via `app.include_router()`

2. **Frontend Pages:**
   - Create page: `frontend/src/pages/{FeatureName}Page.tsx`
   - Compose components and hooks
   - Add route to `frontend/src/App.tsx` with nested `<Route path=...>`
   - Add tests: `frontend/src/pages/{FeatureName}Page.test.tsx`

3. **Frontend Components:**
   - Create component: `frontend/src/components/{feature}/{FeatureName}.tsx`
   - Co-locate tests: `frontend/src/components/{feature}/{FeatureName}.test.tsx`
   - Use Tailwind classes, not manual CSS

4. **Frontend Hooks:**
   - Create hook: `frontend/src/hooks/use${HookName}.ts`
   - Add tests: `frontend/src/hooks/use${HookName}.test.ts`
   - Use React Query for server state (`useQuery`, `useMutation`)

**New Database Table:**

- Add Alembic migration: `backend/app/db/migrations/versions/{version}_create_{table_name}.py`
- Run: `uv run alembic upgrade head`
- Add query functions in: `backend/app/db/queries/{domain}.py`

**New Calculator Plugin:**

1. Create calculator file: `backend/app/calculators/{calculator_name}.py`
2. Implement runner function: `async def run_{calculator_name}(conn, brand_id, manual_data, files) -> dict`
3. Register in `backend/app/calculators/engine.py`:
   - Add entry to `CALCULATOR_REGISTRY`
   - Declare required files and manual inputs in `CalculatorConfig`
4. Add endpoint in `backend/app/modules/evaluations/router.py` if user-triggerable

**New Scoring Rule:**

- Add rule template to `backend/app/db/migrations/versions/{version}_add_*_rule.py`
- Run migration to sync database
- Update frontend rule UI in `frontend/src/pages/RulesPage.tsx`

## Special Directories

**Backend - `app/db/migrations/`:**
- Purpose: Alembic DDL migrations (version control for database schema)
- Generated: No (manually created)
- Committed: Yes
- Pattern: Each file is numbered (001_*, 002_*, etc.) and idempotent
- Running: `uv run alembic upgrade head` (local dev)

**Frontend - `dist/`:**
- Purpose: Build output directory (Vite)
- Generated: Yes (by `npm run build`)
- Committed: No (in .gitignore)

**Frontend - `node_modules/`:**
- Purpose: npm packages
- Generated: Yes (by `npm install`)
- Committed: No (in .gitignore)

**Backend - `.env` files:**
- Purpose: Environment-specific configuration
- Generated: No (user creates from .env.example)
- Committed: No (in .gitignore)
- Contains: Secrets like DATABASE_URL, Firebase credentials, SMTP password, etc.

**CI/CD - `.github/workflows/`:**
- Purpose: GitHub Actions pipeline definitions
- Files: Separate workflows for backend tests, frontend tests, deployment
- Committed: Yes

**Infrastructure - `infrastructure/`:**
- Purpose: Terraform IaC for GCP resources
- Contains: Cloud Run, Cloud SQL, Firebase Hosting, Secret Manager
- Committed: Yes

---

*Structure analysis: 2026-03-16*
