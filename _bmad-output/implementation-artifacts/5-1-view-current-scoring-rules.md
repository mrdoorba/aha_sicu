# Story 5.1: View Current Scoring Rules

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system owner**,
I want **to view the current scoring thresholds and rules**,
so that **I understand how scores are calculated**.

## Acceptance Criteria

1. **Backend returns current scoring rules for both templates**
   **Given** I am authenticated with role `leader` or `admin`
   **When** I call `GET /api/v1/rules`
   **Then** return the current scoring configuration as a list of two rule objects (fashion + non_fashion):
   ```json
   [
     {
       "id": 1,
       "template": "fashion",
       "rules": { ... },
       "version": 1,
       "updated_by": null,
       "updated_at": "2026-02-12T00:00:00Z"
     },
     {
       "id": 2,
       "template": "non_fashion",
       "rules": { ... },
       "version": 1,
       "updated_by": null,
       "updated_at": "2026-02-12T00:00:00Z"
     }
   ]
   ```
   **And** each `rules` JSONB object contains thresholds organized by scoring category:
   ```json
   {
     "operational": {
       "unfulfilled_order_rate": { "threshold": 1.0, "points": 4, "comparison": "lte" },
       "late_shipment_rate": { "threshold": 1.0, "points": 3, "comparison": "lte" },
       "preparation_time": { "threshold": 1.0, "points": 3, "comparison": "lte" },
       "chat_response_rate": { "threshold": 95.0, "comparison": "gte", "info_only": true },
       "overall_rating": { "threshold": 4.7, "comparison": "gte", "info_only": true }
     },
     "business": {
       "monthly_sales_trend": { "threshold_pct": 90.0, "points": 10, "comparison": "gte" },
       "six_month_avg_threshold": { "threshold": 100000000, "points": 10, "comparison": "gte" },
       "conversion_rate": { "threshold": 2.0, "comparison": "gte", "info_only": true }
     },
     "content": {
       "quality_ratio": { "threshold": 95.0, "comparison": "gte", "info_only": true }
     },
     "visitors": {
       "returning_visitors_pct": { "threshold": 23.0, "points": 3, "comparison": "gte" },
       "followers": { "threshold": 50000, "points": 2, "comparison": "gte" }
     },
     "promo_tools": {
       "usage_pct_threshold": { "threshold": 80.0, "opportunity_points": 5 },
       "effectiveness_pct_threshold": { "threshold": 90.0, "opportunity_points": 10 }
     },
     "products_status": {
       "product_count": { "threshold": 35, "points": 5, "comparison": "gte" },
       "store_status_points": { "mall": 10, "star_plus": 5, "star": 0, "regular": 0 }
     },
     "ads": {
       "roi_threshold": { "threshold": 8.0, "opportunity_points": 5, "comparison": "gt" },
       "gmv_ratio_threshold": { "threshold": 84.0, "points": 5, "comparison": "lt" },
       "cost_ratio_range": { "min": 5.0, "max": 10.0, "info_only": true }
     },
     "campaign": {
       "participation_pct_threshold": { "threshold": 90.0, "opportunity_points": 10, "comparison": "gte" }
     },
     "stock": {
       "high_threshold": { "threshold": 24, "points": 10, "comparison": "gte" },
       "mid_threshold": { "threshold": 12, "points": 5, "comparison": "gte" },
       "low_penalty": { "threshold": 12, "points": -5, "comparison": "lt" }
     },
     "discount": {
       "fake_discount_flag": { "points_no_flag": 5, "points_flag": 0 }
     },
     "interpretation": {
       "ranges": [
         { "min": 71, "max": null, "label": "Good Candidate", "verdict": "✔️" },
         { "min": 41, "max": 70, "label": "Needs Review", "verdict": "⭕️" },
         { "min": null, "max": 40, "label": "Not Recommended", "verdict": "❌" }
       ]
     }
   }
   ```
   **Note on Fashion vs Non-Fashion differences:** The `non_fashion` template has `conversion_rate.threshold = 3.0` (vs 2.0 for fashion) and `ads.roi_threshold.threshold = 9.0` (vs 8.0 for fashion). All other thresholds are identical.

