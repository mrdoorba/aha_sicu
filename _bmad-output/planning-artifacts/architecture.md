---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2026-02-04'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/product-brief-BMAD-Method-2026-02-04.md'
  - '_bmad-output/brainstorming/brainstorming-session-2026-02-04.md'
workflowType: 'architecture'
project_name: 'Store ICU'
user_name: 'Mr. Door'
date: '2026-02-04'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
37 functional requirements across 8 domains:

| Domain | FRs | Architectural Implication |
|--------|-----|---------------------------|
| Brand Data Management | FR1-FR5 | Google Sheets API integration, sync scheduling |
| Data Input & Upload | FR6-FR11 | File upload handling, Polars parsing, upsert logic |
| Calculators | FR12-FR18 | Modular calculation engine, formula replication |
| Final Scoring | FR19-FR22 | Template-based scoring, rule application |
| Rule Configuration | FR23-FR26 | Database-driven configuration, admin interface |
| Evaluation Storage | FR27-FR33 | Persistent storage, search, audit trail |
| Real-Time Updates | FR34-FR35 | WebSocket or polling for live updates |
| Authentication | FR36-FR37 | Firebase Auth integration |

**Non-Functional Requirements:**
17 NFRs defining quality attributes:

| Category | Key Requirements |
|----------|------------------|
| Performance | Page load <3s, Excel processing <5s, calculations <2s, search <1s |
| Security | Firebase Auth, JWT validation, HTTPS, secured credentials |
| Integration | Google Sheets API rate limiting, Excel format support |
| Reliability | Transaction integrity, immutable history, graceful recovery |

**Scale & Complexity:**

- Primary domain: Full-stack web application
- Complexity level: Low-Medium
- User base: 5 internal users (BD team)
- Estimated architectural components: 8-10

### Technical Constraints & Dependencies

**Pre-decided Stack (from brainstorming):**
| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | SPA on Firebase Hosting | GCP ecosystem, modern UI |
| Backend | FastAPI on Cloud Run | Python-first for Polars |
| Database | Neon (PostgreSQL) | Project constraint |
| Auth | Firebase Auth | Token-based, decoupled |
| Processing | Polars | Excel parsing + calculations |

**External Dependencies:**
- Google Sheets API (Brand Database sync)
- Firebase Auth SDK
- Neon connection pooling

### Cross-Cutting Concerns Identified

| Concern | Scope | Implementation Approach |
|---------|-------|------------------------|
| Authentication | All API endpoints | Firebase Auth JWT validation middleware |
| Audit Trail | Evaluations, rule changes | Timestamp + user tracking on all records |
| Error Handling | All layers | Structured logging, user-friendly messages |
| Rule Versioning | Scoring calculations | Store rule version with each evaluation |
| Sync Health | Brand data | Last-synced timestamp, failure alerts |

## Starter Template Evaluation

### Primary Technology Domain

Full-stack web application with decoupled frontend (SPA) and backend (API) architecture.

### Starter Options Considered

| Option | Evaluation |
|--------|------------|
| Full Stack FastAPI Template | Too opinionated (JWT, SQLModel, Traefik) - conflicts with Firebase Auth, Polars, Cloud Run |
| Cookiecutter templates | Include ORM/DB abstractions incompatible with Polars-first approach |
| Vite + React starters | Good foundation, need Firebase Auth integration |

### Selected Approach: Lean Modular Structure

**Rationale:** Pre-decided stack (Firebase Auth, Polars, Cloud Run, Neon) conflicts with assumptions in existing templates. A modular custom structure ensures clean architecture aligned with project constraints and supports future growth.

### Project Structure

