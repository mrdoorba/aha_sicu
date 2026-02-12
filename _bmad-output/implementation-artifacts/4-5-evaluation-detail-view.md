# Story 4.5: Evaluation Detail View

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team leader**,
I want **to view full details of a past evaluation**,
so that **I have complete context for decision-making**.

## Acceptance Criteria

1. **Backend detail endpoint returns full evaluation data**
   **Given** I call `GET /api/v1/evaluations/{evaluation_id}` with a valid evaluation ID
   **When** authenticated
   **Then** return the complete evaluation record with:
   - `id`, `brand_id`, `brand_name` (from brand_vp_data join)
   - `final_score` (decimal, can be negative), `verdict` (e.g. "✔️", "❌", "⭕️")
   - `template` ("fashion" or "non_fashion")
   - `score_breakdown` (JSONB — per-category scores: Operational, Business, Visitors, Promo, Products/Status, Ads, Campaign, Stock, Discount)
   - `calculator_results` (JSONB — snapshot of all three calculator outputs: ads_keyword text, top_sku tables + avg stock, discount text + flag)
   - `manual_inputs` (JSONB — all manual input values organized by scoring category)
   - `email_output` (text — generated email body, nullable)
   - `evaluator_email` (from users table join)
   - `created_at` (ISO 8601 timestamp)
   - `rule_version` (integer)

2. **Backend returns 404 for non-existent evaluation**
   **Given** I call `GET /api/v1/evaluations/{evaluation_id}` with an ID that doesn't exist
   **When** authenticated
   **Then** return 404 Not Found with `{"code": "EVAL_NOT_FOUND", "detail": "Evaluation not found"}`

3. **Detail page displays brand info header**
   **Given** I click on an evaluation row in the history list
   **When** the detail page loads at `/history/{id}`
   **Then** I see a header section with:
   - Brand name (prominently displayed)
   - Template badge (Fashion / Non-Fashion)
   - Evaluator email
   - Evaluation date (localized format, e.g. "12 Feb 2026, 14:30 WIB")

4. **Detail page displays final score with breakdown**
   **Given** I am on the evaluation detail page
   **When** viewing the score section
   **Then** I see the final score displayed prominently with verdict icon
   **And** I see a score breakdown table showing per-category scores:
   | Category | Score |
   |----------|-------|
   | Operational | X/10 |
   | Business | X/20 |
   | Visitors | X/5 |
   | Promo Tools | -X (penalty) |
   | Products/Status | X/15 |
   | Ads | X (range -5 to +5) |
   | Campaign | -X (penalty) |
   | Stock | X (range -5 to +10) |
   | Discount | X/5 |

5. **Detail page displays calculator results**
   **Given** I am on the evaluation detail page
   **When** viewing the calculator results section
   **Then** I see all three calculator outputs:
   - **Ads Keyword**: Multi-line text output (AK2 overview, AK3 breakdown, AK4 flags, top/bottom ads, keyword flags) displayed in a preformatted text block
   - **Top SKU**: Two tables (Revenue ranking: Kode Variasi, Product Name, Total Omzet, Rata2 Harga Jual; Stock ranking: Kode Variasi, Nama Produk, Varian, Stok) with average stock metric
   - **Discount Check**: Five text values (% Diskon TOP SKU, Range, Voucher %, Paket Diskon %, Fake Discount flag if present)
   **And** each calculator section is clearly labeled and visually separated
   **And** if a calculator was not run (no data), show "No data available" instead

6. **Detail page displays manual input summary**
   **Given** I am on the evaluation detail page
   **When** viewing the manual inputs section
   **Then** I see all manual input values organized by scoring category sections (Operational, Business, Content, Visitors, Promo Tools, Products/Status, Ads, Campaign, Competition)
   **And** each value has its field label and entered value
   **And** IDR values show Indonesian number formatting (e.g., "125,000,000")
   **And** percentage values display with % suffix

7. **Detail page displays email output**
   **Given** the evaluation has an `email_output` value
   **When** viewing the detail page
   **Then** I see the email output text in a copyable text block
   **And** a "Copy" button copies the text to clipboard
   **Given** the evaluation has no `email_output`
   **When** viewing the detail page
   **Then** the email output section is not shown

