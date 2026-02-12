# Story 4.1: Evaluation History List

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team leader**,
I want **to view a paginated, sortable list of all past evaluations**,
so that **I can review the team's work and quickly find specific evaluations**.

## Acceptance Criteria

1. **History page displays paginated evaluation list**
   **Given** I am logged in and navigate to `/history`
   **When** the page loads
   **Then** I see a paginated table of evaluations (20 per page, default sort: newest first)
   **And** each row shows: Brand name (from `brand_vp_data`), Final score, Template (Fashion/Non-Fashion), Evaluator email (from `users`), Date (formatted localized)
   **And** I see pagination controls showing current page and total pages

2. **Pagination works correctly**
   **Given** there are more than 20 evaluations
   **When** I click "Next" or a page number
   **Then** the table updates with the next page of results
   **And** the URL query params update (e.g., `?page=2`)
   **And** pagination shows correct total count and page info

3. **Column sorting works**
   **Given** I am on the History page
   **When** I click a column header (Date or Score)
   **Then** the list sorts by that column
   **And** clicking again toggles between ascending and descending
   **And** the sort state is reflected in the column header (arrow indicator)

4. **Row click navigates to evaluation detail**
   **Given** I see an evaluation in the list
   **When** I click the row
   **Then** I navigate to the evaluation detail view (placeholder for Story 4.5)
   **And** the row shows hover state on mouse over

5. **Empty state when no evaluations exist**
   **Given** no evaluations have been saved yet
   **When** the History page loads
   **Then** I see "No evaluations found" empty state message
   **And** an optional prompt to start evaluating brands

6. **Loading state during data fetch**
   **Given** the page is loading evaluations
   **When** the API request is in progress
   **Then** I see a loading skeleton/spinner
   **And** the table container has `aria-busy="true"`

7. **Error state on API failure**
   **Given** the evaluations API fails
   **When** the page tries to load
   **Then** I see an error message with a "Retry" button
   **And** clicking retry re-fetches the data

8. **Backend list endpoint**
   **Given** I call `GET /api/v1/evaluations`
   **When** authenticated
   **Then** return paginated evaluations with query params:
   - `page` (default: 1)
   - `limit` (default: 20, max: 100)
   - `sort_by` (default: "created_at", allowed: "created_at", "final_score")
   - `sort_order` (default: "desc", allowed: "asc", "desc")
   **And** each item includes: `id`, `brand_name`, `final_score`, `verdict`, `template`, `evaluator_email`, `created_at`
   **And** response follows paginated format: `{ items, total, page, limit, pages }`

9. **Navigation link in header**
   **Given** I am on any page
   **When** I look at the header navigation
   **Then** I see a "History" link alongside Dashboard and Brands
   **And** the active link is highlighted when on `/history`

## Tasks / Subtasks