**Backend (Modular Domain-Driven):**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Pydantic settings
│   │
│   ├── core/                      # Core infrastructure (shared)
│   │   ├── __init__.py
│   │   ├── dependencies.py        # DI: auth, db connections
│   │   ├── exceptions.py          # Custom exceptions
│   │   ├── middleware.py          # Logging, error handling
│   │   └── security.py            # Firebase Auth validation
│   │
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py          # Neon connection pool
│   │   ├── queries/               # Raw SQL or query builders
│   │   │   ├── brands.py
│   │   │   ├── evaluations.py
│   │   │   └── rules.py
│   │   └── migrations/            # Schema migrations
│   │
│   ├── modules/                   # Feature modules (domain-driven)
│   │   ├── __init__.py
│   │   ├── brands/                # Brand management module
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── sync/                  # Google Sheets sync module
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── evaluations/           # Evaluation storage module
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── upload/                # File upload module
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   └── rules/                 # Rule configuration module
│   │       ├── __init__.py
│   │       ├── router.py
│   │       ├── schemas.py
│   │       └── service.py
│   │
│   └── calculators/               # Calculation engine (isolated)
│       ├── __init__.py
│       ├── base.py                # Abstract calculator interface
│       ├── ads_keyword.py
│       ├── discount.py
│       ├── top_sku.py
│       ├── scoring.py             # Final scoring (Fashion/Non-Fashion)
│       └── engine.py              # Calculator orchestration
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   └── calculators/
│   └── integration/
│       └── api/
│
├── Dockerfile
├── pyproject.toml
└── .env.example
```

**Frontend (Feature-Organized):**
```
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── services/                  # API client
│   └── firebase/                  # Firebase Auth config
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

**Infrastructure (Terraform):**
```
infrastructure/
├── terraform/
│   ├── main.tf              # Provider config, prefix, region
│   ├── variables.tf         # Input variables
│   ├── outputs.tf           # Output values
│   ├── cloud_run.tf         # Backend deployment
│   ├── secrets.tf           # Secret Manager
│   ├── scheduler.tf         # Daily sync job
│   ├── firebase.tf          # Firebase project, hosting site, auth
│   └── environments/
│       ├── dev.tfvars
│       └── prod.tfvars
│
├── firebase/
│   ├── firebase.json        # Hosting config
│   └── .firebaserc          # Project aliases
```

### Architectural Decisions Established

**Language & Runtime:**
- Backend: Python 3.14 with type hints (latest)
- Frontend: TypeScript (strict mode)

**Modularity Principles:**
- Each feature module is self-contained (router, schemas, service)
- No cross-module imports except through core
- Calculators are pure functions with no I/O dependencies
- Clear dependency injection through FastAPI's Depends()

**Styling Solution:**
- Tailwind CSS (utility-first, rapid development)

**Build Tooling:**
- Frontend: Vite (fast HMR, optimized builds)
- Backend: Docker for Cloud Run deployment

**Testing Framework:**
- Backend: pytest (unit tests for calculators, integration for API)
- Frontend: Vitest (Vite-native)

**Development Experience:**
- Hot reload on both frontend and backend
- Type checking throughout
- ESLint + Prettier (frontend), Ruff (backend - fast Python 3.14 compatible)

**Note:** Project initialization is the first implementation story.

## Core Architectural Decisions

### Decision Summary

| Category | Decision | Choice |
|----------|----------|--------|
| Database Query | Approach | asyncpg + parameterized SQL |
| Database Migration | Tool | Alembic (raw SQL mode) |
| Database Caching | Strategy | None - query database directly |
| Authorization | Rule modification | Role-based + password re-confirm |
| API Response | Format | Raw responses (no wrapper) |
| API Pagination | Style | Offset-based (?page=1&limit=20) |
| API Filtering | Style | Query params |
| Error Handling | Format | Structured codes (AUTH_, SYNC_, etc.) |
| Real-Time | Approach | SSE (Server-Sent Events) |
| State Management | Library | TanStack Query + React Context |
| Form Handling | Library | React Hook Form |
| API Client | Approach | openapi-fetch (typed from OpenAPI spec) |
| CI/CD | Platform | GitHub Actions |
| Environments | Setup | Dev + Prod (no staging) |
| Monitoring | Stack | Cloud Logging + uptime alert |
| Backups | Strategy | Neon built-in (7-day PITR) |
| IaC | Tool | Terraform |
| Resource Prefix | Naming | `aha_sicu_` |
| Region | GCP | `asia-southeast1` (Singapore) |

### Data Architecture

**Query Approach:** asyncpg + parameterized SQL
- Direct async PostgreSQL access
- `$1, $2` parameter placeholders prevent SQL injection
- No ORM overhead, Polars handles data processing

