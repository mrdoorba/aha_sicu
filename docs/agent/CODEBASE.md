# CODEBASE.md -- Machine-Optimized File Map

> AHA SICU -- Brand evaluation platform (FastAPI + React + PostgreSQL + Firebase Auth)
> Root: `/Users/mac/HT/Project/aha_sicu/`

---

## Key Entry Points

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app factory, CORS config, router registration, lifespan (Firebase init, DB pool) |
| `frontend/src/main.tsx` | React root -- StrictMode, ThemeProvider (next-themes), imports App |
| `frontend/src/App.tsx` | BrowserRouter, QueryClientProvider, AuthProvider, route definitions (9 routes), DowntimeWarningDialog |

---

## Backend File Map (`backend/app/`)

### Top-Level

| File | Purpose |
|------|---------|
| `config.py` | Pydantic BaseSettings -- all env vars (DB, Firebase, GCS, SMTP, Google Sheets) |
| `main.py` | App factory, CORS origins, AppException handler, 8 router includes, `/health` endpoint |

### `core/` -- Cross-Cutting Concerns

| File | Purpose |
|------|---------|
| `security.py` | `init_firebase()`, `verify_firebase_token()` -- Firebase Admin SDK token verification |
| `oidc.py` | `verify_oidc_token()` -- Google OIDC token verification for Cloud Scheduler service accounts |
| `dependencies.py` | `get_current_user()` DI (Firebase-first, OIDC fallback), `require_role()` factory |
| `exceptions.py` | `AppException` hierarchy (`AuthException`, etc.) with code + status_code |
| `middleware.py` | `app_exception_handler` -- global error handler converting AppException to JSON responses |
| `utils.py` | `ensure_dict()` -- safely parse JSONB values (handles legacy double-encoded strings) |

### `db/` -- Database Layer

| File | Purpose |
|------|---------|
| `connection.py` | AsyncPG pool singleton (`db.init()`, `db.connection()`, `db.close()`) |
| `queries/brands.py` | Brand list/detail/search SQL |
| `queries/calculator_results.py` | Calculator result CRUD SQL |
| `queries/evaluations.py` | Evaluation CRUD + inputs + scoring SQL |
| `queries/rules.py` | Scoring rules read/update SQL |
| `queries/sync_status.py` | Sync status read/update SQL |
| `queries/uploads.py` | File upload record SQL |
| `queries/users.py` | User CRUD (by firebase_uid, by id) SQL |
| `queries/utils.py` | `escape_like()` -- ILIKE pattern character escaping |
| `migrations/` | Alembic migrations (22 versions: 001-022) |
| `migrations/env.py` | Alembic environment config |

### `modules/` -- API Modules (each has router, schemas, service)

| Module | Prefix | Purpose |
|--------|--------|---------|
| `auth/` | `/api/v1` | `GET /me` -- return current user profile |
| `accounts/` | `/api/v1/accounts` | User CRUD (admin-only): list, create, update role, delete |
| `brands/` | `/api/v1/brands` | Brand listing (paginated, searchable) and detail |
| `evaluations/` | `/api/v1/evaluations` | Core evaluation workflow: CRUD, inputs save, scoring, calculator orchestration |
| `rules/` | `/api/v1/rules` | Scoring rules management (leader/admin only) |
| `sync/` | `/api/v1/sync` | Google Sheets brand data sync (manual + Cloud Scheduler triggered) |
| `upload/` | `/api/v1/upload` | Signed URL generation, file upload, processing, local dev fallback |
| `email/` | `/api/v1/email` | Email composition, preview, SMTP sending |

Notable extra files within modules:
- `evaluations/calculator_service.py` -- orchestrates calculator runs per evaluation
- `sync/sheets_client.py` -- Google Sheets API client wrapper
- `upload/gcs_client.py` -- GCS signed URL + upload operations
- `upload/parser.py` -- uploaded file content parsing
- `upload/zip_handler.py` -- ZIP file extraction and processing
- `email/template.py` -- HTML email template rendering

### `calculators/` -- Scoring & Analysis Engine

