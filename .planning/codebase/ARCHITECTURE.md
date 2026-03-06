# Architecture

**Analysis Date:** 2026-03-06

## Pattern Overview

**Overall:** Monorepo with separate frontend SPA and backend REST API, communicating over HTTP/JSON. Classic client-server architecture with Firebase Auth as the identity layer and PostgreSQL (Cloud SQL) as the data store.

**Key Characteristics:**
- Two-tier monorepo: `frontend/` (React SPA) and `backend/` (FastAPI)
- Module-based backend organized by domain (accounts, auth, brands, evaluations, rules, sync, upload)
- Frontend uses hooks-based data fetching with TanStack Query wrapping a typed `openapi-fetch` client
- Firebase Auth handles authentication; backend verifies tokens and manages its own user table
- All API routes prefixed with `/api/v1/`
- Deployment target: Google Cloud Run (backend) + Firebase Hosting (frontend)

## Layers

**Frontend - Pages Layer:**
- Purpose: Route-level components, one per page
- Location: `frontend/src/pages/`
- Contains: `DashboardPage.tsx`, `BrandsPage.tsx`, `EvaluationPage.tsx`, `HistoryPage.tsx`, `EvaluationDetailPage.tsx`, `RulesPage.tsx`, `AccountsPage.tsx`, `LoginPage.tsx`
- Depends on: Components, Hooks, Context
- Used by: `frontend/src/App.tsx` (router)

**Frontend - Components Layer:**
- Purpose: Reusable and feature-specific UI components
- Location: `frontend/src/components/`
- Contains: Feature components organized by domain (`auth/`, `brands/`, `dashboard/`, `evaluation/`, `evaluations/`, `rules/`, `sync/`, `layout/`, `ui/`)
- Depends on: Hooks, Services, UI primitives
- Used by: Pages

**Frontend - Hooks Layer:**
- Purpose: Data fetching, state management, and business logic encapsulation via React hooks
- Location: `frontend/src/hooks/`
- Contains: One hook per concern (e.g., `useBrands.ts`, `useEvaluation.ts`, `useCalculator.ts`, `useScoring.ts`, `useUpload.ts`, `useSync.ts`, `useRules.ts`, `useAccounts.ts`)
- Depends on: `frontend/src/services/apiClient.ts`
- Used by: Components, Pages

**Frontend - Services Layer:**
- Purpose: HTTP client with typed API paths and auth middleware
- Location: `frontend/src/services/apiClient.ts`
- Contains: Single `openapi-fetch` client with manually defined `paths` interface, auth token injection middleware, and server error detection middleware
- Depends on: `frontend/src/firebase/auth.ts`
- Used by: All hooks

**Frontend - Context Layer:**
- Purpose: Global auth state (Firebase user)
- Location: `frontend/src/context/AuthContext.tsx`
- Contains: `AuthProvider`, `useAuth` hook
- Depends on: `frontend/src/firebase/auth.ts`
- Used by: Protected routes, components needing user info

**Backend - Router Layer:**
- Purpose: HTTP endpoint definitions, request/response validation
- Location: `backend/app/modules/*/router.py`
- Contains: FastAPI route handlers with Pydantic schema validation
- Depends on: Service layer, Dependency injection (`backend/app/core/dependencies.py`)
- Used by: `backend/app/main.py` (registered via `include_router`)

**Backend - Service Layer:**
- Purpose: Business logic orchestration
- Location: `backend/app/modules/*/service.py`
- Contains: Functions that coordinate DB queries, calculators, and external services
- Depends on: DB queries, Calculators, Core utilities
- Used by: Routers

**Backend - Calculator Layer:**
- Purpose: Pure computation engines for brand evaluation metrics
- Location: `backend/app/calculators/`
- Contains: `ads_keyword.py`, `discount.py`, `top_sku.py`, `scoring.py`, `engine.py` (orchestrator)
- Depends on: DB queries (for data loading)
- Used by: Evaluation service, Upload service (auto-execute after upload)

**Backend - Database Query Layer:**
- Purpose: Raw SQL queries via asyncpg (no ORM)
- Location: `backend/app/db/queries/`
- Contains: `brands.py`, `calculator_results.py`, `evaluations.py`, `rules.py`, `sync_status.py`, `uploads.py`, `users.py`, `utils.py`
- Depends on: `asyncpg.Connection` passed as parameter
- Used by: Service layer

**Backend - Core Layer:**
- Purpose: Cross-cutting concerns (auth, exceptions, middleware, dependencies)
- Location: `backend/app/core/`
- Contains: `dependencies.py` (DI for auth/role), `exceptions.py`, `middleware.py`, `security.py` (Firebase token verification), `oidc.py` (OIDC verification for service accounts)
- Depends on: Firebase Admin SDK, Config
- Used by: All routers (via `Depends`)

**Backend - Database Migrations:**
- Purpose: Schema evolution
- Location: `backend/app/db/migrations/versions/`
- Contains: 20 sequential migration files (`001_` through `020_`)
- Tool: Alembic

## Data Flow

**Brand Sync (Google Sheets to DB):**

1. User triggers sync from frontend or Cloud Scheduler sends OIDC-authenticated POST to `/api/v1/sync`
2. `backend/app/modules/sync/router.py` delegates to `backend/app/modules/sync/service.py`
3. `GoogleSheetsClient` (`backend/app/modules/sync/sheets_client.py`) fetches VP and Meeting sheet data
4. Service upserts brand rows into `brand_vp_data` and `brand_meeting_data` tables
5. Sync status recorded in `sync_status` table