**Migrations:** Alembic (raw SQL mode)
- Version-controlled schema changes
- Rollback support
- No ORM dependency

**Authorization for Rules:**
- Only `leader`/`admin` roles can modify scoring rules
- Password re-confirmation required before saving changes

### API & Communication

**REST Conventions:**
- Raw responses (no wrapper)
- Offset pagination: `?page=1&limit=20`
- Query param filtering: `?category=fashion&date_from=2026-01-01`

**Error Handling:**
```json
{
    "code": "UPLOAD_INVALID_FORMAT",
    "detail": "Expected .xlsx or .xls file",
    "field": "file",
    "timestamp": "2026-02-04T10:30:00Z"
}
```

**Error Code Prefixes:**
| Prefix | Category |
|--------|----------|
| `AUTH_` | Authentication |
| `SYNC_` | Google Sheets sync |
| `UPLOAD_` | File upload |
| `CALC_` | Calculators |
| `RULE_` | Rule configuration |

**Real-Time Updates:** Server-Sent Events (SSE)
- Endpoint: `/api/v1/events`
- Events: `sync_status`, `new_evaluation`
- One-way server → client push

### Frontend Architecture

**State Management:** TanStack Query + React Context
- TanStack Query: server state (brands, evaluations, rules)
- React Context: auth state only

**Form Handling:** React Hook Form
- Lightweight, performant
- Built-in validation
- TypeScript-native

**API Client:** openapi-fetch
- Auto-generated from FastAPI OpenAPI spec
- Full type safety frontend ↔ backend

### Infrastructure & Deployment

**IaC:** Terraform
- Manages: Cloud Run, Secret Manager, Scheduler, IAM, Firebase setup
- Firebase Hosting deploys via Firebase CLI (not Terraform)
- Runs only when infrastructure changes detected

**Naming Convention:**
- Resource prefix: `aha_sicu_`
- Examples: `aha_sicu_api`, `aha_sicu_registry`, `aha_sicu_db_url`
- Firebase uses hyphens: `aha-sicu`

**Region:** `asia-southeast1` (Singapore)
- Low latency for Indonesia-based BD team

**CI/CD:** GitHub Actions
- Test: pytest (backend) + Vitest (frontend)
- Infrastructure: Terraform apply (only if .tf files changed)
- Build: Docker image → Artifact Registry
- Deploy: Cloud Run (backend) + Firebase Hosting (frontend)

**Environments:**
- Development: local `.env`
- Production: GCP Secret Manager
- No staging (direct dev → prod for MVP)

**Monitoring:**
- Logging: Cloud Logging (built-in)
- Uptime: Cloud Monitoring alert
- Error tracking: Manual log review (add Sentry later if needed)

**Backups:**
- Neon free tier: 7-day point-in-time recovery
- Upgrade to paid tier for 30-day retention when needed

## Implementation Patterns & Consistency Rules

### Why These Patterns Matter

These patterns ensure that when multiple AI agents implement different parts of Store ICU, the code is consistent and compatible. Without explicit patterns, one agent might use `camelCase` while another uses `snake_case` - causing integration failures.

### Naming Patterns

#### Database Naming

| Element | Pattern | Example |
|---------|---------|---------|
| Tables | `snake_case` plural | `brands`, `evaluations`, `scoring_rules` |
| Columns | `snake_case` | `brand_id`, `created_at`, `is_active` |
| Foreign keys | `{table}_id` | `brand_id`, `user_id` |
| Indexes | `idx_{table}_{column}` | `idx_brands_name`, `idx_evaluations_created_at` |
| Primary keys | `id` | Always `id`, never `brand_id` for PK |

#### API Naming

| Element | Pattern | Example |
|---------|---------|---------|
| Endpoints | Plural nouns | `/api/v1/brands`, `/api/v1/evaluations` |
| JSON fields | `snake_case` | `{ "brand_id": 1, "created_at": "..." }` |
| Query params | `snake_case` | `?date_from=2026-01-01&category=fashion` |
| URL slugs | `kebab-case` | `/api/v1/sync-status` |

#### Backend Code (Python)

