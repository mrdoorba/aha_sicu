# Story 4.4: Filter by Category

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team leader**,
I want **to filter evaluations by category (Fashion/Non-Fashion)**,
so that **I can review evaluations for a specific product type**.

## Acceptance Criteria

1. **Category filter dropdown with All/Fashion/Non-Fashion options**
   **Given** I am on the History page
   **When** I view the filter bar
   **Then** I see a category dropdown with three options: "All", "Fashion", "Non-Fashion"
   **And** "All" is selected by default (no category filter active)
   **And** the dropdown is placed alongside the existing search input and date pickers in the filter bar

2. **Filter by Fashion**
   **Given** I select "Fashion" from the category filter dropdown
   **When** the list updates
   **Then** only evaluations with template = "fashion" are shown
   **And** pagination resets to page 1
   **And** the URL includes `?category=fashion`

3. **Filter by Non-Fashion**
   **Given** I select "Non-Fashion" from the category filter dropdown
   **When** the list updates
   **Then** only evaluations with template = "non_fashion" are shown
   **And** pagination resets to page 1
   **And** the URL includes `?category=non_fashion`

4. **Select All removes category filter**
   **Given** I have "Fashion" or "Non-Fashion" selected
   **When** I select "All"
   **Then** the list shows all evaluations regardless of template
   **And** the `category` param is removed from the URL
   **And** pagination resets to page 1

5. **Category filter combines with existing filters**
   **Given** I have an active search term AND/OR a date range AND a category selected
   **When** the list loads
   **Then** all active filters apply (AND logic) — only evaluations matching the brand name AND within the date range AND matching the category
   **And** total count and pages reflect the combined filter

6. **Backend category filter endpoint**
   **Given** I call `GET /api/v1/evaluations?category=fashion`
   **When** authenticated
   **Then** return paginated evaluations where `evaluations.template = 'fashion'`
   **And** `category=non_fashion` returns only non-fashion evaluations
   **And** `category` param omitted returns all evaluations (no category filter)
   **And** invalid category values return 422 Unprocessable Entity (FastAPI Literal validation)

7. **Category dropdown has accessible label**
   **Given** the category filter dropdown on the History page
   **When** a screen reader focuses the dropdown
   **Then** it announces "Filter by category"

8. **Loading state during category filter**
   **Given** I change the category filter value
   **When** the API request is in progress
   **Then** the table shows a subtle loading indicator (opacity reduction via `isPlaceholderData`)
   **And** the table container has `aria-busy="true"` (existing behavior)

## Tasks / Subtasks