| File | Purpose |
|------|---------|
| `engine.py` | Calculator orchestration: dependency graph, readiness checks, run coordination |
| `scoring.py` | Score computation: weighted category scores, verdicts, breakdown generation |
| `ads_keyword.py` | CPC/keyword report analysis from uploaded ads data |
| `top_sku.py` | Top product ranking analysis |
| `discount.py` | Discount pattern analysis from transaction data |

### `services/` -- Shared Services

| File | Purpose |
|------|---------|
| `__init__.py` | (empty -- placeholder for shared service modules) |

---

## Frontend File Map (`frontend/src/`)

### Top-Level

| File | Purpose |
|------|---------|
| `App.tsx` | Route definitions (9 routes), QueryClientProvider, AuthProvider, DowntimeWarningDialog |
| `main.tsx` | React root with StrictMode, ThemeProvider (next-themes) |
| `config.ts` | `API_BASE_URL` constant (from VITE env) |
| `i18n.ts` | i18next setup (Indonesian locale) |
| `vite-env.d.ts` | Vite type declarations |

### `context/`

| File | Purpose |
|------|---------|
| `AuthContext.tsx` | Firebase auth state management, `useAuth()` hook, login/logout flow |

### `firebase/`

| File | Purpose |
|------|---------|
| `config.ts` | Firebase app initialization (project config) |
| `auth.ts` | `loginWithGoogle()`, `logout()`, `getCurrentUserToken()` |

### `services/`

| File | Purpose |
|------|---------|
| `apiClient.ts` | openapi-fetch client with auth middleware (auto-attaches Bearer token), typed path definitions |

### `pages/` -- One Per Route

| File | Route | Purpose |
|------|-------|---------|
| `LoginPage.tsx` | `/login` | Google sign-in page |
| `DashboardPage.tsx` | `/dashboard` | Presentation dashboard for a selected evaluation |
| `BrandsPage.tsx` | `/brands` | Brand listing with search, links to evaluation |
| `EvaluationPage.tsx` | `/evaluation/:brandId` | Main evaluation workspace (forms, uploads, scoring) |
| `HistoryPage.tsx` | `/history` | Evaluation history list with filters |
| `EvaluationDetailPage.tsx` | `/history/:id` | Read-only evaluation detail view |
| `RulesPage.tsx` | `/rules` | Scoring rules editor (leader/admin) |
| `AccountsPage.tsx` | `/accounts` | User account management (admin only) |

### `hooks/` -- React Query Hooks

| Hook | Exports | Purpose |
|------|---------|---------|
| `useAccounts.ts` | query + mutations | User account CRUD (list, create, update, delete) |
| `useAutoSaveForm.ts` | `buildManualData`, `mergeWithOverrides` | Debounced auto-save for evaluation forms |
| `useBrandDetail.ts` | query | Fetch single brand detail by ID |
| `useBrandEvaluations.ts` | query | Fetch evaluations for a specific brand |
| `useBrands.ts` | query | Fetch paginated brand list with search |
| `useCalculator.ts` | `useRunCalculator`, `useCalculatorResults`, `useCalculatorStatus`, `useAutoCalcErrors`, `useRunAllCalculators` | Calculator execution and result fetching |
| `useCurrentUser.ts` | query | Fetch current user profile (`GET /me`) |
| `useDeleteEvaluation.ts` | mutation | Delete an evaluation by ID |
| `useEvaluation.ts` | `useEvaluationState`, `useSaveEvaluationInputs` | Evaluation state query + input save mutation |
| `useEvaluationDetail.ts` | query | Fetch full evaluation detail (read-only) |
| `useEvaluationHistory.ts` | query | Fetch paginated evaluation history list |
| `useGroupedEvaluations.ts` | query | Fetch evaluations grouped by brand |
| `useRules.ts` | query | Fetch scoring rules by template |
| `useSaveEvaluation.ts` | mutation | Save/finalize evaluation with scores |
| `useScoring.ts` | `useScoring` | Score computation mutation + state management |
| `useSendEmail.ts` | mutation | Send evaluation report email via SMTP |
| `useSync.ts` | query + mutation | Sync status query + trigger sync mutation |
| `useUpdateRule.ts` | mutation | Update a scoring rule threshold/weight |
| `useUpload.ts` | `useBrandUploads`, `useRequestSignedUrl`, `useProcessUpload`, `useUploadFile` | File upload workflow (signed URL, upload, process) |