| Element | Pattern | Example |
|---------|---------|---------|
| Files | `snake_case.py` | `brand_service.py`, `ads_keyword.py` |
| Functions | `snake_case` | `get_brand_by_id()`, `calculate_score()` |
| Variables | `snake_case` | `brand_name`, `total_score` |
| Classes | `PascalCase` | `BrandService`, `EvaluationSchema` |
| Constants | `UPPER_SNAKE` | `MAX_UPLOAD_SIZE`, `DEFAULT_PAGE_SIZE` |

#### Frontend Code (TypeScript)

| Element | Pattern | Example |
|---------|---------|---------|
| Component files | `PascalCase.tsx` | `BrandCard.tsx`, `EvaluationForm.tsx` |
| Utility files | `camelCase.ts` | `apiClient.ts`, `useAuth.ts` |
| Functions | `camelCase` | `getBrands()`, `handleSubmit()` |
| Variables | `camelCase` | `brandName`, `isLoading` |
| Components | `PascalCase` | `<BrandCard />`, `<SyncStatus />` |
| Hooks | `useCamelCase` | `useBrands()`, `useEvaluation()` |
| Types/Interfaces | `PascalCase` | `Brand`, `EvaluationInput` |

### Format Patterns

#### Date/Time Handling

| Context | Pattern | Example |
|---------|---------|---------|
| API responses | ISO 8601 with timezone | `2026-02-04T10:30:00Z` |
| Database storage | `TIMESTAMPTZ` | Always store with timezone |
| Frontend display | Localized | `4 Feb 2026, 17:30 WIB` |

#### API Response Format

**Success Response:**
```json
{
  "id": 1,
  "brand_name": "Example Brand",
  "created_at": "2026-02-04T10:30:00Z"
}
```

**Error Response:**
```json
{
  "code": "UPLOAD_INVALID_FORMAT",
  "detail": "Expected .xlsx or .xls file",
  "field": "file",
  "timestamp": "2026-02-04T10:30:00Z"
}
```

**Paginated Response:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "limit": 20,
  "pages": 5
}
```

### Structure Patterns

#### Test Organization

| Layer | Pattern | Location |
|-------|---------|----------|
| Backend | Separate folder | `tests/unit/calculators/`, `tests/integration/api/` |
| Frontend | Co-located | `BrandCard.tsx` + `BrandCard.test.tsx` |

#### Module Structure (Backend)

Every feature module follows this structure:
```
modules/{feature}/
├── __init__.py
├── router.py      # FastAPI routes
├── schemas.py     # Pydantic models (request/response)
└── service.py     # Business logic
```

#### Component Structure (Frontend)

```
src/components/{Feature}/
├── FeatureName.tsx        # Main component
├── FeatureName.test.tsx   # Tests
├── FeatureName.types.ts   # Types (if complex)
└── index.ts               # Re-export
```

### Process Patterns

#### Error Handling

**Backend:**
- Raise custom exceptions from `core/exceptions.py`
- Let middleware convert to structured error responses
- Log errors with context before raising

**Frontend:**
- TanStack Query handles API errors automatically
- Display user-friendly messages from `detail` field
- Log `code` for debugging

#### Loading States

**Frontend naming convention:**
- `isLoading` - initial load
- `isFetching` - background refetch
- `isSubmitting` - form submission
- `isSyncing` - sync operation

#### Authentication Flow

1. Frontend: Firebase Auth SDK handles login
2. Frontend: Get ID token from Firebase
3. Frontend: Send token in `Authorization: Bearer {token}` header
4. Backend: Validate token via Firebase Admin SDK
5. Backend: Extract user info, check role in database

### Enforcement Guidelines

**All AI Agents MUST:**

1. Follow naming conventions exactly - no exceptions
2. Use the module/component structure defined above
3. Return ISO 8601 dates from all API endpoints
4. Use structured error codes from the defined prefixes
5. Place tests in the correct location per layer

**Code Review Checklist:**
- [ ] Naming follows conventions (snake_case Python, camelCase TS)
- [ ] API responses use snake_case JSON
- [ ] Dates are ISO 8601 with timezone
- [ ] Errors use structured format with code prefix
- [ ] New modules follow the defined structure

### Pattern Examples

**Good:**
```python
# Backend
async def get_brand_by_id(brand_id: int) -> Brand:
    ...

