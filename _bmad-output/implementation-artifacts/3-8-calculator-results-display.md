# Story 3.8: Calculator Results Display

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team member**,
I want **to view the results of each calculator in their native format on the evaluation page**,
so that **I understand the brand's performance across different metrics before generating the final score**.

## Acceptance Criteria

1. **Ads Keyword Calculator (Calculator 1) display**
   **Given** I am on the evaluation page and Calculator 1 (Ads Keyword) has run
   **When** viewing its results
   **Then** I see multi-line text output preserving formatting:
   - AK2: Ad overview line (e.g., "34 dari 80 produk (42.5%) sudah beriklan")
   - AK3: Ad type breakdown (multi-line, grouped by type/placement/bidding)
   - AK4: 7 recommendation flags (each on its own line)
   - TOP ads listing with keyword details
   - AL3: ROAS median flag
   - BOTTOM ads listing with keyword details
   - AL6-AL9: Keyword recommendation flags

2. **Top SKU Calculator (Calculator 2) display**
   **Given** Calculator 2 (Top SKU) has run
   **When** viewing its results
   **Then** I see two tables:
   - Revenue ranking table: Kode Variasi, Product Name, Total Omzet (IDR formatted), Rata2 Harga Jual (IDR formatted)
   - Stock ranking table: Kode Variasi, Nama Produk, Varian, Stok
   **And** I see the average stock metric in the header (e.g., "Average Stok: 123")
   **And** tables are sortable by column

3. **Discount Check Calculator (Calculator 3) display**
   **Given** Calculator 3 (Discount Check) has run
   **When** viewing its results
   **Then** I see 5 text values:
   - % Diskon TOP SKU (e.g., "2.7%")
   - Range (e.g., "0.0% ~ 6.7%")
   - Voucher percentage (e.g., "Voucher 0.3%")
   - Paket Diskon percentage (e.g., "Paket Diskon 0.0%")
   - Fake discount flag (warning indicator if present)

4. **Pending state for calculators without results**
   **Given** a calculator hasn't run yet (missing required files)
   **When** viewing results
   **Then** I see a pending state showing which files are still needed (e.g., "Waiting for: Mass Update file")

5. **Error state with retry**
   **Given** a calculator failed
   **When** viewing results
   **Then** I see an error state with the error message
   **And** a "Retry" button that re-runs that specific calculator

6. **Results fetched from backend on page load**
   **Given** I navigate to the evaluation page for a brand with existing calculator results
   **When** the page loads
   **Then** existing calculator results are fetched and displayed immediately
   **And** calculator status is fetched to show pending/ready state for calculators without results

7. **Recalculate All button**
   **Given** I am on the evaluation page with at least some calculator results
   **When** I click "Recalculate All"
   **Then** all ready calculators re-run
   **And** results update in place without page refresh

## Tasks / Subtasks