### `components/ui/` -- 15 Radix/shadcn Primitives

`badge`, `button`, `calendar`, `card`, `collapsible`, `dialog`, `input`, `label`, `popover`, `progress`, `radio-group`, `select`, `sonner` (toast), `table`, `tabs`

### `components/auth/`

| File | Purpose |
|------|---------|
| `ProtectedRoute.tsx` | Redirects unauthenticated users to `/login` |
| `RoleProtectedRoute.tsx` | Blocks users without required role (shows access denied) |

### `components/layout/`

| File | Purpose |
|------|---------|
| `MainLayout.tsx` | App shell with sidebar + content area (uses `<Outlet />`) |
| `Sidebar.tsx` | Navigation sidebar with route links and user info |
| `Header.tsx` | Top header bar |
| `ThemeToggle.tsx` | Light/dark theme toggle button |

### `components/dashboard/`

| File | Purpose |
|------|---------|
| `PresentationDashboard.tsx` | Main dashboard layout: score overview + breakdown + data intelligence |
| `ScoreOverview.tsx` | Final score display with verdict badge |
| `ScoreBreakdownChart.tsx` | Category score breakdown bar chart |
| `SendEmailDialog.tsx` | Dialog to compose and send evaluation report email |
| `EmailChipInput.tsx` | Email address chip/tag input component |
| `BrandSearch.tsx` | Brand search autocomplete for dashboard |
| `CategoryMetricCard.tsx` | Individual category metric display card |
| `DashboardFooter.tsx` | Dashboard footer with metadata |
| `DashboardHeader.tsx` | Dashboard header with brand info and actions |
| `DataIntelligence.tsx` | Calculator results display (ads, discount, top SKU) |
| `DetailedEvaluation.tsx` | Expanded evaluation detail view within dashboard |

### `components/evaluation/`

| File | Purpose |
|------|---------|
| `EvaluationHeader.tsx` | Evaluation page header (brand name, status, period) |
| `EvaluationSections.tsx` | Tab-based section container for forms + scoring + calculators |
| `SectionNav.tsx` | Section navigation tabs |
| `FileUploadSection.tsx` | File upload area with multiple slots |
| `FileUploadSlot.tsx` | Individual file upload slot (drag-drop, progress) |

### `components/evaluation/forms/` -- Input Forms

| File | Purpose |
|------|---------|
| `formConfig.ts` | Form field definitions, `EMPTY_MANUAL_DATA`, category mappings |
| `AdsForm.tsx` | Advertising metrics input form |
| `BusinessForm.tsx` | Business metrics input form |
| `CampaignForm.tsx` | Campaign metrics input form |
| `CompetitionForm.tsx` | Competition metrics input form |
| `OperationalForm.tsx` | Operational metrics input form |
| `ProductsStatusForm.tsx` | Products status input form |
| `PromoToolsForm.tsx` | Promotional tools input form |
| `VisitorsForm.tsx` | Visitor metrics input form |
| `CurrencyField.tsx` | Currency-formatted input field component |
| `NumberField.tsx` | Number-formatted input field component |
| `SelectField.tsx` | Select dropdown field component |
| `SaveIndicator.tsx` | Auto-save status indicator |
| `competitionUtils.ts` | Competition form helper utilities |

### `components/evaluation/scoring/`

| File | Purpose |
|------|---------|
| `ScoringSection.tsx` | Main scoring section container |
| `ScorePanel.tsx` | Score display panel |
| `ScoreBreakdown.tsx` | Per-category score breakdown table |
| `FinalScoreDisplay.tsx` | Final computed score with verdict |
| `VerdictSelector.tsx` | Manual verdict override selector |
| `PeriodSelector.tsx` | Evaluation period picker |
| `EmailOutput.tsx` | Email-formatted score output preview |
| `periodOptions.ts` | Period dropdown option definitions |
| `index.ts` | Barrel exports |

### `components/evaluation/calculators/`

| File | Purpose |
|------|---------|
| `CalculatorResultsSection.tsx` | Container for all calculator result displays |
| `AdsKeywordResults.tsx` | Ads/keyword calculator results display |
| `DiscountResults.tsx` | Discount calculator results display |
| `TopSkuResults.tsx` | Top SKU calculator results display |
| `index.ts` | Barrel exports |