2. **Role-based access control on backend**
   **Given** I am authenticated with role `member`
   **When** I call `GET /api/v1/rules`
   **Then** return 403 Forbidden with `{"code": "RULE_ACCESS_DENIED", "detail": "Only leaders and admins can access scoring rules"}`

3. **Frontend displays rules organized by category**
   **Given** I am logged in with role `leader` or `admin`
   **When** I navigate to `/rules`
   **Then** I see the current scoring configuration displayed in a readable format:
   - Template selector tabs (Fashion / Non-Fashion) at the top
   - Each scoring category as a collapsible card section
   - Within each category: threshold name, value, points/penalty, and comparison logic
   - Score interpretation ranges at the bottom
   - Rule version number and last updated timestamp in the page header
   **And** values that differ between templates are highlighted when switching tabs

4. **Frontend role gate for /rules route**
   **Given** I am logged in with role `member`
   **When** I try to navigate to `/rules`
   **Then** I am redirected to `/dashboard`
   **And** a toast notification says "Access denied — scoring rules require leader or admin role"

5. **Database migration creates scoring_rules table and seeds defaults**
   **Given** the migration runs
   **When** it completes
   **Then** the `scoring_rules` table exists with columns: `id`, `template`, `rules` (JSONB), `version`, `updated_by` (FK users), `updated_at`
   **And** two rows are seeded: one for `fashion`, one for `non_fashion`
   **And** both rows have `version = 1` and `updated_by = NULL` (system-seeded)
   **And** the JSONB structure matches the schema defined in AC #1

## Tasks / Subtasks