class EvaluationSchema(BaseModel):
    brand_id: int
    created_at: datetime
```

```typescript
// Frontend
const BrandCard: FC<BrandCardProps> = ({ brandId }) => {
  const { data: brand, isLoading } = useBrand(brandId);
  ...
};
```

**Bad (Anti-patterns):**
```python
# Wrong: camelCase in Python
async def getBrandById(brandId: int):  # ❌
    ...

# Wrong: camelCase in API response
return {"brandId": 1, "createdAt": "..."}  # ❌
```

```typescript
// Wrong: snake_case in TypeScript
const brand_card = () => { ... }  // ❌
const is_loading = true;  // ❌
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```
store-icu/
├── README.md
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Test on PR
│       ├── deploy-backend.yml        # Cloud Run deploy
│       └── deploy-frontend.yml       # Firebase Hosting deploy
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app, CORS, routers
│   │   ├── config.py                 # Pydantic BaseSettings
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py       # get_db, get_current_user
│   │   │   ├── exceptions.py         # AppException, error codes
│   │   │   ├── middleware.py         # Error handler, logging
│   │   │   └── security.py           # verify_firebase_token()
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py         # asyncpg pool to Neon
│   │   │   ├── queries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── brands.py         # Brand CRUD queries
│   │   │   │   ├── evaluations.py    # Evaluation queries
│   │   │   │   ├── rules.py          # Rule config queries
│   │   │   │   └── users.py          # User/role queries
│   │   │   └── migrations/
│   │   │       ├── env.py            # Alembic config
│   │   │       ├── versions/
│   │   │       │   ├── 001_initial_schema.py
│   │   │       │   ├── 002_add_users_table.py
│   │   │       │   └── 003_add_rules_table.py
│   │   │       └── alembic.ini
│   │   │
│   │   ├── modules/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── brands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py         # GET /brands, GET /brands/{id}
│   │   │   │   ├── schemas.py        # BrandResponse, BrandList
│   │   │   │   └── service.py        # get_brands(), get_brand_by_id()
│   │   │   │
│   │   │   ├── sync/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py         # POST /sync, GET /sync-status
│   │   │   │   ├── schemas.py        # SyncStatus, SyncRequest
│   │   │   │   └── service.py        # sync_from_sheets(), get_status()
│   │   │   │
│   │   │   ├── evaluations/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py         # CRUD /evaluations
│   │   │   │   ├── schemas.py        # EvaluationInput, EvaluationResponse
│   │   │   │   └── service.py        # create_evaluation(), search()
│   │   │   │
│   │   │   ├── upload/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py         # POST /upload
│   │   │   │   ├── schemas.py        # UploadResponse, FileValidation
│   │   │   │   └── service.py        # process_excel_file()
│   │   │   │
│   │   │   ├── rules/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py         # GET/PUT /rules (admin only)
│   │   │   │   ├── schemas.py        # RuleConfig, RuleUpdate
│   │   │   │   └── service.py        # get_rules(), update_rules()
│   │   │   │
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py         # POST /auth/verify-password
│   │   │   │   ├── schemas.py        # PasswordVerify, UserInfo
│   │   │   │   └── service.py        # verify_password(), get_user_role()
│   │   │   │
│   │   │   └── events/
│   │   │       ├── __init__.py
│   │   │       ├── router.py         # GET /events (SSE endpoint)
│   │   │       └── service.py        # event_generator()
│   │   │
│   │   └── calculators/
│   │       ├── __init__.py
│   │       ├── base.py               # BaseCalculator abstract class
│   │       ├── ads_keyword.py        # AdsKeywordCalculator
│   │       ├── discount.py           # DiscountCalculator
│   │       ├── top_sku.py            # TopSkuCalculator
│   │       ├── scoring.py            # ScoringCalculator (Fashion/Non-Fashion)
│   │       └── engine.py             # run_all_calculators()
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py               # Fixtures: test_db, test_client
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   └── calculators/
│   │   │       ├── __init__.py
│   │   │       ├── test_ads_keyword.py
│   │   │       ├── test_discount.py
│   │   │       ├── test_top_sku.py
│   │   │       └── test_scoring.py
│   │   └── integration/
│   │       ├── __init__.py
│   │       └── api/
│   │           ├── __init__.py
│   │           ├── test_brands.py
│   │           ├── test_evaluations.py
│   │           └── test_sync.py
│   │
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── .env.example
│   └── .python-version               # 3.14
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                  # App entry point
│   │   ├── App.tsx                   # Root component, routing
│   │   ├── index.css                 # Tailwind imports
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                   # Reusable UI components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Select.tsx
│   │   │   │   ├── Table.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx        # Nav, sync status, user menu
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── PageLayout.tsx
│   │   │   │
│   │   │   ├── brands/
│   │   │   │   ├── BrandList.tsx
│   │   │   │   ├── BrandList.test.tsx
│   │   │   │   ├── BrandCard.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── evaluations/
│   │   │   │   ├── EvaluationForm.tsx
│   │   │   │   ├── EvaluationForm.test.tsx
│   │   │   │   ├── EvaluationHistory.tsx
│   │   │   │   ├── EvaluationDetail.tsx
│   │   │   │   ├── CalculatorResults.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── upload/
│   │   │   │   ├── FileUpload.tsx
│   │   │   │   ├── FileUpload.test.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── sync/
│   │   │   │   ├── SyncStatus.tsx
│   │   │   │   ├── SyncButton.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   └── rules/
│   │   │       ├── RulesEditor.tsx   # Admin only
│   │   │       ├── RulesEditor.test.tsx
│   │   │       └── index.ts
│   │   │
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── BrandsPage.tsx
│   │   │   ├── EvaluationPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   └── RulesPage.tsx         # Admin only
│   │   │
│   │   ├── hooks/
│   │   │   ├── useBrands.ts
│   │   │   ├── useEvaluations.ts
│   │   │   ├── useUpload.ts
│   │   │   ├── useSync.ts
│   │   │   ├── useRules.ts
│   │   │   ├── useSSE.ts             # Server-sent events hook
│   │   │   └── useAuth.ts
│   │   │
│   │   ├── services/
│   │   │   ├── apiClient.ts          # openapi-fetch setup
│   │   │   └── api-schema.d.ts       # Generated from OpenAPI
│   │   │
│   │   ├── firebase/
│   │   │   ├── config.ts             # Firebase app init
│   │   │   └── auth.ts               # signIn, signOut, onAuthStateChanged
│   │   │
│   │   ├── context/
│   │   │   └── AuthContext.tsx       # User state, role
│   │   │
│   │   └── types/
│   │       └── index.ts              # Shared TypeScript types
│   │
│   ├── public/
│   │   └── favicon.ico
│   │
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── .env.example
│   └── .eslintrc.cjs
│
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf                   # Provider, project, region
│   │   ├── variables.tf              # aha_sicu_ prefix, asia-southeast1
│   │   ├── outputs.tf                # Cloud Run URL, etc.
│   │   ├── cloud_run.tf              # aha_sicu_api service
│   │   ├── artifact_registry.tf      # aha_sicu_registry
│   │   ├── secrets.tf                # aha_sicu_db_url, etc.
│   │   ├── scheduler.tf              # aha_sicu_daily_sync
│   │   ├── firebase.tf               # Project, hosting site
│   │   ├── iam.tf                    # Service accounts, permissions
│   │   └── environments/
│   │       ├── dev.tfvars
│   │       └── prod.tfvars
│   │
│   └── firebase/
│       ├── firebase.json             # Hosting config (dist folder)
│       └── .firebaserc               # Project aliases
│
└── docs/
    ├── api.md                        # API documentation
    └── calculator-formulas.md        # Formula documentation
```