- [x] Task 1: Add backend GET endpoint for calculator results (AC: #6)
  - [x] 1.1 Add `GET /api/v1/evaluations/brands/{brand_id}/calculators/results` endpoint in `evaluations/router.py`
  - [x] 1.2 Add `CalculatorResultsListResponse` schema in `evaluations/schemas.py`
  - [x] 1.3 Wire endpoint to existing `get_results_by_brand()` DB query
  - [x] 1.4 Add integration test for the new endpoint

- [x] Task 2: Add frontend hook and API types for fetching results (AC: #6)
  - [x] 2.1 Add path type for GET results endpoint in `apiClient.ts`
  - [x] 2.2 Add `useCalculatorResults(brandId)` query hook in `useCalculator.ts`
  - [x] 2.3 Ensure cache invalidation on run-all and individual run success

- [x] Task 3: Create Ads Keyword results display component (AC: #1)
  - [x] 3.1 Create `frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx`
  - [x] 3.2 Render `output_text` as multi-line pre-formatted text preserving line breaks
  - [x] 3.3 Display calculated_at timestamp

- [x] Task 4: Create Top SKU results display component (AC: #2)
  - [x] 4.1 Create `frontend/src/components/evaluation/calculators/TopSkuResults.tsx`
  - [x] 4.2 Render revenue ranking table from `details.output_1` with IDR formatting
  - [x] 4.3 Render stock ranking table from `details.output_2`
  - [x] 4.4 Display average stock metric in header
  - [x] 4.5 Add column sorting for both tables (client-side sort)

- [x] Task 5: Create Discount Check results display component (AC: #3)
  - [x] 5.1 Create `frontend/src/components/evaluation/calculators/DiscountResults.tsx`
  - [x] 5.2 Display 5 text values from `details`
  - [x] 5.3 Display fake discount flag as warning indicator (amber/red badge)

- [x] Task 6: Create CalculatorResultsSection orchestrator component (AC: #1-7)
  - [x] 6.1 Create `frontend/src/components/evaluation/calculators/CalculatorResultsSection.tsx`
  - [x] 6.2 Use `useCalculatorResults` to fetch existing results
  - [x] 6.3 Use `useCalculatorStatus` to show pending state with missing file info
  - [x] 6.4 Implement per-calculator pending state (AC: #4)
  - [x] 6.5 Implement per-calculator error state with Retry button (AC: #5)
  - [x] 6.6 Add "Recalculate All" button using `useRunAllCalculators` (AC: #7)
  - [x] 6.7 Handle loading/empty states

- [x] Task 7: Integrate into EvaluationSections (AC: #1-7)
  - [x] 7.1 Replace placeholder calculator cards in `EvaluationSections.tsx` with `CalculatorResultsSection`
  - [x] 7.2 Pass `brandId` to the new component
  - [x] 7.3 Verify cache invalidation works end-to-end (upload → auto-calc → display updates)

- [x] Task 8: Write frontend component tests (AC: #1-5)
  - [x] 8.1 Add test for AdsKeywordResults rendering output_text
  - [x] 8.2 Add test for TopSkuResults rendering tables and average stock
  - [x] 8.3 Add test for DiscountResults rendering values and flag
  - [x] 8.4 Add test for CalculatorResultsSection pending/error/loaded states

## Dev Notes

### Story Context — This is Primarily a Frontend Story

Story 3.7 built the orchestration engine, auto-execute pipeline, and all backend endpoints. This story is about **displaying** the results. The backend change is minimal (one new GET endpoint to fetch stored results). The majority of work is frontend component creation.

### Backend Gap: No GET Endpoint for Stored Results

The current backend has:
- `POST .../calculators/ads_keyword` — **runs** calculator (returns result)
- `POST .../calculators/discount` — **runs** calculator
- `POST .../calculators/top_sku` — **runs** calculator
- `POST .../calculators/run-all` — runs all ready calculators
- `GET .../calculators/status` — returns readiness info (has_result flag, but NOT the actual result data)

**Missing:** A way to **fetch existing results without re-running**. The DB query `get_results_by_brand()` exists in `db/queries/calculator_results.py` but has no router endpoint.

**Solution:** Add `GET /api/v1/evaluations/brands/{brand_id}/calculators/results` that returns all stored calculator results for a brand.

Response shape:
```json
{
  "brand_id": 123,
  "results": [
    {
      "calculator_type": "discount",
      "output_text": "% Diskon TOP SKU: 2.7%\nRange: ...",
      "details": { ... },
      "calculated_at": "2026-02-11T10:30:00Z"
    },
    {
      "calculator_type": "top_sku",
      "output_text": "",
      "details": { "output_1": [...], "output_2": [...], "average_stock": 123 },
      "calculated_at": "2026-02-11T10:31:00Z"
    }
  ]
}
```

### Calculator Result Data Structures — Critical Reference

Each calculator stores results with different `details` structures. The frontend types already exist in `useCalculator.ts`:

**Ads Keyword (`AdsKeywordDetails`):**
```typescript
{
  ak2: string;           // Ad overview line
  ak3: string;           // Ad type breakdown (multi-line)
  ak4: string;           // 7 recommendation flags
  al2: string;           // TOP ads listing
  al3: string;           // ROAS median flag
  al5: string;           // BOTTOM ads listing
  al6: string;           // Keyword flag
  al7: string;           // Keyword flag
  al8: string;           // Keyword flag
  al9: string;           // Keyword flag
  thresholds: { am6, am7, am9, am10 };
}
```
**Display:** Multi-line text. Use `output_text` directly (already formatted) or compose from detail fields. The `output_text` field contains the full formatted text concatenation.

**Top SKU (`TopSkuDetails`):**
```typescript
{
  output_1: Array<{      // Revenue ranking table
    kode_variasi: string;
    product_name: string;
    total_omzet: number;
    rata2_harga_jual: number;
  }>;
  output_2: Array<{      // Stock ranking table
    kode_variasi: string;
    nama_produk: string;
    varian: string;
    stok: number;
  }>;
  average_stock: number;
  product_count: number;
  total_unique_products: number;
}
```
**Display:** Two sortable HTML tables + average stock metric. IDR formatting for currency columns.

**Discount Check (`DiscountDetails`):**
```typescript
{
  discount_pct: string;        // "2.7%"
  range_min: string;           // "0.0%"
  range_max: string;           // "6.7%"
  voucher_pct: string;         // "0.3%"
  paket_pct: string;           // "0.0%"
  fake_discount_flag: boolean; // true = flag triggered
  product_summary: Array<...>;
  top_sku: Array<...>;
  totals: { ... };
}
```
**Display:** 5 formatted text values + warning badge for fake discount flag.

### Frontend Component Architecture

```
EvaluationSections.tsx
  └── CalculatorResultsSection.tsx  ← NEW orchestrator
        ├── AdsKeywordResults.tsx    ← NEW display
        ├── TopSkuResults.tsx        ← NEW display (with sortable tables)
        ├── DiscountResults.tsx      ← NEW display
        └── (pending/error states)   ← inline in orchestrator
```

**File placement:** `frontend/src/components/evaluation/calculators/` — a new subdirectory under evaluation components, following the feature-organized pattern from architecture.

### State Management Design

```
useCalculatorResults(brandId)  → TanStack Query, queryKey: ['calculatorResults', brandId]
useCalculatorStatus(brandId)   → TanStack Query, queryKey: ['calculatorStatus', brandId] (already exists)
useRunAllCalculators(brandId)  → TanStack Mutation (already exists)
useRunCalculator(brandId, type) → TanStack Mutation (already exists)
```

**Cache invalidation flow (already wired from Story 3.7):**
1. Upload file → `useUploadFile` → on success → invalidates `['calculatorResults', brandId]` + `['calculatorStatus', brandId]`
2. Run-all → `useRunAllCalculators` → on success → invalidates same keys
3. Individual run → `useRunCalculator` → on success → invalidates `['calculatorResults', brandId]`

**New hook `useCalculatorResults`** must use queryKey `['calculatorResults', brandId]` to receive invalidations from existing mutation hooks.

### Table Sorting for Top SKU

Use client-side sorting (data is small — max ~20 rows per table). Implement with React state:
```typescript
const [sortField, setSortField] = useState<string>('total_omzet');
const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
const sorted = useMemo(() => [...data].sort(compareFn), [data, sortField, sortDir]);
```

No need for TanStack Table — the tables are simple with 4 columns each. Use existing shadcn/ui Table component with clickable headers.

### IDR Number Formatting

Use existing `formatIDR` utility from `formConfig.ts` if compatible, or use `Intl.NumberFormat`:
```typescript
const formatIDR = (value: number) =>
  new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(value);
```

Check if `formConfig.ts` exports a reusable formatter. The existing `formatIDR` function handles this pattern.

### Pending State Design

Use `useCalculatorStatus` to get per-calculator readiness:
```
Calculator status = "pending" → Show missing files list
Calculator status = "ready" + no result → Show "Ready to calculate" with Run button
Calculator status = "ready" + has_result → Show actual results
```

**Pending message mapping (human-readable file names):**
```typescript
const FILE_LABELS: Record<string, string> = {
  cpc_ad_report: 'CPC Ad Report (.csv)',
  keyword_report: 'Keyword Placement Report (.csv)',
  order_export: 'Order Export (.xlsx)',
  mass_update: 'Mass Update / Sales Info (.xlsx)',
};
```

### Error State Design

If a calculator fails (from run-all or auto-execute), show:
- Error icon + message
- "Retry" button that calls `useRunCalculator(brandId, calculatorType).mutate()`

### Existing Placeholder to Replace

In `EvaluationSections.tsx` (lines ~180-210), there's a static `CALCULATOR_CARDS` array and a map rendering placeholder cards:
```tsx
const CALCULATOR_CARDS = [
  { name: 'Ads Keyword Calculator', description: 'Requires CPC Ad Report + Keyword Placement Report' },
  { name: 'Top SKU Calculator', description: 'Requires Order Export + Mass Update' },
  { name: 'Discount Check Calculator', description: 'Requires Order Export' },
];
```

Replace this entire block with `<CalculatorResultsSection brandId={brandId} />`.

### Project Structure Notes

**New files to create:**
```
frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx
frontend/src/components/evaluation/calculators/TopSkuResults.tsx
frontend/src/components/evaluation/calculators/DiscountResults.tsx
frontend/src/components/evaluation/calculators/CalculatorResultsSection.tsx
frontend/src/components/evaluation/calculators/index.ts
```

**Existing files to modify:**
```
backend/app/modules/evaluations/router.py          ← Add GET results endpoint
backend/app/modules/evaluations/schemas.py         ← Add results list response schema
backend/tests/integration/api/test_calculators.py  ← Add test for GET results endpoint
frontend/src/hooks/useCalculator.ts                ← Add useCalculatorResults hook
frontend/src/services/apiClient.ts                 ← Add GET results path type
frontend/src/components/evaluation/EvaluationSections.tsx ← Replace placeholder with CalculatorResultsSection
```

### Architecture Compliance

**Backend Pattern (MUST follow):**
- New endpoint in `modules/evaluations/router.py` — follows REST convention
- Response schema in `modules/evaluations/schemas.py` — Pydantic model
- Reuse existing `get_results_by_brand()` DB query — no new migrations
- Auth required via `Depends(get_current_user)`
- Exception chaining: always `raise ... from e`

**Frontend Pattern (MUST follow):**
- Components in `components/evaluation/calculators/` — feature-organized
- Hooks use `apiClient.ts` (openapi-fetch) — never raw `fetch()`
- TanStack Query for data fetching — throw errors in queryFn
- Error states have visible UI (error message, retry button) — no swallowed errors
- Use shadcn/ui components (Card, Table, Badge, Button)
- camelCase for variables, PascalCase for components
- Loading states: `isLoading` for initial, `isFetching` for background

**Calculator Architecture (MUST follow):**
```
Frontend components (display)
    ↓ consumes via hooks
Backend GET endpoint (read-only)
    ↓ reads from
calculator_results table (existing — no migrations)
```

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| @tanstack/react-query | existing | Data fetching, cache management | Installed |
| openapi-fetch | existing | Typed API client | Installed |
| shadcn/ui (Card, Table, Badge, Button) | existing | UI components | Installed |
| lucide-react | existing | Icons (AlertTriangle, RefreshCw, Clock) | Installed |
| tailwindcss v4 | existing | Styling | Installed |

**No new dependencies needed.** All required libraries are already installed.

### Testing Requirements

**Backend Integration Tests (pytest):**
```
backend/tests/integration/api/test_calculators.py:
  - test_get_calculator_results_returns_all_results
  - test_get_calculator_results_empty_when_none
  - test_get_calculator_results_auth_required
```

**Frontend Component Tests (vitest):**
```
frontend/src/components/evaluation/calculators/AdsKeywordResults.test.tsx:
  - test renders output_text preserving line breaks
  - test renders calculated_at timestamp

frontend/src/components/evaluation/calculators/TopSkuResults.test.tsx:
  - test renders revenue table with IDR formatting
  - test renders stock table
  - test renders average stock metric
  - test table sorting changes order

frontend/src/components/evaluation/calculators/DiscountResults.test.tsx:
  - test renders 5 text values
  - test renders fake discount warning when flag true
  - test hides warning when flag false

frontend/src/components/evaluation/calculators/CalculatorResultsSection.test.tsx:
  - test renders results when data available
  - test shows pending state with missing files
  - test shows error state with retry button
  - test recalculate all button triggers mutation
```

Run commands:
- Backend: `cd backend && uv run python -m pytest -v`
- Frontend: `cd frontend && npx vitest run --reporter=verbose`

### Previous Story Intelligence

**From Story 3.7 (Calculator Orchestration):**
- `useCalculatorStatus` and `useRunAllCalculators` hooks already exist and work
- Cache invalidation already wired: upload → invalidate `calculatorResults` and `calculatorStatus` keys
- `ProcessUploadResponse` includes `auto_calculated` array — upload triggers auto-calc and cache invalidation
- 371 tests currently pass (baseline) — maintain full regression
- Engine architecture: `engine.py` → `calculator_service.py` → `calculators/*.py`

**From Story 3.3 (Manual Data Input Form):**
- `formConfig.ts` has `formatIDR()` and `parseIDR()` utilities — reuse for Top SKU IDR columns
- EvaluationSections.tsx pattern: section refs with IntersectionObserver for active section tracking
- Auto-save with debounce pattern established

**From Code Reviews (all stories):**
- Response schemas must match ACs field-by-field
- Frontend hooks must use `apiClient.ts` — never raw `fetch()`
- Error states must have visible UI — no swallowed errors
- File List must include ALL changed files

### Git Intelligence

Recent commits (Story 3.7 merged to develop):
```
ac9b73f Merge feature/3-7-calculator-orchestration-and-auto-execute into develop
4602956 Mark Story 3.7 done after code review — all issues resolved
3630ea5 Fix 9 code review issues for Story 3.7 (2H/4M/3L)
```

**Patterns to follow:**
- Feature branch naming: `feature/3-8-calculator-results-display`
- Atomic commits per task
- Tests committed alongside implementation

### How This Feeds into Story 3.9 (Final Scoring)

Story 3.9 needs calculator results displayed so users can see the data before generating the final score. The components built here will remain visible alongside the final scoring section. Specifically:
- Calculator 2 `average_stock` feeds into scoring D70 (stock score)
- Calculator 3 `fake_discount_flag` feeds into scoring D73 (discount score)
- Users need to verify calculator outputs are correct before triggering final scoring

### How This Feeds into Story 3.10 (Save Evaluation)

Story 3.10 saves completed evaluations with snapshots of all calculator outputs. The display components from this story will also be reused in the evaluation detail view (Story 4.5) for showing historical evaluation data.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.8 — Story 3.8 ACs, FR16]
- [Source: _bmad-output/planning-artifacts/architecture.md — Frontend patterns, component structure, naming conventions]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md — Score Panel anatomy, calculator results display]
- [Source: _bmad-output/planning-artifacts/prd.md — FR16: View calculator results]
- [Source: _bmad-output/implementation-artifacts/3-7-calculator-orchestration-and-auto-execute.md — Previous story, hooks, endpoints]
- [Source: backend/app/modules/evaluations/router.py — Existing calculator endpoints]
- [Source: backend/app/modules/evaluations/schemas.py — Existing response schemas]
- [Source: backend/app/db/queries/calculator_results.py — get_results_by_brand query]
- [Source: backend/app/calculators/engine.py — Orchestration engine, dependency maps]
- [Source: frontend/src/hooks/useCalculator.ts — Calculator hooks, types (AdsKeywordDetails, TopSkuDetails, DiscountDetails)]
- [Source: frontend/src/hooks/useUpload.ts — Cache invalidation on upload]
- [Source: frontend/src/services/apiClient.ts — API path types]
- [Source: frontend/src/components/evaluation/EvaluationSections.tsx — Placeholder calculator cards to replace]
- [Source: frontend/src/components/evaluation/forms/formConfig.ts — formatIDR utility]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, testing patterns]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

No blocking issues encountered during implementation.

### Completion Notes List

- **Task 1:** Added `GET /api/v1/evaluations/brands/{brand_id}/calculators/results` endpoint with `CalculatorResultsListResponse` and `CalculatorResultItem` schemas. Wired to existing `get_results_by_brand()` DB query. 3 integration tests added (auth required, returns all results, empty when none).
- **Task 2:** Added GET results path type to `apiClient.ts`. Created `useCalculatorResults(brandId)` query hook with queryKey `['calculatorResults', brandId]` matching existing cache invalidation in `useRunCalculator`, `useRunAllCalculators`, and `useUploadFile`.
- **Task 3:** Created `AdsKeywordResults.tsx` — renders `output_text` in `<pre>` tag preserving multi-line formatting, displays `calculated_at` timestamp.
- **Task 4:** Created `TopSkuResults.tsx` — two sortable tables (revenue ranking with IDR formatting via `formatIDR`, stock ranking), average stock metric in header. Client-side sort with React state using `useMemo`.
- **Task 5:** Created `DiscountResults.tsx` — displays 5 text values (discount_pct, range, voucher, paket_pct) plus destructive Badge for fake discount flag when true.
- **Task 6:** Created `CalculatorResultsSection.tsx` — orchestrator fetching results + status, rendering per-calculator cards with pending (missing files list), error (with Retry button), and loaded states. "Recalculate All" button triggers `useRunAllCalculators`.
- **Task 7:** Replaced `CALCULATOR_CARDS` placeholder in `EvaluationSections.tsx` with `<CalculatorResultsSection brandId={brandId} />`. Removed unused `Calculator` icon import.
- **Task 8:** 13 frontend tests across 4 test files covering all components and states.

### Change Log

- 2026-02-11: Implemented Story 3.8 — Calculator Results Display (all 8 tasks)

### File List

**New files:**
- frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx
- frontend/src/components/evaluation/calculators/AdsKeywordResults.test.tsx
- frontend/src/components/evaluation/calculators/TopSkuResults.tsx
- frontend/src/components/evaluation/calculators/TopSkuResults.test.tsx
- frontend/src/components/evaluation/calculators/DiscountResults.tsx
- frontend/src/components/evaluation/calculators/DiscountResults.test.tsx
- frontend/src/components/evaluation/calculators/CalculatorResultsSection.tsx
- frontend/src/components/evaluation/calculators/CalculatorResultsSection.test.tsx
- frontend/src/components/evaluation/calculators/index.ts

**Modified files:**
- backend/app/modules/evaluations/router.py
- backend/app/modules/evaluations/schemas.py
- backend/tests/integration/api/test_calculators.py
- frontend/src/hooks/useCalculator.ts
- frontend/src/services/apiClient.ts
- frontend/src/components/evaluation/EvaluationSections.tsx
- _bmad-output/implementation-artifacts/sprint-status.yaml
