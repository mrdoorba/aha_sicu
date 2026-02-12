# Story 4.3: Filter by Date Range

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team leader**,
I want **to filter evaluations by date range**,
so that **I can find evaluations from a specific time period**.

## Acceptance Criteria

1. **Date range filter with From/To date pickers**
   **Given** I am on the History page
   **When** I select a date range using date pickers (From / To)
   **Then** the list filters to evaluations within that date range (inclusive of both dates)
   **And** pagination resets to page 1 on filter change
   **And** the selected dates are reflected in the URL query params (`?date_from=2026-01-01&date_to=2026-01-31`)

2. **From-only filter**
   **Given** I select only a "From" date
   **When** filtering
   **Then** show evaluations from that date onwards (no upper bound)
   **And** the `date_to` picker remains empty

3. **To-only filter**
   **Given** I select only a "To" date
   **When** filtering
   **Then** show evaluations up to and including that date (no lower bound)
   **And** the `date_from` picker remains empty

4. **Date filter combines with existing search**
   **Given** I have an active search term AND a date range
   **When** the list loads
   **Then** both filters apply (AND logic) — only evaluations matching the brand name AND within the date range
   **And** total count and pages reflect the combined filter

5. **Clearing date filters restores list**
   **Given** I have active date filters
   **When** I clear a date picker (via clear button or deleting the value)
   **Then** that date filter is removed
   **And** pagination resets to page 1
   **And** the corresponding URL param is removed

6. **Backend date filter endpoint**
   **Given** I call `GET /api/v1/evaluations?date_from=2026-01-01&date_to=2026-01-31`
   **When** authenticated
   **Then** return paginated evaluations where `evaluations.created_at` falls within the date range (inclusive of both boundary dates)
   **And** `date_from` without `date_to` filters from that date onwards
   **And** `date_to` without `date_from` filters up to and including that date
   **And** both params omitted returns all evaluations (no date filter)
   **And** invalid date formats return 422 Unprocessable Entity

7. **Date pickers have accessible labels**
   **Given** the date picker inputs on the History page
   **When** a screen reader focuses either picker
   **Then** the "From" picker announces "Filter from date"
   **And** the "To" picker announces "Filter to date"

8. **Loading state during date filter**
   **Given** I change a date filter value
   **When** the API request is in progress
   **Then** the table shows a subtle loading indicator (opacity reduction via `isPlaceholderData`)
   **And** the table container has `aria-busy="true"` (existing behavior)

## Tasks / Subtasks

