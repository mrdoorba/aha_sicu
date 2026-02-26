# Source Tree Analysis

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive

## Repository Structure

```
aha_sicu/
├── frontend/                    # React TypeScript SPA (Part: frontend)
│   ├── src/
│   │   ├── main.tsx             # ★ React entry point
│   │   ├── App.tsx              # ★ Root router & providers
│   │   ├── config.ts            # API_BASE_URL from env
│   │   ├── index.css            # Global Tailwind styles
│   │   ├── context/
│   │   │   └── AuthContext.tsx   # Firebase auth state provider
│   │   ├── firebase/
│   │   │   ├── config.ts        # Firebase app initialization
│   │   │   └── auth.ts          # Login, logout, reauthentication
│   │   ├── services/
│   │   │   └── apiClient.ts     # openapi-fetch client with auth middleware
│   │   ├── hooks/               # 13+ custom React hooks
│   │   │   ├── useCurrentUser.ts
│   │   │   ├── useBrands.ts
│   │   │   ├── useBrandDetail.ts
│   │   │   ├── useEvaluation.ts
│   │   │   ├── useEvaluationDetail.ts
│   │   │   ├── useEvaluationHistory.ts
│   │   │   ├── useAutoSaveForm.ts
│   │   │   ├── useSaveEvaluation.ts
│   │   │   ├── useCalculator.ts
│   │   │   ├── useScoring.ts
│   │   │   ├── useRules.ts
│   │   │   ├── useUpdateRule.ts
│   │   │   ├── useUpload.ts
│   │   │   ├── useSync.ts
│   │   │   └── useSSE.ts
│   │   ├── pages/               # 7 page components
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── BrandsPage.tsx
│   │   │   ├── EvaluationPage.tsx   # ★ Main evaluation workflow
│   │   │   ├── EvaluationDetailPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   └── RulesPage.tsx
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── Header.tsx   # Nav header with logout
│   │   │   ├── auth/
│   │   │   │   ├── ProtectedRoute.tsx
│   │   │   │   └── RoleProtectedRoute.tsx
│   │   │   ├── brands/
│   │   │   │   └── BrandTable.tsx
│   │   │   ├── evaluation/
│   │   │   │   ├── EvaluationHeader.tsx
│   │   │   │   ├── SectionNav.tsx
│   │   │   │   ├── EvaluationSections.tsx
│   │   │   │   ├── FileUploadSection.tsx
│   │   │   │   ├── FileUploadSlot.tsx
│   │   │   │   ├── SaveButton.tsx
│   │   │   │   ├── forms/       # 8 domain form components
│   │   │   │   │   ├── formConfig.ts    # Field definitions, ManualData type
│   │   │   │   │   ├── OperationalForm.tsx
│   │   │   │   │   ├── BusinessForm.tsx
│   │   │   │   │   ├── VisitorsForm.tsx
│   │   │   │   │   ├── PromoToolsForm.tsx
│   │   │   │   │   ├── ProductsStatusForm.tsx
│   │   │   │   │   ├── AdsForm.tsx
│   │   │   │   │   ├── CampaignForm.tsx
│   │   │   │   │   ├── CompetitionForm.tsx
│   │   │   │   │   ├── NumberField.tsx
│   │   │   │   │   ├── CurrencyField.tsx
│   │   │   │   │   ├── SelectField.tsx
│   │   │   │   │   └── SaveIndicator.tsx
│   │   │   │   ├── calculators/ # Calculator result displays
│   │   │   │   │   ├── CalculatorResultsSection.tsx
│   │   │   │   │   ├── AdsKeywordResults.tsx
│   │   │   │   │   ├── TopSkuResults.tsx
│   │   │   │   │   └── DiscountResults.tsx
│   │   │   │   └── scoring/     # Scoring UI components
│   │   │   │       ├── ScoringSection.tsx
│   │   │   │       ├── FinalScoreDisplay.tsx
│   │   │   │       ├── ScoreBreakdown.tsx
│   │   │   │       ├── ScorePanel.tsx
│   │   │   │       ├── VerdictSelector.tsx
│   │   │   │       ├── EmailOutput.tsx
│   │   │   │       └── WhatsAppLink.tsx
│   │   │   ├── evaluations/
│   │   │   │   └── EvaluationHistoryTable.tsx
│   │   │   ├── rules/
│   │   │   │   ├── RulesCategoryCard.tsx
│   │   │   │   └── PasswordConfirmDialog.tsx
│   │   │   ├── sync/
│   │   │   │   └── SyncStatus.tsx
│   │   │   └── ui/              # 15 Shadcn/Radix UI primitives
│   │   ├── lib/
│   │   │   └── utils.ts         # cn() className merger
│   │   └── test/
│   │       └── setup.ts         # Vitest setup
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── eslint.config.js
│   ├── components.json          # Shadcn component config
│   ├── index.html
│   ├── .env.example
│   └── .env.test
│
├── backend/                     # FastAPI Python API (Part: backend)
│   ├── app/
│   │   ├── main.py              # ★ FastAPI app entry point
│   │   ├── config.py            # Pydantic Settings (env vars)
│   │   ├── core/
│   │   │   ├── security.py      # Firebase token verification
│   │   │   ├── oidc.py          # OIDC token verification (Cloud Scheduler)
│   │   │   ├── dependencies.py  # Dependency injection (DB conn, auth)
│   │   │   ├── middleware.py    # Request logging middleware
│   │   │   └── exceptions.py   # Custom exception handlers
│   │   ├── db/
│   │   │   ├── connection.py    # asyncpg connection pool
│   │   │   ├── queries/
│   │   │   │   ├── users.py
│   │   │   │   ├── brands.py
│   │   │   │   ├── evaluations.py
│   │   │   │   ├── rules.py
│   │   │   │   ├── sync_status.py
│   │   │   │   ├── uploads.py
│   │   │   │   ├── calculator_results.py
│   │   │   │   └── utils.py     # SQL escape helpers
│   │   │   └── migrations/      # 13 Alembic migrations
│   │   │       ├── 001_create_users_table.py
│   │   │       ├── ...
│   │   │       └── 013_unify_scoring_rules_template.py
│   │   ├── modules/
│   │   │   ├── auth/            # GET /api/v1/me
│   │   │   │   ├── router.py
│   │   │   │   └── schemas.py
│   │   │   ├── brands/          # GET /api/v1/brands[/:id]
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   └── schemas.py
│   │   │   ├── evaluations/     # ★ Core evaluation module
│   │   │   │   ├── router.py    # 12+ endpoints
│   │   │   │   ├── service.py   # Scoring orchestration
│   │   │   │   ├── calculator_service.py
│   │   │   │   └── schemas.py
│   │   │   ├── rules/           # GET/PUT /api/v1/rules
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   └── schemas.py
│   │   │   ├── sync/            # Google Sheets sync
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   ├── sheets_client.py
│   │   │   │   └── schemas.py
│   │   │   ├── upload/          # File upload & processing
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   ├── gcs_client.py
│   │   │   │   ├── parser.py
│   │   │   │   ├── zip_handler.py
│   │   │   │   └── schemas.py
│   │   │   └── events/          # SSE endpoint
│   │   │       └── router.py
│   │   ├── calculators/         # ★ Pure function calculators
│   │   │   ├── engine.py        # Orchestration & dependency resolution
│   │   │   ├── scoring.py       # 75-row scoring system
│   │   │   ├── ads_keyword.py   # CPC Ad + Keyword analysis
│   │   │   ├── top_sku.py       # Top SKU ranking
│   │   │   └── discount.py      # Discount check & fake detection
│   │   └── services/
│   │       └── event_broadcaster.py  # SSE fan-out to subscribers
│   ├── tests/
│   │   ├── conftest.py          # Fixtures (DB, auth mocks)
│   │   ├── integration/
│   │   │   └── api/             # 16 integration test files
│   │   └── unit/                # 13+ unit test files
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── uv.lock
│   └── .env.example
│
├── infrastructure/              # Terraform GCP IaC (Part: infrastructure)
│   └── terraform/
│       ├── main.tf              # ★ Provider config & API enablement
│       ├── cloud_run.tf         # Cloud Run service definition
│       ├── iam.tf               # Service accounts & permissions
│       ├── artifact_registry.tf # Docker image registry
│       ├── firebase.tf          # Firebase hosting sites
│       ├── secrets.tf           # Secret Manager secrets
│       ├── storage.tf           # Cloud Storage buckets
│       ├── scheduler.tf         # Cloud Scheduler jobs
│       ├── variables.tf         # Input variables
│       ├── outputs.tf           # Output values
│       ├── setup.sh             # Bootstrap script
│       ├── README.md
│       └── environments/
│           ├── dev.tfvars       # Dev environment config
│           └── prod.tfvars      # Prod environment config
│
├── smoke-tests/                 # Playwright smoke tests
│   ├── tests/                   # API-only smoke tests
│   ├── playwright.config.ts
│   ├── package.json
│   ├── README.md
│   └── MANUAL_CHECKLIST.md
│
├── scripts/                     # Utility scripts
│   ├── provision-users.py       # Firebase Auth user provisioning
│   ├── assign-roles.sql         # Database role assignment
│   └── users-config.example.yaml
│
├── docs/                        # Project documentation
│   ├── index.md                 # ★ Master index (this workflow)
│   ├── calculator-logic-reference.md  # Scoring algorithm docs (37KB)
│   ├── deployment-guide.md
│   ├── onboarding-guide.md      # BD team walkthrough (27KB)
│   ├── launch-readiness.md
│   └── validation-report-template.md
│
├── .github/workflows/           # CI/CD pipelines
│   ├── ci.yml                   # PR validation (tests + lint)
│   ├── deploy-backend.yml       # Backend → Cloud Run
│   └── deploy-frontend.yml      # Frontend → Firebase Hosting
│
├── firebase.json                # Firebase Hosting config (2 targets)
├── .firebaserc                  # Firebase project aliases
├── README.md                    # Project overview
└── CLAUDE.md                    # Claude AI project rules
```

## Critical Entry Points

| Entry Point | Path | Purpose |
|-------------|------|---------|
| Frontend App | `frontend/src/main.tsx` | React DOM render |
| Frontend Router | `frontend/src/App.tsx` | Route definitions & providers |
| Backend App | `backend/app/main.py` | FastAPI app with all routers |
| Backend Config | `backend/app/config.py` | Environment variable loading |
| Terraform | `infrastructure/terraform/main.tf` | Cloud resource definitions |

## Critical Directories

| Directory | Purpose | Importance |
|-----------|---------|-----------|
| `frontend/src/hooks/` | All data fetching and state logic | Core business logic (frontend) |
| `frontend/src/components/evaluation/` | Evaluation workflow UI | Primary user workflow |
| `backend/app/calculators/` | Pure function scoring engine | Core business logic (backend) |
| `backend/app/modules/evaluations/` | Evaluation API endpoints | Central API surface |
| `backend/app/db/queries/` | All SQL query functions | Data access layer |
| `backend/app/db/migrations/` | Schema version history | Database evolution |
| `infrastructure/terraform/` | All cloud resources | Deployment configuration |
