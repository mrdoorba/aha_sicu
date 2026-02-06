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
| File Storage | Google Cloud Storage | Large file uploads (>32MB Cloud Run limit) |

**External Dependencies:**
- Google Sheets API (VP sheet + 1st Meeting sheet sync)
- Firebase Auth SDK
- Neon connection pooling
- Google Cloud Storage (file uploads)

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
│   │   │   ├── brand_vp_data.py   # VP sheet brand queries
│   │   │   ├── brand_meeting_data.py # Meeting sheet brand queries
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
│   │   ├── sync/                  # Google Sheets sync module (VP + Meeting sheets)
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py         # SyncStatus, SyncRequest, SyncDetails
│   │   │   ├── service.py         # sync_from_sheets(), get_status()
│   │   │   └── sheets_client.py   # Google Sheets API client (dual-sheet fetch)
│   │   ├── evaluations/           # Evaluation storage module
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── upload/                # File upload module (GCS + ZIP support)
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # Signed URL generation, process trigger
│   │   │   ├── schemas.py
│   │   │   ├── service.py         # GCS operations, processing orchestration
│   │   │   └── zip_handler.py     # ZIP extraction, multi-part Excel merge
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
├── pyproject.toml                # UV project config with dependencies
├── uv.lock                       # UV lockfile for reproducible builds
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
│   ├── artifact_registry.tf # Docker registry with cleanup policy (keep 2)
│   ├── cloud_run.tf         # Backend deployment
│   ├── secrets.tf           # Secret Manager (db_url, gsheets, firebase_admin)
│   ├── storage.tf           # GCS bucket for file uploads
│   ├── scheduler.tf         # Daily sync job
│   ├── firebase.tf          # Firebase project, hosting site, auth
│   ├── iam.tf               # Service accounts (api, scheduler, sheets, deploy)
│   ├── workload_identity.tf # GitHub Actions OIDC federation (keyless auth)
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
- Frontend: TypeScript 5.9 (strict mode)

**Modularity Principles:**
- Each feature module is self-contained (router, schemas, service)
- No cross-module imports except through core
- Calculators are pure functions with no I/O dependencies
- Clear dependency injection through FastAPI's Depends()

**Styling Solution:**
- Tailwind CSS v4 (utility-first, rapid development)
- shadcn/ui (accessible component library built on Radix UI + Tailwind)

**Build Tooling:**
- Frontend: Vite 7 (fast HMR, optimized builds)
- Backend: UV (fast Python package/project manager) + Docker for Cloud Run deployment

**Package Management:**
- Backend: UV (replaces pip, pip-tools, virtualenv - single tool for dependency resolution, virtual environments, and project management)
- Frontend: npm

**Testing Framework:**
- Backend: pytest (unit tests for calculators, integration for API)
- Frontend: Vitest (Vite-native)

**Development Experience:**
- Hot reload on both frontend and backend
- Type checking throughout
- ESLint + Prettier (frontend), Ruff (backend - fast Python 3.14 compatible)
- UV for fast dependency management (`uv sync`, `uv run`, `uv add`)

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

**Database Schema — Brand Data (Dual-Sheet Model):**

The brand data comes from two separate Google Sheets (VP and 1st Meeting). Each sheet is stored in its own table with raw JSONB data:

| Table | Source | Purpose | Key Columns |
|-------|--------|---------|-------------|
| `brand_vp_data` | VP Sheet | Primary brand list | `id`, `brand_name`, `raw_data` (JSONB), `synced_at` |
| `brand_meeting_data` | 1st Meeting Sheet | Supplementary data | `id`, `brand_name`, `raw_data` (JSONB), `synced_at` |

- `brand_vp_data` is the **primary brand reference** — all downstream FKs (`brand_uploads`, `evaluation_inputs`, `calculator_results`, `evaluations`) reference `brand_vp_data(id)`
- `brand_meeting_data` enriches brand info when available (joined by `brand_name`)
- Both tables store raw sheet data as JSONB in `raw_data` to accommodate schema changes without migrations

**Database Schema — Sync Status:**

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `sync_log` | Track sync operations | `id`, `status`, `started_at`, `completed_at`, `sync_details` (JSONB) |