- [x] Task 1: Add date filtering to backend DB queries (AC: #6)
  - [x] 1.1 Modify `list_evaluations()` in `db/queries/evaluations.py` to accept optional `date_from: date | None` and `date_to: date | None` params
  - [x] 1.2 Add conditional WHERE clauses: `e.created_at >= $N` for date_from, `e.created_at < ($N::date + interval '1 day')` for date_to — preserves index usage on `idx_evaluations_created_at`
  - [x] 1.3 Modify `count_evaluations()` to accept same date params and apply same WHERE clauses
  - [x] 1.4 Dynamic parameter numbering: extend the existing pattern from search (build params list conditionally, increment $N for each active filter)

- [x] Task 2: Wire date filtering through backend service layer (AC: #6)
  - [x] 2.1 Add `date_from: date | None = None` and `date_to: date | None = None` params to `list_evaluations()` in `service.py`
  - [x] 2.2 Pass `date_from` and `date_to` to both `eval_queries.list_evaluations()` and `eval_queries.count_evaluations()`

- [x] Task 3: Wire date filtering in backend router (AC: #6)
  - [x] 3.1 Pass `date_from` and `date_to` params from router to `list_evaluations()` service call (currently accepted but not forwarded — lines 51-52 of router.py)
  - [x] 3.2 Remove forward-compat comment for date filtering now that it's implemented

- [x] Task 4: Write backend tests (AC: #1, #2, #3, #4, #6)
  - [x] 4.1 Integration test: `GET /evaluations?date_from=2026-01-01&date_to=2026-01-31` returns only evaluations within range
  - [x] 4.2 Integration test: `date_from` only — returns evaluations from that date onwards
  - [x] 4.3 Integration test: `date_to` only — returns evaluations up to and including that date
  - [x] 4.4 Integration test: `date_to` is inclusive of the entire day (evaluation created at 23:59 on date_to day is included)
  - [x] 4.5 Integration test: Date filter combined with search — both filters apply (AND logic)
  - [x] 4.6 Integration test: No date params returns all evaluations (existing behavior preserved)
  - [x] 4.7 Integration test: Invalid date format returns 422
  - [x] 4.8 Integration test: Date filter with pagination — total/pages reflect filtered count

- [x] Task 5: Install date picker dependencies (AC: #1)
  - [x] 5.1 Install shadcn/ui `calendar` and `popover` components: `npx shadcn@latest add calendar popover`
  - [x] 5.2 Verify `react-day-picker` and `date-fns` are added as dependencies (shadcn calendar depends on them)

- [x] Task 6: Add date filter params to frontend hook (AC: #1, #4)
  - [x] 6.1 Add `dateFrom?: string` and `dateTo?: string` params to `useEvaluationHistory()` hook signature
  - [x] 6.2 Include `date_from` and `date_to` in API query params sent to backend (conditional — only when values present)
  - [x] 6.3 Include `dateFrom` and `dateTo` in TanStack Query key: `['evaluations', page, limit, sortBy, sortOrder, search, dateFrom, dateTo]`

- [x] Task 7: Add date picker UI to EvaluationHistoryTable (AC: #1, #2, #3, #5, #7, #8)
  - [x] 7.1 Create a `DateRangeFilter` inline component (or section) with two date pickers: "From" and "To"
  - [x] 7.2 Use shadcn `Popover` + `Calendar` for each date picker — single date selection mode
  - [x] 7.3 Display selected date in the trigger button (format: "Jan 1, 2026" or placeholder "From date" / "To date")
  - [x] 7.4 Add clear button (X icon) on each date picker when a date is selected, with `aria-label="Clear from date"` / `"Clear to date"`
  - [x] 7.5 Wire date selection to URL params: `date_from` and `date_to` in `YYYY-MM-DD` format
  - [x] 7.6 Reset page to 1 when date filter changes
  - [x] 7.7 Place date filter row between search input and table (search on left, date filters on right — or both in a filter bar)
  - [x] 7.8 Add `aria-label` on picker triggers: "Filter from date" and "Filter to date"

- [x] Task 8: Write frontend tests (AC: #1, #2, #3, #4, #5, #7)
  - [x] 8.1 Test: Date pickers render with accessible labels
  - [x] 8.2 Test: Selecting a from-date updates URL with `date_from` param and resets page to 1
  - [x] 8.3 Test: Selecting a to-date updates URL with `date_to` param
  - [x] 8.4 Test: Clearing a date picker removes the corresponding URL param
  - [x] 8.5 Test: Date filter combines with search (both params in URL and hook call)
  - [x] 8.6 Test: Date filter persists across sort changes

## Dev Notes

### Story Context — Third Story of Epic 4 (Evaluation History & Search)

This story adds date range filtering to the evaluation history page. It extends the conditional WHERE clause pattern established in Story 4.2 (search) with additional AND conditions for `date_from` and `date_to`. The router already accepts these params as forward-compatible no-ops — this story wires them through all layers and adds the date picker UI.

**Cross-story context within Epic 4:**
- Story 4.1 (done): Base list with pagination + sorting + forward-compat params
- Story 4.2 (done): Adds brand name search (ILIKE query with `escape_like()`)
- Story 4.3 (this): Adds date range filter (`date_from`, `date_to`)
- Story 4.4: Adds category filter (fashion/non_fashion)
- Story 4.5: Adds full detail view (click through from list)
- Story 4.6: Adds SSE real-time notifications for new evaluations

**Design decision:** Date filtering is server-side (WHERE clause on `created_at`) for consistency with the search pattern and because the dataset can exceed a single page. Both filters combine with AND logic.

### Database — Date Range WHERE Clause

**Date filtering approach (index-friendly):**

The `evaluations` table has `idx_evaluations_created_at DESC` index on the `created_at TIMESTAMPTZ` column. To preserve index usage, filter on the column directly without casting:

```sql
-- date_from: include evaluations created on or after this date
WHERE e.created_at >= $N::date

-- date_to: include evaluations created on or before this date (entire day)
WHERE e.created_at < ($N::date + interval '1 day')
```

The `::date` cast on the parameter (not the column) tells PostgreSQL to convert the date string to a date, which auto-promotes to `timestamptz` at midnight. The `+ interval '1 day'` for `date_to` ensures the entire day is included (up to but not including midnight of the next day).

**Extending conditional WHERE from Story 4.2:**

The current `list_evaluations()` builds WHERE conditionally for search. Extend with date conditions:

```python
conditions = []
params = []
param_idx = 1

if search:
    escaped = escape_like(search)
    conditions.append(f"b.brand_name ILIKE '%' || ${param_idx} || '%' ESCAPE '\\'")
    params.append(escaped)
    param_idx += 1

if date_from:
    conditions.append(f"e.created_at >= ${param_idx}::date")
    params.append(str(date_from))
    param_idx += 1

if date_to:
    conditions.append(f"e.created_at < (${param_idx}::date + interval '1 day')")
    params.append(str(date_to))
    param_idx += 1

where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

# Pagination params
params.extend([limit, offset])
limit_param = f"${param_idx}"
offset_param = f"${param_idx + 1}"
```

**Critical:** Count query MUST include the same WHERE clauses — otherwise pagination shows wrong total/pages.

### Backend Router — Forward-Compatible Params Already In Place

The router (lines 51-52 of `router.py`) already accepts:
```python
date_from: date | None = Query(default=None),
date_to: date | None = Query(default=None),
```

These are currently accepted but not forwarded to the service. Story 4.3 wires them through. FastAPI auto-validates the `date` type — invalid formats return 422 automatically.

**Note:** The params use Python's `datetime.date` type. FastAPI parses `YYYY-MM-DD` format strings to `date` objects automatically.

### Frontend — Date Picker Components

**No date picker is currently installed.** Need to add:

1. **shadcn Calendar component** — uses `react-day-picker` under the hood
2. **shadcn Popover component** — for dropdown trigger
3. These bring `react-day-picker` and `date-fns` as transitive dependencies

**Install command:**
```bash
cd frontend && npx shadcn@latest add calendar popover
```

**Date picker pattern (shadcn/ui):**
```tsx
<Popover>
  <PopoverTrigger asChild>
    <Button variant="outline" className={cn("w-[200px] justify-start text-left font-normal", !date && "text-muted-foreground")}>
      <CalendarIcon className="mr-2 h-4 w-4" />
      {date ? format(date, "PPP") : <span>Pick a date</span>}
    </Button>
  </PopoverTrigger>
  <PopoverContent className="w-auto p-0">
    <Calendar mode="single" selected={date} onSelect={setDate} initialFocus />
  </PopoverContent>
</Popover>
```

**URL format:** Dates stored in URL as `YYYY-MM-DD` strings (ISO 8601 date format). Parse with `new Date(dateString)` or `date-fns` `parseISO()` for the Calendar component, format back to `YYYY-MM-DD` with `format(date, 'yyyy-MM-dd')` from `date-fns`.

**Date selection flow:**
1. User clicks date picker trigger → Popover opens with Calendar
2. User selects a date → `onSelect` fires
3. Update URL params: `setSearchParams` with `date_from=YYYY-MM-DD` and `page=1`
4. Component reads `date_from` from `searchParams` → passes to `useEvaluationHistory()`
5. Hook builds query key with dateFrom → TanStack Query fetches with `?date_from=YYYY-MM-DD`

**No debounce needed** for date pickers — unlike text input, date selection is a single discrete action (click on a day).

### Existing Code to Integrate With

**Backend (existing — modify):**
- `modules/evaluations/router.py` — Wire `date_from` and `date_to` params to service call (currently accepted but not passed to service)
- `modules/evaluations/service.py` — Add `date_from` and `date_to` params to `list_evaluations()` signature, pass to DB queries
- `db/queries/evaluations.py` — Add WHERE clauses to `list_evaluations()` and `count_evaluations()` for date range filtering

**Frontend (existing — modify):**
- `hooks/useEvaluationHistory.ts` — Add `dateFrom` and `dateTo` params to hook, include in query key and API params
- `components/evaluations/EvaluationHistoryTable.tsx` — Add date picker UI, wire to URL params
- `services/apiClient.ts` — `date_from` and `date_to` already defined in API types (forward-compat from 4.1)

**Frontend (new files via shadcn install):**
- `components/ui/calendar.tsx` — shadcn Calendar component (auto-generated)
- `components/ui/popover.tsx` — shadcn Popover component (auto-generated)

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Date params use Python `datetime.date` type — FastAPI auto-validates `YYYY-MM-DD` format, returns 422 for invalid
- WHERE clause on `created_at` column directly (not `::date` cast on column) — preserves `idx_evaluations_created_at` index
- `date_to` uses `< ($N::date + interval '1 day')` — includes entire day boundary
- Parameterized SQL with `$1, $2, ...` — date values passed as parameters, never interpolated
- Exception chaining: `raise AppException(...) from e` — preserve tracebacks
- Response schema unchanged — same `EvaluationListResponse` with `items, total, page, limit, pages`

**Frontend Pattern (MUST follow):**
- Hook uses `apiClient.ts` (openapi-fetch) — `date_from` and `date_to` already in API types
- TanStack Query key includes date params: `['evaluations', page, limit, sortBy, sortOrder, search, dateFrom, dateTo]`
- `keepPreviousData` for smooth transitions (already from 4.1)
- Error states have visible UI (unchanged from 4.1)
- Use `aria-label` on date picker triggers
- `aria-busy="true"` during loading (handled by existing `isPlaceholderData` logic)
- Date format in URL: `YYYY-MM-DD` (ISO 8601)
- Date display in picker trigger: localized (e.g., "Jan 1, 2026") using `date-fns` `format()`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| FastAPI | existing | Query params with `date` type (auto-validates YYYY-MM-DD) | Installed |
| asyncpg | existing | Parameterized date comparison (`$N::date`) | Installed |
| pydantic | existing | No schema changes needed | Installed |
| @tanstack/react-query | v5 (existing) | Query key with date params, `keepPreviousData` | Installed |
| openapi-fetch | existing | `date_from` / `date_to` params already in API types | Installed |
| shadcn/ui Calendar | — | Date selection UI | **NEEDS INSTALL** |
| shadcn/ui Popover | — | Date picker dropdown container | **NEEDS INSTALL** |
| react-day-picker | — | Calendar rendering engine (shadcn dependency) | **NEEDS INSTALL** (via shadcn) |
| date-fns | — | Date formatting (`format()`, `parseISO()`) | **NEEDS INSTALL** (via shadcn) |
| lucide-react | existing | `CalendarIcon`, `X` icons | Installed |

**New dependencies:** `react-day-picker` and `date-fns` will be added automatically when installing shadcn Calendar component.

### Project Structure Notes

**New files (auto-generated by shadcn):**
```
frontend/src/components/ui/calendar.tsx    ← shadcn Calendar component
frontend/src/components/ui/popover.tsx     ← shadcn Popover component
```

**Existing files to modify:**
```
backend/app/db/queries/evaluations.py          -- Add date WHERE clauses to list/count queries
backend/app/modules/evaluations/service.py     -- Add date_from, date_to params, pass to queries
backend/app/modules/evaluations/router.py      -- Wire date params to service call, remove forward-compat comment
backend/tests/integration/api/test_evaluation_list.py  -- Add date filter tests
frontend/src/hooks/useEvaluationHistory.ts     -- Add dateFrom, dateTo params to hook + query key
frontend/src/components/evaluations/EvaluationHistoryTable.tsx  -- Add date picker UI, wire to URL params
frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx  -- Add date filter tests
```

**Alignment with unified project structure:**
- Backend follows `modules/{feature}/{router,schemas,service}.py` pattern — no structural changes
- DB queries extend existing file — adds date WHERE clause logic
- Frontend modifies existing hook and component — no new custom directories
- shadcn components installed into standard `components/ui/` directory
- Tests extend existing test files

### Testing Requirements

**Backend Integration Tests (pytest) — extend `tests/integration/api/test_evaluation_list.py`:**

| Test | AC | Description |
|------|-----|-------------|
| `test_filter_by_date_range` | #1, #6 | `date_from=2026-01-01&date_to=2026-01-31` returns only evaluations within range |
| `test_filter_date_from_only` | #2, #6 | `date_from=2026-01-15` returns evaluations from that date onwards |
| `test_filter_date_to_only` | #3, #6 | `date_to=2026-01-15` returns evaluations up to and including that date |
| `test_filter_date_to_inclusive_end_of_day` | #6 | Evaluation created at 23:59 on `date_to` day is included |
| `test_filter_date_combined_with_search` | #4, #6 | Both `search` and `date_from`/`date_to` apply as AND |
| `test_filter_no_dates_returns_all` | #6 | Omitting both date params returns all evaluations |
| `test_filter_invalid_date_returns_422` | #6 | `date_from=not-a-date` returns 422 |
| `test_filter_date_with_pagination` | #1, #6 | Date-filtered results have correct total/pages |

**Frontend Component Tests (vitest) — extend `EvaluationHistoryTable.test.tsx`:**

| Test | AC | Description |
|------|-----|-------------|
| `date pickers render with accessible labels` | #7 | Both pickers have `aria-label` |
| `selecting from-date updates URL param and resets page` | #1 | URL includes `?date_from=2026-01-01&page=1` |
| `selecting to-date updates URL param` | #1 | URL includes `?date_to=2026-01-31` |
| `clearing date picker removes URL param` | #5 | Clicking clear removes `date_from` or `date_to` from URL |
| `date filter combines with search in URL` | #4 | Both `search` and `date_from` present in URL |
| `date filter persists across sort changes` | #4 | Changing sort doesn't lose date filter |

**Run commands:**
- Backend: `cd backend && uv run python -m pytest tests/integration/api/test_evaluation_list.py -v`
- Frontend: `cd frontend && npx vitest run --reporter=verbose`

### Previous Story Intelligence

**From Story 4.2 (Search by Brand Name) — Direct predecessor:**

- Forward-compat `date_from` and `date_to` params already in router (accepted but not forwarded to service)
- Conditional WHERE clause pattern established: search present → add `WHERE b.brand_name ILIKE ...`, absent → skip
- Dynamic parameter numbering: `$1` for search (when present), then `$2/$3` for limit/offset — extend with `$N` for date params
- `useSearchParams` pattern for URL state management — same approach for date params
- `SearchInput` component placed above table — date pickers should be placed alongside in a filter bar
- `isPlaceholderData` already provides smooth transitions — works for date filter changes too
- Shared `escape_like()` in `db/queries/utils.py` — not needed for date filtering, but shows refactoring pattern
- **Code review fix H1:** Debounce `useEffect` initial mount skip with `useRef(true)` — not needed for date pickers (no debounce) but pattern available if needed
- **Code review fix M3:** `aria-busy` on input was semantically incorrect, only on results container — don't add `aria-busy` to date pickers

**From Story 4.2 Dev Notes — forward guidance:**
> **Pattern for 4.3/4.4:** The conditional WHERE clause pattern established in this story (search present → add clause, absent → skip) will be extended with additional AND conditions for date and category filters.

**From Story 4.1 — design for forward compatibility:**
> The `GET /api/v1/evaluations` endpoint should accept optional `search`, `date_from`, `date_to`, `category` query params even if not implemented yet.

This was implemented. Story 4.3 now wires the `date_from` and `date_to` params through all layers.

**From Lessons Learned:**
- Response schemas must match ACs field-by-field — no schema changes needed here
- File List must include ALL changed files
- Backend tests: `uv run python -m pytest` (not `pytest` directly)
- Frontend tests: `npx vitest run --reporter=verbose`

### Git Intelligence

**Recent commits (Story 4.2 completed and merged):**
```
441ba8d Merge feature/4-2-search-by-brand-name into develop
11872d0 Fix code review findings: shared escape_like, debounce skip, query tests, aria-busy (Story 4.2)
c52d3e2 Mark Story 4.2 complete — all tasks done, status → review
85279af Add frontend search input with debounce, URL sync, and tests (Tasks 5-7)
ccfcde3 Add backend search filtering for evaluations by brand name (Tasks 1-4)
```

**Patterns to follow:**
- Feature branch naming: `feature/4-3-filter-by-date-range`
- Branch created from `develop` (current branch)
- Atomic commits per task
- Tests committed alongside implementation

### How This Feeds Into Later Epic 4 Stories

| Story | What 4.3 Provides | What It Adds |
|-------|-------------------|--------------|
| 4.4 (Filter by Category) | Date + search filter pattern, multi-condition WHERE | `category` param, dropdown filter UI |
| 4.5 (Detail View) | Filtered list context | Detail page, full evaluation display |
| 4.6 (Real-time Notifications) | Filter-aware list | SSE event listener, toast notifications |

**Pattern for 4.4:** The conditional WHERE clause pattern will be extended with one more AND condition for `category` (exact match: `WHERE e.template = $N`). The frontend filter bar will gain a dropdown alongside the existing search input and date pickers.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.3 — Story ACs, FR29: filter by date range]
- [Source: _bmad-output/planning-artifacts/architecture.md#API-Naming — Query param snake_case: ?date_from=YYYY-MM-DD]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Architecture — asyncpg parameterized SQL, $1 $2 placeholders]
- [Source: _bmad-output/planning-artifacts/architecture.md#Core-Architectural-Decisions — Offset pagination: ?page=1&limit=20]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Journey-2 — Historical Lookup: filter by date range]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Feedback-Patterns — Loading states, empty states]
- [Source: _bmad-output/planning-artifacts/prd.md — FR29: BD team member can filter evaluations by date range]
- [Source: _bmad-output/implementation-artifacts/4-2-search-by-brand-name.md — Conditional WHERE pattern, URL param flow, forward-compat date params]
- [Source: _bmad-output/implementation-artifacts/4-1-evaluation-history-list.md — Forward-compat query params, existing table component, hook patterns]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, test commands, response schema validation]
- [Source: backend/app/db/queries/evaluations.py — Existing list_evaluations() and count_evaluations() with search WHERE clause]
- [Source: backend/app/modules/evaluations/router.py — Forward-compat date_from/date_to params (lines 51-52)]
- [Source: backend/app/modules/evaluations/service.py — Existing list_evaluations() service with search param]
- [Source: frontend/src/services/apiClient.ts — Forward-compat date_from/date_to in API types (lines 224-234)]
- [Source: frontend/src/hooks/useEvaluationHistory.ts — Existing hook structure, query key pattern]
- [Source: frontend/src/components/evaluations/EvaluationHistoryTable.tsx — SearchInput pattern, useSearchParams flow]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

No issues encountered during implementation.

### Completion Notes List

- Refactored DB queries to use shared `_build_filter_clauses()` helper for conditional WHERE clause construction (search + date_from + date_to with dynamic $N param numbering)
- Router `date_from`/`date_to` params (already `date | None` from Story 4.1) now wired through to service and DB queries — FastAPI auto-validates YYYY-MM-DD format and returns 422 for invalid dates
- `date_to` uses `< ($N::date + interval '1 day')` pattern for inclusive end-of-day boundary (23:59 on date_to day is included)
- `count_evaluations()` now uses the same shared WHERE builder — ensures pagination totals match filtered results
- Installed shadcn Calendar + Popover components bringing `react-day-picker` v9 and `date-fns` v4
- Created `DatePickerField` component with Popover+Calendar, clear button, and accessible aria-labels
- Date selection is discrete (no debounce needed unlike search text input)
- Date pickers placed in a filter bar alongside SearchInput for cohesive filter UX
- All date params persist across sort/page changes via URL search params

### File List

**Modified:**
- backend/app/db/queries/evaluations.py — Added `_build_filter_clauses()`, `date_from`/`date_to` params to `list_evaluations()` and `count_evaluations()`
- backend/app/modules/evaluations/service.py — Added `date_from`/`date_to` params, passes to DB queries
- backend/app/modules/evaluations/router.py — Wired existing `date_from`/`date_to` params to service call
- backend/tests/integration/api/test_evaluation_list.py — Added 11 date filter integration tests (8 original + 3 review fixes)
- backend/tests/unit/test_evaluation_queries.py — Added 7 unit tests for `_build_filter_clauses()`
- frontend/package.json — Added `react-day-picker`, `date-fns` dependencies
- frontend/package-lock.json — Updated lockfile
- frontend/src/hooks/useEvaluationHistory.ts — Added `dateFrom`/`dateTo` params, query key, API params
- frontend/src/components/evaluations/EvaluationHistoryTable.tsx — Added DatePickerField, filter bar, date URL param handling
- frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx — Added 8 date filter tests (6 original + 1 empty state + 1 review fix)
- frontend/src/components/ui/button.tsx — Updated by shadcn install

**New:**
- frontend/src/components/ui/calendar.tsx — shadcn Calendar component
- frontend/src/components/ui/popover.tsx — shadcn Popover component

### Senior Developer Review (AI)

**Reviewed by:** Mr. Door on 2026-02-12
**Outcome:** Changes Requested → All Fixed

**Issues Found:** 0 Critical, 5 Medium, 4 Low — all resolved

| ID | Severity | Description | Resolution |
|----|----------|-------------|------------|
| M1 | Medium | No `date_from <= date_to` validation | Added 422 validation in service.py + disabled invalid dates in Calendar UI |
| M2 | Medium | `_build_filter_clauses()` has no direct unit tests | Added 7 unit tests covering all filter combinations and param ordering |
| M3 | Medium | Unnecessary `str()` conversion of date params | Removed `str()` wrappers, pass `date` objects directly to asyncpg |
| M4 | Medium | Sprint status stale: 4-2 still `review` instead of `done` | Updated sprint-status.yaml |
| M5 | Medium | Combined filter param ordering not verified in tests | Added param order assertions to integration test |
| L1 | Low | Empty state message ignores date filter context | Added contextual "No evaluations found for the selected date range" |
| L2 | Low | Invalid `date_to` not tested | Added `test_filter_invalid_date_to_returns_422` |
| L3 | Low | Brittle index-based calendar test selectors | Changed to ordinal-suffix patterns (`/15th/`, `/18th/`) |
| L4 | Low | Dev Agent Record contradictory type change claim | Fixed completion notes to reflect params were already `date | None` |

### Change Log

- 2026-02-12: Implemented Story 4.3 — Date range filtering for evaluation history. Backend: shared WHERE clause builder with date_from/date_to conditions, wired through DB → service → router. Frontend: shadcn Calendar+Popover date pickers in filter bar, URL param sync, 8 backend + 6 frontend tests added. All 499 backend + 238 frontend tests pass.
- 2026-02-12: Code review fixes — 5 Medium + 4 Low issues resolved. Added date range validation (backend 422 + frontend Calendar disabled dates), 7 unit tests for `_build_filter_clauses()`, removed unnecessary `str()` date conversion, fixed sprint status for 4.2, improved empty state messaging, fixed brittle test selectors, added param ordering verification. All 508 backend + 239 frontend tests pass.
