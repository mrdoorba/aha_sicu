# Architecture

**Analysis Date:** 2026-03-16

## Pattern Overview

**Overall:** Modular Full-Stack SPA with Layered Backend API

**Key Characteristics:**
- Modular REST API architecture (FastAPI) with domain-driven module organization
- Pluggable calculator engine with registry pattern for scoring computation
- React SPA with React Router, hooks-based state management, and React Query for server state
- Async-first database access using asyncpg connection pooling
- Dual authentication path: Firebase for users, Google OIDC for Cloud Scheduler jobs
- Feature driven by a centralized calculator registry

## Layers

**Frontend - UI Components Layer:**
- Purpose: Render user-facing pages, forms, dialogs, and layout
- Location: `src/components/`
- Contains: React components (`.tsx`), UI primitives from Radix UI
- Depends on: Hooks, context, services
- Used by: Pages

**Frontend - Pages Layer:**
- Purpose: Route-bound entry points that compose components and orchestrate data flows
- Location: `src/pages/`
- Contains: Page components (e.g., `EvaluationPage.tsx`, `BrandsPage.tsx`)
- Depends on: Hooks, components, context
- Used by: React Router

**Frontend - Hooks Layer:**
- Purpose: Encapsulate business logic, API calls, and state management
- Location: `src/hooks/`
- Contains: Custom React hooks that use `@tanstack/react-query`, form handling, and orchestration
- Examples: `useEvaluationOrchestrator.ts`, `useCalculator.ts`, `useAutoSaveForm.ts`
- Depends on: API client, context
- Used by: Components and pages

**Frontend - Services Layer:**
- Purpose: API client abstraction, authentication, and external integrations
- Location: `src/services/`
- Contains: `apiClient.ts` (openapi-fetch generated), auth services
- Depends on: Firebase SDK, HTTP client
- Used by: Hooks

**Frontend - Context Layer:**
- Purpose: Global state (auth, theme) using React Context API
- Location: `src/context/`
- Examples: `AuthContext.tsx` (user state and login/logout)
- Used by: Components, hooks

**Backend - Router Layer:**
- Purpose: HTTP endpoint definitions, request/response binding
- Location: `app/modules/{module}/router.py`
- Contains: FastAPI routes, path/query parameters, request validation
- Pattern: Each module has a `router.py` with endpoints for that domain
- Depends on: Service layer, dependency injection
- Used by: FastAPI app registration

**Backend - Service Layer:**
- Purpose: Business logic, orchestration, and coordination
- Location: `app/modules/{module}/service.py`
- Contains: Async functions that handle domain operations
- Examples: `evaluations/service.py`, `brands/service.py`, `sync/service.py`
- Depends on: Database queries, calculators, external APIs
- Used by: Routers

**Backend - Schemas Layer:**
- Purpose: Request/response validation and serialization
- Location: `app/modules/{module}/schemas.py`
- Contains: Pydantic models for API contracts
- Examples: `EvaluationStateResponse`, `ScoringRequest`, `EvaluationInputsUpdate`
- Used by: Routers (response_model), Services (return types)

**Backend - Database Queries Layer:**
- Purpose: Direct SQL/asyncpg interactions isolated from business logic
- Location: `app/db/queries/{domain}.py`
- Examples: `users.py`, `evaluations.py`, `brands.py`, `calculator_results.py`
- Pattern: Async functions that return raw query results
- Depends on: asyncpg connection pool
- Used by: Services

**Backend - Calculator Engine:**
- Purpose: Registry-based orchestration of calculator plugins
- Location: `app/calculators/engine.py`
- Contains: `CALCULATOR_REGISTRY` (single source of truth), status checking, execution dispatch
- Pattern: `CalculatorConfig` dataclass holds required files, manual inputs, and runner function
- Dependencies tracked via `FILE_TO_CALCULATORS` derived lookup
- Used by: Evaluations service

**Backend - Core Layer:**
- Purpose: Cross-cutting concerns (auth, exceptions, middleware, dependencies)
- Location: `app/core/`
- Contains:
  - `security.py` - Firebase token verification
  - `oidc.py` - Google OIDC token verification for Cloud Scheduler
  - `dependencies.py` - Dependency injection (auth, RBAC, db connection)
  - `exceptions.py` - Custom exception hierarchy
  - `middleware.py` - Exception handling middleware

**Backend - Database Connection Pool:**
- Purpose: Async connection management for Cloud SQL PostgreSQL
- Location: `app/db/connection.py`
- Contains: `DatabasePool` class with asyncpg pool lifecycle
- Pattern: Single `db` instance used throughout via async context manager
- Used by: All layers via `get_db_connection` dependency

## Data Flow

**Evaluation Workflow:**

1. User navigates to `/evaluation/{brandId}` (page component)
2. `EvaluationPage` uses `useEvaluationOrchestrator` hook to fetch brand, evaluation state, and calculator status
3. User fills form fields → `handleFieldChange` triggers `useAutoSaveForm` auto-save to `/api/v1/evaluations/{id}/inputs`
4. User uploads file → `useUpload` hook calls `/api/v1/evaluations/{id}/upload`
5. Upload triggers recalc of calculator status via `GET /api/v1/evaluations/{id}/status`
6. User clicks "Generate Score" → `useScoring` calls `POST /api/v1/evaluations/{id}/score`
7. Backend `evaluations/service.py:generate_score()`:
   - Gets evaluation inputs from DB
   - Runs scoring calculator via `app/calculators/scoring/_calculator.py`
   - Stores result in `calculator_results` table
   - Returns `ScoringResponse` with verdict, messages, detailed scores
8. Frontend displays score, category breakdown, and recommendations

**Calculator Execution Flow:**

