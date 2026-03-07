# Project Documentation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:executing-plans to implement this plan task-by-task.

**Goal:** Create comprehensive project documentation — 10 engineer docs and 3 agent docs — from scratch.

**Architecture:** Two flat directories (`docs/engineer/`, `docs/agent/`). Engineer docs are the source of truth for architecture and domain knowledge. Agent docs are a thin layer referencing engineer docs, focused on file maps, conventions, and change recipes. Only stable/shipped features are documented.

**Tech Stack:** Markdown, Mermaid diagrams where helpful.

---

### Task 0: Create directory structure

**Files:**
- Create: `docs/engineer/` (directory)
- Create: `docs/agent/` (directory)

**Step 1: Create directories**

```bash
mkdir -p docs/engineer docs/agent
```

**Step 2: Commit**

```bash
git add docs/
git commit -m "Create docs directory structure for engineer and agent documentation"
```

---

### Task 1: Write project-overview.md

**Files:**
- Create: `docs/engineer/project-overview.md`

**Content scope:**
- What AHA SICU is: brand health evaluation system for Shopee e-commerce stores
- Who uses it: Business Development teams evaluating brand performance
- Core workflow diagram (Mermaid): Sync brands from Google Sheets → Select brand → Upload Shopee export files → Run calculators (ads keyword, discount, top SKU) → Enter manual data → Generate score → Save evaluation → Send email report
- Tech stack table (from README.md)
- Live environment URLs (prod + staging)
- Project structure overview (backend/, frontend/, infrastructure/, scripts/, smoke-tests/)
- Role system: member, leader, admin

**Step 1: Read source files for accuracy**

Read these files to extract accurate details:
- `README.md` — tech stack, environments, structure
- `backend/app/config.py` — settings overview
- `backend/app/core/dependencies.py` — roles
- `backend/app/main.py` — app setup

**Step 2: Write the document**

Write `docs/engineer/project-overview.md` with all sections above.

**Step 3: Commit**

```bash
git add docs/engineer/project-overview.md
git commit -m "Add project overview documentation"
```

---

### Task 2: Write architecture-backend.md

**Files:**
- Create: `docs/engineer/architecture-backend.md`

**Content scope:**
- Module layout diagram: `app/modules/` (auth, accounts, brands, evaluations, rules, sync, upload, email) each with router.py, service.py, schemas.py
- Calculator engine: `app/calculators/` — pure functions, no I/O
- Database layer: `app/db/` — connection pooling (asyncpg), queries as parameterized SQL
- Core utilities: `app/core/` — security, dependencies, exceptions, middleware
- Request lifecycle: HTTP request → middleware → router → service → queries → response
- Dependency injection pattern: `get_current_user()`, `require_role()`
- Dual authentication: Firebase tokens (human users) + Google OIDC (Cloud Scheduler)
- Error handling: `AppException` hierarchy + global middleware
- Async patterns: connection pooling (min=1, max=5), async context managers

**Step 1: Read source files for accuracy**

Key files to read:
- `backend/app/main.py` — app setup, middleware, router includes
- `backend/app/core/security.py` — Firebase auth
- `backend/app/core/oidc.py` — OIDC auth
- `backend/app/core/dependencies.py` — DI setup
- `backend/app/core/exceptions.py` — exception hierarchy
- `backend/app/core/middleware.py` — error handling
- `backend/app/db/connection.py` — DB pooling
- One representative module (e.g., `backend/app/modules/evaluations/`) to show the router→service→query pattern

**Step 2: Write the document**

Write `docs/engineer/architecture-backend.md` with all sections above. Include a Mermaid diagram for module layout.

**Step 3: Commit**

```bash
git add docs/engineer/architecture-backend.md
git commit -m "Add backend architecture documentation"
```

---

### Task 3: Write architecture-frontend.md

**Files:**
- Create: `docs/engineer/architecture-frontend.md`

**Content scope:**
- Pages and routes table: 8 routes with path, component, auth requirement, role restriction
- Component organization: feature folders (dashboard/, evaluation/, brands/, evaluations/, rules/, sync/, layout/) + shared UI primitives (ui/)
- State management: React Query v5 for server state, useState for UI state, AuthContext for auth, next-themes for theme
- API client: openapi-fetch with Firebase token middleware (`services/apiClient.ts`)
- Auth flow: Firebase email/password → AuthContext → ProtectedRoute/RoleProtectedRoute
- Form management: react-hook-form + useAutoSaveForm (debounced auto-save)
- i18n: i18next with single Indonesian locale (`locales/id.json`)
- Data flow diagram: Components → Hooks (useQuery/useMutation) → API Client → Backend

