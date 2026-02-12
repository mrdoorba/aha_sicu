# Story 4.2: Search by Brand Name

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team leader**,
I want **to search evaluations by brand name**,
so that **I can quickly find a specific brand's evaluation history**.

## Acceptance Criteria

1. **Search input filters evaluation list by brand name**
   **Given** I am on the History page
   **When** I type in the search box (e.g., "Nike")
   **Then** the list filters to evaluations where brand name (from `brand_vp_data`) contains the search term (case-insensitive)
   **And** partial matches work (e.g., "Nik" matches "Nike")
   **And** pagination resets to page 1 on new search
   **And** the search term is reflected in the URL query params (`?search=Nike`)

2. **Empty search results show contextual message**
   **Given** no results match my search
   **When** viewing the list
   **Then** I see "No evaluations found for '[search term]'" (showing the actual search term)

3. **Search works with sorting and pagination**
   **Given** I have searched for a brand name
   **When** I change sort order or navigate pages
   **Then** the search filter remains applied
   **And** total count and pages reflect only matching results

4. **Clearing search restores full list**
   **Given** I have an active search filter
   **When** I clear the search input (clear button or empty the field)
   **Then** the full evaluation list is restored
   **And** pagination resets to page 1

5. **Backend search endpoint**
   **Given** I call `GET /api/v1/evaluations?search=Nike`
   **When** authenticated
   **Then** return paginated evaluations where `brand_vp_data.brand_name` contains "Nike" (case-insensitive partial match via ILIKE)
   **And** total count reflects only matching results
   **And** empty search string or omitted `search` param returns all evaluations
   **And** special characters (`%`, `_`, `\`) in search term are escaped safely

6. **Search input has accessible label and clear affordance**
   **Given** the search input on the History page
   **When** a screen reader focuses the input
   **Then** it announces a descriptive label (e.g., "Search evaluations by brand name")
   **And** the clear button (if visible) has an `aria-label`

7. **Loading state during search**
   **Given** I type a search term
   **When** the API request is in progress
   **Then** the table shows a subtle loading indicator (opacity reduction via `isPlaceholderData`)
   **And** the table container has `aria-busy="true"`

## Tasks / Subtasks

- [x] Task 1: Add search filtering to backend DB queries (AC: #5)
  - [x] 1.1 Import or create `_escape_like()` helper in `db/queries/evaluations.py` — reuse from `db/queries/brands.py` or extract to shared module
  - [x] 1.2 Modify `list_evaluations()` to accept optional `search` param and add `WHERE b.brand_name ILIKE '%' || $N || '%' ESCAPE '\'` clause when search is provided
  - [x] 1.3 Modify `count_evaluations()` to accept optional `search` param and apply same WHERE clause for accurate total count
  - [x] 1.4 Ensure parameterized SQL (`$1, $2, ...`) — search term passed as parameter, never interpolated

- [x] Task 2: Wire search through backend service layer (AC: #5)
  - [x] 2.1 Add `search: str | None = None` param to `list_evaluations()` in `service.py`
  - [x] 2.2 Pass `search` to both `eval_queries.list_evaluations()` and `eval_queries.count_evaluations()`
  - [x] 2.3 Apply `_escape_like()` to search term before passing to DB query (escape at service or query level)

- [x] Task 3: Wire search in backend router (AC: #5)
  - [x] 3.1 Pass `search` param from router to `list_evaluations()` service call (currently accepted but not forwarded)
  - [x] 3.2 Remove forward-compat comment now that search is implemented

- [x] Task 4: Write backend tests (AC: #1, #2, #3, #5)
  - [x] 4.1 Integration test: `GET /evaluations?search=Nike` returns only matching evaluations
  - [x] 4.2 Integration test: Partial match — `search=Nik` matches "Nike"
  - [x] 4.3 Integration test: Case-insensitive — `search=nike` matches "Nike"
  - [x] 4.4 Integration test: No matches — returns `{ items: [], total: 0, pages: 0 }`
  - [x] 4.5 Integration test: Search with pagination — total/pages reflect filtered count
  - [x] 4.6 Integration test: Search with sorting — sort applies within filtered results
  - [x] 4.7 Integration test: Special characters escaped — `search=brand%test` doesn't break query
  - [x] 4.8 Integration test: Empty/omitted search returns all evaluations

- [x] Task 5: Add search param to frontend hook (AC: #1, #3)
  - [x] 5.1 Add `search?: string` param to `useEvaluationHistory()` hook signature
  - [x] 5.2 Include `search` in API query params sent to backend
  - [x] 5.3 Include `search` in TanStack Query key for proper cache management: `['evaluations', page, limit, sortBy, sortOrder, search]`

- [x] Task 6: Add search input UI to EvaluationHistoryTable (AC: #1, #2, #4, #6, #7)
  - [x] 6.1 Add search input field above the table with `aria-label="Search evaluations by brand name"` and placeholder text "Search by brand name..."
  - [x] 6.2 Add clear button (X icon) visible when search has text, with `aria-label="Clear search"`
  - [x] 6.3 Wire search input to URL search params via `setSearchParams()` — sync `search` param to URL
  - [x] 6.4 Add debounce (300ms) to avoid excessive API calls on each keystroke
  - [x] 6.5 Reset page to 1 when search changes
  - [x] 6.6 Update empty state message: show "No evaluations found for '[term]'" when search is active vs "No evaluations found" when no search
  - [x] 6.7 Ensure `aria-busy="true"` during search API calls (already handled by `isPlaceholderData` logic from Story 4.1)

- [x] Task 7: Write frontend tests (AC: #1, #2, #3, #4, #6)
  - [x] 7.1 Test: Search input renders with accessible label
  - [x] 7.2 Test: Typing in search triggers API call with search param
  - [x] 7.3 Test: Search updates URL query params
  - [x] 7.4 Test: Clear button clears search and resets page
  - [x] 7.5 Test: Empty search results show contextual message with search term
  - [x] 7.6 Test: Search persists across sort changes

## Dev Notes

### Story Context — Second Story of Epic 4 (Evaluation History & Search)

This story adds brand name search to the evaluation history page built in Story 4.1. The search is server-side (ILIKE query) because the full dataset may exceed a single page. Story 4.1 already added forward-compatible `search` params at all layers (router, apiClient types, URL params), so this story primarily wires them through and adds the search UI.

**Cross-story context within Epic 4:**
- Story 4.1 (done): Base list with pagination + sorting + forward-compat params
- Story 4.2 (this): Adds brand name search (ILIKE query with `_escape_like()`)
- Story 4.3: Adds date range filter (`date_from`, `date_to`)
- Story 4.4: Adds category filter (fashion/non_fashion)
- Story 4.5: Adds full detail view (click through from list)
- Story 4.6: Adds SSE real-time notifications for new evaluations

**Design decision:** Search is server-side via ILIKE query, not client-side filtering, because:
1. Dataset can exceed page size (20 items) — client-side would only search current page
2. Backend already has the JOIN to `brand_vp_data` for brand names
3. Consistent with architecture pattern (server-side filtering via query params)

### Database — ILIKE Search Pattern

**Existing pattern from `brands.py`:**
```python
def _escape_like(term: str) -> str:
    """Escape special LIKE/ILIKE pattern characters."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
```

**Search query modification:**
```sql
SELECT e.id, b.brand_name, e.final_score, e.verdict, e.template,
       u.email AS evaluator_email, e.created_at
FROM evaluations e
JOIN brand_vp_data b ON e.brand_id = b.id
JOIN users u ON e.user_id = u.id
WHERE b.brand_name ILIKE '%' || $1 || '%' ESCAPE '\'
ORDER BY e.{sort_by} {sort_order}
LIMIT $2 OFFSET $3
```

**Critical rules (from lessons-learned.md):**
- ILIKE queries MUST include `ESCAPE '\'` clause — the escape helper is useless without it
- Search term passed as `$1` parameter — never f-string or string concatenation for user input
- `_escape_like()` applied BEFORE passing to query — escapes `%`, `_`, `\` characters
- Parameter numbering shifts when search is added ($1 for search, $2 for limit, $3 for offset)

**When search is None/empty:** Skip the WHERE clause entirely (return all results). Use conditional query building:
```python
if search:
    escaped = _escape_like(search)
    where_clause = "WHERE b.brand_name ILIKE '%' || $1 || '%' ESCAPE '\\'"
    params = [escaped, limit, offset]
else:
    where_clause = ""
    params = [limit, offset]
```

**Count query must also include the WHERE clause** when search is active — otherwise pagination shows wrong total/pages.

### Frontend — Search Input with Debounce

**Search UX pattern:**
- Input field above the table
- Debounce 300ms to avoid excessive API calls
- Clear button (X icon) visible when text is present
- Page resets to 1 on search change
- Search term synced to URL params (`?search=Nike&page=1`)

**Debounce implementation options:**
1. **`useDeferredValue`** (React 18+) — built-in, but defers rendering, not API calls
2. **Custom `useDebounce` hook** — simple setTimeout/clearTimeout pattern
3. **Controlled input + debounced URL update** — input shows immediate typing, URL/API call debounced

**Recommended approach:** Use a local state for immediate input display + debounced `setSearchParams()` update. This gives instant typing feedback while throttling API calls:

```typescript
const [searchInput, setSearchInput] = useState(searchParams.get('search') ?? '');

// Debounce: update URL params after 300ms idle
useEffect(() => {
  const timer = setTimeout(() => {
    const newParams = new URLSearchParams(searchParams);
    if (searchInput) {
      newParams.set('search', searchInput);
    } else {
      newParams.delete('search');
    }
    newParams.set('page', '1'); // Reset page on search
    setSearchParams(newParams, { replace: true });
  }, 300);
  return () => clearTimeout(timer);
}, [searchInput]);
```

**URL param flow:**
1. User types → `searchInput` state updates immediately (responsive UI)
2. After 300ms idle → `setSearchParams()` updates URL with `search=term&page=1`
3. Component reads `search` from `searchParams` → passes to `useEvaluationHistory()`
4. Hook builds query key with search → TanStack Query fetches with `?search=term`

**Empty state message:**
```typescript
// When search is active and no results:
"No evaluations found for '{searchTerm}'"

// When no search and no results:
"No evaluations found"
```

### Existing Code to Integrate With

**Backend (existing — modify):**
- `modules/evaluations/router.py` — Wire `search` param to service call (currently accepted but not passed)
- `modules/evaluations/service.py` — Add `search` param to `list_evaluations()` signature, pass to DB queries
- `db/queries/evaluations.py` — Add WHERE clause to `list_evaluations()` and `count_evaluations()`, add/import `_escape_like()`

**Frontend (existing — modify):**
- `hooks/useEvaluationHistory.ts` — Add `search` param to hook, include in query key and API params
- `components/evaluations/EvaluationHistoryTable.tsx` — Add search input UI, wire to URL params with debounce

**No new files needed** — this story modifies existing files only.

### Architecture Compliance

**Backend Pattern (MUST follow):**
- ILIKE with `_escape_like()` + `ESCAPE '\'` — mandatory per architecture.md and lessons-learned.md
- Search param has `max_length=200` validation (already in router from 4.1 forward-compat)
- Parameterized SQL with `$1, $2, ...` for search term — safe against injection
- Sort column still validated via `Literal` type (unchanged from 4.1)
- Exception chaining: `raise AppException(...) from e` — preserve tracebacks
- Response schema unchanged — same `EvaluationListResponse` with `items, total, page, limit, pages`

**Frontend Pattern (MUST follow):**
- Hook uses `apiClient.ts` (openapi-fetch) — `search` param already in API types
- TanStack Query key includes search: `['evaluations', page, limit, sortBy, sortOrder, search]`
- `keepPreviousData` for smooth transitions during search (already from 4.1)
- Error states have visible UI (unchanged from 4.1)
- Use `aria-label` on search input and clear button
- `aria-busy="true"` during search loading (handled by existing `isPlaceholderData` logic)

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| FastAPI | existing | Query params (search already defined with max_length=200) | Installed |
| asyncpg | existing | ILIKE parameterized query with `ESCAPE` clause | Installed |
| pydantic | existing | No schema changes needed | Installed |
| @tanstack/react-query | v5 (existing) | Query key with search param, `keepPreviousData` | Installed |
| openapi-fetch | existing | `search` param already in API types | Installed |
| shadcn/ui (Input, Button) | existing | Search input field, clear button | Installed |
| lucide-react | existing | `Search` and `X` icons for input affordances | Installed |
| react-router-dom | existing | `useSearchParams` for URL sync | Installed |

**No new dependencies needed.** All required libraries are already installed.

### Project Structure Notes

**No new files to create.**

**Existing files to modify:**
```
backend/app/db/queries/evaluations.py          -- Add _escape_like import/create, WHERE clause
backend/app/modules/evaluations/service.py     -- Add search param, pass to queries
backend/app/modules/evaluations/router.py      -- Wire search to service call
backend/tests/integration/api/test_evaluation_list.py  -- Add search-specific tests
frontend/src/hooks/useEvaluationHistory.ts     -- Add search param to hook + query key
frontend/src/components/evaluations/EvaluationHistoryTable.tsx  -- Add search input UI
frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx  -- Add search tests
```

**Alignment with unified project structure:**
- Backend follows `modules/{feature}/{router,schemas,service}.py` pattern — no structural changes
- DB queries extend existing file — adds WHERE clause logic
- Frontend modifies existing hook and component — no new directories
- Tests extend existing test files — adds search-specific test cases

### Testing Requirements

**Backend Integration Tests (pytest) — extend `tests/integration/api/test_evaluation_list.py`:**

| Test | AC | Description |
|------|-----|-------------|
| `test_search_evaluations_by_brand_name` | #1, #5 | `search=Nike` returns only evaluations for "Nike" brand |
| `test_search_partial_match` | #1, #5 | `search=Nik` matches "Nike Indonesia" |
| `test_search_case_insensitive` | #1, #5 | `search=nike` matches "Nike Indonesia" |
| `test_search_no_results` | #2, #5 | `search=NonExistentBrand` returns `{ items: [], total: 0, pages: 0 }` |
| `test_search_with_pagination` | #3, #5 | Search results have correct total/pages for filtered set |
| `test_search_with_sorting` | #3, #5 | Sorting applies within search-filtered results |
| `test_search_special_characters_escaped` | #5 | `search=brand%test` doesn't break query (% is escaped) |
| `test_search_empty_returns_all` | #5 | `search=` or omitted search returns all evaluations |

**Frontend Component Tests (vitest) — extend `EvaluationHistoryTable.test.tsx`:**

| Test | AC | Description |
|------|-----|-------------|
| `search input renders with accessible label` | #6 | Input has `aria-label` for screen readers |
| `typing in search triggers API with search param` | #1 | Hook receives search value after debounce |
| `search updates URL query params` | #1 | URL includes `?search=Nike` after typing |
| `clear button clears search and resets page` | #4 | Clicking X clears input and removes `search` from URL |
| `empty search results show message with search term` | #2 | Shows "No evaluations found for 'Nike'" |
| `search persists across sort changes` | #3 | Changing sort doesn't lose search filter |

**Run commands:**
- Backend: `cd backend && uv run python -m pytest tests/integration/api/test_evaluation_list.py -v`
- Frontend: `cd frontend && npx vitest run --reporter=verbose`

### Previous Story Intelligence

**From Story 4.1 (Evaluation History List) — Direct predecessor:**

- Forward-compat params already in place: router accepts `search` (max 200), apiClient has `search?: string`, URL params supported via `useSearchParams`
- EvaluationHistoryTable uses `useSearchParams()` to manage URL query state — search input can follow same pattern
- `keepPreviousData` already provides smooth transitions during data fetches — works naturally for search
- `isPlaceholderData` already triggers `aria-busy="true"` — no additional accessibility work for loading state
- Code review finding L2 from 4.1: "no forward-compat optional query params" — fixed, params are now in place
- Test patterns established: mock-heavy backend integration tests, React Testing Library with hook mocking

**From Story 4.1 Dev Notes — cross-story design:**
> The `GET /api/v1/evaluations` endpoint should accept optional `search`, `date_from`, `date_to`, `category` query params even if not implemented yet — this prevents breaking the API contract in Stories 4.2-4.4.

This was implemented. Story 4.2 now wires the `search` param through all layers.

**From Epic 3 Code Reviews:**
- ILIKE queries: MUST include both `_escape_like()` AND `ESCAPE '\'` clause
- Response schemas must match ACs field-by-field — no schema changes needed here
- File List must include ALL changed files

**From `brands.py` (existing search implementation):**
- `_escape_like()` helper already tested and proven
- Same ILIKE pattern used for brand search in brands module
- Import it directly or copy for evaluations module

### Git Intelligence

**Recent commits (Story 4.1 completed):**
```
86aa92f Mark Story 4.1 complete — all review findings fixed, status → done
9308150 Fix code review findings: URL params, aria-busy, sort labels, tests (Story 4.1)
ac5f740 Add frontend evaluation history page with table, routing, and tests (Tasks 5-8)
7962e21 Add backend evaluation list endpoint with pagination and sorting (Tasks 1-4)
```

**Patterns to follow:**
- Feature branch naming: `feature/4-2-search-by-brand-name`
- Branch created from `develop` (merge 4.1 feature branch first if not already)
- Atomic commits per task
- Tests committed alongside implementation

### How This Feeds Into Later Epic 4 Stories

| Story | What 4.2 Provides | What It Adds |
|-------|-------------------|--------------|
| 4.3 (Filter by Date) | Search + filter pattern, conditional WHERE | `date_from`, `date_to` params, date picker UI |
| 4.4 (Filter by Category) | Search + filter pattern, conditional WHERE | `category` param, dropdown filter UI |
| 4.5 (Detail View) | Search-filtered context | Detail page, full evaluation display |
| 4.6 (Real-time Notifications) | Search-aware list | SSE event listener, toast notifications |

**Pattern for 4.3/4.4:** The conditional WHERE clause pattern established in this story (search present → add clause, absent → skip) will be extended with additional AND conditions for date and category filters.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.2 — Story ACs, FR28: search by brand name]
- [Source: _bmad-output/planning-artifacts/architecture.md#SQL-Safety-Rules — ILIKE escape pattern, _escape_like(), ESCAPE clause]
- [Source: _bmad-output/planning-artifacts/architecture.md#API-Naming — Query param snake_case: ?search=term]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Architecture — asyncpg parameterized SQL, $1 $2 placeholders]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Journey-2 — Historical Lookup: search by partial brand name]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Feedback-Patterns — Loading states, empty states]
- [Source: _bmad-output/planning-artifacts/prd.md — FR28: Search evaluations by brand name (partial match)]
- [Source: _bmad-output/implementation-artifacts/4-1-evaluation-history-list.md — Forward-compat params, existing code, test patterns]
- [Source: _bmad-output/lessons-learned.md — ILIKE escape rules, search param max_length, test commands]
- [Source: backend/app/db/queries/brands.py — _escape_like() helper implementation and usage pattern]
- [Source: backend/app/db/queries/evaluations.py — Existing list_evaluations() and count_evaluations() queries]
- [Source: backend/app/modules/evaluations/router.py — Forward-compat search param (line 50)]
- [Source: frontend/src/services/apiClient.ts — Forward-compat search type in API paths]
- [Source: frontend/src/hooks/useEvaluationHistory.ts — Existing hook structure, query key pattern]
- [Source: frontend/src/components/evaluations/EvaluationHistoryTable.tsx — useSearchParams pattern, URL param flow]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Frontend fake timer tests timed out — resolved by switching to `waitFor` with real timers instead of `vi.useFakeTimers()`. The fake timers conflicted with React's internal scheduling causing infinite hangs.

### Completion Notes List

- **Tasks 1-3 (Backend):** Imported `_escape_like` from `brands.py`, added conditional WHERE clause with ILIKE + ESCAPE to both `list_evaluations()` and `count_evaluations()`. Dynamic parameter numbering ($1/$2/$3 vs $1/$2) based on search presence. Wired search through service layer and router, removed forward-compat comment for search.
- **Task 4 (Backend Tests):** Added 8 integration tests covering exact match, partial match, case-insensitive, no results, pagination with search, sorting with search, special character escaping, and empty/omitted search.
- **Task 5 (Frontend Hook):** Added `search?: string` param to `useEvaluationHistory()`, included in query key and API params with conditional spread.
- **Task 6 (Frontend UI):** Added `SearchInput` component with Search/X icons, `aria-label`, placeholder, 300ms debounce via `useEffect`+`setTimeout`, URL sync via `setSearchParams()`, page reset on search change, contextual empty state message.
- **Task 7 (Frontend Tests):** Added 6 tests covering accessible label, search triggering API call, URL param update, clear button, contextual empty message, and search persistence across sort changes.
- **All 489 backend tests pass. All 232 frontend tests pass (2 pre-existing Firebase config failures unrelated to this story).**

### Change Log

- 2026-02-12: Implemented brand name search for evaluations — backend ILIKE query with escape, service/router wiring, search input UI with debounce and URL sync, 14 new tests (8 backend + 6 frontend)

### File List

- backend/app/db/queries/evaluations.py (modified — added `_escape_like` import, WHERE clause in list/count queries)
- backend/app/modules/evaluations/service.py (modified — added `search` param, passed to DB queries)
- backend/app/modules/evaluations/router.py (modified — wired `search` to service call, updated comments)
- backend/tests/integration/api/test_evaluation_list.py (modified — added 8 search integration tests)
- frontend/src/hooks/useEvaluationHistory.ts (modified — added `search` param to hook signature, query key, API params)
- frontend/src/components/evaluations/EvaluationHistoryTable.tsx (modified — added SearchInput component, debounce, URL sync, contextual empty state)
- frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx (modified — added 6 search tests)