- [x] Task 1: Create database migration for scoring_rules table (AC: #5)
  - [x] 1.1 Create `backend/app/db/migrations/versions/010_create_scoring_rules_table.py`
  - [x] 1.2 Define table: id SERIAL PK, template VARCHAR(20) UNIQUE NOT NULL, rules JSONB NOT NULL, version INTEGER DEFAULT 1, updated_by INTEGER REFERENCES users(id), updated_at TIMESTAMPTZ DEFAULT NOW()
  - [x] 1.3 Add index: `idx_scoring_rules_template`
  - [x] 1.4 Seed fashion template row with all thresholds extracted from `scoring.py`
  - [x] 1.5 Seed non_fashion template row (identical except: conversion_rate threshold=3.0, roi_threshold threshold=9.0)
  - [x] 1.6 Implement downgrade() that drops table

- [x] Task 2: Create database queries module (AC: #1)
  - [x] 2.1 Create `backend/app/db/queries/rules.py`
  - [x] 2.2 Implement `get_all_rules(conn) -> list[dict]` — SELECT all rows ordered by template
  - [x] 2.3 Implement `get_rules_by_template(conn, template: str) -> dict | None` — SELECT single row by template

- [x] Task 3: Create backend rules module — schemas (AC: #1)
  - [x] 3.1 Create `backend/app/modules/rules/__init__.py`
  - [x] 3.2 Create `backend/app/modules/rules/schemas.py` with `ScoringRuleResponse` Pydantic model (id, template, rules as dict, version, updated_by as Optional[int], updated_at as datetime)

- [x] Task 4: Create backend rules module — service (AC: #1, #2)
  - [x] 4.1 Create `backend/app/modules/rules/service.py`
  - [x] 4.2 Implement `get_all_rules()` that fetches from DB via rules queries
  - [x] 4.3 Returns list of ScoringRuleResponse

- [x] Task 5: Create backend rules module — router with role guard (AC: #1, #2)
  - [x] 5.1 Create `backend/app/modules/rules/router.py` with `APIRouter(prefix="/api/v1/rules", tags=["rules"])`
  - [x] 5.2 Implement `GET /` endpoint that returns list of scoring rules
  - [x] 5.3 Add role-check dependency: if `current_user["role"]` not in `("leader", "admin")`, raise AppException with code `RULE_ACCESS_DENIED`, status 403
  - [x] 5.4 Register router in `backend/app/main.py`

- [x] Task 6: Write backend tests (AC: #1, #2, #5)
  - [x] 6.1 Test `GET /api/v1/rules` returns 200 with two rule objects for leader role
  - [x] 6.2 Test `GET /api/v1/rules` returns 200 for admin role
  - [x] 6.3 Test `GET /api/v1/rules` returns 403 for member role
  - [x] 6.4 Test response structure matches AC #1 schema (template, rules JSONB, version, updated_by, updated_at)
  - [x] 6.5 Test fashion and non_fashion rules have correct differing thresholds (conversion_rate, roi_threshold)
  - [x] 6.6 Test rules JSONB contains all expected categories (operational, business, content, visitors, promo_tools, products_status, ads, campaign, stock, discount, interpretation)

- [x] Task 7: Create frontend useRules hook (AC: #3)
  - [x] 7.1 Create `frontend/src/hooks/useRules.ts`
  - [x] 7.2 Implement `useRules()` hook using `useQuery` with key `['rules']`
  - [x] 7.3 Use `apiClient.GET("/api/v1/rules")` — throw on error
  - [x] 7.4 Define `ScoringRule` TypeScript interface matching backend response

- [x] Task 8: Create frontend RulesPage (AC: #3, #4)
  - [x] 8.1 Create `frontend/src/pages/RulesPage.tsx`
  - [x] 8.2 Template selector tabs (Fashion / Non-Fashion) using shadcn Tabs
  - [x] 8.3 Collapsible category cards showing thresholds, points, comparison logic per category
  - [x] 8.4 Score interpretation ranges section at bottom
  - [x] 8.5 Page header with version number and last updated timestamp
  - [x] 8.6 Loading and error states
  - [x] 8.7 Highlight differing values when switching template tabs

- [x] Task 9: Add /rules route with role gate (AC: #4)
  - [x] 9.1 Add `/rules` route in `App.tsx` pointing to `RulesPage`
  - [x] 9.2 Create role-based route guard (check `user.role` from AuthContext)
  - [x] 9.3 If member role, redirect to `/dashboard` with toast "Access denied — scoring rules require leader or admin role"

- [x] Task 10: Add Rules navigation link (AC: #3)
  - [x] 10.1 Add "Rules" link in sidebar navigation (visible only to leader/admin roles)
  - [x] 10.2 Show/hide based on current user's role from AuthContext

- [x] Task 11: Write frontend tests (AC: #3, #4)
  - [x] 11.1 Test RulesPage renders rule categories for leader role
  - [x] 11.2 Test template tab switching shows different thresholds
  - [x] 11.3 Test role gate redirects member to dashboard
  - [x] 11.4 Test navigation link hidden for member role
  - [x] 11.5 Test loading and error states

## Dev Notes

### Story Context — First Story of Epic 5 (Rule Configuration)

This is the first story in Epic 5, introducing the rules infrastructure. Epic 5 has 3 stories:
- **Story 5.1 (this):** View current scoring rules — read-only display + DB migration + seed
- **Story 5.2:** Edit scoring rules with password confirmation — write operations
- **Story 5.3:** Apply configured rules in scoring — integrate DB rules into calculator

**Critical design decision:** This story creates the `scoring_rules` table and seeds it with the **exact thresholds currently hardcoded in `backend/app/calculators/scoring.py`**. The scoring calculator itself is NOT modified in this story — it continues using hardcoded values until Story 5.3. This story establishes the data model and viewing capability.

**Cross-epic context:** Epics 1-4 are all `done`. The codebase has 526 backend tests and 264 frontend tests, all passing. The scoring calculator (`calculators/scoring.py`, 1429 lines) is a pure function with all thresholds hardcoded.

### Backend — Rules Module Pattern

**Follow the existing module pattern exactly** (see `modules/brands/` for reference):

```
backend/app/modules/rules/
├── __init__.py
├── router.py      # GET /api/v1/rules (role-restricted)
├── schemas.py     # ScoringRuleResponse
└── service.py     # get_all_rules()
```

**Role-check pattern** — create a reusable dependency:

```python
# In router.py or a shared dependency
from app.core.exceptions import AppException

def require_role(*allowed_roles: str):
    async def check(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise AppException(
                code="RULE_ACCESS_DENIED",
                detail="Only leaders and admins can access scoring rules",
                status_code=403,
            )
        return current_user
    return check
```

**Router registration in main.py:**
```python
from app.modules.rules.router import router as rules_router
app.include_router(rules_router)
```

### Backend — Database Migration

**File:** `backend/app/db/migrations/versions/010_create_scoring_rules_table.py`

**Table schema:**
```sql
CREATE TABLE scoring_rules (
    id SERIAL PRIMARY KEY,
    template VARCHAR(20) UNIQUE NOT NULL,
    rules JSONB NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_scoring_rules_template ON scoring_rules (template);
```

**Seed data:** Extract all current thresholds from `backend/app/calculators/scoring.py`. The JSONB structure must capture every threshold, point value, comparison operator, and info_only flag so that Story 5.3 can replace hardcoded values with DB-driven values.

**Fashion vs Non-Fashion differences** (only 2 fields differ):
| Field | Fashion | Non-Fashion |
|-------|---------|-------------|
| `business.conversion_rate.threshold` | 2.0 | 3.0 |
| `ads.roi_threshold.threshold` | 8.0 | 9.0 |

All other thresholds are identical between templates.

### Backend — Scoring Threshold Extraction from scoring.py

The following thresholds are hardcoded in `backend/app/calculators/scoring.py` and must be captured in the seed data:

**Operational (Rows 7-11):**
- Row 7: `unfulfilled_order_rate` — threshold: 1.0%, points: 4, else: -(rate value) penalty
- Row 8: `late_shipment_rate` — threshold: 1.0%, points: 3, else: 0
- Row 9: `preparation_time` — threshold: 1.0 days, points: 3, else: 0
- Row 10: `chat_response_rate` — threshold: 95.0%, info_only (no points, verdict only)
- Row 11: `overall_rating` — threshold: 4.7, info_only

**Business (Rows 13, 19, 20):**
- Row 13: `monthly_sales_trend` — current month > 90% of 6-month avg → 10 points
- Row 19: `six_month_avg` — avg > 100,000,000 IDR → 10 points
- Row 20: `conversion_rate` — Fashion: >2%, Non-Fashion: >3% (info_only, no points)

**Content (Row 24):**
- Row 24: `quality_ratio` — threshold: 95.0%, info_only

**Visitors (Rows 28-29):**
- Row 28: `returning_visitors_pct` — threshold: 23.0%, points: 3
- Row 29: `followers` — threshold: 50,000, points: 2

**Promo Tools (Rows 42-43):**
- Row 42: `usage_pct` — threshold: 80.0%, opportunity_points: 5
- Row 43: `effectiveness_pct` — threshold: 90.0%, opportunity_points: 10

**Products/Status (Rows 45-46):**
- Row 45: `product_count` — threshold: 35, points: 5
- Row 46: `store_status` — Mall: 10, Star+: 5, Star/Regular: 0

**Ads (Rows 50-52):**
- Row 50: `roi` — Fashion: >8, Non-Fashion: >9, opportunity_points: 5
- Row 51: `gmv_ratio` — threshold: <84%, points: 5
- Row 52: `cost_ratio` — range: 5-10%, info_only

**Campaign (Row 57):**
- Row 57: `participation_pct` — threshold: 90%, opportunity_points: 10

**Stock (Row 70):**
- Row 70: `average_stock` — >=24: 10pts, >=12: 5pts, <12: -5pts

**Discount (Row 73):**
- Row 73: `fake_discount` — no flag: 5pts, flag: 0pts

**Interpretation Ranges:**
- 71-100: "Good Candidate" (✔️)
- 41-70: "Needs Review" (⭕️)
- 0-40: "Not Recommended" (❌)

### Frontend — RulesPage Design

**Follow UX spec pattern:** Professional card-based layout with clear data hierarchy.

**Layout:**
```
┌──────────────────────────────────────────────────┐
│  Scoring Rules        v1 · Updated 2026-02-12    │
├──────────────────────────────────────────────────┤
│  [Fashion] [Non-Fashion]                         │  ← Tabs component
├──────────────────────────────────────────────────┤
│  ▼ Operational (Max: 10 pts)                     │  ← Collapsible card
│    Unfulfilled Rate  ≤ 1.0%    → 4 pts           │
│    Late Shipment     ≤ 1.0%    → 3 pts           │
│    Preparation Time  ≤ 1.0 day → 3 pts           │
│    Chat Response     ≥ 95.0%   (info only)       │
│    Overall Rating    ≥ 4.7     (info only)       │
├──────────────────────────────────────────────────┤
│  ▼ Business (Max: 20 pts)                        │
│    ...                                           │
├──────────────────────────────────────────────────┤
│  ... (all categories)                            │
├──────────────────────────────────────────────────┤
│  Score Interpretation                            │
│    71+ = Good Candidate ✔️                       │
│    41-70 = Needs Review ⭕️                       │
│    ≤40 = Not Recommended ❌                      │
└──────────────────────────────────────────────────┘
```

**shadcn/ui components to use:**
- `Tabs` / `TabsContent` for Fashion/Non-Fashion switching
- `Collapsible` for category sections
- `Card` for each category container
- `Badge` for point values and comparison operators
- `Table` for threshold rows within each category

**Highlighting template differences:** When switching tabs, values that differ (conversion_rate, roi_threshold) should have a subtle visual indicator (e.g., blue highlight or small "differs" badge).

### Frontend — Role Gate Pattern

**New pattern needed:** The codebase currently uses `ProtectedRoute` for auth-only protection. This story introduces role-based route protection.

**Approach:** Create a `RoleProtectedRoute` wrapper component:

```typescript
function RoleProtectedRoute({
  allowedRoles,
  children
}: {
  allowedRoles: string[];
  children: React.ReactNode
}) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  if (!allowedRoles.includes(user.role)) {
    toast.error("Access denied — scoring rules require leader or admin role");
    return <Navigate to="/dashboard" />;
  }
  return <>{children}</>;
}
```

**In App.tsx:**
```tsx
<Route path="/rules" element={
  <RoleProtectedRoute allowedRoles={["leader", "admin"]}>
    <RulesPage />
  </RoleProtectedRoute>
} />
```

### Frontend — Sidebar Navigation

**File to modify:** The sidebar/header navigation component (check `Header.tsx` or layout component).

The "Rules" link should only be visible when `user.role` is `leader` or `admin`. Use conditional rendering based on AuthContext user role.

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Module structure: `modules/rules/{__init__, router, schemas, service}.py`
- Router prefix: `/api/v1/rules`
- Schemas: Pydantic BaseModel with field types matching DB columns
- Service: async functions with `db.connection()` context manager
- Queries: parameterized SQL in `db/queries/rules.py`
- Error handling: `AppException` with RULE_ prefix codes
- Role check: `current_user["role"]` validation in dependency

**Frontend Pattern (MUST follow):**
- Hook: `useRules.ts` using `useQuery` with `apiClient.GET()`
- Page: `RulesPage.tsx` with loading/error states
- Route: Role-protected in `App.tsx`
- Components: Compose from shadcn/ui primitives

**Naming Conventions:**
- Backend: snake_case (Python) — `get_all_rules()`, `scoring_rules`, `rules_router`
- Frontend: camelCase (TypeScript) — `useRules()`, `scoringRule`, `RulesPage`
- API: snake_case JSON — `{ "rule_version": 1, "updated_at": "..." }`
- Database: snake_case — `scoring_rules`, `updated_by`, `idx_scoring_rules_template`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| FastAPI | existing | Router, Depends, HTTPException | Installed |
| asyncpg | existing | Database queries | Installed |
| Pydantic | existing | Request/response schemas | Installed |
| Alembic | existing | Database migration | Installed |
| @tanstack/react-query | v5 (existing) | `useQuery` for rules fetch | Installed |
| openapi-fetch | existing | `apiClient.GET()` | Installed |
| shadcn/ui Tabs | existing | Template selector | Installed |
| shadcn/ui Collapsible | check | Category sections | May need install |
| shadcn/ui Card | existing | Category containers | Installed |
| shadcn/ui Badge | existing | Point values | Installed |
| shadcn/ui Table | existing | Threshold rows | Installed |
| sonner | existing | Toast notifications for role denial | Installed |

**Check if Collapsible is installed:** Run `ls frontend/src/components/ui/collapsible*` — if not present, install via `npx shadcn@latest add collapsible`.

**No new backend dependencies required.**

### File Structure Requirements

**New files (backend):**
```
backend/app/db/migrations/versions/010_create_scoring_rules_table.py
backend/app/db/queries/rules.py
backend/app/modules/rules/__init__.py
backend/app/modules/rules/router.py
backend/app/modules/rules/schemas.py
backend/app/modules/rules/service.py
backend/tests/integration/api/test_rules.py
```

**New files (frontend):**
```
frontend/src/hooks/useRules.ts
frontend/src/pages/RulesPage.tsx
frontend/src/components/rules/RulesCategoryCard.tsx
frontend/src/components/rules/RulesPage.test.tsx
```

**Modified files:**
```
backend/app/main.py                              — Register rules_router
frontend/src/App.tsx                              — Add /rules route with role gate
frontend/src/components/layout/Header.tsx         — Add Rules nav link (role-conditional)
_bmad-output/implementation-artifacts/sprint-status.yaml  — Update 5-1 status
```

### Testing Requirements

**Backend Tests (pytest):**

| Test | AC | Description |
|------|-----|-------------|
| `test_get_rules_returns_both_templates` | #1 | GET /api/v1/rules returns 200 with 2 rule objects |
| `test_get_rules_fashion_thresholds` | #1 | Fashion rules contain all expected categories and values |
| `test_get_rules_non_fashion_thresholds` | #1 | Non-fashion has conversion=3.0 and roi=9.0 |
| `test_get_rules_schema_structure` | #1 | Response fields match: id, template, rules, version, updated_by, updated_at |
| `test_get_rules_leader_role_allowed` | #1, #2 | Leader role gets 200 |
| `test_get_rules_admin_role_allowed` | #1, #2 | Admin role gets 200 |
| `test_get_rules_member_role_forbidden` | #2 | Member role gets 403 with RULE_ACCESS_DENIED |
| `test_get_rules_rules_jsonb_categories` | #1 | JSONB contains: operational, business, content, visitors, promo_tools, products_status, ads, campaign, stock, discount, interpretation |

**Frontend Tests (vitest):**

| Test | AC | Description |
|------|-----|-------------|
| `renders rules page with category sections` | #3 | Page shows all scoring categories |
| `switches between fashion and non-fashion tabs` | #3 | Tab click changes displayed thresholds |
| `highlights differing values between templates` | #3 | conversion_rate and roi show visual difference |
| `shows version and updated timestamp` | #3 | Header displays v1 and date |
| `redirects member role to dashboard` | #4 | Role gate works correctly |
| `hides rules nav link for member role` | #4 | Sidebar conditional rendering |
| `shows loading state` | #3 | Skeleton/spinner while fetching |
| `shows error state` | #3 | Error message with retry on fetch failure |

**Run commands:**
- Backend: `cd backend && uv run python -m pytest tests/integration/api/test_rules.py -v`
- Frontend: `cd frontend && npx vitest run src/components/rules/RulesPage.test.tsx --reporter=verbose`

### Previous Story Intelligence

**From Story 4.6 (last completed story):**
- 526 backend tests, 264 frontend tests — all passing
- SSE infrastructure fully operational
- Code review found 4M + 3L issues (mainly Literal types, field validation, test resilience)
- Pattern established: keep File List accurate, use refs for mutable state in hooks

**From Lessons Learned:**
- ILIKE queries need `ESCAPE '\'` — not relevant here (no search in this story)
- Response schemas must match ACs field-by-field — critical for the rules JSONB structure
- File List must include ALL changed files — be thorough
- Use `Literal` types for constrained values (template: `Literal["fashion", "non_fashion"]`)
- Backend tests: `uv run python -m pytest` (not `pytest` directly)
- Cache invalidation must be explicit (relevant for Story 5.2 mutations, not this read-only story)

### Git Intelligence

**Recent commits (Epic 4 completed):**
```
e9b092c Merge feature/epic-4-retro into develop
8abfb6d Remove _bmad file from tracking
9f60dd0 Execute Epic 4 retro action item A3: document scoring calculator logic
e103341 Execute Epic 4 retro action items A1 and A2
e7053e4 Add Epic 4 retrospective and mark epic done
```

**Branch strategy for this story:**
- Branch from: `develop` (current branch)
- Feature branch: `feature/5-1-view-current-scoring-rules`
- Atomic commits: migration first, then backend module, then frontend
- Tests alongside implementation

### Project Structure Notes

- Alignment with unified project structure: All new files follow established patterns
- No structural conflicts — `modules/rules/` is a clean addition
- `db/queries/rules.py` follows existing query module pattern
- Migration numbering continues from 009 → 010
- Frontend follows feature-organized structure with hooks, pages, components

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.1 — Story ACs: view rules, role restriction, scoring_rules table]
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-5 — Epic overview: FR23-FR26, scoring thresholds without code deployment]
- [Source: _bmad-output/planning-artifacts/prd.md#Rule-Configuration — FR23: view thresholds, FR25: store in DB]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Architecture — scoring_rules table schema, role-based authorization]
- [Source: _bmad-output/planning-artifacts/architecture.md#API-Boundaries — /api/v1/rules PUT admin only, GET authenticated]
- [Source: _bmad-output/planning-artifacts/architecture.md#Module-Boundaries — modules/rules/ for rule config CRUD only]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation-Patterns — Naming conventions, error code prefix RULE_]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Component-Strategy — RulesEditor in Phase 1 custom components]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Journey-3 — System owner rule management flow]
- [Source: backend/app/calculators/scoring.py — All hardcoded thresholds to extract for seed data]
- [Source: backend/app/modules/brands/router.py — Module pattern reference (router, schemas, service)]
- [Source: backend/app/db/migrations/versions/009_create_evaluations_table.py — Migration pattern reference]
- [Source: backend/app/db/queries/evaluations.py — Query pattern reference (parameterized SQL, async)]
- [Source: backend/app/core/dependencies.py — get_current_user dependency, role field in user dict]
- [Source: backend/app/main.py — Router registration pattern]
- [Source: frontend/src/App.tsx — Route definition and ProtectedRoute pattern]
- [Source: frontend/src/hooks/useEvaluationHistory.ts — useQuery hook pattern reference]
- [Source: _bmad-output/lessons-learned.md — Literal types, File List accuracy, response schema matching]
- [Source: _bmad-output/implementation-artifacts/4-6-real-time-new-evaluation-notifications.md — Previous story dev notes and patterns]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Test mock fix: asyncpg returns JSONB as Python dicts, not strings — mock data updated accordingly
- Tab switching test: `/3/` regex too broad, replaced with specific `\u2265 3` assertion
- Existing test fixes: Added `useCurrentUser` mock to Header.test.tsx and additional page mocks to App.test.tsx to prevent Firebase import chain errors

### Completion Notes List

- **Tasks 1-5 (Backend):** Created `scoring_rules` table migration (010) with fashion/non_fashion seed data containing all thresholds extracted from scoring.py. Built rules module (router, service, schemas, queries) with `require_role("leader", "admin")` dependency for 403 access control. Registered router in main.py.
- **Task 6 (Backend Tests):** 8 integration tests covering: auth (401 without token), role access (200 for leader/admin, 403 for member with RULE_ACCESS_DENIED), response structure (2 templates, correct schema fields, all 11 JSONB categories), and template differences (conversion_rate 2.0 vs 3.0, roi_threshold 8.0 vs 9.0).
- **Tasks 7-8 (Frontend):** Created `useRules` hook with React Query, `useCurrentUser` hook for role access, `RulesPage` with shadcn Tabs for Fashion/Non-Fashion switching, collapsible category cards with threshold tables, score interpretation section, version/timestamp in header, and "differs" badges for template-differing values. Added `/api/v1/rules` path to apiClient.ts.
- **Tasks 9-10 (Frontend routing):** Created `RoleProtectedRoute` component (redirects member to /dashboard with toast), added `/rules` route in App.tsx, added role-conditional "Rules" link in Header nav.
- **Task 11 (Frontend Tests):** 13 tests covering: RulesPage rendering (categories, tab switching, differs badges, version/timestamp, loading, error+retry), RoleProtectedRoute (member redirect, leader/admin access, unauthenticated redirect), Header nav (link visible for leader/admin, hidden for member).

### File List

**New files (backend):**
- backend/app/db/migrations/versions/010_create_scoring_rules_table.py
- backend/app/db/queries/rules.py
- backend/app/modules/rules/__init__.py
- backend/app/modules/rules/router.py
- backend/app/modules/rules/schemas.py
- backend/app/modules/rules/service.py
- backend/tests/integration/api/test_rules.py

**New files (frontend):**
- frontend/src/hooks/useRules.ts
- frontend/src/hooks/useCurrentUser.ts
- frontend/src/pages/RulesPage.tsx
- frontend/src/components/rules/RulesCategoryCard.tsx
- frontend/src/components/rules/RulesPage.test.tsx
- frontend/src/components/auth/RoleProtectedRoute.tsx
- frontend/src/components/ui/collapsible.tsx
- frontend/src/components/ui/tabs.tsx

**Modified files:**
- backend/app/main.py — Register rules_router
- frontend/src/services/apiClient.ts — Add /api/v1/rules path type
- frontend/src/App.tsx — Add /rules route with RoleProtectedRoute, import RulesPage
- frontend/src/components/layout/Header.tsx — Add Rules nav link (role-conditional via useCurrentUser)
- frontend/src/components/layout/Header.test.tsx — Add useCurrentUser mock
- frontend/src/App.test.tsx — Add RoleProtectedRoute and RulesPage mocks
- frontend/package.json — Updated dependencies (collapsible, tabs)
- frontend/package-lock.json — Updated lockfile
- _bmad-output/implementation-artifacts/sprint-status.yaml — Update 5-1 status

### Change Log

- **2026-02-12:** Implemented Story 5.1 — View Current Scoring Rules. Created scoring_rules DB table with seed data, backend rules module with role-based access control, and frontend RulesPage with template tabs, collapsible categories, and role gate. 534 backend tests + 268 frontend tests passing.