**Step 1: Read source files for accuracy**

Key files to read:
- `frontend/src/App.tsx` — routes
- `frontend/src/services/apiClient.ts` — API client
- `frontend/src/context/AuthContext.tsx` — auth context
- `frontend/src/hooks/` — scan hook names and patterns
- `frontend/src/components/auth/ProtectedRoute.tsx` — route protection
- `frontend/src/i18n.ts` — i18n setup

**Step 2: Write the document**

Write `docs/engineer/architecture-frontend.md` with all sections above.

**Step 3: Commit**

```bash
git add docs/engineer/architecture-frontend.md
git commit -m "Add frontend architecture documentation"
```

---

### Task 4: Write architecture-infrastructure.md

**Files:**
- Create: `docs/engineer/architecture-infrastructure.md`

**Content scope:**
- GCP resource inventory table: Cloud Run, Cloud SQL, Artifact Registry, Secret Manager, GCS, Firebase Hosting, Cloud Scheduler, Workload Identity
- Terraform module breakdown: each .tf file and what it provisions
- Service accounts (4): cloud_run, deploy, scheduler, sql_scheduler — each with roles
- Workload Identity Federation: keyless GitHub Actions auth via OIDC
- Cloud SQL: single db-f1-micro instance hosting dev + prod databases, scheduled start/stop
- Secret Manager: 3 secrets (db_password, gsheets_credentials, firebase_admin)
- GCS: upload bucket with 24h auto-delete, CORS config
- Cloud Scheduler: daily brand sync at 09:00 WIB
- Security model: least-privilege SAs, no SA keys, secret externalization
- Environment separation: dev.tfvars vs prod.tfvars

**Step 1: Read source files for accuracy**

Key files to read:
- `infrastructure/terraform/*.tf` — all Terraform files
- `infrastructure/terraform/environments/*.tfvars` — env configs

**Step 2: Write the document**

Write `docs/engineer/architecture-infrastructure.md` with all sections above.

**Step 3: Commit**

```bash
git add docs/engineer/architecture-infrastructure.md
git commit -m "Add infrastructure architecture documentation"
```

---

### Task 5: Write api-reference.md

**Files:**
- Create: `docs/engineer/api-reference.md`

**Content scope:**
- All ~40 endpoints grouped by module
- For each endpoint: HTTP method, path, authentication requirement, role restriction, request body/params, response shape, key behaviors/side effects
- Modules: Health, Auth, Accounts, Brands, Evaluations (CRUD + grouped + calculators + scoring + save), Upload, Rules, Sync, Email

**Step 1: Read source files for accuracy**

Read all router files:
- `backend/app/modules/auth/router.py`
- `backend/app/modules/accounts/router.py`
- `backend/app/modules/brands/router.py`
- `backend/app/modules/evaluations/router.py`
- `backend/app/modules/upload/router.py`
- `backend/app/modules/rules/router.py`
- `backend/app/modules/sync/router.py`
- `backend/app/modules/email/router.py`
- `backend/app/main.py` — health endpoint

Read schema files for request/response shapes:
- `backend/app/modules/*/schemas.py`

**Step 2: Write the document**

Write `docs/engineer/api-reference.md` with complete endpoint reference.

**Step 3: Commit**

```bash
git add docs/engineer/api-reference.md
git commit -m "Add API reference documentation"
```

---

### Task 6: Write data-models.md

**Files:**
- Create: `docs/engineer/data-models.md`

**Content scope:**
- All 9 tables: users, brand_vp_data, brand_meeting_data, evaluation_inputs, brand_uploads, calculator_results, evaluations, scoring_rules, sync_status
- For each table: columns, types, constraints, indexes
- Relationships: FK references, logical associations
- ER diagram (Mermaid)
- Key patterns: evaluation_inputs as shared mutable state per brand, evaluations as immutable INSERT-only snapshots, calculator_results keyed by brand+type
- Migration summary: 22 Alembic migrations