### Architectural Boundaries

**API Boundaries:**

| Boundary | Endpoints | Auth Required |
|----------|-----------|---------------|
| Public | None | - |
| Authenticated | All `/api/v1/*` | Bearer token |
| Admin Only | `/api/v1/rules` (PUT) | Bearer + leader/admin role |
| Password Confirm | `/api/v1/rules` (PUT) | Bearer + password re-verify |

**Module Boundaries:**

```
┌─────────────────────────────────────────────────────────────┐
│  FastAPI App (main.py)                                      │
│  └── Mounts all module routers under /api/v1/               │
├─────────────────────────────────────────────────────────────┤
│  modules/brands     ← DB queries only, no calculator logic  │
│  modules/sync       ← Google Sheets API only                │
│  modules/upload     ← Polars processing only                │
│  modules/evaluations ← Orchestrates calculators + storage   │
│  modules/rules      ← Rule config CRUD only                 │
│  modules/auth       ← Firebase token verification only      │
│  modules/events     ← SSE broadcasting only                 │
├─────────────────────────────────────────────────────────────┤
│  calculators/       ← PURE FUNCTIONS, no I/O                │
│  └── Called by modules/evaluations, never directly by API   │
├─────────────────────────────────────────────────────────────┤
│  core/              ← Shared infrastructure                 │
│  └── Used by all modules via Depends()                      │
├─────────────────────────────────────────────────────────────┤
│  db/                ← Database access layer                 │
│  └── Used by modules, never by calculators                  │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow:**

```
User Action → Frontend Component → TanStack Query → API Client
    ↓