8. **Back navigation returns to history list**
   **Given** I am on the evaluation detail page
   **When** I click "Back to History" link/button
   **Then** I am navigated back to `/history`
   **And** my previous filter state (search, date range, category, page) is preserved via URL params

9. **Loading and error states**
   **Given** I navigate to `/history/{id}`
   **When** the API request is in progress
   **Then** I see a loading skeleton/spinner
   **Given** the API request fails
   **When** viewing the page
   **Then** I see an error message with a "Retry" button
   **Given** I navigate to `/history/{id}` with an invalid/non-existent ID
   **When** the backend returns 404
   **Then** I see "Evaluation not found" message with a "Back to History" link

10. **Detail page has accessible structure**
    **Given** I am using keyboard navigation or a screen reader
    **When** viewing the evaluation detail page
    **Then** the page has semantic headings (h1 for brand name, h2 for sections)
    **And** the score breakdown table has proper `<th>` headers
    **And** the "Back to History" link is keyboard-accessible
    **And** the copy button has an `aria-label`

## Tasks / Subtasks

- [x] Task 1: Add get-by-id DB query (AC: #1, #2)
  - [x] 1.1 Add `get_evaluation_by_id(conn, evaluation_id: int)` to `db/queries/evaluations.py`
  - [x] 1.2 SQL joins `evaluations` with `brand_vp_data` (for brand_name) and `users` (for evaluator email)
  - [x] 1.3 Select all evaluation columns including JSONB fields: score_breakdown, calculator_results, manual_inputs, email_output
  - [x] 1.4 Return `None` if no row found (service layer handles 404)

- [x] Task 2: Add detail response schema (AC: #1)
  - [x] 2.1 Add `EvaluationDetailResponse` schema to `modules/evaluations/schemas.py`
  - [x] 2.2 Fields: id, brand_id, brand_name, final_score, verdict, template, score_breakdown (dict), calculator_results (dict), manual_inputs (dict), email_output (str | None), evaluator_email, created_at, rule_version

- [x] Task 3: Add service function for get-by-id (AC: #1, #2)
  - [x] 3.1 Add `get_evaluation_detail(evaluation_id: int, conn)` to `modules/evaluations/service.py`
  - [x] 3.2 Call `eval_queries.get_evaluation_by_id()` and map to `EvaluationDetailResponse`
  - [x] 3.3 Raise `AppException("EVAL_NOT_FOUND", "Evaluation not found", 404)` if not found

- [x] Task 4: Add GET endpoint for single evaluation (AC: #1, #2)
  - [x] 4.1 Add `GET /api/v1/evaluations/{evaluation_id}` route to `modules/evaluations/router.py`
  - [x] 4.2 Path param: `evaluation_id: int`
  - [x] 4.3 Requires authentication via `Depends(get_current_user)`
  - [x] 4.4 Returns `EvaluationDetailResponse`

- [x] Task 5: Write backend tests (AC: #1, #2)
  - [x] 5.1 Integration test: `GET /evaluations/{id}` returns full evaluation with all fields
  - [x] 5.2 Integration test: Response includes brand_name from join, evaluator_email from join
  - [x] 5.3 Integration test: JSONB fields (score_breakdown, calculator_results, manual_inputs) are properly serialized
  - [x] 5.4 Integration test: Non-existent ID returns 404 with EVAL_NOT_FOUND code
  - [x] 5.5 Integration test: Unauthenticated request returns 401

- [x] Task 6: Add frontend API types and hook (AC: #1, #3, #9)
  - [x] 6.1 Add `GET /api/v1/evaluations/{evaluation_id}` path type to `apiClient.ts`
  - [x] 6.2 Create `useEvaluationDetail(id: number)` hook in `hooks/useEvaluationDetail.ts`
  - [x] 6.3 TanStack Query key: `['evaluation-detail', id]`
  - [x] 6.4 Handle loading, error, and 404 states

- [x] Task 7: Create evaluation detail page component (AC: #3, #4, #5, #6, #7, #8, #9, #10)
  - [x] 7.1 Create `pages/EvaluationDetailPage.tsx` — page wrapper with route param parsing
  - [x] 7.2 Brand info header section: brand name (h1), template badge, evaluator, date
  - [x] 7.3 Score section: final score + verdict prominently displayed, score breakdown table with per-category rows
  - [x] 7.4 Calculator results section: Ads Keyword (preformatted text), Top SKU (two data tables), Discount Check (text values)
  - [x] 7.5 Manual inputs section: values organized by scoring category, IDR formatting, percentage display
  - [x] 7.6 Email output section: copyable text block with Copy button (conditional — only shown if email_output exists)
  - [x] 7.7 "Back to History" navigation link at top
  - [x] 7.8 Loading skeleton, error state with retry, 404 state with back link
  - [x] 7.9 Semantic HTML: h1/h2 headings, table headers, aria-label on copy button

- [x] Task 8: Add route to App.tsx (AC: #3, #8)
  - [x] 8.1 Add `/history/:id` route pointing to `EvaluationDetailPage` wrapped in `ProtectedRoute`
  - [x] 8.2 Verify row click in `EvaluationHistoryTable` navigates correctly (already does `navigate('/history/${id}')`)

- [x] Task 9: Write frontend tests (AC: #3, #4, #5, #7, #8, #9, #10)
  - [x] 9.1 Test: Detail page renders brand info header with name, template badge, evaluator, date
  - [x] 9.2 Test: Score breakdown table renders per-category scores
  - [x] 9.3 Test: Calculator results sections render (ads keyword text, top SKU tables, discount values)
  - [x] 9.4 Test: Manual inputs display organized by category
  - [x] 9.5 Test: Email output section shows with copy button when email_output present
  - [x] 9.6 Test: Email output section hidden when email_output is null
  - [x] 9.7 Test: Loading state shows skeleton/spinner
  - [x] 9.8 Test: Error state shows retry button
  - [x] 9.9 Test: 404 state shows "Evaluation not found" with back link
  - [x] 9.10 Test: "Back to History" link navigates to /history

## Dev Notes

### Story Context — Fifth Story of Epic 4 (Evaluation History & Search)

This story adds the evaluation detail view — a full-page display of a completed evaluation's data. It's the "click-through" destination from the history list built in Stories 4.1-4.4. The row click handler in `EvaluationHistoryTable.tsx` (line 500) already navigates to `/history/${id}`, but no backend endpoint, frontend page, or route exists yet.

**Cross-story context within Epic 4:**
- Story 4.1 (done): Base list with pagination + sorting + forward-compat params
- Story 4.2 (done): Brand name search (ILIKE)
- Story 4.3 (done): Date range filter
- Story 4.4 (done): Category filter (fashion/non_fashion)
- **Story 4.5 (this): Full evaluation detail view — the destination for row clicks**
- Story 4.6: SSE real-time notifications for new evaluations

**Design decision: Full Page (not modal).** The detail view displays a large amount of data (score breakdown, 3 calculator outputs, 40+ manual input values, email text). A modal would be cramped. Using a dedicated page at `/history/:id` matches the existing navigation pattern (row click already targets this URL).

### Database — Get Evaluation By ID Query

**New query: `get_evaluation_by_id(conn, evaluation_id: int)`**

This is a simple SELECT with two JOINs — follows the same pattern as `list_evaluations()` but returns all columns including heavy JSONB fields.

```sql
SELECT e.id, e.brand_id, b.brand_name,
       e.final_score, e.verdict, e.template,
       e.score_breakdown, e.calculator_results, e.manual_inputs,
       e.email_output, e.rule_version, e.created_at,
       u.email AS evaluator_email
FROM evaluations e
JOIN brand_vp_data b ON e.brand_id = b.id
JOIN users u ON e.user_id = u.id
WHERE e.id = $1
```

**Key differences from `list_evaluations()`:**
- Selects ALL columns including `score_breakdown`, `calculator_results`, `manual_inputs`, `email_output` (the list query intentionally omits these heavy JSONB fields)
- Single row by primary key — no pagination, sorting, or filtering
- Returns `dict | None` (None when not found)

**JSONB field structure (stored when evaluation is saved via `insert_evaluation()`):**

`score_breakdown` — list of CategoryScoreItem dicts:
```json
[
  {
    "category": "Operational",
    "score": 10.0,
    "max_score": 10.0,
    "rows": [{"row": 7, "metric": "...", "value": ..., "benchmark": "...", "verdict": "...", "message": "...", "score": ...}],
    "available": true
  },
  ...
]
```

`calculator_results` — dict keyed by calculator_type:
```json
{
  "ads_keyword": {"details": {...}, "output_text": "..."},
  "top_sku": {"details": {"output_1": [...], "output_2": [...], "average_stock": 123}, "output_text": "..."},
  "discount": {"details": {...}, "output_text": "..."}
}
```

`manual_inputs` — dict keyed by scoring category:
```json
{
  "operational": {"pesanan_tidak_terselesaikan": 0.5, "keterlambatan": 0.3, ...},
  "business": {"monthly_sales": [...], "conversion_rate": 2.5, ...},
  ...
}
```

### Backend — Endpoint Placement

**CRITICAL: Route ordering in `router.py`**

The new `GET /api/v1/evaluations/{evaluation_id}` route MUST be placed AFTER `GET /api/v1/evaluations` (the list endpoint) but BEFORE `GET /api/v1/evaluations/brands/{brand_id}`. FastAPI matches routes in declaration order, and `{evaluation_id}` would match "brands" as a string if placed before the literal `/brands/` routes.

**Recommended placement:** Immediately after the `list_evaluations_endpoint` function (line 71 of router.py).

```python
@router.get("/{evaluation_id}", response_model=EvaluationDetailResponse)
async def get_evaluation_detail_endpoint(
    evaluation_id: int,
    current_user: dict = Depends(get_current_user),
) -> EvaluationDetailResponse:
    """Get full details of a single evaluation by ID."""
    return await get_evaluation_detail(evaluation_id=evaluation_id)
```

**Note:** `evaluation_id: int` type annotation ensures FastAPI won't match string paths like `/brands/` — but ordering after the list endpoint is still best practice.

### Backend — Schema Design

**New schema: `EvaluationDetailResponse`**

```python
class EvaluationDetailResponse(BaseModel):
    """Full evaluation detail for the detail view page."""

    id: int
    brand_id: int
    brand_name: str
    final_score: float
    verdict: str
    template: str
    score_breakdown: list[dict[str, Any]]
    calculator_results: dict[str, Any]
    manual_inputs: dict[str, Any]
    email_output: str | None = None
    evaluator_email: str
    created_at: datetime
    rule_version: int
```

**score_breakdown type note:** Stored in DB as JSONB (from `json.dumps(score_breakdown)` in `insert_evaluation()`, line 93 of evaluations.py). The data is a list of CategoryScoreItem-like dicts. We use `list[dict[str, Any]]` because this is a READ of an already-serialized snapshot — we don't re-validate the internal structure.

### Backend — Service Pattern

Follow the existing `get_evaluation_state()` pattern (service.py lines 85-103):

```python
async def get_evaluation_detail(evaluation_id: int) -> EvaluationDetailResponse:
    async with db.connection() as conn:
        row = await eval_queries.get_evaluation_by_id(conn, evaluation_id)

    if not row:
        raise AppException(
            code="EVAL_NOT_FOUND",
            detail="Evaluation not found",
            status_code=404,
        )

    return EvaluationDetailResponse(
        id=row["id"],
        brand_id=row["brand_id"],
        brand_name=row["brand_name"],
        final_score=float(row["final_score"]),
        verdict=row["verdict"],
        template=row["template"],
        score_breakdown=row["score_breakdown"],
        calculator_results=row["calculator_results"],
        manual_inputs=row["manual_inputs"],
        email_output=row["email_output"],
        evaluator_email=row["evaluator_email"],
        created_at=row["created_at"],
        rule_version=row["rule_version"],
    )
```

**Note:** asyncpg auto-deserializes JSONB columns to Python dicts/lists — no manual `json.loads()` needed on read.

### Frontend — API Client Path Type

Add to `apiClient.ts` (after the existing `/api/v1/evaluations` path, around line 258):

```typescript
'/api/v1/evaluations/{evaluation_id}': {
  get: {
    parameters: {
      path: {
        evaluation_id: number;
      };
    };
    responses: {
      200: {
        content: {
          'application/json': {
            id: number;
            brand_id: number;
            brand_name: string;
            final_score: number;
            verdict: string;
            template: string;
            score_breakdown: Array<Record<string, unknown>>;
            calculator_results: Record<string, unknown>;
            manual_inputs: Record<string, unknown>;
            email_output: string | null;
            evaluator_email: string;
            created_at: string;
            rule_version: number;
          };
        };
      };
    };
  };
};
```

### Frontend — Hook Pattern

Follow the existing `useEvaluationHistory` pattern but simpler (single item, no pagination):

```typescript
// hooks/useEvaluationDetail.ts
export function useEvaluationDetail(id: number) {
  const query = useQuery<EvaluationDetail>({
    queryKey: ['evaluation-detail', id],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/evaluations/{evaluation_id}', {
        params: { path: { evaluation_id: id } },
      });
      if (error) throw new Error('Failed to fetch evaluation detail');
      return data as EvaluationDetail;
    },
    enabled: id > 0,
  });

  return {
    evaluation: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}
```

**No `keepPreviousData` needed** — detail view shows one evaluation, no pagination transitions.

### Frontend — Page Component Structure

**`EvaluationDetailPage.tsx` layout:**

```
┌────────────────────────────────────────────────────────────┐
│  Header (nav)                                               │
├────────────────────────────────────────────────────────────┤
│  ← Back to History                                          │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Brand Name                     [Fashion] badge        │ │
│  │  evaluator@email.com · 12 Feb 2026, 14:30 WIB         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────┐  ┌─────────────────────────────┐ │
│  │  FINAL SCORE          │  │  SCORE BREAKDOWN             │ │
│  │      82 ✔️            │  │  Operational    10/10        │ │
│  │  Fashion template     │  │  Business       20/20        │ │
│  │  Rule v1              │  │  Visitors        5/5         │ │
│  │                       │  │  Promo          -5           │ │
│  │                       │  │  Products       15/15        │ │
│  │                       │  │  Ads             5           │ │
│  │                       │  │  Campaign       -10          │ │
│  │                       │  │  Stock          10           │ │
│  │                       │  │  Discount        5/5         │ │
│  └──────────────────────┘  └─────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  CALCULATOR RESULTS                                     │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Ads Keyword Analysis                             │  │ │
│  │  │  [preformatted text block]                        │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Top SKU Analysis          Avg Stock: 123        │  │ │
│  │  │  [Revenue table] [Stock table]                   │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Discount Check                                   │  │ │
│  │  │  % Diskon TOP SKU: 2.7%  Range: 0.0% ~ 6.7%    │  │ │
│  │  │  Voucher: 0.3%  Paket: 0.0%                     │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MANUAL INPUTS                                          │ │
│  │  Operational | Business | Content | Visitors | ...      │ │
│  │  [key-value pairs per category]                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  EMAIL OUTPUT                            [Copy] button  │ │
│  │  [preformatted email text]                              │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

**shadcn/ui components to use:**
- `Card` — for each section (score, calculator results, manual inputs, email)
- `Badge` — for template type (Fashion/Non-Fashion)
- `Table` / `TableHeader` / `TableRow` / `TableCell` — for score breakdown and Top SKU tables
- `Button` — for "Back to History" and "Copy" button
- `Skeleton` — for loading state (follow the EvaluationHistoryTable pattern)

**Back navigation approach:** Use `<Link to="/history">` or `navigate(-1)`. Using `<Link to="/history">` is simpler and more predictable. URL params from the previous history page will be lost with direct link but preserved with `navigate(-1)`. Consider using `navigate(-1)` for better UX.

**Copy to clipboard:** Use `navigator.clipboard.writeText()` with fallback. Toast notification on success.

### Frontend — Route in App.tsx

Add the new route in `App.tsx` BEFORE the `/history` route to ensure `:id` param matching works correctly with React Router:

```tsx
import { EvaluationDetailPage } from './pages/EvaluationDetailPage';

// Add between /history route and /evaluation/:brandId route:
<Route
  path="/history/:id"
  element={
    <ProtectedRoute>
      <EvaluationDetailPage />
    </ProtectedRoute>
  }
/>
```

**Important:** React Router v6 handles specificity correctly (`/history` vs `/history/:id`), so ordering doesn't strictly matter, but placing specific routes first is good practice.

### Existing Code to Integrate With

**Backend (existing — modify):**
- `backend/app/db/queries/evaluations.py` — Add `get_evaluation_by_id()` query function
- `backend/app/modules/evaluations/schemas.py` — Add `EvaluationDetailResponse` schema
- `backend/app/modules/evaluations/service.py` — Add `get_evaluation_detail()` service function
- `backend/app/modules/evaluations/router.py` — Add `GET /{evaluation_id}` endpoint

**Frontend (existing — modify):**
- `frontend/src/services/apiClient.ts` — Add path type for `GET /api/v1/evaluations/{evaluation_id}`
- `frontend/src/App.tsx` — Add `/history/:id` route

**Frontend (new files):**
- `frontend/src/hooks/useEvaluationDetail.ts` — New hook for fetching single evaluation
- `frontend/src/pages/EvaluationDetailPage.tsx` — New page component

**No existing files need breaking changes.** The row click handler in `EvaluationHistoryTable.tsx` (line 500: `navigate('/history/${row.original.id}')`) already targets the correct URL — no modification needed.

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Parameterized SQL with `$1` — evaluation_id passed as parameter, never interpolated
- `AppException("EVAL_NOT_FOUND", ...)` with status_code=404 — follows existing error code pattern (prefix `EVAL_`)
- Exception chaining: `raise AppException(...) from e` if wrapping another exception
- Service function uses `db.connection()` context manager (not receiving conn as param)
- Response schema matches ACs field-by-field: verify every field name and type
- `Depends(get_current_user)` required on the endpoint
- Route response_model explicitly set to `EvaluationDetailResponse`

**Frontend Pattern (MUST follow):**
- Hook uses `apiClient.ts` (openapi-fetch) — never raw `fetch()`
- TanStack Query key: `['evaluation-detail', id]` — unique namespace from list queries
- Error states have visible UI: error message + retry button (not just console.log)
- `queryFn` MUST throw on error — never return null or swallow errors
- Use `useParams()` from react-router-dom to extract `:id` param
- Parse ID as number: `const id = Number(params.id)` — handle NaN gracefully
- Semantic HTML: `<h1>` for brand name, `<h2>` for section headers, `<th>` for table headers
- `aria-label` on copy button: `"Copy email output to clipboard"`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| FastAPI | existing | Path param `evaluation_id: int`, `response_model` | Installed |
| asyncpg | existing | `fetchrow()` with parameterized SQL | Installed |
| pydantic | existing | `EvaluationDetailResponse` schema | Installed |
| @tanstack/react-query | v5 (existing) | `useQuery` for detail fetch | Installed |
| openapi-fetch | existing | Typed GET with path params | Installed |
| react-router-dom | existing | `useParams()`, `useNavigate()`, `<Link>` | Installed |
| shadcn/ui | existing | Card, Badge, Table, Button, Skeleton | Installed |
| lucide-react | existing | ArrowLeft (back), Copy, ClipboardCheck icons | Installed |
| sonner | existing | Toast for copy confirmation | Installed |

**No new dependencies required.** All libraries are already installed.

### Project Structure Notes

**New files:**
```
frontend/src/hooks/useEvaluationDetail.ts              -- New hook for single evaluation fetch
frontend/src/pages/EvaluationDetailPage.tsx             -- New detail page component
frontend/src/pages/EvaluationDetailPage.test.tsx        -- New page component tests
```

**Existing files to modify:**
```
backend/app/db/queries/evaluations.py                   -- Add get_evaluation_by_id()
backend/app/modules/evaluations/schemas.py              -- Add EvaluationDetailResponse
backend/app/modules/evaluations/service.py              -- Add get_evaluation_detail()
backend/app/modules/evaluations/router.py               -- Add GET /{evaluation_id} endpoint
backend/tests/integration/api/test_evaluation_list.py   -- Add detail endpoint tests (or new test file)
frontend/src/services/apiClient.ts                      -- Add path type for evaluations/{id}
frontend/src/App.tsx                                    -- Add /history/:id route
```

**Alignment with unified project structure:**
- Backend follows `modules/{feature}/{router,schemas,service}.py` pattern — no structural changes
- DB query adds one function to existing file
- Frontend new page follows `pages/{PageName}.tsx` convention
- Frontend new hook follows `hooks/use{Feature}.ts` convention
- Tests colocated: backend in `tests/integration/api/`, frontend in same directory as component

### Testing Requirements

**Backend Integration Tests (pytest) — in `tests/integration/api/`:**

| Test | AC | Description |
|------|-----|-------------|
| `test_get_evaluation_detail_success` | #1 | Returns full evaluation with all fields including JSONB data |
| `test_get_evaluation_detail_has_brand_name` | #1 | brand_name from brand_vp_data join is present |
| `test_get_evaluation_detail_has_evaluator_email` | #1 | evaluator_email from users join is present |
| `test_get_evaluation_detail_jsonb_fields` | #1 | score_breakdown is list, calculator_results is dict, manual_inputs is dict |
| `test_get_evaluation_detail_not_found` | #2 | Returns 404 with code EVAL_NOT_FOUND |
| `test_get_evaluation_detail_unauthenticated` | #2 | Returns 401 without auth token |

**Frontend Component Tests (vitest) — in `pages/EvaluationDetailPage.test.tsx`:**

| Test | AC | Description |
|------|-----|-------------|
| `renders brand info header` | #3 | Shows brand name, template badge, evaluator, date |
| `renders score breakdown table` | #4 | Table with per-category rows and score values |
| `renders calculator results` | #5 | Ads keyword text, top SKU tables, discount values |
| `renders manual inputs by category` | #6 | Organized sections with field labels and values |
| `renders email output with copy button` | #7 | Shows text block and Copy button when email_output present |
| `hides email section when null` | #7 | Email section not rendered when email_output is null |
| `shows loading skeleton` | #9 | Loading state renders skeletons |
| `shows error state with retry` | #9 | Error message and retry button |
| `shows 404 not found` | #9 | "Evaluation not found" with back link |
| `back to history link works` | #8 | Link navigates to /history |

**Run commands:**
- Backend: `cd backend && uv run python -m pytest tests/integration/api/test_evaluation_detail.py -v`
- Frontend: `cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx --reporter=verbose`

### Previous Story Intelligence

**From Story 4.4 (Filter by Category) — Direct predecessor:**

- All 4 filter types operational (search, date_from, date_to, category)
- Row click handler confirmed at `EvaluationHistoryTable.tsx:500` → `navigate('/history/${row.original.id}')`
- EvaluationListItem includes `id` field — the key needed for detail fetch
- 543+ backend tests, 239+ frontend tests — all passing
- No regressions from Epic 4 work

**From Story 4.4 Dev Notes — forward guidance:**
> **Pattern for 4.5:** The detail view will be accessed by clicking a row in the filtered list. The list already returns evaluation `id` — the detail view will fetch by ID. No filter changes needed.

**From Story 3.10 (Save Evaluation) — Data source:**
- `insert_evaluation()` in `db/queries/evaluations.py:60-99` — this is what creates the records we're reading
- JSONB fields are stored via `json.dumps()` — asyncpg auto-deserializes on read
- `SaveEvaluationRequest` schema shows the structure of data being stored

**From Lessons Learned:**
- Response schemas must match ACs field-by-field
- File List must include ALL changed files
- Backend tests: `uv run python -m pytest` (not `pytest` directly)
- Frontend hooks MUST use `apiClient.ts` — never raw `fetch()`
- JSONB fields auto-deserialize in asyncpg — no manual `json.loads()` needed

### Git Intelligence

**Recent commits (Story 4.4 completed and merged):**
```
dba2194 Merge feature/4-4-filter-by-category into develop
074acde Fix code review findings: Literal types, empty state message, None check (Story 4.4)
ab9e6d0 Mark Story 4.4 complete — all tasks done, status → review
c55781d Add frontend category filter with dropdown UI (Tasks 5-7)
92d6685 Add backend category filtering for evaluations (Tasks 1-4)
```

**Patterns to follow:**
- Feature branch naming: `feature/4-5-evaluation-detail-view`
- Branch created from `develop` (current branch)
- Atomic commits per task group (backend tasks 1-5, frontend tasks 6-9)
- Tests committed alongside implementation

### How This Feeds Into Story 4.6

| Story | What 4.5 Provides | What It Adds |
|-------|-------------------|--------------|
| 4.6 (Real-time Notifications) | Full detail view accessible via `/history/:id` | SSE event listener on history page, toast notifications when new evaluations are saved by teammates |

**Pattern for 4.6:** The SSE `new_evaluation` event should include the evaluation `id` so the toast can link to `/history/{id}` for quick navigation to the new evaluation's detail view.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.5 — Story ACs, FR31: view full evaluation details]
- [Source: _bmad-output/planning-artifacts/architecture.md#API-Naming — API conventions: GET /evaluations/{id}]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Architecture — asyncpg parameterized SQL, evaluations table schema]
- [Source: _bmad-output/planning-artifacts/architecture.md#Error-Handling — Structured error codes: EVAL_NOT_FOUND]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend-Architecture — TanStack Query, openapi-fetch, shadcn/ui]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Journey-2 — Historical Lookup: detail view with Brand Info, Score+Breakdown, Calculator Results, Input Summary, Metadata]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Score-Panel — Score display patterns, category breakdown layout]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Component-Strategy — Card, Badge, Table, Button components]
- [Source: _bmad-output/planning-artifacts/prd.md — FR31: view full evaluation details, FR32: track evaluator, FR33: maintain history]
- [Source: _bmad-output/implementation-artifacts/4-4-filter-by-category.md — Row click handler at line 500, forward guidance for 4.5]
- [Source: _bmad-output/lessons-learned.md — Response schema validation, test commands, JSONB handling]
- [Source: backend/app/db/queries/evaluations.py — list_evaluations JOIN pattern (lines 164-175), insert_evaluation JSONB storage (lines 60-99)]
- [Source: backend/app/modules/evaluations/schemas.py — EvaluationListItem (line 150), SaveEvaluationRequest (line 172), ScoringResponse (line 128)]
- [Source: backend/app/modules/evaluations/service.py — get_evaluation_state pattern (lines 85-103), save_evaluation pattern (lines 213-262)]
- [Source: backend/app/modules/evaluations/router.py — list endpoint (line 44), route ordering context]
- [Source: backend/app/core/exceptions.py — AppException(code, detail, status_code)]
- [Source: frontend/src/services/apiClient.ts — Path type patterns, GET with path params example (line 112)]
- [Source: frontend/src/hooks/useEvaluationHistory.ts — Hook pattern: useQuery, queryKey, queryFn, error throwing]
- [Source: frontend/src/components/evaluations/EvaluationHistoryTable.tsx:500 — Row click: navigate('/history/${row.original.id}')]
- [Source: frontend/src/App.tsx — Route structure, ProtectedRoute wrapper pattern]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

No issues encountered during implementation.

### Completion Notes List

- Tasks 1-4: Backend endpoint fully implemented — DB query with JOINs for brand_name and evaluator_email, Pydantic schema with all 12 fields, service with 404 handling, GET endpoint with auth
- Task 5: 6 backend integration tests covering success, JOINs, JSONB serialization, 404, and auth
- Task 6: Frontend API path type added to apiClient.ts, useEvaluationDetail hook created with TanStack Query
- Task 7: Full detail page with 6 sections — brand header, score breakdown table, calculator results (3 sub-sections), manual inputs by category, conditional email output with clipboard copy
- Task 8: Route `/history/:id` added to App.tsx with ProtectedRoute wrapper
- Task 9: 10 frontend tests covering all AC scenarios (header, score table, calculators, manual inputs, email, loading, error, 404, back navigation)
- All 522 backend tests pass, all 256 frontend tests pass, zero regressions

### File List

**Modified:**
- backend/app/db/queries/evaluations.py — Added `get_evaluation_by_id()` query
- backend/app/modules/evaluations/schemas.py — Added `EvaluationDetailResponse` schema
- backend/app/modules/evaluations/service.py — Added `get_evaluation_detail()` service function
- backend/app/modules/evaluations/router.py — Added `GET /{evaluation_id}` endpoint
- frontend/src/services/apiClient.ts — Added path type for `GET /evaluations/{evaluation_id}`
- frontend/src/App.tsx — Added `/history/:id` route

**New:**
- backend/tests/integration/api/test_evaluation_detail.py — 6 integration tests
- frontend/src/hooks/useEvaluationDetail.ts — Hook for fetching single evaluation
- frontend/src/pages/EvaluationDetailPage.tsx — Detail page component
- frontend/src/pages/EvaluationDetailPage.test.tsx — 10 frontend tests

## Change Log

- 2026-02-12: Story 4.5 implemented — full evaluation detail view with backend endpoint (GET /evaluations/{id}), frontend page (/history/:id), 6 backend + 10 frontend tests. All ACs satisfied.