**Step 1: Read source files for accuracy**

Read migration files to extract schema:
- `backend/app/db/migrations/versions/` — scan migration files for CREATE TABLE and ALTER TABLE
- `backend/app/db/queries/*.py` — query files show column usage

**Step 2: Write the document**

Write `docs/engineer/data-models.md` with all sections above.

**Step 3: Commit**

```bash
git add docs/engineer/data-models.md
git commit -m "Add data models documentation"
```

---

### Task 7: Write scoring-engine.md

**Files:**
- Create: `docs/engineer/scoring-engine.md`

**Content scope:**
- Scoring system overview: 10 categories (Operational, Business, Content, Visitors, Promo Tools, Products, Ads, Campaign, Stock, Discount)
- Fashion vs Non-Fashion templates with different thresholds
- Dynamic rules (stored in scoring_rules table, editable by leader/admin)
- Verdict thresholds: 71+ Good, 41-70 Needs Review, <40 Not Recommended
- Calculator pipeline: engine.py orchestration, file dependencies per calculator, readiness checks, auto-execution on upload
- Ads Keyword calculator: inputs (CPC ad report + keyword report + total_products), outputs (CTR, CPC, ROAS, GMV)
- Top SKU calculator: inputs (order export + mass update), outputs (top products by revenue), filtering logic
- Discount checker: inputs (order export), outputs (discount %, voucher %, fake discount flag), Indonesian price handling
- Data flow: Upload files → auto-trigger calculators → enter manual data → generate score → save evaluation

**Step 1: Read source files for accuracy**

Read all calculator files:
- `backend/app/calculators/engine.py`
- `backend/app/calculators/scoring.py`
- `backend/app/calculators/ads_keyword.py`
- `backend/app/calculators/top_sku.py`
- `backend/app/calculators/discount.py`

**Step 2: Write the document**

Write `docs/engineer/scoring-engine.md` with all sections above.

**Step 3: Commit**

```bash
git add docs/engineer/scoring-engine.md
git commit -m "Add scoring engine documentation"
```

---

### Task 8: Write development-guide.md

**Files:**
- Create: `docs/engineer/development-guide.md`

**Content scope:**
- Prerequisites: Python 3.14, Node 20, uv, npm, PostgreSQL
- Backend setup: `cd backend && uv sync && cp .env.example .env`, edit .env, `uv run alembic upgrade head`, `uv run uvicorn app.main:app --reload`
- Frontend setup: `cd frontend && npm install && cp .env.example .env`, set VITE_API_BASE_URL, `npm run dev`
- Environment variables reference: all backend .env vars, all frontend VITE_ vars
- Running tests: `uv run pytest -v` (backend), `npm run test` / `npm run test:run` (frontend)
- Linting: `ruff check .` (backend), `npm run lint` (frontend)
- Type checking: `tsc --noEmit` (frontend)
- Database migrations: `uv run alembic revision --autogenerate -m "description"`, `uv run alembic upgrade head`
- Local file upload: filesystem fallback when GCS_UPLOAD_BUCKET not set
- Useful commands quick reference table

**Step 1: Read source files for accuracy**

Key files to read:
- `backend/pyproject.toml` — dependencies, scripts
- `backend/.env.example` (if exists) or `backend/app/config.py` — env vars
- `frontend/package.json` — scripts
- `frontend/.env.example` (if exists) — env vars

**Step 2: Write the document**

Write `docs/engineer/development-guide.md` with all sections above.

**Step 3: Commit**

```bash
git add docs/engineer/development-guide.md
git commit -m "Add development guide documentation"
```

---

### Task 9: Write deployment-guide.md

**Files:**
- Create: `docs/engineer/deployment-guide.md`

**Content scope:**
- CI pipeline: PR triggers backend + frontend test/lint jobs
- Deployment flow: merge to develop → auto-deploy dev; merge to main → deploy prod
- Backend deployment: Docker build → push to Artifact Registry → deploy to Cloud Run → health check → cleanup old revisions
- Frontend deployment: Vite build → deploy to Firebase Hosting → health check
- Terraform bootstrap: prerequisites, setup.sh walkthrough, manual secret injection
- Secret management: how to update secrets via gcloud CLI
- Smoke tests: how to run (`npm test` in smoke-tests/), environment variables needed
- Manual verification checklist reference