**Evaluation Flow:**

1. User selects a brand on frontend (`/evaluation/:brandId`)
2. Frontend loads brand detail, evaluation inputs, uploaded files, and calculator results via hooks
3. User uploads CSV/XLSX files via signed-URL two-step flow: `POST /upload/signed-url` -> PUT to GCS -> `POST /upload/process`
4. Upload processing: download from GCS, parse with Polars, validate columns, store parsed data in DB, auto-execute affected calculators
5. User fills manual form inputs, auto-saved via `PUT /evaluations/brands/{brand_id}`
6. User triggers scoring: `POST /evaluations/brands/{brand_id}/score` runs `backend/app/calculators/scoring.py` with manual inputs + calculator results + rules
7. User saves evaluation: `POST /evaluations/brands/{brand_id}/save` creates immutable evaluation record

**Authentication Flow:**

1. Frontend: Firebase `signInWithEmailAndPassword` -> receives Firebase ID token
2. `apiClient.ts` middleware attaches `Authorization: Bearer <token>` to every request
3. Backend: `get_current_user` dependency verifies Firebase token (or OIDC token for service accounts)
4. On first login, backend creates user row in `users` table; subsequent logins update `last_login`
5. Role-based access: `require_role()` dependency factory checks `user.role` against allowed roles

**State Management:**
- Server state managed via TanStack Query (React Query) with query key invalidation on mutations
- Auth state managed via React Context (`AuthContext`)
- No client-side state management library (no Redux/Zustand)
- Evaluation form auto-save via `useAutoSaveForm` hook

## Key Abstractions

**Calculator System:**
- Purpose: Modular computation engines that process uploaded data into evaluation metrics
- Location: `backend/app/calculators/`
- Types: `ads_keyword`, `discount`, `top_sku` (data calculators) and `scoring` (final score calculator)
- Pattern: Each calculator has a dependency map (required files + manual inputs). `engine.py` orchestrates readiness checking, selective execution, and dependency-aware cache clearing.

**Module Pattern (Backend):**
- Purpose: Domain-driven organization of API features
- Location: `backend/app/modules/{module_name}/`
- Structure: Each module contains `router.py`, `schemas.py`, `service.py` (some also have specialized clients like `sheets_client.py`, `gcs_client.py`)
- Pattern: Router -> Service -> DB Queries. Routers only handle HTTP concerns; services contain business logic.

**Typed API Client (Frontend):**
- Purpose: Type-safe API communication without code generation
- Location: `frontend/src/services/apiClient.ts`
- Pattern: Manually defined TypeScript `paths` interface matching backend endpoints, used with `openapi-fetch` for compile-time type checking on request/response shapes

**Hooks as Data Access Layer (Frontend):**
- Purpose: Encapsulate API calls + cache management per domain
- Location: `frontend/src/hooks/`
- Pattern: Each hook wraps TanStack Query `useQuery`/`useMutation` calls with proper query keys and invalidation

## Entry Points

**Backend Application:**
- Location: `backend/app/main.py`
- Triggers: `uvicorn` starts the FastAPI app
- Responsibilities: CORS setup, Firebase init, DB pool init, router registration, health check endpoint

**Frontend Application:**
- Location: `frontend/src/App.tsx` (with `frontend/src/main.tsx` as DOM entry)
- Triggers: Browser loads SPA
- Responsibilities: Route definitions, QueryClient provider, AuthProvider, layout structure

**Database Migrations:**
- Location: `backend/app/db/migrations/`
- Triggers: `alembic upgrade head`
- Config: `backend/app/db/migrations/alembic.ini` (or `env.py`)

**CI Pipeline:**
- Location: `.github/workflows/ci.yml`
- Triggers: PR to `develop` or `main`

## Error Handling

**Strategy:** Structured exception hierarchy on backend; error boundary pattern on frontend.

**Backend Patterns:**
- Base `AppException` with `code`, `detail`, `status_code` fields (`backend/app/core/exceptions.py`)
- Specialized subclasses: `AuthException` (401), `SyncException` (500), `UploadException` (400), `CalculatorException` (400)
- Global exception handler converts `AppException` to JSON response with `code`, `detail`, `timestamp` (`backend/app/core/middleware.py`)
- Services raise domain exceptions; routers do not catch

**Frontend Patterns:**
- API client throws on error responses; hooks re-throw with descriptive messages
- Server 500 errors trigger `api-server-error` custom event -> `DowntimeWarningDialog`
- TanStack Query handles retry and error state per query

## Cross-Cutting Concerns

**Logging:** Python `logging` module with `logging.basicConfig` at INFO level. Loggers created per module via `logging.getLogger(__name__)`.

**Validation:** Pydantic schemas for request/response validation on backend. Frontend uses TypeScript types aligned with API paths interface. Form validation via `react-hook-form`.

**Authentication:** Firebase Auth (email/password) for human users. Google OIDC for service accounts (Cloud Scheduler). Dual-path verification in `get_current_user` dependency. Role-based access control via `require_role()` dependency factory with roles: `member`, `leader`, `admin`, `scheduler`.

**Internationalization:** Frontend uses `i18next` + `react-i18next` with Indonesian locale (`frontend/src/locales/id.json`).

---

*Architecture analysis: 2026-03-06*