1. Service calls `engine.get_calculator_status(conn, brand_id, category_type, manual_data, uploaded_files)`
2. Engine iterates `CALCULATOR_REGISTRY`, checks:
   - Required files present in `uploads` table (via query)
   - Required manual inputs present in `manual_data` (via helper)
3. Returns `CalculatorStatusResponse` with "ready"/"pending" per calculator
4. When "ready", user can trigger run:
   - `POST /api/v1/evaluations/{id}/run/{calculator_type}`
   - Service retrieves calculator from registry, calls its `runner()` function
   - Result stored in `calculator_results` table via `calculator_results.insert_result()`

**Sync Workflow (Google Sheets → Database):**

1. Admin clicks "Sync Brands" or Cloud Scheduler triggers `POST /api/v1/sync/execute`
2. `sync/service.py` calls `sheets_client.py` to fetch VP and Meeting data
3. Synced data written to `brands`, `brand_vp_data`, `brand_meeting_data` tables
4. Status tracked in `sync_status` table
5. Frontend polls `/api/v1/sync/status` for progress
6. UI updates via `useSync` hook with real-time progress

**Authentication Flow:**

1. User logs in via Firebase Auth SDK (frontend: `firebaseAuthService`)
2. Token sent in `Authorization: Bearer {token}` header
3. Backend `dependencies.py:get_current_user()`:
   - Tries Firebase path first (user login)
   - Falls back to OIDC path (Cloud Scheduler service account)
   - Creates/updates user in DB, returns user context
4. RBAC via `require_role("admin", "leader")` dependency enforcer

## Key Abstractions

**Calculator Registry:**
- Purpose: Single source of truth for all calculators and their dependencies
- Location: `app/calculators/engine.py`
- Example: `CALCULATOR_REGISTRY["ads_keyword"]` holds `CalculatorConfig` with required files/manual, runner function
- Pattern: New calculators added by extending registry, no code changes to orchestration logic

**Evaluation Inputs:**
- Purpose: Represents user-entered data for a brand evaluation
- Stored as JSONB in `evaluation_inputs.manual_data`
- Structure: `{ products: { productCount }, competition: {...}, profitability: {...} }`
- Updated via `PATCH /api/v1/evaluations/{id}/inputs` with auto-save

**Calculator Results:**
- Purpose: Immutable snapshot of calculator execution
- Located: `calculator_results` table
- Schema: `{ calculator_type, output_text, details (JSONB), calculated_at }`
- Pattern: New calculations don't overwrite old ones; new row created

**Module Pattern:**
- Each domain (accounts, brands, evaluations, rules) follows:
  - `router.py` - HTTP contract
  - `service.py` - Business logic
  - `schemas.py` - Request/response types
  - `queries.py` (if needed) - DB access
- Modules mounted in `app/main.py` via `include_router()`

**API Client:**
- Location: `src/services/apiClient.ts`
- Pattern: openapi-fetch client with manually typed `paths` interface
- Provides: Type-safe `GET`, `POST`, `PATCH`, `DELETE` methods
- Authentication: Token automatically added by `firebaseAuthService`

**React Query Integration:**
- Pattern: Hooks use `useQuery`, `useMutation` from `@tanstack/react-query`
- Caching: Server state automatically cached by React Query
- Mutations: Form submissions trigger `useMutation` with auto-retry

## Entry Points

**Backend:**
- Location: `app/main.py`
- Triggers: Cloud Run container startup
- Responsibilities:
  - Initialize Firebase SDK
  - Create asyncpg pool
  - Register all module routers
  - Configure CORS middleware
  - Define lifespan (startup/shutdown)
- Health check: `GET /health`

**Frontend:**
- Location: `src/main.tsx`
- Triggers: Browser navigation to Firebase Hosting domain
- Responsibilities:
  - Mount React app to DOM
  - Set up theme provider
  - Initialize i18n
- Router: `src/App.tsx` defines all routes (login, dashboard, evaluation, etc.)

## Error Handling

**Strategy:** Custom exception hierarchy with semantic error codes and HTTP status codes

**Pattern:**
- Base exception: `AppException(code, detail, status_code)`
- Subclasses for domains: `AuthException`, `SyncException`, `UploadException`, `CalculatorException`
- Middleware handler: `app_exception_handler` in `core/middleware.py` converts exceptions to JSON responses
- Frontend: API calls include error handling via `useQuery` `isError`/`error`, `useMutation` `onError` callbacks

**Examples:**
- `AuthException("AUTH_TOKEN_INVALID", "Token validation failed", 401)`
- `UploadException("UPLOAD_FILE_EXISTS", "File already exists", 400)`
- `CalculatorException("CALC_MISSING_DATA", "Required files not available", 400)`

## Cross-Cutting Concerns

**Logging:**
- Backend: Python `logging` module configured in `app/main.py` at INFO level
- Frontend: Browser console via `console.log/warn/error`

**Validation:**
- Backend: Pydantic schemas validate all request bodies and query parameters
- Frontend: React Hook Form with Zod schemas for user input

**Authentication:**
- Backend: Dual-path in `dependencies.py` (Firebase for users, OIDC for schedulers)
- Frontend: `AuthContext` wraps app, `ProtectedRoute` enforces login, `RoleProtectedRoute` enforces RBAC

**Database Transactions:**
- Backend: Single connection per request (no explicit transactions in current code)
- Pattern: Alembic migrations handle schema changes, DDL is idempotent

**Rate Limiting:**
- Not implemented (could be added via middleware if needed)

**Caching:**
- Backend: Not implemented (queries execute fresh each request)
- Frontend: React Query handles result caching with stale-while-revalidate pattern

---

*Architecture analysis: 2026-03-16*