**Step 1: Read source files for accuracy**

Key files to read:
- `.github/workflows/ci.yml`
- `.github/workflows/deploy-backend.yml`
- `.github/workflows/deploy-frontend.yml`
- `infrastructure/terraform/setup.sh`
- `smoke-tests/README.md` or `smoke-tests/package.json`

**Step 2: Write the document**

Write `docs/engineer/deployment-guide.md` with all sections above.

**Step 3: Commit**

```bash
git add docs/engineer/deployment-guide.md
git commit -m "Add deployment guide documentation"
```

---

### Task 10: Write onboarding-guide.md

**Files:**
- Create: `docs/engineer/onboarding-guide.md`

**Content scope:**
- User provisioning workflow: provision-users.py → users log in → assign-roles.sql
- Daily BD workflow: sync brands → select brand → upload files → run calculators → enter manual data → score → save → email report
- Role permissions: what each role (member, leader, admin) can do
- Manual verification checklist: 10-step E2E evaluation cycle (from smoke-tests/MANUAL_CHECKLIST.md)

**Step 1: Read source files for accuracy**

Key files to read:
- `scripts/provision-users.py` — provisioning workflow
- `scripts/users-config.example.yaml` — user config format
- `scripts/assign-roles.sql` — role assignment
- `smoke-tests/MANUAL_CHECKLIST.md` (if exists)

**Step 2: Write the document**

Write `docs/engineer/onboarding-guide.md` with all sections above.

**Step 3: Commit**

```bash
git add docs/engineer/onboarding-guide.md
git commit -m "Add onboarding guide documentation"
```

---

### Task 11: Write agent CODEBASE.md

**Files:**
- Create: `docs/agent/CODEBASE.md`

**Content scope:**
- Complete file map: every directory and key file with a one-line purpose
- Backend map: `app/main.py`, `app/config.py`, `app/core/*`, `app/db/*`, `app/modules/*`, `app/calculators/*`
- Frontend map: `src/App.tsx`, `src/main.tsx`, `src/pages/*`, `src/components/*`, `src/hooks/*`, `src/services/*`, `src/context/*`, `src/firebase/*`, `src/lib/*`, `src/locales/*`
- Infrastructure map: `infrastructure/terraform/*.tf`
- Key entry points: `backend/app/main.py` (FastAPI app), `frontend/src/App.tsx` (routes), `frontend/src/main.tsx` (React root)
- Module boundaries: which directories own which concerns
- "Where to find X" quick reference: routes, auth, DB queries, API client, components, hooks, scoring logic, upload logic, etc.
- Cross-references: link to engineer docs for deeper architecture context

**Step 1: Use codebase exploration results**

Use the file structure knowledge already gathered. Verify any gaps by reading specific files.

**Step 2: Write the document**

Write `docs/agent/CODEBASE.md` — structured for machine consumption (tables, bullet lists, no prose).

**Step 3: Commit**

```bash
git add docs/agent/CODEBASE.md
git commit -m "Add agent codebase map documentation"
```

---

### Task 12: Write agent CONVENTIONS.md

**Files:**
- Create: `docs/agent/CONVENTIONS.md`

**Content scope:**
- Python conventions: type hints on all signatures, Pydantic schemas with strict mode, async/await patterns, parameterized SQL (no ORM), exception hierarchy usage
- TypeScript conventions: strict mode, path aliases (`@/`), React Query hooks pattern, openapi-fetch usage, Radix UI + shadcn components
- File naming: snake_case (Python), PascalCase components / camelCase hooks (TypeScript)
- File organization: module-based (backend), feature-folder (frontend), colocated tests
- Import ordering conventions
- Test patterns: pytest + pytest-asyncio (backend), vitest + RTL (frontend), mocks for Firebase
- Commit style: atomic commits, Mr. Door format (from CLAUDE.md)
- What NOT to do: no ORMs, no Redux, no custom state managers, no relative imports crossing module boundaries

**Step 1: Read source files for conventions**

Sample representative files to extract real patterns:
- A backend router, service, schema, query file
- A frontend page, component, hook, test file
- `CLAUDE.md` — commit and code style conventions

**Step 2: Write the document**

