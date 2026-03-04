# AHA SICU — Codebase Map

Brand health evaluation system for Shopee e-commerce stores. Enables BD teams to score brands across operational, business, content, and advertising dimensions.

| Environment | Frontend | Backend |
|---|---|---|
| **Production** | [aha-sicu-prod.web.app](https://aha-sicu-prod.web.app) | Cloud Run (asia-southeast2) |
| **Staging** | [aha-sicu-dev.web.app](https://aha-sicu-dev.web.app) | Cloud Run (asia-southeast2) |

---

## Tech Stack Summary

| Layer | Stack |
|---|---|
| **Frontend** | React 19, TypeScript 5.9, Vite 7.2, TailwindCSS 4.1, Tanstack Query/Table, Radix UI (shadcn), Recharts, react-hook-form, react-router-dom 7, Firebase Auth, i18next (Indonesian) |
| **Backend** | Python 3.14, FastAPI, asyncpg, Alembic, polars, fastexcel, Firebase Admin, GCS |
| **Database** | Cloud SQL PostgreSQL 18 |
| **Infrastructure** | Terraform → GCP (Cloud Run, Cloud SQL, Firebase Hosting, Cloud Storage, Secret Manager, Cloud Scheduler, Artifact Registry, Workload Identity) |
| **CI/CD** | GitHub Actions (3 workflows: `ci.yml`, `deploy-backend.yml`, `deploy-frontend.yml`) |

---

## Project Root

```
aha_sicu/
├── backend/           # FastAPI REST API
├── frontend/          # React SPA
├── infrastructure/    # Terraform IaC (GCP)
├── scripts/           # Utility scripts (provision-users.py, assign-roles.sql)
├── smoke-tests/       # Playwright production smoke tests
├── docs/              # 18 documentation files
├── my-local-resources/# Local test upload files
├── .github/workflows/ # CI/CD pipelines
├── firebase.json      # Firebase Hosting config
├── CLAUDE.md / GEMINI.md  # AI agent instructions
└── README.md
```

---

## Backend — `backend/`

**Entry**: [main.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/main.py) — FastAPI app with lifespan, CORS, 7 routers, `/health` endpoint.

### `app/core/` — Cross-cutting concerns
| File | Purpose |
|---|---|
| [config.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/config.py) | Pydantic Settings (DB URL, Firebase creds, pool sizes) |
| [dependencies.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/core/dependencies.py) | FastAPI dependency injection (auth, DB pool) |
| [security.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/core/security.py) | Firebase Admin SDK initialization |
| [oidc.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/core/oidc.py) | OIDC token verification |
| [exceptions.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/core/exceptions.py) | Custom `AppException` class |
| [middleware.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/core/middleware.py) | Exception handler middleware |
| [utils.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/core/utils.py) | Shared utilities |

### `app/modules/` — API routers (7 modules)

Each module follows the pattern: `router.py` + `schemas.py` (+ optional service/utils).

| Module | Route Prefix | Purpose |
|---|---|---|
| `auth/` | `/api/v1/me` | Current user info |
| `accounts/` | `/api/v1/accounts` | User account management (admin) |
| `brands/` | `/api/v1/brands` | Brand CRUD |
| `evaluations/` | `/api/v1/evaluations` | Evaluation CRUD, scoring, history |
| `rules/` | `/api/v1/rules` | Scoring rule configuration |
| `sync/` | `/api/v1/sync` | Data sync status & triggers |
| `upload/` | `/api/v1/upload` | File upload (Excel → GCS → parsed) |

### `app/calculators/` — Scoring Engine

| File | Purpose |
|---|---|
| [scoring.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/calculators/scoring.py) | **Main scoring logic** (79KB, 75-row system) |
| [engine.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/calculators/engine.py) | Score calculation orchestrator |
| [ads_keyword.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/calculators/ads_keyword.py) | Ads keyword analysis calculator |
| [discount.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/calculators/discount.py) | Discount analysis calculator |
| [top_sku.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/calculators/top_sku.py) | Top SKU analysis calculator |

### `app/db/` — Database Layer

| Path | Purpose |
|---|---|
| [connection.py](file:///Users/mac/HT/Project/aha_sicu/backend/app/db/connection.py) | asyncpg connection pool singleton |
| `queries/brands.py` | Brand queries |
| `queries/evaluations.py` | Evaluation queries (10KB, largest query module) |
| `queries/rules.py` | Scoring rules queries |
| `queries/uploads.py` | Upload record queries |
| `queries/sync_status.py` | Sync status queries |
| `queries/calculator_results.py` | Calculator result queries |
| `queries/users.py` | User queries |
| `migrations/` | Alembic config + **21 migration versions** |

### `tests/` — Backend Tests
- `unit/` — 23 files (calculators, modules, core)
- `integration/` — 19 files (API endpoint tests)
- [conftest.py](file:///Users/mac/HT/Project/aha_sicu/backend/tests/conftest.py) — Shared fixtures

---

## Frontend — `frontend/`

**Entry**: [main.tsx](file:///Users/mac/HT/Project/aha_sicu/frontend/src/main.tsx) → [App.tsx](file:///Users/mac/HT/Project/aha_sicu/frontend/src/App.tsx) (QueryClientProvider + BrowserRouter + AuthProvider wrapping all routes).

### Routes (from `App.tsx`)

| Path | Page | Auth |
|---|---|---|
| `/login` | `LoginPage` | Public |
| `/dashboard` | `DashboardPage` | Protected |
| `/brands` | `BrandsPage` | Protected |
| `/evaluation/:brandId` | `EvaluationPage` | Protected |
| `/history/:id` | `EvaluationDetailPage` | Protected |
| `/history` | `HistoryPage` | Protected |
| `/rules` | `RulesPage` | Role: leader, admin |
| `/accounts` | `AccountsPage` | Role: admin only |
| `/` | → Redirect to `/dashboard` | — |

### `components/` — 9 component groups

#### `ui/` — 16 shadcn/Radix primitives
badge, button, calendar, card, collapsible, dialog, input, label, popover, progress, radio-group, select, sonner (toast), table, tabs

#### `layout/` — App shell
`MainLayout.tsx`, `Header.tsx`, `Sidebar.tsx`, `ThemeToggle.tsx`

#### `evaluation/forms/` — 8 evaluation form types
`AdsForm`, `BusinessForm`, `CampaignForm`, `CompetitionForm`, `OperationalForm`, `ProductsStatusForm`, `PromoToolsForm`, `VisitorsForm`
+ shared fields: `CurrencyField`, `NumberField`, `SelectField`, `SaveIndicator`
+ [formConfig.ts](file:///Users/mac/HT/Project/aha_sicu/frontend/src/components/evaluation/forms/formConfig.ts) (16KB — field definitions for all forms)

#### `evaluation/scoring/` — Score display
`ScoringSection`, `ScorePanel`, `ScoreBreakdown`, `FinalScoreDisplay`, `VerdictSelector`, `PeriodSelector`, `EmailOutput`

#### `evaluation/calculators/` — Calculator results
`CalculatorResultsSection`, `AdsKeywordResults`, `DiscountResults`, `TopSkuResults`

#### `evaluation/` — Top-level evaluation components
`EvaluationHeader`, `EvaluationSections`, `FileUploadSection`, `FileUploadSlot`, `SectionNav`

#### `dashboard/` — Dashboard presentation
`PresentationDashboard`, `ScoreOverview`, `ScoreBreakdownChart`, `CategoryMetricCard`, `DataIntelligence`, `BrandSearch`, `DashboardHeader`, `DashboardFooter`, `DetailedEvaluation`

#### `brands/` — Brand management (2 files)
#### `auth/` — Auth components (3 files: `ProtectedRoute`, `RoleProtectedRoute`, +1)
#### `evaluations/` — Evaluation list components (7 files)
#### `rules/` — Rules editor (4 files)
#### `sync/` — Sync controls (2 files)

### `hooks/` — 20+ custom hooks

| Hook | Purpose |
|---|---|
| `useAutoSaveForm` | Auto-save form state with debounce |
| `useCalculator` | Trigger & poll calculator results |
| `useUpload` | File upload with progress |
| `useScoring` | Score computation |
| `useEvaluation` | Single evaluation CRUD |
| `useEvaluationDetail` | Detailed evaluation fetch |
| `useEvaluationHistory` | Historical evaluations |
| `useGroupedEvaluations` | Grouped eval list |
| `useSaveEvaluation` | Save evaluation mutation |
| `useDeleteEvaluation` | Delete evaluation mutation |
| `useBrands` / `useBrandDetail` / `useBrandEvaluations` | Brand data |
| `useRules` / `useUpdateRule` | Rules CRUD |
| `useSync` | Sync trigger & status |
| `useAccounts` | Account management |
| `useCurrentUser` | Current authenticated user |

### `services/` — API Client
[apiClient.ts](file:///Users/mac/HT/Project/aha_sicu/frontend/src/services/apiClient.ts) — **822 lines**, uses `openapi-fetch` with fully typed `paths` interface covering all API endpoints. Includes auth middleware (Firebase token injection) and server error middleware.

### `firebase/` — Firebase config
[config.ts](file:///Users/mac/HT/Project/aha_sicu/frontend/src/firebase/config.ts) — Firebase app initialization
[auth.ts](file:///Users/mac/HT/Project/aha_sicu/frontend/src/firebase/auth.ts) — `signInWithPopup`, `getCurrentUserToken`

### `context/` — React Context
[AuthContext.tsx](file:///Users/mac/HT/Project/aha_sicu/frontend/src/context/AuthContext.tsx) — Auth state provider

### `lib/` — Utilities
`categoryMap.ts` — Category ID→name mapping
`utils.ts` — `cn()` class merge helper

### `locales/` — i18n
`id.json` — Indonesian translations (20KB)

---

## Infrastructure — `infrastructure/terraform/`

| File | GCP Resource |
|---|---|
| `main.tf` | Provider config, project, region |
| `cloud_run.tf` | Cloud Run service (backend) |
| `cloud_sql.tf` | Cloud SQL PostgreSQL instance |
| `firebase.tf` | Firebase Hosting |
| `storage.tf` | Cloud Storage buckets (uploads) |
| `secrets.tf` | Secret Manager secrets |
| `iam.tf` | IAM bindings |
| `scheduler.tf` | Cloud Scheduler (cron sync jobs) |
| `artifact_registry.tf` | Docker image registry |
| `workload_identity.tf` | Workload Identity Federation (GitHub Actions) |
| `variables.tf` | Input variables |
| `outputs.tf` | Output values |
| `environments/` | Per-env variable overrides |

---

## CI/CD — `.github/workflows/`

| Workflow | Trigger | Steps |
|---|---|---|
| `ci.yml` | PR to develop/main | Backend: ruff + pytest; Frontend: lint + tsc + vitest + build |
| `deploy-backend.yml` | Push to develop/main | Docker build → push to Artifact Registry → deploy Cloud Run |
| `deploy-frontend.yml` | Push to develop/main | npm build → deploy Firebase Hosting |

---

## Scripts — `scripts/`

| File | Purpose |
|---|---|
| `provision-users.py` | Batch create Firebase users from YAML config |
| `assign-roles.sql` | SQL to assign user roles in DB |
| `users-config.example.yaml` | Example user config |

---

## Smoke Tests — `smoke-tests/`

Playwright-based production smoke tests with `MANUAL_CHECKLIST.md` for manual validation scenarios.

---

## Documentation — `docs/`

18 files covering: project overview, backend/frontend/infrastructure architecture, API contracts, data models, component inventory, integration architecture, development guide, deployment guide, onboarding guide, calculator logic reference (96KB), launch readiness, validation report template, source tree analysis.

---

## Key Patterns & Conventions

1. **Backend module pattern**: Each module has `router.py` (FastAPI routes) + `schemas.py` (Pydantic models), queries in `db/queries/`
2. **Frontend data flow**: `apiClient.ts` (typed openapi-fetch) → Tanstack Query hooks → Components
3. **Auth flow**: Firebase Auth (Google Sign-In popup) → token in `AuthContext` → injected via `authMiddleware` in `apiClient` → verified server-side via Firebase Admin SDK
4. **Roles**: 3 roles — `member` (default), `leader` (rules access), `admin` (full access + accounts)
5. **Scoring**: 75-row scoring framework with 4 categories (Operational, Business, Content/Ads, Competition), rule weights configurable via `/rules` page
6. **File uploads**: Excel files → GCS → parsed with polars/fastexcel → calculator results stored in DB
7. **State management**: Tanstack Query (server state), react-hook-form (form state), `useAutoSaveForm` (debounced persistence)
8. **Styling**: TailwindCSS 4.1 + shadcn/ui (Radix-based) + `cn()` class merge utility
9. **i18n**: react-i18next with Indonesian locale (`locales/id.json`)
10. **Testing**: Backend pytest (unit + integration); Frontend vitest + Testing Library (colocated `*.test.tsx`)