The `sync_details` JSONB column stores per-sheet results:
```json
{
  "vp_sheet": { "rows_synced": 150, "status": "success" },
  "meeting_sheet": { "rows_synced": 48, "status": "success" }
}
```
This enables partial failure tracking — one sheet can fail without blocking the other.

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

### File Upload Architecture

**Why GCS is Required:**
Cloud Run has a 32MB request body limit. Seller Center exports can reach 100MB+ when data is large, exported as ZIP archives containing multiple Excel parts.

**GCS Bucket Configuration:**
- Bucket name: `aha_sicu_uploads`
- Location: `asia-southeast1` (same as Cloud Run)
- Lifecycle: Auto-delete files after 24 hours (processed files don't need persistence)
- Access: Private, signed URLs only

**Supported Upload Types:**

| Type | Extension | Description |
|------|-----------|-------------|
| Single Excel | `.xlsx`, `.xls` | Standard single-file upload |
| ZIP Archive | `.zip` | Seller Center multi-part export |

**ZIP Archive Structure (Seller Center Export):**
```
seller_export.zip
├── data_part_1_of_3.xlsx
├── data_part_2_of_3.xlsx
└── data_part_3_of_3.xlsx
```
- Seller Center splits large datasets across multiple Excel files
- Each part contains a subset of rows with identical column structure
- Parts are numbered sequentially (part 1 of N, part 2 of N, etc.)

**Upload Flow (Signed URL Pattern):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. REQUEST SIGNED URL                                                        │
│    Frontend → POST /api/v1/upload/signed-url                                │
│    Body: { filename: "export.zip", content_type: "application/zip" }        │
│    Response: { upload_url: "https://storage...", upload_id: "uuid" }        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. DIRECT UPLOAD TO GCS                                                      │
│    Frontend → PUT {upload_url}                                              │
│    Body: <file binary>                                                      │
│    (Bypasses Cloud Run entirely - no size limit)                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. TRIGGER PROCESSING                                                        │
│    Frontend → POST /api/v1/upload/process                                   │
│    Body: { upload_id: "uuid", brand_id: 123 }                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. BACKEND PROCESSING                                                        │
│    a. Download file from GCS to memory                                      │
│    b. Detect file type (Excel or ZIP)                                       │
│    c. If ZIP: Extract → Sort parts → Merge into single DataFrame            │
│    d. If Excel: Parse directly with Polars                                  │
│    e. Run calculators                                                       │
│    f. Store evaluation in database                                          │
│    g. Delete file from GCS                                                  │
│    h. Broadcast SSE event: `new_evaluation`                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

**ZIP Processing Logic:**

```python
# Pseudocode for zip_handler.py
def process_zip(zip_bytes: bytes) -> pl.DataFrame:
    """Extract and merge multi-part Excel files from ZIP."""
    with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
        # 1. List Excel files, filter out __MACOSX, temp files
        excel_files = [f for f in zf.namelist()
                       if f.endswith(('.xlsx', '.xls'))
                       and not f.startswith('__')]

        # 2. Sort by part number (extract "part X of Y" pattern)
        excel_files = sort_by_part_number(excel_files)

        # 3. Read and concatenate all parts
        dataframes = []
        for excel_file in excel_files:
            with zf.open(excel_file) as f:
                df = pl.read_excel(f)
                dataframes.append(df)

        # 4. Vertical concat (all parts have same columns)
        return pl.concat(dataframes)
```

**Upload Error Codes:**

| Code | Description |
|------|-------------|
| `UPLOAD_INVALID_FORMAT` | Not .xlsx, .xls, or .zip |
| `UPLOAD_ZIP_NO_EXCEL` | ZIP contains no Excel files |
| `UPLOAD_ZIP_STRUCTURE_MISMATCH` | Excel parts have different columns |
| `UPLOAD_FILE_TOO_LARGE` | Exceeds maximum allowed size |
| `UPLOAD_SIGNED_URL_EXPIRED` | Signed URL validity (15 min) exceeded |
| `UPLOAD_PROCESSING_FAILED` | General processing error |

**GCS IAM Permissions:**
- Cloud Run service account needs `roles/storage.objectAdmin` on the bucket
- Signed URLs generated with `signBlob` permission

### Frontend Architecture

**State Management:** TanStack Query + React Context
- TanStack Query: server state (brands, evaluations, rules)
- React Context: auth state only

**Form Handling:** React Hook Form
- Lightweight, performant
- Built-in validation
- TypeScript-native

**API Client:** openapi-fetch 0.15
- Auto-generated from FastAPI OpenAPI spec
- Full type safety frontend ↔ backend

**UI Component Library:** shadcn/ui
- Accessible components built on Radix UI primitives
- Installed into src/components/ui/ (code ownership, no dependency lock-in)
- Tailwind v4 compatible

### Infrastructure & Deployment

**IaC:** Terraform
- Manages: Cloud Run, Secret Manager, Scheduler, IAM, Firebase setup, GCS bucket, Artifact Registry
- Firebase Hosting deploys via Firebase CLI (not Terraform)
- Runs only when infrastructure changes detected

**Artifact Registry:**
- Repository: `aha-sicu-registry` (Docker format)
- Cleanup policy: Keep 2 latest versions, auto-delete older images
- Rationale: Saves storage costs, 2 versions sufficient for rollback

**Cloud Run Revisions:**
- No automatic cleanup configured
- Rationale: Revisions don't cost compute when idle, minimal metadata storage
- Old revisions become non-functional anyway when their images are cleaned up
- Optional: Add CI/CD cleanup step if revision clutter becomes an issue

**Secret Manager:**
- Stores all sensitive configuration for production
- Secrets:
  | Secret Name | Purpose |
  |-------------|---------|
  | `aha_sicu_db_url` | Neon PostgreSQL connection string |
  | `aha_sicu_gsheets_credentials` | Google Sheets API service account key |
  | `aha_sicu_firebase_admin` | Firebase Admin SDK credentials (for token verification) |
- Cloud Run accesses secrets via `secretKeyRef` in service config
- Local dev uses `.env` file (not committed to git)

**Service Accounts & IAM (Least Privilege):**

| Service Account | Purpose | IAM Roles |
|-----------------|---------|-----------|
| `aha-sicu-api-sa` | Cloud Run runtime | `secretmanager.secretAccessor`, `storage.objectAdmin` (on upload bucket only) |
| `aha-sicu-scheduler-sa` | Cloud Scheduler | `run.invoker` (on Cloud Run service only) |
| `aha-sicu-sheets-sa` | Google Sheets API | No GCP roles (key stored in Secret Manager, Sheet shared with SA email) |
| `aha-sicu-deploy-sa` | GitHub Actions CI/CD | `run.admin`, `artifactregistry.writer`, `iam.serviceAccountUser` |

**Cloud Run Service Account (`aha-sicu-api-sa`):**
```
# Dedicated SA - NOT using default Compute Engine SA
resource "google_service_account" "cloud_run" {
  account_id   = "aha-sicu-api-sa"
  display_name = "Store ICU Cloud Run Service Account"
}

# Least privilege: Only access secrets it needs
resource "google_secret_manager_secret_iam_member" "db_url" {
  secret_id = google_secret_manager_secret.db_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Least privilege: Only access upload bucket, not all GCS
resource "google_storage_bucket_iam_member" "uploads" {
  bucket = google_storage_bucket.uploads.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run.email}"
}
```

**Cloud Scheduler Service Account (`aha-sicu-scheduler-sa`):**
```
# Separate SA for scheduler - can only invoke Cloud Run
resource "google_service_account" "scheduler" {
  account_id   = "aha-sicu-scheduler-sa"
  display_name = "Store ICU Scheduler Service Account"
}

# Can only invoke the specific Cloud Run service
resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  service  = google_cloud_run_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}
```

**GitHub Actions - Workload Identity Federation (No Keys!):**
```
# Workload Identity Pool for GitHub
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "aha-sicu-github-pool"
  display_name              = "GitHub Actions Pool"
}

# OIDC Provider for GitHub
resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Provider"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Deploy SA for GitHub Actions
resource "google_service_account" "deploy" {
  account_id   = "aha-sicu-deploy-sa"
  display_name = "Store ICU Deploy Service Account"
}

# Allow GitHub repo to impersonate deploy SA
resource "google_service_account_iam_member" "github_impersonate" {
  service_account_id = google_service_account.deploy.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/YOUR_ORG/store-icu"
}

# Deploy SA permissions
resource "google_project_iam_member" "deploy_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}

resource "google_project_iam_member" "deploy_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}

resource "google_service_account_iam_member" "deploy_act_as" {
  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.deploy.email}"
}
```

**GitHub Actions Workflow (uses Workload Identity):**
```yaml
# .github/workflows/deploy.yml
jobs:
  deploy:
    permissions:
      contents: read
      id-token: write  # Required for Workload Identity

    steps:
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/PROJECT_NUM/locations/global/workloadIdentityPools/aha-sicu-github-pool/providers/github-provider
          service_account: aha-sicu-deploy-sa@PROJECT_ID.iam.gserviceaccount.com

      # No SA key needed! GitHub OIDC token exchanged for GCP access token
```

**IAM Anti-Patterns Avoided:**

| Anti-Pattern | Why It's Bad | Our Approach |
|--------------|--------------|--------------|
| Default Compute SA | Over-privileged, shared | Dedicated SA per service |
| SA key in GitHub Secrets | Leak risk, rotation pain | Workload Identity Federation |
| `roles/owner` or `roles/editor` | Full project access | Specific roles only |
| One SA for everything | Blast radius if compromised | Isolated per purpose |
| Project-wide storage access | Can access any bucket | Bucket-level IAM only |

**Google Sheets Configuration:**
- VP Sheet: configurable spreadsheet ID, range (`VP!A:Y`), brand column (`Nama Brand`)
- 1st Meeting Sheet: configurable spreadsheet ID, range (`ZAP: 1st Meeting!A:D`), brand column (`Brand`)
- Each sheet syncs independently with per-sheet error tracking
- Sync service handles partial failures (one sheet can fail without blocking the other)

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
- Optional cleanup (add later if needed):
  ```bash
  # Delete Cloud Run revisions older than latest 2
  gcloud run revisions list --service=aha-sicu-api \
    --region=asia-southeast1 --format="value(name)" \
    --sort-by="~createTime" | tail -n +3 \
    | xargs -r gcloud run revisions delete --quiet
  ```

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
| Tables | `snake_case` plural | `brand_vp_data`, `brand_meeting_data`, `evaluations`, `scoring_rules` |
| Columns | `snake_case` | `brand_id`, `created_at`, `is_active` |
| Foreign keys | `{table}_id` | `brand_id` (references `brand_vp_data`), `user_id` |
| Indexes | `idx_{table}_{column}` | `idx_brand_vp_data_brand_name`, `idx_evaluations_created_at` |
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
- Always use exception chaining: `raise NewException(...) from original_exception` — never lose the original traceback
- Never use bare `except Exception` that swallows errors silently — always log or re-raise
- Network/external service errors must have broad `except Exception` with logging fallback, not just specific exception types

**Frontend:**
- TanStack Query handles API errors automatically
- Display user-friendly messages from `detail` field
- Log `code` for debugging
- TanStack Query `queryFn` MUST throw on error — never return `null` or swallow errors silently
- Every query/mutation error state MUST have visible UI (error message, retry button) — not just `console.log`

#### SQL Safety Rules

**ILIKE Queries (MUST follow):**
- All user-input used in `ILIKE` queries MUST be escaped using `_escape_like()` helper to prevent pattern injection (`%`, `_`, `\`)
- All `ILIKE` clauses using escaped input MUST include `ESCAPE '\'` — the escape helper is useless without this clause
- Example: `WHERE brand_name ILIKE '%' || $1 || '%' ESCAPE '\'`
- Search query parameters MUST have `max_length` validation (e.g., `Query(max_length=200)`)

**Parameterized SQL:**
- Always use `$1, $2` parameter placeholders — never f-strings or string concatenation for user input
- Table names cannot be parameterized — use a validated allowlist (e.g., `_VALID_TABLES` frozenset with `_validate_table()` helper)

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
- [ ] Response schemas match Acceptance Criteria field-by-field (names, types, structure)
- [ ] ILIKE queries include both `_escape_like()` AND `ESCAPE '\'` clause
- [ ] Error states have visible UI — no swallowed errors in queryFn or services
- [ ] Exception chaining preserved (`raise ... from e`) — no lost tracebacks
- [ ] Frontend hooks use `apiClient.ts` (openapi-fetch) — never raw `fetch()`
- [ ] File List matches `git diff` output — all changed files accounted for

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
│   │   │   │   ├── brand_vp_data.py   # VP sheet brand queries
│   │   │   │   ├── brand_meeting_data.py # Meeting sheet brand queries
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
│   │   │   │   ├── schemas.py        # SyncStatus, SyncRequest, SyncDetails
│   │   │   │   ├── service.py        # sync_from_sheets(), get_status()
│   │   │   │   └── sheets_client.py  # Google Sheets API client (dual-sheet fetch)
│   │   │   │
│   │   │   ├── evaluations/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py         # CRUD /evaluations
│   │   │   │   ├── schemas.py        # EvaluationInput, EvaluationResponse
│   │   │   │   └── service.py        # create_evaluation(), search()
│   │   │   │
│   │   │   ├── upload/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py         # POST /upload/signed-url, POST /upload/process
│   │   │   │   ├── schemas.py        # SignedUrlRequest, UploadProcess, UploadStatus
│   │   │   │   ├── service.py        # generate_signed_url(), process_upload()
│   │   │   │   ├── gcs_client.py     # GCS operations (upload, download, delete)
│   │   │   │   └── zip_handler.py    # extract_and_merge_excel_parts()
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
│   │   │   │   ├── FileUpload.tsx        # Drag-drop, accepts .xlsx/.xls/.zip
│   │   │   │   ├── FileUpload.test.tsx
│   │   │   │   ├── UploadProgress.tsx    # Progress bar, status messages
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
│   │   │   ├── useUpload.ts          # Signed URL flow, progress tracking
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
│   │   ├── artifact_registry.tf      # aha_sicu_registry (cleanup: keep 2 latest)
│   │   ├── cloud_run.tf              # aha_sicu_api service
│   │   ├── secrets.tf                # db_url, gsheets_credentials, firebase_admin
│   │   ├── storage.tf                # aha_sicu_uploads bucket (24h lifecycle)
│   │   ├── scheduler.tf              # aha_sicu_daily_sync
│   │   ├── firebase.tf               # Project, hosting site
│   │   ├── iam.tf                    # Service accounts (api, scheduler, sheets, deploy)
│   │   ├── workload_identity.tf      # GitHub Actions OIDC (no SA keys!)
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
│  modules/brands     ← DB queries (brand_vp_data + brand_meeting_data) │
│  modules/sync       ← Google Sheets API (VP + Meeting sheets)│
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
- `db/queries/brand_vp_data.py` - VP brand data queries
- `db/queries/brand_meeting_data.py` - Meeting brand data queries
- `components/brands/` - Brand UI components
- `hooks/useBrands.ts`, `hooks/useSync.ts`

**FR6-FR11 (Data Input & Upload):**
- `modules/upload/` - GCS signed URLs, Excel/ZIP processing
- `modules/upload/zip_handler.py` - Multi-part Excel merge from Seller Center exports
- `modules/upload/gcs_client.py` - GCS operations
- `components/upload/` - File upload UI with progress
- `hooks/useUpload.ts` - Signed URL flow, direct GCS upload

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
| Google Sheets API | `modules/sync/service.py`, `sheets_client.py` | VP sheet + 1st Meeting sheet sync |
| Firebase Auth | `core/security.py`, `firebase/` | User authentication |
| Neon PostgreSQL | `db/connection.py` | Data persistence |
| Google Cloud Storage | `modules/upload/gcs_client.py` | Large file uploads (Excel/ZIP) |

**Internal Communication:**

| From | To | Method |
|------|-----|--------|
| Frontend | Backend | REST API via openapi-fetch |
| Frontend | GCS | Direct upload via signed URL |
| Backend | Frontend | SSE for real-time updates |
| Backend | GCS | Download for processing, then delete |
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
| FR6-FR11 (Data Input) | `modules/upload/`, GCS signed URLs, ZIP handler, Polars | ✅ |
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
- Calculator formula details are implementation, not architecture

**Note:** UX Design Specification (`ux-design-specification.md`) has been created and provides comprehensive UI/UX guidance including design system (shadcn/ui), component patterns, user journeys, and accessibility requirements.

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