Write `docs/agent/CONVENTIONS.md` — structured as rules/guidelines, not prose.

**Step 3: Commit**

```bash
git add docs/agent/CONVENTIONS.md
git commit -m "Add agent conventions documentation"
```

---

### Task 13: Write agent PATTERNS.md

**Files:**
- Create: `docs/agent/PATTERNS.md`

**Content scope:**

Step-by-step recipes for common changes. Each recipe lists the exact files to create/modify and the pattern to follow (with code templates extracted from existing code):

1. **Add a new API endpoint**: Create router.py, service.py, schemas.py in `app/modules/<name>/`, add `__init__.py`, register router in `main.py`
2. **Add a new frontend page**: Create page in `src/pages/`, add route in `App.tsx`, create feature components in `src/components/<name>/`, add hooks in `src/hooks/`
3. **Add a new calculator**: Create calculator in `app/calculators/`, register in `engine.py` with file dependencies, add endpoint in evaluations router
4. **Add a new evaluation form section**: Create form component in `src/components/evaluation/forms/`, register in `formConfig.ts`, add to `EvaluationSections.tsx`
5. **Add a database migration**: `uv run alembic revision --autogenerate -m "description"`, edit migration, `uv run alembic upgrade head`
6. **Add a new React Query hook**: Create hook in `src/hooks/`, follow useQuery/useMutation pattern, add query key, handle errors
7. **Add a new UI component**: Use shadcn pattern in `src/components/ui/`, Radix UI primitives, class-variance-authority for variants

**Step 1: Read source files for patterns**

Read one example of each pattern to extract accurate templates:
- One complete module (e.g., `app/modules/brands/`)
- One page + its components
- `app/calculators/engine.py` — calculator registration
- `src/components/evaluation/forms/formConfig.ts` — form registration
- One hook file

**Step 2: Write the document**

Write `docs/agent/PATTERNS.md` — structured as numbered steps with code templates.

**Step 3: Commit**

```bash
git add docs/agent/PATTERNS.md
git commit -m "Add agent change patterns documentation"
```

---

### Task 14: Update README.md documentation links

**Files:**
- Modify: `README.md`

**Step 1: Read current README.md**

Read `README.md` to see existing documentation table.

**Step 2: Update documentation links**

Update the Documentation section to point to the new docs:

```markdown
## Documentation

### For Engineers
| Document | Description |
|----------|------------|
| [Project Overview](docs/engineer/project-overview.md) | Domain, workflow, tech stack, environments |
| [Architecture - Backend](docs/engineer/architecture-backend.md) | FastAPI modules, patterns, auth, DB |
| [Architecture - Frontend](docs/engineer/architecture-frontend.md) | React SPA, components, state, API client |
| [Architecture - Infrastructure](docs/engineer/architecture-infrastructure.md) | GCP resources, Terraform, CI/CD |
| [API Reference](docs/engineer/api-reference.md) | All REST endpoints with schemas |
| [Data Models](docs/engineer/data-models.md) | Database tables, relationships, migrations |
| [Scoring Engine](docs/engineer/scoring-engine.md) | Calculators, rules, verdict logic |
| [Development Guide](docs/engineer/development-guide.md) | Setup, testing, commands |
| [Deployment Guide](docs/engineer/deployment-guide.md) | CI/CD, environments, secrets |
| [Onboarding Guide](docs/engineer/onboarding-guide.md) | BD team walkthrough |

### For AI Agents
| Document | Description |
|----------|------------|
| [Codebase Map](docs/agent/CODEBASE.md) | File map, entry points, module boundaries |
| [Conventions](docs/agent/CONVENTIONS.md) | Naming, patterns, style guidelines |
| [Change Patterns](docs/agent/PATTERNS.md) | Step-by-step recipes for common changes |
```

**Step 3: Commit**

```bash
git add README.md
git commit -m "Update README documentation links"
```

---

### Task 15: Final review and cleanup

**Step 1: Verify all files exist**

```bash
ls docs/engineer/ docs/agent/
```

Expected: 10 files in engineer/, 3 files in agent/

**Step 2: Check for broken cross-references**

Grep for internal links and verify targets exist:
```bash
grep -r '\](docs/' docs/ README.md
```

**Step 3: Commit any fixes**

If any fixes needed, commit them.