### `components/evaluations/` -- History List Components

| File | Purpose |
|------|---------|
| `EvaluationHistoryTable.tsx` | Paginated evaluation history data table |
| `DeleteEvaluationDialog.tsx` | Confirmation dialog for evaluation deletion |
| `SendMailDialog.tsx` | Send email dialog from history view |
| `sendMailUtils.ts` | Email sending helper utilities |

### `components/brands/`

| File | Purpose |
|------|---------|
| `BrandTable.tsx` | Brand listing data table with search |

### `components/rules/`

| File | Purpose |
|------|---------|
| `RulesCategoryCard.tsx` | Editable scoring rule card per category |
| `PasswordConfirmDialog.tsx` | Password confirmation before rule changes |

### `components/sync/`

| File | Purpose |
|------|---------|
| `SyncStatus.tsx` | Google Sheets sync status display and trigger button |

### `components/` (root)

| File | Purpose |
|------|---------|
| `DowntimeWarningDialog.tsx` | Server error / downtime warning dialog |

### `lib/`

| File | Purpose |
|------|---------|
| `utils.ts` | `cn()` -- Tailwind class merge utility (clsx + tailwind-merge) |
| `categoryMap.ts` | Category ID to display name mappings |
| `verdictCounts.ts` | Verdict counting/aggregation utilities |

### `locales/`

| File | Purpose |
|------|---------|
| `id.json` | Indonesian translations (i18next) |

### `test/`

| File | Purpose |
|------|---------|
| `setup.ts` | Vitest global test setup |

---

## Infrastructure File Map (`infrastructure/terraform/`)

| File | Purpose |
|------|---------|
| `main.tf` | Terraform config: required providers (google, google-beta), project/region defaults |
| `variables.tf` | Input variables: project_id, region, env, Cloud SQL, Cloud Run settings |
| `outputs.tf` | Output values: cloud_run_url, service account emails |
| `cloud_run.tf` | Cloud Run v2 service for backend API |
| `cloud_sql.tf` | Cloud SQL PostgreSQL instance (single instance, dual databases: dev + prod) |
| `artifact_registry.tf` | Artifact Registry Docker repository for container images |
| `firebase.tf` | Firebase Hosting site resource (deployment via Firebase CLI, not Terraform) |
| `iam.tf` | Service accounts and IAM bindings |
| `secrets.tf` | Secret Manager secret resources (values injected via gcloud CLI) |
| `scheduler.tf` | Cloud Scheduler job: daily brand sync at 09:00 WIB via POST /api/v1/sync |
| `storage.tf` | GCS upload bucket for temporary file storage |
| `workload_identity.tf` | Workload Identity Federation: keyless GitHub Actions to GCP auth |
| `environments/dev.tfvars` | Dev environment variable values |
| `environments/prod.tfvars` | Prod environment variable values |

---

## Scripts

| File | Purpose |
|------|---------|
| `scripts/provision-users.py` | Provision Firebase + DB users from YAML config |
| `scripts/assign-roles.sql` | SQL to assign user roles directly |
| `scripts/users-config.example.yaml` | Example user provisioning config |

---

## Smoke Tests (`smoke-tests/`)

Playwright API tests (6 spec files):

| File | Tests |
|------|-------|
| `tests/auth-enforcement.spec.ts` | Auth token enforcement on protected endpoints |
| `tests/backend-health.spec.ts` | Health check endpoint |
| `tests/database-connectivity.spec.ts` | Database connection verification |
| `tests/frontend-spa.spec.ts` | Frontend SPA loading and routing |
| `tests/signed-url.spec.ts` | GCS signed URL generation |
| `tests/sse-endpoint.spec.ts` | Server-Sent Events endpoint |

---

## CI/CD (`.github/workflows/`)

| File | Purpose |
|------|---------|
| `ci.yml` | Lint, type-check, test (backend + frontend) |
| `deploy-backend.yml` | Build Docker image, push to Artifact Registry, deploy to Cloud Run |
| `deploy-frontend.yml` | Build frontend, deploy to Firebase Hosting |