- [x] Task 1: Add category filtering to backend DB queries (AC: #6)
  - [x] 1.1 Add `category: str | None = None` param to `_build_filter_clauses()` in `db/queries/evaluations.py`
  - [x] 1.2 Add WHERE clause: `e.template = $N` when category is provided (exact match, no ILIKE)
  - [x] 1.3 Category condition extends existing param numbering (after search, date_from, date_to)
  - [x] 1.4 `list_evaluations()` and `count_evaluations()` accept and pass `category` param to `_build_filter_clauses()`

- [x] Task 2: Wire category filtering through backend service layer (AC: #6)
  - [x] 2.1 Add `category: Literal["fashion", "non_fashion"] | None = None` param to `list_evaluations()` in `service.py`
  - [x] 2.2 Pass `category` to both `eval_queries.list_evaluations()` and `eval_queries.count_evaluations()`

- [x] Task 3: Wire category filtering in backend router (AC: #6)
  - [x] 3.1 Pass existing `category` param from router to `list_evaluations()` service call (currently accepted but not forwarded)
  - [x] 3.2 Remove forward-compat comment for category filtering now that it's implemented

- [x] Task 4: Write backend tests (AC: #2, #3, #4, #5, #6)
  - [x] 4.1 Integration test: `GET /evaluations?category=fashion` returns only fashion evaluations
  - [x] 4.2 Integration test: `GET /evaluations?category=non_fashion` returns only non-fashion evaluations
  - [x] 4.3 Integration test: No `category` param returns all evaluations (existing behavior preserved)
  - [x] 4.4 Integration test: Category filter combined with search — both filters apply (AND logic)
  - [x] 4.5 Integration test: Category filter combined with date range — all three filters apply (AND logic)
  - [x] 4.6 Integration test: Category filter combined with search AND date range — all filters apply
  - [x] 4.7 Integration test: Category filter with pagination — total/pages reflect filtered count
  - [x] 4.8 Integration test: Invalid category value returns 422

- [x] Task 5: Add category filter param to frontend hook (AC: #1, #5)
  - [x] 5.1 Add `category?: string` param to `useEvaluationHistory()` hook signature
  - [x] 5.2 Include `category` in API query params sent to backend (conditional — only when value present and not "all")
  - [x] 5.3 Include `category` in TanStack Query key: `['evaluations', page, limit, sortBy, sortOrder, search, dateFrom, dateTo, category]`

- [x] Task 6: Add category dropdown UI to EvaluationHistoryTable (AC: #1, #2, #3, #4, #7, #8)
  - [x] 6.1 Add a category filter using shadcn `Select` component with three options: "All" (value: empty), "Fashion" (value: "fashion"), "Non-Fashion" (value: "non_fashion")
  - [x] 6.2 Place category dropdown in the existing filter bar alongside search input and date pickers
  - [x] 6.3 Wire category selection to URL params: `category` param (remove from URL when "All" is selected)
  - [x] 6.4 Read `category` from `searchParams` and pass to `useEvaluationHistory()` hook
  - [x] 6.5 Reset page to 1 when category filter changes
  - [x] 6.6 Add `aria-label="Filter by category"` on the Select trigger
  - [x] 6.7 Update empty state message to include category context when category filter is active

- [x] Task 7: Write frontend tests (AC: #1, #2, #3, #4, #5, #7)
  - [x] 7.1 Test: Category dropdown renders with accessible label
  - [x] 7.2 Test: Selecting "Fashion" updates URL with `category=fashion` and resets page to 1
  - [x] 7.3 Test: Selecting "Non-Fashion" updates URL with `category=non_fashion`
  - [x] 7.4 Test: Selecting "All" removes `category` from URL
  - [x] 7.5 Test: Category filter combines with search (both params in URL and hook call)
  - [x] 7.6 Test: Category filter persists across sort and date changes

## Dev Notes

### Story Context — Fourth Story of Epic 4 (Evaluation History & Search)

This story adds category filtering (Fashion/Non-Fashion) to the evaluation history page. It extends the conditional WHERE clause pattern established in Stories 4.2 (search) and 4.3 (date range) with one more AND condition for `category`. The router already accepts the `category` param as a forward-compatible no-op — this story wires it through all layers and adds the dropdown UI.

**Cross-story context within Epic 4:**
- Story 4.1 (done): Base list with pagination + sorting + forward-compat params
- Story 4.2 (done): Adds brand name search (ILIKE query with `escape_like()`)
- Story 4.3 (done): Adds date range filter (`date_from`, `date_to`)
- Story 4.4 (this): Adds category filter (fashion/non_fashion)
- Story 4.5: Adds full detail view (click through from list)
- Story 4.6: Adds SSE real-time notifications for new evaluations

**Design decision:** Category filtering is an exact match (`WHERE e.template = $N`) — much simpler than the ILIKE search or date range patterns. No escaping, no boundary handling. The template column in the evaluations table stores 'fashion' or 'non_fashion', which maps directly to the API param values.

### Database — Category WHERE Clause

**Category filtering approach (simple exact match):**

The `evaluations` table stores the template type as `template VARCHAR(20)` with values `'fashion'` or `'non_fashion'`. This is a simple equality filter:

```sql
-- category filter: exact match on template column
WHERE e.template = $N
```

**Extending `_build_filter_clauses()` from Story 4.3:**

The current helper builds WHERE conditionally for search, date_from, and date_to. Add category as another condition:

```python
def _build_filter_clauses(
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    category: str | None = None,  # NEW
) -> tuple[str, list[Any], int]:
    conditions: list[str] = []
    params: list[Any] = []
    param_idx = 1

    if search:
        escaped = escape_like(search)
        conditions.append(f"b.brand_name ILIKE '%' || ${param_idx} || '%' ESCAPE '\\'")
        params.append(escaped)
        param_idx += 1

    if date_from:
        conditions.append(f"e.created_at >= ${param_idx}::date")
        params.append(date_from)
        param_idx += 1

    if date_to:
        conditions.append(f"e.created_at < (${param_idx}::date + interval '1 day')")
        params.append(date_to)
        param_idx += 1

    if category:
        conditions.append(f"e.template = ${param_idx}")
        params.append(category)
        param_idx += 1

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    return where_clause, params, param_idx
```

**Critical:** Count query MUST include the same `category` WHERE clause — otherwise pagination shows wrong total/pages.

### Backend Router — Forward-Compatible Params Already In Place

The router already accepts (line 54 of `router.py`):
```python
# Forward-compat param — accepted but not yet implemented (Story 4.4)
category: Literal["fashion", "non_fashion"] | None = Query(default=None),
```

This is currently accepted but not forwarded to the service. Story 4.4 wires it through. FastAPI's `Literal` type validation means invalid values (anything other than "fashion" or "non_fashion") automatically return 422 — no custom validation needed.

### Frontend — Category Dropdown Component

**shadcn Select is already installed.** Use it directly for the category filter:

```tsx
<Select
  value={categoryFromUrl || 'all'}
  onValueChange={(value) => {
    const newParams = new URLSearchParams(searchParams);
    if (value === 'all') {
      newParams.delete('category');
    } else {
      newParams.set('category', value);
    }
    newParams.set('page', '1');
    setSearchParams(newParams);
  }}
>
  <SelectTrigger className="w-[180px]" aria-label="Filter by category">
    <SelectValue placeholder="All Categories" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="all">All Categories</SelectItem>
    <SelectItem value="fashion">Fashion</SelectItem>
    <SelectItem value="non_fashion">Non-Fashion</SelectItem>
  </SelectContent>
</Select>
```

**URL format:** `?category=fashion` or `?category=non_fashion`. When "All" is selected, the `category` param is removed from the URL entirely.

**Category selection flow:**
1. User selects option from dropdown → `onValueChange` fires
2. Update URL params: `setSearchParams` with `category=fashion` and `page=1` (or remove `category` for "All")
3. Component reads `category` from `searchParams` → passes to `useEvaluationHistory()`
4. Hook builds query key with category → TanStack Query fetches with `?category=fashion`

**No debounce needed** — dropdown selection is a single discrete action.

### Existing Code to Integrate With

**Backend (existing — modify):**
- `modules/evaluations/router.py` — Wire existing `category` param to service call (currently accepted but not passed to service), remove forward-compat comment
- `modules/evaluations/service.py` — Add `category` param to `list_evaluations()` signature, pass to DB queries
- `db/queries/evaluations.py` — Add `category` param to `_build_filter_clauses()`, `list_evaluations()`, and `count_evaluations()`

**Frontend (existing — modify):**
- `hooks/useEvaluationHistory.ts` — Add `category` param to hook, include in query key and API params
- `components/evaluations/EvaluationHistoryTable.tsx` — Add Select dropdown UI, wire to URL params, update empty state message

**No new files or dependencies needed.** All components (shadcn Select) and libraries are already installed from previous stories.

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Category param uses `Literal["fashion", "non_fashion"] | None` type — FastAPI auto-validates, returns 422 for invalid values
- WHERE clause uses exact match `e.template = $N` — parameterized, no string interpolation
- Parameterized SQL with `$1, $2, ...` — category value passed as parameter, never interpolated
- Exception chaining: `raise AppException(...) from e` — preserve tracebacks
- Response schema unchanged — same `EvaluationListResponse` with `items, total, page, limit, pages`
- No ILIKE or `escape_like()` needed — this is exact match, not pattern search

**Frontend Pattern (MUST follow):**
- Hook uses `apiClient.ts` (openapi-fetch) — `category` already defined in API types
- TanStack Query key includes category param: `['evaluations', page, limit, sortBy, sortOrder, search, dateFrom, dateTo, category]`
- `keepPreviousData` for smooth transitions (already from 4.1)
- Error states have visible UI (unchanged from 4.1)
- Use `aria-label="Filter by category"` on Select trigger
- `aria-busy="true"` during loading (handled by existing `isPlaceholderData` logic)
- URL param: `category=fashion` or `category=non_fashion` (remove param when "All")

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| FastAPI | existing | `Literal["fashion", "non_fashion"]` query param validation | Installed |
| asyncpg | existing | Parameterized exact match (`$N`) | Installed |
| pydantic | existing | No schema changes needed | Installed |
| @tanstack/react-query | v5 (existing) | Query key with category param, `keepPreviousData` | Installed |
| openapi-fetch | existing | `category` param already in API types | Installed |
| shadcn/ui Select | existing | Category dropdown | Installed |
| lucide-react | existing | No new icons needed | Installed |

**No new dependencies required.** All libraries are already installed.

### Project Structure Notes

**No new files needed.**

**Existing files to modify:**
```
backend/app/db/queries/evaluations.py          -- Add category param to _build_filter_clauses(), list_evaluations(), count_evaluations()
backend/app/modules/evaluations/service.py     -- Add category param, pass to DB queries
backend/app/modules/evaluations/router.py      -- Wire existing category param to service call, remove forward-compat comment
backend/tests/integration/api/test_evaluation_list.py  -- Add category filter tests
frontend/src/hooks/useEvaluationHistory.ts     -- Add category param to hook + query key
frontend/src/components/evaluations/EvaluationHistoryTable.tsx  -- Add Select dropdown, wire to URL params, update empty state
frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx  -- Add category filter tests
```

**Alignment with unified project structure:**
- Backend follows `modules/{feature}/{router,schemas,service}.py` pattern — no structural changes
- DB queries extend existing `_build_filter_clauses()` helper — adds one more condition
- Frontend modifies existing hook and component — no new custom components needed
- Tests extend existing test files

### Testing Requirements

**Backend Integration Tests (pytest) — extend `tests/integration/api/test_evaluation_list.py`:**

| Test | AC | Description |
|------|-----|-------------|
| `test_filter_by_category_fashion` | #2, #6 | `category=fashion` returns only fashion evaluations |
| `test_filter_by_category_non_fashion` | #3, #6 | `category=non_fashion` returns only non-fashion evaluations |
| `test_filter_no_category_returns_all` | #4, #6 | Omitting `category` returns all evaluations |
| `test_filter_category_combined_with_search` | #5, #6 | Both `search` and `category` apply as AND |
| `test_filter_category_combined_with_date_range` | #5, #6 | Both `category` and `date_from`/`date_to` apply as AND |
| `test_filter_category_combined_with_all_filters` | #5, #6 | `search` + `date_from` + `date_to` + `category` all apply as AND |
| `test_filter_category_with_pagination` | #6 | Category-filtered results have correct total/pages |
| `test_filter_invalid_category_returns_422` | #6 | `category=invalid` returns 422 |

**Frontend Component Tests (vitest) — extend `EvaluationHistoryTable.test.tsx`:**

| Test | AC | Description |
|------|-----|-------------|
| `category dropdown renders with accessible label` | #7 | Select has `aria-label` |
| `selecting Fashion updates URL param and resets page` | #2 | URL includes `?category=fashion&page=1` |
| `selecting Non-Fashion updates URL param` | #3 | URL includes `?category=non_fashion` |
| `selecting All removes category from URL` | #4 | `category` param removed from URL |
| `category filter combines with search in URL` | #5 | Both `search` and `category` present in URL |
| `category filter persists across sort and date changes` | #5 | Changing sort/dates doesn't lose category filter |

**Run commands:**
- Backend: `cd backend && uv run python -m pytest tests/integration/api/test_evaluation_list.py -v`
- Frontend: `cd frontend && npx vitest run --reporter=verbose`

### Previous Story Intelligence

**From Story 4.3 (Filter by Date Range) — Direct predecessor:**

- `_build_filter_clauses()` helper established for conditional WHERE construction (search + date_from + date_to)
- Dynamic parameter numbering: `$1, $2, ...` incremented per active filter
- URL param pattern: read from `searchParams`, pass to hook, hook passes to API
- Filter bar layout: search on left, date pickers on right with flex wrap — category dropdown should fit alongside
- `isPlaceholderData` already provides smooth transitions — works for category filter changes too
- Empty state messages include filter context — extend for category
- **Code review fix M1:** Date validation `date_from <= date_to` added — no equivalent needed for category (single value)
- **Code review fix M2:** `_build_filter_clauses()` has unit tests covering all filter combinations — extend with category combinations
- **Code review fix L1:** Empty state message updated for date context — extend for category context
- All 508 backend + 239 frontend tests pass after Story 4.3 merge

**From Story 4.3 Dev Notes — forward guidance:**
> **Pattern for 4.4:** The conditional WHERE clause pattern will be extended with one more AND condition for `category` (exact match: `WHERE e.template = $N`). The frontend filter bar will gain a dropdown alongside the existing search input and date pickers.

**From Story 4.2 — Conditional WHERE pattern origin:**
> Forward-compat query params accepted in router for Stories 4.2-4.4. The `_escape_like()` helper and dynamic param numbering established here.

**From Lessons Learned:**
- Response schemas must match ACs field-by-field — no schema changes needed here
- File List must include ALL changed files
- Backend tests: `uv run python -m pytest` (not `pytest` directly)
- Frontend tests: `npx vitest run --reporter=verbose`
- ILIKE queries need `escape_like()` + `ESCAPE '\'` — NOT needed for category (exact match)

### Git Intelligence

**Recent commits (Story 4.3 completed and merged):**
```
9f78d84 Merge feature/4-3-filter-by-date-range into develop
11b74cd Fix code review findings: date validation, unit tests, str() removal, UI improvements (Story 4.3)
d33d3a3 Mark Story 4.3 complete — all tasks done, status → review
9f597da Add frontend tests for date range filter (Task 8)
5ae9803 Add frontend date range filter with date pickers (Tasks 5-7)
d5f7316 Add backend date range filtering for evaluations (Tasks 1-4)
```

**Patterns to follow:**
- Feature branch naming: `feature/4-4-filter-by-category`
- Branch created from `develop` (current branch)
- Atomic commits per task group (backend tasks 1-4, frontend tasks 5-7)
- Tests committed alongside implementation

### How This Feeds Into Later Epic 4 Stories

| Story | What 4.4 Provides | What It Adds |
|-------|-------------------|--------------|
| 4.5 (Detail View) | Fully filtered list context (search + date + category) | Detail page, full evaluation display |
| 4.6 (Real-time Notifications) | Filter-aware list with all 3 filter types | SSE event listener, toast notifications |

**Pattern for 4.5:** The detail view will be accessed by clicking a row in the filtered list. The list already returns evaluation `id` — the detail view will fetch by ID. No filter changes needed.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.4 — Story ACs, FR30: filter by category]
- [Source: _bmad-output/planning-artifacts/architecture.md#API-Naming — Query param snake_case: ?category=fashion]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Architecture — asyncpg parameterized SQL, $1 $2 placeholders]
- [Source: _bmad-output/planning-artifacts/architecture.md#Core-Architectural-Decisions — Offset pagination: ?page=1&limit=20]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Journey-2 — Historical Lookup: filter by category]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Component-Strategy — shadcn Select component]
- [Source: _bmad-output/planning-artifacts/prd.md — FR30: BD team member can filter evaluations by category]
- [Source: _bmad-output/implementation-artifacts/4-3-filter-by-date-range.md — _build_filter_clauses pattern, filter bar layout, URL param flow]
- [Source: _bmad-output/implementation-artifacts/4-2-search-by-brand-name.md — Conditional WHERE pattern, escape_like, forward-compat params]
- [Source: _bmad-output/implementation-artifacts/4-1-evaluation-history-list.md — Forward-compat query params, existing table component, hook patterns]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, test commands, response schema validation]
- [Source: backend/app/db/queries/evaluations.py — Existing _build_filter_clauses() with search + date conditions]
- [Source: backend/app/modules/evaluations/router.py — Forward-compat category param (line 54)]
- [Source: backend/app/modules/evaluations/service.py — Existing list_evaluations() service with search + date params]
- [Source: backend/app/modules/evaluations/schemas.py — CategoryType = Literal["fashion", "non_fashion"]]
- [Source: frontend/src/services/apiClient.ts — Forward-compat category in API types (line 233)]
- [Source: frontend/src/hooks/useEvaluationHistory.ts — Existing hook structure, query key pattern]
- [Source: frontend/src/components/evaluations/EvaluationHistoryTable.tsx — Filter bar layout, URL param handling]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

No debug issues encountered — clean implementation.

### Completion Notes List

- **Backend (Tasks 1-3):** Extended `_build_filter_clauses()` with `category` param for exact match `WHERE e.template = $N`. Wired through service layer and router. Removed forward-compat comment from router. All 28 existing backend tests pass + 8 new category tests pass (36 total).
- **Frontend (Tasks 5-6):** Added `category` param to `useEvaluationHistory` hook and TanStack Query key. Added shadcn Select dropdown in filter bar with All/Fashion/Non-Fashion options. Wired to URL params with page reset on change. Updated empty state for category context. Added `aria-label="Filter by category"`.
- **Tests (Tasks 4, 7):** 8 backend integration tests covering fashion/non_fashion filtering, combined filters (search+category, date+category, all filters), pagination, and invalid category 422. 7 frontend component tests covering accessible label, URL param updates, combined filters, persistence across sort/date changes, and empty state messaging.
- All acceptance criteria satisfied. Full regression suite passes (no regressions).

### File List

- `backend/app/db/queries/evaluations.py` — Modified: added `category` param to `_build_filter_clauses()`, `list_evaluations()`, `count_evaluations()`
- `backend/app/modules/evaluations/service.py` — Modified: added `category` param to `list_evaluations()`, passed to DB queries
- `backend/app/modules/evaluations/router.py` — Modified: wired `category` to service call, removed forward-compat comment
- `backend/tests/integration/api/test_evaluation_list.py` — Modified: added 8 category filter integration tests
- `frontend/src/hooks/useEvaluationHistory.ts` — Modified: added `category` param to hook signature, query key, and API params
- `frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — Modified: added Select dropdown UI, `setCategory` callback, URL param handling, empty state message
- `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx` — Modified: added 7 category filter component tests
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Modified: updated story status
- `_bmad-output/implementation-artifacts/4-4-filter-by-category.md` — Modified: task checkboxes, Dev Agent Record, File List, Change Log, Status

### Change Log

- **2026-02-12:** Implemented Story 4.4 — Filter by Category. Added category filtering (fashion/non_fashion) across all backend layers (DB query, service, router) and frontend (hook, dropdown UI, URL params). 15 new tests added (8 backend + 7 frontend). All tests pass.