- [x] Task 1: Create backend DB query for listing evaluations (AC: #8)
  - [x] 1.1 Add `list_evaluations()` in `backend/app/db/queries/evaluations.py` — SELECT with JOIN on `brand_vp_data` (brand_name) and `users` (email as evaluator_email)
  - [x] 1.2 Implement offset-based pagination (`OFFSET` + `LIMIT` from page/limit params)
  - [x] 1.3 Implement dynamic sorting with validated `sort_by` column (allowlist: `created_at`, `final_score`) and `sort_order` (asc/desc)
  - [x] 1.4 Add `count_evaluations()` query for total count
  - [x] 1.5 Use parameterized SQL with `$1, $2, ...` placeholders — sort column validated at router level via `Literal` type (see Task 3), use f-string only for the validated column name

- [x] Task 2: Create backend schemas and service for evaluation list (AC: #8)
  - [x] 2.1 Add `EvaluationListItem` schema: `id`, `brand_name`, `final_score`, `verdict`, `template`, `evaluator_email`, `created_at`
  - [x] 2.2 Add `EvaluationListResponse` schema: `items` (list of `EvaluationListItem`), `total`, `page`, `limit`, `pages`
  - [x] 2.3 Add `list_evaluations()` service function that calls DB queries and returns paginated response
  - [x] 2.4 Validate `page` >= 1, `limit` 1-100 — `sort_by` and `sort_order` validated at router level via `Literal` types (no service-layer validation needed)

- [x] Task 3: Create backend API endpoint (AC: #8)
  - [x] 3.1 Add `GET /api/v1/evaluations` endpoint in `evaluations/router.py`
  - [x] 3.2 Query params: `page: int = Query(default=1, ge=1)`, `limit: int = Query(default=20, ge=1, le=100)`, `sort_by: Literal["created_at", "final_score"] = Query(default="created_at")`, `sort_order: Literal["asc", "desc"] = Query(default="desc")` — FastAPI auto-validates and returns 422 for invalid values
  - [x] 3.3 Endpoint requires auth via `Depends(get_current_user)`
  - [x] 3.4 Return `EvaluationListResponse`

- [x] Task 4: Write backend tests (AC: #1, #2, #3, #8)
  - [x] 4.1 Integration test: GET /evaluations returns paginated list with correct fields (brand_name, evaluator_email, etc.)
  - [x] 4.2 Integration test: Pagination works (page=1 vs page=2 return different results)
  - [x] 4.3 Integration test: Sort by created_at desc (default) and asc
  - [x] 4.4 Integration test: Sort by final_score
  - [x] 4.5 Integration test: Invalid sort_by returns 422
  - [x] 4.6 Integration test: Empty results return `{ items: [], total: 0, page: 1, limit: 20, pages: 0 }`
  - [x] 4.7 Integration test: Auth required (401 without token)

- [x] Task 5: Create frontend `useEvaluationHistory` hook (AC: #1, #2, #3)
  - [x] 5.1 Create `frontend/src/hooks/useEvaluationHistory.ts` with TanStack `useQuery`
  - [x] 5.2 GET `/api/v1/evaluations` via `apiClient.ts` with page, limit, sort_by, sort_order params
  - [x] 5.3 Add path type for list endpoint in `apiClient.ts`
  - [x] 5.4 Return: `{ evaluations, total, page, pages, isLoading, isError, error, refetch, isPlaceholderData }`
  - [x] 5.5 Use queryKey: `['evaluations', page, limit, sortBy, sortOrder]` for cache management
  - [x] 5.6 Use `placeholderData: keepPreviousData` (TanStack Query v5 API) for smooth page transitions — keeps previous page visible while next page loads. Use `isPlaceholderData` flag to show subtle loading indicator without full skeleton swap

- [x] Task 6: Create `HistoryPage.tsx` and evaluation table component (AC: #1, #2, #3, #4, #5, #6, #7, #9)
  - [x] 6.1 Create `frontend/src/pages/HistoryPage.tsx` with page layout (Header + main content)
  - [x] 6.2 Create `frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — use shadcn/ui `Table` with `@tanstack/react-table` (`useReactTable` with `manualPagination: true` and `manualSorting: true` for server-side control). Columns: Brand, Score, Template, Evaluator, Date
  - [x] 6.3 Add pagination controls (Previous/Next buttons, page indicator) — wire `onPaginationChange` to update page state
  - [x] 6.4 Add sortable column headers — use `Button variant="ghost"` with `column.toggleSorting()` and `ArrowUpDown`/`ArrowUp`/`ArrowDown` icons from lucide-react for direction indicators (Date, Score columns only)
  - [x] 6.5 Add row click handler → navigate to `/history/{id}` (placeholder for Story 4.5)
  - [x] 6.6 Add loading state (skeleton or spinner with `aria-busy`) — when `isPlaceholderData` is true, show subtle opacity reduction instead of full skeleton swap
  - [x] 6.7 Add empty state ("No evaluations found")
  - [x] 6.8 Add error state with "Retry" button

- [x] Task 7: Add route and navigation (AC: #9)
  - [x] 7.1 Add `/history` route in `App.tsx` with `ProtectedRoute` wrapper
  - [x] 7.2 Add "History" link in `Header.tsx` navigation alongside Dashboard and Brands
  - [x] 7.3 Highlight active link when on `/history`

- [x] Task 8: Write frontend tests (AC: #1, #2, #3, #5, #6, #7)
  - [x] 8.1 Test: History page renders table with evaluation data
  - [x] 8.2 Test: Pagination buttons navigate between pages
  - [x] 8.3 Test: Column header click triggers sort
  - [x] 8.4 Test: Loading state displayed during fetch
  - [x] 8.5 Test: Empty state when no evaluations
  - [x] 8.6 Test: Error state with retry button
  - [x] 8.7 Test: History link appears in header navigation

## Dev Notes

### Story Context — First Story of Epic 4 (Evaluation History & Search)

This is the foundation story for Epic 4. It creates the evaluation history list page that subsequent stories (4.2-4.6) will enhance with search, filtering, detail view, and real-time notifications. The `evaluations` table already exists from Story 3.10 — this story only READS from it.

**Cross-story context within Epic 4:**
- Story 4.1 (this): Base list with pagination + sorting
- Story 4.2: Adds brand name search (ILIKE query with `_escape_like()`)
- Story 4.3: Adds date range filter
- Story 4.4: Adds category filter (fashion/non_fashion)
- Story 4.5: Adds full detail view (click through from list)
- Story 4.6: Adds SSE real-time notifications for new evaluations

**Design decision:** The `GET /api/v1/evaluations` endpoint in this story should be designed to accept search and filter params from the start, even if they're not wired yet — this prevents breaking changes in Stories 4.2-4.4. At minimum, define the query params but make them optional. The dev agent may choose to implement only pagination/sort now and leave search/filter params as no-ops, OR implement them all at once. Either approach is acceptable.

### Database — Querying the `evaluations` Table

The `evaluations` table was created in Story 3.10:

```sql
CREATE TABLE evaluations (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER NOT NULL REFERENCES brand_vp_data(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    template VARCHAR(20) NOT NULL,
    final_score DECIMAL(5,2) NOT NULL,
    verdict VARCHAR(20) NOT NULL,
    score_breakdown JSONB NOT NULL,
    calculator_results JSONB NOT NULL,
    manual_inputs JSONB NOT NULL,
    rule_version INTEGER NOT NULL DEFAULT 1,
    email_output TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evaluations_brand_id ON evaluations(brand_id);
CREATE INDEX idx_evaluations_created_at ON evaluations(created_at DESC);
```

**List query needs JOINs:**
```sql
SELECT e.id, b.brand_name, e.final_score, e.verdict, e.template,
       u.email AS evaluator_email, e.created_at
FROM evaluations e
JOIN brand_vp_data b ON e.brand_id = b.id
JOIN users u ON e.user_id = u.id
ORDER BY e.created_at DESC
LIMIT $1 OFFSET $2
```

**Count query:**
```sql
SELECT COUNT(*) FROM evaluations
```

**Important:** Do NOT select the heavy JSONB columns (`score_breakdown`, `calculator_results`, `manual_inputs`, `email_output`) in the list query — they're only needed for the detail view (Story 4.5). Selecting them would waste bandwidth and memory.

### Dynamic Sort Column Validation

The `sort_by` parameter allows sorting by `created_at` or `final_score`. Use **FastAPI `Literal` types** on the Query params for automatic validation — FastAPI returns a 422 with clear error details for invalid values and auto-generates OpenAPI enum documentation:

```python
from typing import Literal

@router.get("/api/v1/evaluations")
async def list_evaluations(
    sort_by: Literal["created_at", "final_score"] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    # ...
):
```

This eliminates the need for a manual `_VALID_SORT_COLUMNS` frozenset or `_validate_sort()` helper — validation happens at the FastAPI layer before the handler executes.

Since table/column names cannot be parameterized in SQL, use f-string for the validated column name ONLY (safe because `Literal` guarantees the value is one of the allowed strings):
```python
query = f"""
    SELECT ... FROM evaluations e
    JOIN brand_vp_data b ON e.brand_id = b.id
    JOIN users u ON e.user_id = u.id
    ORDER BY e.{sort_by} {sort_order}
    LIMIT $1 OFFSET $2
"""
```

**Note:** The `_VALID_TABLES` frozenset pattern from lessons-learned.md is still valid for dynamic table names where `Literal` types can't be used. For sort columns with a small fixed set, `Literal` is cleaner.

### API Response Format

**Paginated response (follows architecture convention):**
```json
{
  "items": [
    {
      "id": 1,
      "brand_name": "Nike Indonesia",
      "final_score": 78.50,
      "verdict": "✔️",
      "template": "fashion",
      "evaluator_email": "rina@company.com",
      "created_at": "2026-02-04T10:30:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

**Pagination math:**
```python
pages = math.ceil(total / limit) if total > 0 else 0
offset = (page - 1) * limit
```

### Frontend Component Architecture

**Page structure:**
```
HistoryPage.tsx
├── Header (existing, add "History" nav link)
├── <main id="main-content">
│   ├── Page title: "Evaluation History"
│   └── EvaluationHistoryTable
│       ├── Table header (sortable columns)
│       ├── Table body (evaluation rows)
│       ├── Empty state
│       ├── Loading state (skeleton)
│       ├── Error state (retry button)
│       └── Pagination controls
```

**Table columns:**
| Column | Field | Sortable | Format |
|--------|-------|----------|--------|
| Brand | `brand_name` | No (Story 4.2 adds search) | Text |
| Score | `final_score` | Yes | Number with verdict icon |
| Template | `template` | No (Story 4.4 adds filter) | Badge: "Fashion" / "Non-Fashion" |
| Evaluator | `evaluator_email` | No | Email text |
| Date | `created_at` | Yes (default sort) | Localized: "4 Feb 2026, 17:30" |

**Sorting UX:**
- Click column header to sort ascending
- Click again for descending
- Show arrow indicator: ↑ (asc) or ↓ (desc)
- Only Date and Score are sortable in this story

**Pagination UX:**
- "Previous" / "Next" buttons
- "Page X of Y" indicator
- Previous disabled on page 1, Next disabled on last page

### Existing Code to Integrate With

**Backend (existing — extend, don't replace):**
- `modules/evaluations/router.py` — Add `GET /api/v1/evaluations` list endpoint (separate from existing brand-specific endpoints)
- `modules/evaluations/schemas.py` — Add `EvaluationListItem`, `EvaluationListResponse`
- `modules/evaluations/service.py` — Add `list_evaluations()` function
- `db/queries/evaluations.py` — Add `list_evaluations()` and `count_evaluations()` queries
- `db/queries/brands.py` — Existing brand queries (do NOT modify)

**Frontend (existing — extend, don't replace):**
- `App.tsx` — Add `/history` route
- `components/layout/Header.tsx` — Add "History" nav link
- `services/apiClient.ts` — Add path type for `GET /api/v1/evaluations`

**Frontend (new files to create):**
- `pages/HistoryPage.tsx` — History page
- `hooks/useEvaluationHistory.ts` — TanStack Query hook for evaluation list
- `components/evaluations/EvaluationHistoryTable.tsx` — Table component

### Architecture Compliance

**Backend Pattern (MUST follow):**
- New endpoint in `modules/evaluations/router.py` — REST convention: `GET /api/v1/evaluations`
- Service layer handles pagination math and validation — no business logic in router
- DB queries use parameterized SQL (`$1, $2, ...`) for LIMIT/OFFSET — validated sort columns via allowlist (f-string only for validated column name)
- Auth required via `Depends(get_current_user)`
- Exception chaining: always `raise AppException(...) from e` — never lose tracebacks
- Response schema MUST match AC #8 field-by-field: `id`, `brand_name`, `final_score`, `verdict`, `template`, `evaluator_email`, `created_at`
- Paginated response format: `{ items, total, page, limit, pages }`

**Frontend Pattern (MUST follow):**
- Hook uses `apiClient.ts` (openapi-fetch) — never raw `fetch()`
- TanStack Query `useQuery` with proper queryKey including all filter/sort params
- Error states have visible UI (error message, retry button) — no swallowed errors
- Use existing shadcn/ui components: `Table`, `Button`, `Badge`
- Use `aria-busy="true"` on loading table container (lessons learned)
- camelCase for variables, PascalCase for components
- Row click navigates to detail page — use `useNavigate` from react-router-dom

**Data Display Rules:**
- Date format: localized (e.g., "4 Feb 2026, 17:30 WIB") — use `Intl.DateTimeFormat` or a lightweight formatter
- Score format: display with verdict icon/emoji alongside (e.g., "78.50 ✔️")
- Template: display as Badge — "Fashion" or "Non-Fashion" (map `non_fashion` → `Non-Fashion`)
- Numbers: use monospace font for score values (`font-mono` class per UX spec)

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| FastAPI | existing | Router, Query params with `Literal` types, Depends | Installed |
| asyncpg | existing | Parameterized SQL SELECT with JOIN | Installed |
| pydantic | existing | EvaluationListItem/Response schemas | Installed |
| @tanstack/react-query | v5 (existing) | `useQuery` with `placeholderData: keepPreviousData` for paginated list | Installed |
| openapi-fetch | ^0.15.0 (existing) | Typed API client (latest 0.16.0, no breaking changes) | Installed |
| @tanstack/react-table | existing | `useReactTable` with `manualPagination`/`manualSorting` | Installed |
| shadcn/ui (Table, Button, Badge) | existing | Table display, sortable headers, pagination, template badges | Installed |
| react-router-dom | existing | Route, Link, useNavigate | Installed |
| lucide-react | existing | `ArrowUpDown`/`ArrowUp`/`ArrowDown` icons for sort indicators | Installed |

**No new dependencies needed.** All required libraries are already installed.

### Project Structure Notes

**New files to create:**
```
frontend/src/pages/HistoryPage.tsx                              ← History page
frontend/src/hooks/useEvaluationHistory.ts                      ← Paginated list hook
frontend/src/components/evaluations/EvaluationHistoryTable.tsx   ← Table component
backend/tests/integration/api/test_evaluation_list.py            ← Integration tests
```

**Existing files to modify:**
```
backend/app/db/queries/evaluations.py          ← Add list_evaluations(), count_evaluations()
backend/app/modules/evaluations/schemas.py     ← Add EvaluationListItem, EvaluationListResponse
backend/app/modules/evaluations/service.py     ← Add list_evaluations() service
backend/app/modules/evaluations/router.py      ← Add GET /api/v1/evaluations endpoint
frontend/src/services/apiClient.ts             ← Add evaluation list path type
frontend/src/App.tsx                           ← Add /history route
frontend/src/components/layout/Header.tsx      ← Add History nav link
```

**Alignment with unified project structure:**
- Backend follows `modules/{feature}/{router,schemas,service}.py` pattern — confirmed
- DB queries in `db/queries/evaluations.py` — extends existing file
- Frontend hook in `hooks/` directory — follows established pattern
- Frontend page in `pages/` directory — follows established pattern
- New component in `components/evaluations/` — matches architecture.md frontend structure
- No new component directories needed outside existing pattern

### Testing Requirements

**Backend Integration Tests (pytest) — `tests/integration/api/test_evaluation_list.py`:**

| Test | AC | Description |
|------|-----|-------------|
| `test_list_evaluations_success` | #1, #8 | GET /evaluations returns paginated list with `id`, `brand_name`, `final_score`, `verdict`, `template`, `evaluator_email`, `created_at` |
| `test_list_evaluations_pagination` | #2, #8 | Two pages of data, page=1 and page=2 return different items, total/pages are correct |
| `test_list_evaluations_sort_date_desc` | #3, #8 | Default sort: newest first |
| `test_list_evaluations_sort_date_asc` | #3, #8 | `sort_order=asc` returns oldest first |
| `test_list_evaluations_sort_score` | #3, #8 | `sort_by=final_score` sorts by score |
| `test_list_evaluations_invalid_sort` | #8 | `sort_by=invalid_column` returns 422 |
| `test_list_evaluations_empty` | #5, #8 | No evaluations returns `{ items: [], total: 0, page: 1, limit: 20, pages: 0 }` |
| `test_list_evaluations_auth_required` | #8 | GET /evaluations without auth returns 401 |

**Frontend Component Tests (vitest):**

| Test | AC | File | Description |
|------|-----|------|-------------|
| `renders evaluation history table` | #1 | EvaluationHistoryTable.test.tsx | Table displays brand name, score, template, evaluator, date |
| `pagination navigates pages` | #2 | EvaluationHistoryTable.test.tsx | Next/Previous buttons update page |
| `column sort toggles direction` | #3 | EvaluationHistoryTable.test.tsx | Click Date header toggles sort |
| `shows loading state` | #6 | EvaluationHistoryTable.test.tsx | Loading skeleton displayed |
| `shows empty state` | #5 | EvaluationHistoryTable.test.tsx | "No evaluations found" when empty |
| `shows error with retry` | #7 | EvaluationHistoryTable.test.tsx | Error message and retry button |
| `history link in header` | #9 | Header.test.tsx | "History" link present in navigation |

**Run commands:**
- Backend: `cd backend && uv run python -m pytest tests/integration/api/test_evaluation_list.py -v`
- Frontend: `cd frontend && npx vitest run --reporter=verbose`

### Previous Story Intelligence

**From Story 3.10 (Save Evaluation) — Direct predecessor:**

- `evaluations` table created with indexes on `brand_id` and `created_at DESC` — ready for list queries
- `insert_evaluation()` in `db/queries/evaluations.py` — this story adds read queries alongside existing write queries
- `SaveEvaluationResponse` returns `id`, `brand_id`, `final_score`, `verdict`, `template`, `created_at` — the list endpoint returns similar fields plus `brand_name` and `evaluator_email` from JOINs
- Transaction pattern: `async with conn.transaction()` used for writes — list queries are read-only, no transaction needed
- Frontend `useSaveEvaluation` hook pattern — follow same structure for `useEvaluationHistory`
- `apiClient.ts` already has save endpoint path type — add list endpoint path type alongside it

**From Epic 3 Code Reviews:**
- Response schemas MUST match ACs field-by-field
- Frontend hooks MUST use `apiClient.ts` — never raw `fetch()`
- Error states MUST have visible UI
- File List MUST include ALL changed files
- `aria-busy` on loading table containers (from accessibility retrofit Story 2.6)

**From Lessons Learned:**
- Sort column validation: use `_VALID_TABLES` frozenset pattern (adapted for sort columns)
- ILIKE queries need `_escape_like()` + `ESCAPE '\'` — not needed in this story (search is Story 4.2) but keep in mind for future
- Backend tests: `uv run python -m pytest` (not `pytest` directly)
- Frontend tests: `npx vitest run --reporter=verbose`

### Git Intelligence

**Recent commits (Epic 3 completed, retro done):**
```
810c979 Execute Epic 3 retro action items: update correct-course, dev checklist, add Epic 6
0b56d1a Complete Epic 3 retrospective — all findings documented, sprint status updated
4f7691e Merge feature/3-10-save-evaluation into develop
4b65364 Fix code review findings: save reset, transaction, error text, tests (Story 3.10)
a200192 Mark Story 3.10 complete — all tasks done, status → review
```

**Patterns to follow:**
- Feature branch naming: `feature/4-1-evaluation-history-list`
- Branch created from `develop` (current branch)
- Atomic commits per task
- Tests committed alongside implementation

### How This Feeds Into Later Epic 4 Stories

| Story | What 4.1 Provides | What It Adds |
|-------|-------------------|--------------|
| 4.2 (Search by Brand) | List endpoint, table component | `search` query param, search input UI |
| 4.3 (Filter by Date) | List endpoint, table component | `date_from`, `date_to` query params, date picker UI |
| 4.4 (Filter by Category) | List endpoint, table component | `category` query param, dropdown filter UI |
| 4.5 (Detail View) | Row click navigation | Detail page, full evaluation display |
| 4.6 (Real-time Notifications) | History page, list hook | SSE event listener, toast notifications |

**Design for forward compatibility:**
- The `GET /api/v1/evaluations` endpoint should accept optional `search`, `date_from`, `date_to`, `category` query params even if not implemented yet — return all results when these are not provided. This prevents breaking the API contract in Stories 4.2-4.4.
- The `useEvaluationHistory` hook queryKey should include all filter params (even if unused) so cache invalidation works correctly when filters are added later.

### Latest Technical Specifics (Web Research — Feb 2026)

**TanStack Query v5 Pagination:**
- Use `placeholderData: keepPreviousData` (imported from `@tanstack/react-query`) — replaces the old v4 boolean `keepPreviousData: true`
- `isPlaceholderData` flag (from `useQuery` return) replaces old `isPreviousData` — use it to show subtle loading indicator (e.g., opacity reduction) during page transitions
- Query key factory pattern recommended: `evaluationKeys.list(page, limit, sortBy, sortOrder)` — but a simple array `['evaluations', page, limit, sortBy, sortOrder]` is fine for this scope

**FastAPI `Literal` Type Validation:**
- `Literal["created_at", "final_score"]` on `Query()` params auto-validates at the framework level — returns 422 with clear error for invalid values
- Generates proper OpenAPI enum documentation (Swagger UI shows dropdown)
- Eliminates need for manual frozenset + validate helper for this use case

**shadcn/ui Data Table + @tanstack/react-table:**
- Use `useReactTable` with `manualPagination: true` and `manualSorting: true` for server-side control
- Sortable header pattern: `<Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>` with `ArrowUpDown` icon from lucide-react
- `pageCount` must be passed to `useReactTable` for `getCanNextPage()` / `getCanPreviousPage()` to work correctly with server-side pagination

**openapi-fetch:**
- Current codebase uses `^0.15.0`; latest is `0.16.0` — no breaking changes, safe to keep current version
- No changes needed to `apiClient.ts` patterns

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.1 — Story ACs, list requirements, FR28-FR33]
- [Source: _bmad-output/planning-artifacts/architecture.md — Module structure, DB conventions, API patterns, pagination format, naming rules]
- [Source: _bmad-output/planning-artifacts/architecture.md#API-Naming — Paginated response format: { items, total, page, limit, pages }]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Architecture — asyncpg + parameterized SQL, sort column validation]
- [Source: _bmad-output/planning-artifacts/architecture.md#SQL-Safety-Rules — _VALID_TABLES frozenset pattern for sort columns]
- [Source: _bmad-output/planning-artifacts/prd.md — FR28-FR33: Evaluation history search and display]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Journey-2 — Historical Lookup: search, filter, review details]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Component-Strategy — Table, Badge, Button components for history]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Feedback-Patterns — Loading states, empty states, error states]
- [Source: _bmad-output/implementation-artifacts/3-10-save-evaluation.md — evaluations table schema, insert_evaluation(), save patterns]
- [Source: backend/app/modules/evaluations/router.py — Existing evaluation endpoints (extend with GET /evaluations)]
- [Source: backend/app/modules/evaluations/schemas.py — Existing types: CategoryType, VerdictType, SaveEvaluationResponse]
- [Source: backend/app/modules/evaluations/service.py — Existing service patterns (save_evaluation, generate_score)]
- [Source: backend/app/db/queries/evaluations.py — Existing queries (insert_evaluation, upsert_evaluation_inputs)]
- [Source: frontend/src/App.tsx — Routing structure, ProtectedRoute pattern]
- [Source: frontend/src/components/layout/Header.tsx — Navigation structure, active link pattern]
- [Source: frontend/src/services/apiClient.ts — Path type definitions, auth middleware]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, sort validation, test commands]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- @tanstack/react-table was listed as "Installed" in story Library table but was missing — installed as part of Task 6

### Completion Notes List

- Tasks 1-4 (Backend): Added `list_evaluations()` and `count_evaluations()` DB queries with JOIN on brand_vp_data and users. Created `EvaluationListItem`/`EvaluationListResponse` schemas. Service layer handles pagination math (offset, pages). Router uses `Literal` types for sort_by/sort_order validation — FastAPI auto-returns 422 for invalid values. 8 integration tests covering all AC #8 scenarios.
- Tasks 5-6 (Frontend): Created `useEvaluationHistory` hook with TanStack Query v5 `placeholderData: keepPreviousData` for smooth page transitions. Built `EvaluationHistoryTable` with `@tanstack/react-table` (`manualPagination`/`manualSorting`), sortable Date/Score columns with arrow indicators, row click navigation to `/history/{id}`, loading skeletons with `aria-busy`, empty state, error state with retry.
- Task 7 (Navigation): Added `/history` route with `ProtectedRoute` wrapper and "History" link in Header nav alongside Dashboard and Brands with active state highlighting.
- Task 8 (Frontend Tests): 6 EvaluationHistoryTable tests (data rendering, pagination, sort, loading, empty, error+retry) + 1 Header test for History link. All pass.
- Full regression: 481 backend tests pass (0 failures), 224 frontend tests pass (2 pre-existing Firebase API key failures in App.test.tsx and EvaluationForms.test.tsx — unrelated to this story).

### Change Log

- 2026-02-12: Implemented evaluation history list — backend endpoint `GET /api/v1/evaluations` with pagination/sorting, frontend history page with table, route, and navigation

### File List

**New files:**
- backend/tests/integration/api/test_evaluation_list.py
- frontend/src/hooks/useEvaluationHistory.ts
- frontend/src/components/evaluations/EvaluationHistoryTable.tsx
- frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx
- frontend/src/pages/HistoryPage.tsx

**Modified files:**
- backend/app/db/queries/evaluations.py
- backend/app/modules/evaluations/schemas.py
- backend/app/modules/evaluations/service.py
- backend/app/modules/evaluations/router.py
- frontend/src/services/apiClient.ts
- frontend/src/App.tsx
- frontend/src/components/layout/Header.tsx
- frontend/src/components/layout/Header.test.tsx
- frontend/package.json
- frontend/package-lock.json
- _bmad-output/implementation-artifacts/sprint-status.yaml