---

## "Where to Find X" Quick Reference

| I want to... | Look at... |
|--------------|------------|
| Add a new API endpoint | Create module in `backend/app/modules/<name>/` (router, schemas, service), register in `main.py` |
| Add a new frontend page | Create `frontend/src/pages/<Name>Page.tsx`, add route in `App.tsx` |
| Add a new React Query hook | Create `frontend/src/hooks/use<Name>.ts`, import `apiClient` |
| Add a new UI component | Create in `frontend/src/components/ui/` (shadcn/Radix pattern) |
| Change auth logic | Backend: `core/dependencies.py`, `core/security.py`, `core/oidc.py`. Frontend: `context/AuthContext.tsx`, `firebase/auth.ts` |
| Modify scoring rules/weights | Backend: `calculators/scoring.py`, `modules/rules/`. Frontend: `components/rules/`, `hooks/useRules.ts` |
| Modify score computation | `backend/app/calculators/scoring.py` |
| Add a calculator | Create `backend/app/calculators/<name>.py`, register in `engine.py` |
| Add a DB table | Create migration in `backend/app/db/migrations/versions/`, add queries in `db/queries/` |
| Change upload processing | Backend: `modules/upload/parser.py`, `zip_handler.py`, `service.py`. Frontend: `hooks/useUpload.ts`, `components/evaluation/FileUploadSlot.tsx` |
| Modify email template | `backend/app/modules/email/template.py` |
| Change email sending logic | Backend: `modules/email/service.py`. Frontend: `hooks/useSendEmail.ts`, `components/dashboard/SendEmailDialog.tsx` |
| Add env var / config | `backend/app/config.py` (Settings class), set in `.env` or Cloud Run env |
| Change CORS origins | `backend/app/main.py` (allow_origins list) |
| Modify brand sync | Backend: `modules/sync/service.py`, `sheets_client.py`. Frontend: `components/sync/SyncStatus.tsx` |
| Add/change evaluation form fields | `frontend/src/components/evaluation/forms/formConfig.ts`, relevant `*Form.tsx` |
| Change category mappings | `frontend/src/lib/categoryMap.ts` |
| Add translations | `frontend/src/locales/id.json` |
| Modify Terraform infra | `infrastructure/terraform/` -- relevant `.tf` file |
| Add a CI check | `.github/workflows/ci.yml` |
| Add a smoke test | `smoke-tests/tests/<name>.spec.ts` |
| Change role permissions | Backend: `core/dependencies.py` (`require_role`). Frontend: `App.tsx` (`RoleProtectedRoute`) |

---

## Route Map

### Backend API Routes

| Method | Path | Module | Auth |
|--------|------|--------|------|
| GET | `/health` | main.py | none |
| GET | `/api/v1/me` | auth | user |
| GET | `/api/v1/brands` | brands | user |
| GET | `/api/v1/brands/{id}` | brands | user |
| GET/POST/PUT/DELETE | `/api/v1/evaluations/...` | evaluations | user |
| GET/PUT | `/api/v1/rules/...` | rules | leader/admin |
| GET/POST | `/api/v1/sync/...` | sync | user/scheduler |
| POST/GET | `/api/v1/upload/...` | upload | user |
| POST/GET | `/api/v1/email/...` | email | user |
| GET/POST/PUT/DELETE | `/api/v1/accounts/...` | accounts | admin |

### Frontend Routes

| Path | Page | Access |
|------|------|--------|
| `/login` | LoginPage | public |
| `/dashboard` | DashboardPage | authenticated |
| `/brands` | BrandsPage | authenticated |
| `/evaluation/:brandId` | EvaluationPage | authenticated |
| `/history` | HistoryPage | authenticated |
| `/history/:id` | EvaluationDetailPage | authenticated |
| `/rules` | RulesPage | leader, admin |
| `/accounts` | AccountsPage | admin |
| `/` | redirects to `/dashboard` | -- |

---

## Cross-References

- Architecture deep-dive: see `docs/agent/ARCHITECTURE.md` (if exists)
- Project instructions: `/CLAUDE.md`
- Terraform README: `infrastructure/terraform/README.md`
- Smoke test README: `smoke-tests/README.md`