FastAPI Router → Service → DB Queries / Calculators
    ↓
Response → TanStack Query Cache → UI Update
    ↓
SSE Event (if applicable) → useSSE hook → Other users' UI
```

### Requirements to Structure Mapping

**FR1-FR5 (Brand Data Management):**
- `modules/sync/` - Google Sheets sync
- `modules/brands/` - Brand listing and selection
- `db/queries/brands.py` - Brand data queries
- `components/brands/` - Brand UI components
- `hooks/useBrands.ts`, `hooks/useSync.ts`

**FR6-FR11 (Data Input & Upload):**
- `modules/upload/` - Excel file processing
- `components/upload/` - File upload UI
- `hooks/useUpload.ts`

**FR12-FR22 (Calculators & Scoring):**
- `calculators/` - All calculation logic (pure functions)
- `modules/evaluations/` - Orchestration and storage
- `components/evaluations/` - Evaluation UI
- `hooks/useEvaluations.ts`

**FR23-FR26 (Rule Configuration):**
- `modules/rules/` - Rule CRUD (admin only)
- `db/queries/rules.py` - Rule queries
- `components/rules/` - Rules editor UI
- `hooks/useRules.ts`
- `pages/RulesPage.tsx` - Admin page

**FR27-FR33 (Evaluation Storage & History):**
- `modules/evaluations/` - Storage and search
- `db/queries/evaluations.py` - Evaluation queries
- `components/evaluations/EvaluationHistory.tsx`
- `pages/HistoryPage.tsx`

**FR34-FR35 (Real-Time Updates):**
- `modules/events/` - SSE endpoint
- `hooks/useSSE.ts` - Client-side event listener
- `components/sync/SyncStatus.tsx` - Live sync status

**FR36-FR37 (Authentication):**
- `modules/auth/` - Token verification, password re-confirm
- `core/security.py` - Firebase token validation
- `firebase/` - Client-side Firebase Auth
- `context/AuthContext.tsx` - Auth state
- `hooks/useAuth.ts`

### Cross-Cutting Concerns Mapping

| Concern | Backend Location | Frontend Location |
|---------|------------------|-------------------|
| Authentication | `core/security.py`, `modules/auth/` | `firebase/`, `context/AuthContext.tsx` |
| Error Handling | `core/exceptions.py`, `core/middleware.py` | TanStack Query error handling |
| Logging | `core/middleware.py` | Browser console (dev only) |
| Authorization | `modules/auth/service.py` | `hooks/useAuth.ts` (role checks) |

### Integration Points

**External Services:**

| Service | Integration Point | Purpose |
|---------|-------------------|---------|
| Google Sheets API | `modules/sync/service.py` | Brand Database sync |
| Firebase Auth | `core/security.py`, `firebase/` | User authentication |
| Neon PostgreSQL | `db/connection.py` | Data persistence |

**Internal Communication:**

| From | To | Method |
|------|-----|--------|
| Frontend | Backend | REST API via openapi-fetch |
| Backend | Frontend | SSE for real-time updates |
| Modules | Calculators | Direct function calls |
| Modules | Database | Via `db/queries/` |

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:** All technology choices are compatible and work together without conflicts. The Python 3.14 + FastAPI + Polars backend integrates cleanly with the React + Vite + TypeScript frontend through REST APIs and SSE.

**Pattern Consistency:** Implementation patterns (naming conventions, structure, error handling) align with the technology stack. Python uses snake_case, TypeScript uses camelCase, and API uses snake_case JSON - matching ecosystem conventions.

**Structure Alignment:** Project structure supports all architectural decisions. Module boundaries are clear, calculators are isolated as pure functions, and integration points are well-defined.

### Requirements Coverage Validation ✅

**Functional Requirements:** All 37 FRs have explicit architectural support mapped to specific modules, components, and integration points.

| FR Category | Architectural Support | Status |
|-------------|----------------------|--------|
| FR1-FR5 (Brand Data) | `modules/sync/`, `modules/brands/` | ✅ |
| FR6-FR11 (Data Input) | `modules/upload/`, Polars | ✅ |
| FR12-FR22 (Calculators) | `calculators/`, `modules/evaluations/` | ✅ |
| FR23-FR26 (Rules) | `modules/rules/`, role-based auth | ✅ |
| FR27-FR33 (History) | `modules/evaluations/`, pagination | ✅ |
| FR34-FR35 (Real-time) | SSE endpoint, `useSSE` hook | ✅ |
| FR36-FR37 (Auth) | Firebase Auth, `modules/auth/` | ✅ |

**Non-Functional Requirements:** All 17 NFRs are addressed through technology choices (performance), patterns (security), and infrastructure decisions (reliability).

### Implementation Readiness Validation ✅

**Decision Completeness:** All critical decisions documented with rationale. Technology versions specified. Integration patterns defined.

**Structure Completeness:** Full directory tree with every file named. Module boundaries and responsibilities clear. Requirements mapped to specific locations.

**Pattern Completeness:** Comprehensive naming conventions, structure patterns, error handling, and authentication flow documented with examples.

### Gap Analysis Results

**Critical Gaps:** None identified

**Important Gaps:** None identified

**Minor Gaps:**
- No UX specification (acceptable for "function over form" MVP)
- Calculator formula details are implementation, not architecture

**Future Enhancements:**
- Add Sentry error tracking when needed
- Add staging environment if project grows

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed (Low-Medium, 5 users)
- [x] Technical constraints identified (GCP, Firebase, Neon, Polars)
- [x] Cross-cutting concerns mapped (Auth, Logging, Error Handling)

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined (REST, SSE, Google Sheets API)
- [x] Performance considerations addressed (async, Polars)

**✅ Implementation Patterns**
- [x] Naming conventions established (snake_case Python, camelCase TS)
- [x] Structure patterns defined (modular backend, feature-based frontend)
- [x] Communication patterns specified (REST, SSE, Depends())
- [x] Process patterns documented (error handling, auth flow)

**✅ Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**
- Clear modular structure prevents spaghetti code
- Calculators isolated as pure functions (easy to test, migrate)
- Technology choices aligned with team skills and project constraints
- Comprehensive patterns prevent AI agent conflicts
- Infrastructure as Code ensures reproducible deployments

**Areas for Future Enhancement:**
- Add Sentry for proactive error tracking
- Consider staging environment if tool becomes critical
- Expand rule engine if business needs grow

### Implementation Handoff

**AI Agent Guidelines:**
1. Follow all architectural decisions exactly as documented
2. Use implementation patterns consistently across all components
3. Respect project structure and module boundaries
4. Refer to this document for all architectural questions
5. Calculators must remain pure functions with no I/O

**First Implementation Priority:**
1. Initialize project structure (backend/, frontend/, infrastructure/)
2. Set up Terraform infrastructure (`aha_sicu_` resources in `asia-southeast1`)
3. Implement calculator modules with historical data validation
4. Build API endpoints following module patterns
5. Create frontend with TanStack Query integration

