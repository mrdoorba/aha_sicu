# Story 3.3: Manual Data Input Form

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team member**,
I want **to enter manual data values for a brand evaluation organized by scoring categories**,
so that **I can provide the ~40 fields required by the scoring system**.

## Acceptance Criteria

1. **Form fields organized by scoring system categories**
   **Given** I am on the evaluation page for a brand
   **When** I view the Manual Input sections (Sections 1, 2, 3, and 5)
   **Then** I see form fields organized by these categories:

   | Section | Category | Fields | Input Types |
   |---------|----------|--------|-------------|
   | 1 | Operational (rows 7-11) | Pesanan Tidak Terselesaikan (%), Keterlambatan (%), Masa Pengemasan (days), Chat Dibalas (%), Penilaian (rating) | 5 number inputs |
   | 2 | Business (rows 13-18, 20) | Monthly sales for 6 months (IDR), Conversion rate (%) | 7 number inputs |
   | 2 | Content (rows 22-23) | "Perlu ditingkatkan" count, "Kualitas baik" count | 2 number inputs |
   | 2 | Visitors (rows 26-27, 29) | Total Pengunjung, Pengunjung Lama, Total Pengikut | 3 number inputs |
   | 3 | Promo Tools (rows 31-41) | 11 promo tool revenue fields (IDR each): Promo Toko, Paket Diskon, Kombo Hemat, Flash Sale Toko Saya, Voucher, Shopee Live, Game Toko, Brand Membership, Gratis Ongkir XTRA, Chat Broadcast, Program Afiliasi | 11 number inputs |
   | 3 | Products/Status (rows 45-46) | Jumlah Produk (count), Status Toko (dropdown: Shopee Mall / Star+ / Star / Regular) | 1 number + 1 select |
   | 5 | Ads (rows 48-49) | Penjualan iklan (IDR), Biaya iklan (IDR) | 2 number inputs |
   | 5 | Campaign (rows 55-56) | Sesi dinominasikan (count), Sesi tersedia (count) | 2 number inputs |
   | 5 | Competition (rows 61-63) | Top 3 competitor products: keyword (text) + market average price (IDR) each | 3 text + 3 number inputs |

   **And** the total is ~40 form controls across 9 categories
   **And** each field has an appropriate input type (number for IDR/percentages/counts, text for keywords, dropdown for Status Toko)

2. **Benchmark helper text on fields**
   **Given** I am viewing the manual input fields
   **When** I look at a field that has a scoring benchmark
   **Then** I see helper text below the field showing the benchmark value:
     - Operational: "<1%", "<1", ">95%", ">4.7"
     - Business: conversion ">3%" (Non-Fashion) or ">2%" (Fashion)
     - Visitors: followers ">50,000"
     - Promo Tools: each tool shows its benchmark % (e.g., ">8%", ">16%", etc.)
     - Products: ">=35"
     - Status: "Shopee Mall"
     - Ads ROI: ">9" (Non-Fashion) or ">8" (Fashion)
     - Campaign: ">90%"
   **And** Fashion-specific benchmarks update when the Fashion/Non-Fashion category selector changes

3. **IDR number formatting on currency fields**
   **Given** I am entering a value in an IDR currency field (sales, promo revenues, ad costs)
   **When** I type or blur the field
   **Then** the displayed value shows Indonesian number formatting (e.g., "125.000.000" for 125 million)
   **And** the stored value is a plain number (no formatting characters)

4. **Auto-save on field change**
   **Given** I fill in or change a manual input field
   **When** I blur the field (or after a short debounce ~500ms)
   **Then** the form auto-saves via `PUT /api/v1/evaluations/brands/{brand_id}`
   **And** I see a "Saved" indicator (timestamp or "Saved just now")
   **And** only the changed `manual_data` JSONB is sent (preserving other fields via COALESCE)

5. **Pre-fill previously entered data**
   **Given** I return to an evaluation page for a brand I previously entered data for
   **When** the page loads
   **Then** all previously saved manual data fields are pre-filled from `evaluation_inputs.manual_data`
   **And** the Fashion/Non-Fashion selector shows the saved `category_type`

6. **Edit existing manual data**
   **Given** I want to change a previously entered value
   **When** I modify a field and blur
   **Then** the new value auto-saves (upsert via existing API)
   **And** the "Saved" indicator updates

7. **Status Toko dropdown**
   **Given** I am viewing the Products/Status section
   **When** I interact with the Status Toko field
   **Then** I see a dropdown/select with options: "Shopee Mall", "Star+", "Star", "Regular"
   **And** the selected value is stored in `manual_data.products.storeStatus`

8. **Section progress indication**
   **Given** I am filling in manual data
   **When** I complete fields in a section
   **Then** the section navigation (left sidebar) reflects progress
   **And** sections with all fields filled show a completion indicator

## Tasks / Subtasks

- [x] Task 1: Create form field configuration constants (AC: #1, #2)
  - [x] 1.1 Create `frontend/src/components/evaluation/forms/formConfig.ts` with:
    - Field definitions per category: field key, label, input type, unit (%, IDR, days, rating, count), benchmark value, benchmark display text, Fashion-specific benchmark (if different)
    - Category definitions: category key, display name, fields array, Shopee link URL template
    - `MANUAL_DATA_FIELDS` constant mapping all 9 categories
  - [x] 1.2 Define TypeScript types for `ManualData` structure matching JSONB schema:
    - `OperationalData`, `BusinessData`, `ContentData`, `VisitorsData`, `PromoToolsData`, `ProductsData`, `AdsData`, `CampaignData`, `CompetitionData`
    - Root `ManualData` type combining all categories

- [x] Task 2: Create reusable form field components (AC: #1, #2, #3)
  - [x] 2.1 Create `frontend/src/components/evaluation/forms/NumberField.tsx`:
    - Accepts: name, label, unit, benchmark, helperText, value, onChange, onBlur
    - Renders shadcn Input with type="text" (for IDR formatting) or type="number"
    - Shows benchmark as helper text below field (muted color)
    - Shows unit label (%, IDR, days, etc.)
  - [x] 2.2 Create `frontend/src/components/evaluation/forms/CurrencyField.tsx`:
    - Extends NumberField with IDR formatting (dot thousands separator)
    - Formats display value on blur, strips formatting on focus for raw number editing
    - Stores plain number in form state
  - [x] 2.3 Create `frontend/src/components/evaluation/forms/SelectField.tsx`:
    - Accepts: name, label, options, benchmark, value, onChange
    - Renders shadcn Select component
    - Used for Status Toko dropdown

- [x] Task 3: Create category form components (AC: #1, #2, #3, #7)
  - [x] 3.1 Create `frontend/src/components/evaluation/forms/OperationalForm.tsx`:
    - 5 fields: unfulfilledOrderRate (%), lateShipmentRate (%), preparationTime (days), chatResponseRate (%), overallRating (rating)
    - Benchmarks: <1%, <1%, <1, >95%, >4.7
  - [x] 3.2 Create `frontend/src/components/evaluation/forms/BusinessForm.tsx`:
    - 7 fields: 6 monthly sales (IDR with CurrencyField), conversionRate (%)
    - Sales labels: current month + 5 previous months
    - Conversion benchmark: >3% (Non-Fashion) or >2% (Fashion) — dynamic based on categoryType prop
  - [x] 3.3 Create `frontend/src/components/evaluation/forms/ContentForm.tsx`:
    - 2 fields: needsImprovement (count), goodQuality (count)
    - No benchmarks on individual fields (benchmark is on derived % konten baik)
  - [x] 3.4 Create `frontend/src/components/evaluation/forms/VisitorsForm.tsx`:
    - 3 fields: totalVisitors (count), returningVisitors (count), totalFollowers (count)
    - Benchmark on followers: >50,000
  - [x] 3.5 Create `frontend/src/components/evaluation/forms/PromoToolsForm.tsx`:
    - 11 fields: all IDR revenue fields using CurrencyField
    - Each with its own benchmark: >8%, >16%, >1%, >1%, >84%, >15%, >1%, >1%, >0, >1%, >18%
    - Benchmark text: "Benchmark: >{x}% dari penjualan"
  - [x] 3.6 Create `frontend/src/components/evaluation/forms/ProductsStatusForm.tsx`:
    - 2 fields: productCount (number, benchmark >=35), storeStatus (dropdown)
    - Status Toko options: Shopee Mall, Star+, Star, Regular
  - [x] 3.7 Create `frontend/src/components/evaluation/forms/AdsForm.tsx`:
    - 2 fields: adSales (IDR), adCost (IDR)
    - No direct benchmarks (derived ROI/% benchmarks are for the scoring calculator)
  - [x] 3.8 Create `frontend/src/components/evaluation/forms/CampaignForm.tsx`:
    - 2 fields: nominatedSessions (count), availableSessions (count)
    - No direct benchmarks (derived % partisipasi benchmark >90% is for scoring)
  - [x] 3.9 Create `frontend/src/components/evaluation/forms/CompetitionForm.tsx`:
    - 3 product groups, each with: keyword (text), marketPrice (IDR)
    - Labels: "Produk Kompetitor 1/2/3"

- [x] Task 4: Create auto-save hook (AC: #4, #5, #6)
  - [x] 4.1 Create `frontend/src/hooks/useAutoSaveForm.ts`:
    - Wraps React Hook Form with auto-save on blur
    - Debounces save calls (500ms)
    - Calls `useSaveEvaluationInputs` mutation on change
    - Merges changed fields into existing `manual_data` (spread, not replace)
    - Returns save status: 'idle' | 'saving' | 'saved' | 'error'
    - Returns last saved timestamp
  - [x] 4.2 Add save status indicator component in form header area:
    - Shows "Saving..." with spinner during save
    - Shows "Saved just now" / "Saved X min ago" after save
    - Shows "Save failed. Retry" on error with retry action

- [x] Task 5: Integrate forms into EvaluationSections (AC: #1, #4, #5, #8)
  - [x] 5.1 Update `EvaluationSections.tsx` Section 1:
    - Replace `SectionPlaceholder` for "Operational Metrics" with `OperationalForm`
    - Pass `manualData`, `onFieldChange`, `categoryType` props
  - [x] 5.2 Update `EvaluationSections.tsx` Section 2:
    - Replace placeholders with `BusinessForm`, `ContentForm`, `VisitorsForm`
  - [x] 5.3 Update `EvaluationSections.tsx` Section 3:
    - Replace placeholders with `PromoToolsForm`, `ProductsStatusForm`
  - [x] 5.4 Update `EvaluationSections.tsx` Section 5:
    - Replace placeholders for "Ads Metrics", "Campaign", "Competition" with `AdsForm`, `CampaignForm`, `CompetitionForm`
    - Keep calculator results and final score placeholders unchanged (Stories 3.8, 3.9)
  - [x] 5.5 Wire auto-save:
    - Initialize React Hook Form with `useForm<ManualData>()` in `EvaluationSections` or parent
    - Pre-fill from `evaluationState.manual_data`
    - Connect `useAutoSaveForm` hook for debounced save to API
    - Pass `categoryType` to forms with Fashion-specific benchmarks

- [x] Task 6: Write frontend tests (AC: #1, #2, #3, #4, #5, #7)
  - [x] 6.1 Test `NumberField` renders label, input, benchmark helper text
  - [x] 6.2 Test `CurrencyField` formats IDR value on blur, strips on focus
  - [x] 6.3 Test `SelectField` renders options and fires onChange
  - [x] 6.4 Test `OperationalForm` renders 5 fields with correct benchmarks
  - [x] 6.5 Test `BusinessForm` renders 7 fields, Fashion benchmark switches conversion threshold
  - [x] 6.6 Test `PromoToolsForm` renders 11 fields with benchmarks
  - [x] 6.7 Test `ProductsStatusForm` renders dropdown with 4 options
  - [x] 6.8 Test `CompetitionForm` renders 3 product groups with text + number inputs
  - [x] 6.9 Test `EvaluationSections` renders form fields instead of placeholders
  - [x] 6.10 Test pre-fill: when `evaluationState.manual_data` has values, forms show them
  - [x] 6.11 Test auto-save: changing a field triggers save mutation after debounce

## Dev Notes

### This Is a Frontend-Only Story

**No backend changes required.** The API and database already support everything this story needs:
- `evaluation_inputs` table exists with `manual_data JSONB` column (Migration 006)
- `PUT /api/v1/evaluations/brands/{brand_id}` accepts `{ category_type, manual_data }` and upserts
- `GET /api/v1/evaluations/brands/{brand_id}` returns saved state including `manual_data`
- Backend uses `COALESCE` in the upsert query — sending partial `manual_data` preserves existing values

All work is in `frontend/` — form components, auto-save hook, and integration into existing EvaluationSections.

### Manual Data JSONB Structure

The `manual_data` field in `evaluation_inputs` stores a nested object. This is the canonical structure the forms must read/write:

```typescript
interface ManualData {
  operational: {
    unfulfilledOrderRate: number | null;   // Row 7: % (e.g., 0.005 = 0.5%)
    lateShipmentRate: number | null;       // Row 8: % (e.g., 0.003 = 0.3%)
    preparationTime: number | null;        // Row 9: days (e.g., 0.8)
    chatResponseRate: number | null;       // Row 10: % (e.g., 0.97 = 97%)
    overallRating: number | null;          // Row 11: rating (e.g., 4.8)
  };
  business: {
    salesMonth0: number | null;            // Row 13: current month IDR
    salesMonth1: number | null;            // Row 14: previous month IDR
    salesMonth2: number | null;            // Row 15: IDR
    salesMonth3: number | null;            // Row 16: IDR
    salesMonth4: number | null;            // Row 17: IDR
    salesMonth5: number | null;            // Row 18: IDR
    conversionRate: number | null;         // Row 20: % (e.g., 0.035 = 3.5%)
  };
  content: {
    needsImprovement: number | null;       // Row 22: count
    goodQuality: number | null;            // Row 23: count
  };
  visitors: {
    totalVisitors: number | null;          // Row 26: count
    returningVisitors: number | null;      // Row 27: count
    totalFollowers: number | null;         // Row 29: count
  };
  promoTools: {
    promoToko: number | null;              // Row 31: IDR
    paketDiskon: number | null;            // Row 32: IDR
    komboHemat: number | null;             // Row 33: IDR
    flashSale: number | null;              // Row 34: IDR
    voucher: number | null;               // Row 35: IDR
    shopeeLive: number | null;             // Row 36: IDR
    gameToko: number | null;               // Row 37: IDR
    brandMembership: number | null;        // Row 38: IDR
    gratisOngkir: number | null;           // Row 39: IDR
    chatBroadcast: number | null;          // Row 40: IDR
    programAfiliasi: number | null;        // Row 41: IDR
  };
  products: {
    productCount: number | null;           // Row 45: count
    storeStatus: string | null;            // Row 46: "Shopee Mall" | "Star+" | "Star" | "Regular"
  };
  ads: {
    adSales: number | null;                // Row 48: IDR
    adCost: number | null;                 // Row 49: IDR
  };
  campaign: {
    nominatedSessions: number | null;      // Row 55: count
    availableSessions: number | null;      // Row 56: count
  };
  competition: {
    product1: { keyword: string | null; marketPrice: number | null }; // Row 61
    product2: { keyword: string | null; marketPrice: number | null }; // Row 62
    product3: { keyword: string | null; marketPrice: number | null }; // Row 63
  };
}
```

**Storage convention**: Percentages are stored as decimals (0.035 = 3.5%), IDR amounts as plain integers (125000000), counts as integers, ratings as decimals (4.8). The UI displays them in human-friendly format but stores the raw number.

### Scoring Template Field Mapping

Each form field maps to a specific row in the 75-row scoring template. This mapping is critical — downstream Story 3.9 (Final Scoring) will consume this data by key name.

| Category | Field Key | Scoring Row | D Column | Benchmark (E) |
|----------|-----------|-------------|----------|---------------|
| operational | unfulfilledOrderRate | 7 | Manual % | <1% |
| operational | lateShipmentRate | 8 | Manual % | <1% |
| operational | preparationTime | 9 | Manual days | <1 |
| operational | chatResponseRate | 10 | Manual % | >95% |
| operational | overallRating | 11 | Manual rating | >4.7 |
| business | salesMonth0 | 13 | Manual IDR | >[6mo avg] |
| business | salesMonth1-5 | 14-18 | Manual IDR | — |
| business | conversionRate | 20 | Manual % | >3% (>2% Fashion) |
| content | needsImprovement | 22 | Manual count | — |
| content | goodQuality | 23 | Manual count | — |
| visitors | totalVisitors | 26 | Manual count | — |
| visitors | returningVisitors | 27 | Manual count | — |
| visitors | totalFollowers | 29 | Manual count | >50000 |
| promoTools | promoToko | 31 | Manual IDR | >8% of sales |
| promoTools | paketDiskon | 32 | Manual IDR | >16% of sales |
| promoTools | komboHemat | 33 | Manual IDR | >1% of sales |
| promoTools | flashSale | 34 | Manual IDR | >1% of sales |
| promoTools | voucher | 35 | Manual IDR | >84% of sales |
| promoTools | shopeeLive | 36 | Manual IDR | >15% of sales |
| promoTools | gameToko | 37 | Manual IDR | >1% of sales |
| promoTools | brandMembership | 38 | Manual IDR | >1% of sales |
| promoTools | gratisOngkir | 39 | Manual IDR | >0 |
| promoTools | chatBroadcast | 40 | Manual IDR | >1% of sales |
| promoTools | programAfiliasi | 41 | Manual IDR | >18% of sales |
| products | productCount | 45 | Manual count | >=35 |
| products | storeStatus | 46 | Manual text | Shopee Mall |
| ads | adSales | 48 | Manual IDR | — |
| ads | adCost | 49 | Manual IDR | — |
| campaign | nominatedSessions | 55 | Manual count | — |
| campaign | availableSessions | 56 | Manual count | — |
| competition | product1.keyword | 61 | Manual text | — |
| competition | product1.marketPrice | 61 | Manual IDR | — |
| competition | product2.keyword | 62 | Manual text | — |
| competition | product2.marketPrice | 62 | Manual IDR | — |
| competition | product3.keyword | 63 | Manual text | — |
| competition | product3.marketPrice | 63 | Manual IDR | — |

**Note on promo benchmarks**: The promo tool benchmarks (>8%, >16%, etc.) are percentages of current month sales (Row 13 / `salesMonth0`). The display should show "Benchmark: >{x}% dari penjualan" as helper text. The actual pass/fail calculation happens in the scoring calculator (Story 3.9), not in this form.

### IDR Formatting Strategy

Currency fields need display formatting but must store plain numbers:

```
User types: 125000000
On blur display: "125.000.000"
On focus: back to "125000000" (or keep formatted, strip on save)
Stored in manual_data: 125000000 (plain number)
```

**Implementation approach**: Use a controlled input with `type="text"`. On blur, format with dot separators. On focus, strip formatting. On save, ensure the value is a plain number. Use a shared `formatIDR(value)` / `parseIDR(formatted)` utility.

### Auto-Save Architecture

The auto-save flow builds on the existing pattern from the category selector:

```
Field blur/change → debounce 500ms → merge into manual_data → PUT /api/v1/evaluations/brands/{brand_id}
```

**Key considerations:**
1. **Merge, don't replace**: The save must send the FULL `manual_data` object (merging the changed field into the existing state). The backend COALESCE handles null fields, but the frontend should always send the complete `manual_data` to avoid data loss.
2. **Debounce across fields**: If the user tabs rapidly through fields, debounce should coalesce multiple changes into a single save call.
3. **Optimistic updates**: Use TanStack Query's `onMutate` to update the local cache immediately, then let the mutation confirm.
4. **Error recovery**: On save failure, show error indicator. Don't block the user from continuing to enter data. Retry on next field change.
5. **React Hook Form integration**: Use `useForm()` with `defaultValues` from `evaluationState.manual_data`. Use `watch()` or `onBlur` handler to trigger saves.

### Existing Code to Build On

**EvaluationSections.tsx** — Current placeholder structure to replace:
- Section 1: `SectionPlaceholder` for "Operational Metrics — 5 fields" → replace with `OperationalForm`
- Section 2: Three `SectionPlaceholder`s for Business (8 fields), Content (2 fields), Visitors (4 fields)
- Section 3: Two `SectionPlaceholder`s for Promo Tools (11 fields), Products/Status (2 fields)
- Section 5: Three `SectionPlaceholder`s for Ads (2+3 fields), Campaign (2 fields), Competition (3 fields)
- Section 4 (File Upload) — already fully implemented in Story 3.2, DO NOT TOUCH

**EvaluationPage.tsx** — Already passes `brandId` to `EvaluationSections`, has `useEvaluationState(brandId)` and `useSaveEvaluationInputs(brandId)`.

**useEvaluation.ts** — Existing hooks:
- `useEvaluationState(brandId)`: GET evaluation state (returns `{ brand_id, category_type, manual_data, updated_at }`)
- `useSaveEvaluationInputs(brandId)`: PUT mutation (accepts `{ category_type?, manual_data? }`)
- These hooks already exist and work. DO NOT recreate them. Wire the new forms into these.

**Category selector** — Already in Section 1 of EvaluationSections.tsx (RadioGroup for Fashion/Non-Fashion). Keep it — just add the form fields below it.

### Architecture Compliance

**Frontend Pattern (MUST follow):**
- Components in `src/components/evaluation/forms/` (new `forms/` subdirectory under existing `evaluation/`)
- Hooks in `src/hooks/`
- Use existing `apiClient.ts` — DO NOT add new API endpoints or types (the evaluation endpoints already exist)
- Use TanStack Query mutations via existing `useSaveEvaluationInputs` hook
- Use React Hook Form for form state management (`react-hook-form` already installed v7.71.1)
- Use shadcn/ui components: Input, Label, Card, Select (all already installed)
- Component naming: `PascalCase.tsx` files, `camelCase` variables/functions

**What This Story Does NOT Do:**
1. **NO** new backend endpoints — existing GET/PUT evaluation endpoints are sufficient
2. **NO** new database migrations — `evaluation_inputs.manual_data` JSONB already exists
3. **NO** calculator execution — that is Story 3.7
4. **NO** score calculation — that is Story 3.9
5. **NO** field-level validation (required/range) — form accepts any value, scoring calculator handles business logic
6. **NO** changes to Section 4 (File Upload) — that is complete from Story 3.2
7. **NO** changes to calculator results or final score placeholders in Section 5 — Stories 3.8/3.9

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| react-hook-form | ^7.71.1 | Form state management, field registration, watch | Installed |
| @tanstack/react-query | ^5.90.20 | Mutations via useSaveEvaluationInputs | Installed |
| shadcn/ui (Input, Label, Card, Select) | existing | Form field UI components | Installed |
| lucide-react | existing | Icons (Save, Loader2, Check, AlertCircle) | Installed |

**No new dependencies needed.** All required libraries are already installed.

### Testing Requirements

**Frontend Tests (Vitest + @testing-library/react):**

```
frontend/src/components/evaluation/forms/NumberField.test.tsx       — NumberField rendering + benchmark
frontend/src/components/evaluation/forms/CurrencyField.test.tsx     — IDR formatting on blur/focus
frontend/src/components/evaluation/forms/SelectField.test.tsx       — Dropdown rendering + onChange
frontend/src/components/evaluation/forms/OperationalForm.test.tsx   — 5 fields + benchmarks
frontend/src/components/evaluation/forms/BusinessForm.test.tsx      — 7 fields + Fashion benchmark
frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx    — 11 fields + benchmarks
frontend/src/components/evaluation/forms/ProductsStatusForm.test.tsx — dropdown + number field
frontend/src/components/evaluation/forms/CompetitionForm.test.tsx   — 3 product groups
frontend/src/components/evaluation/forms/EvaluationForms.test.tsx   — Integration: pre-fill + auto-save
```

- Test each reusable field component renders correctly with props
- Test CurrencyField IDR formatting: "125000000" → "125.000.000" on blur, strips on focus
- Test SelectField renders options and fires onChange
- Test category forms render correct number of fields with correct benchmarks
- Test Fashion-specific benchmark switching (BusinessForm conversion threshold)
- Test pre-fill: when `manual_data` has values, forms show them
- Test auto-save: field change triggers debounced save mutation
- Run: `cd frontend && npx vitest run --reporter=verbose`

### Previous Story Intelligence

**From Story 3.2 (Data File Upload):**
- Frontend component pattern: components go in `src/components/evaluation/`
- Test pattern: co-located `.test.tsx` files next to components
- EvaluationSections has `brandId` prop passed from EvaluationPage
- `SectionPlaceholder` component exists for sections not yet implemented — replace these
- shadcn Card + CardContent pattern used for section containers
- Upload section uses `useBrandUploads(brandId)` pattern — follow similar hook usage

**From Story 3.1 (Start Evaluation):**
- EvaluationPage already calls `useEvaluationState(brandId)` and renders `EvaluationSections`
- Category selector (Fashion/Non-Fashion) auto-saves via `useSaveEvaluationInputs` mutation
- Left sidebar `SectionNav` tracks active section — section IDs are `section-1` through `section-5`
- Three-column layout: SectionNav (left) + Main Content (center) + Score Summary placeholder (right)

**From Code Reviews:**
- Exception chaining: always `raise ... from e` (not applicable — frontend only)
- Frontend hooks must use `apiClient.ts` — but for this story, use existing `useEvaluation.ts` hooks directly
- Response schemas must match ACs — verify field names match JSONB keys
- Type definitions must stay in sync between hooks and components

### Git Intelligence

Recent commits show Story 3.2 (file upload) is complete and merged to develop. The last 10 commits:
```
eb761a2 Merge feature/3-2-file-upload-and-parsing into develop
53e452f Fix 8 code review issues for Story 3.2 (1H/4M/3L)
79beb5f Fix parser to match actual Shopee export file formats
6699f02 Mark Story 3.2 complete — all tasks done, status → review
72056b4 Add backend and frontend tests for file upload
```

**Patterns to follow:**
- Feature branch naming: `feature/3-3-manual-data-input-form`
- Atomic commits per task (e.g., "Add form config types", "Add reusable field components", etc.)
- Tests committed alongside implementation

### Code Review Lessons — Pre-Apply

From lessons-learned.md and Story 3.2 review:
- DO NOT use raw `fetch()` — use existing hooks from `useEvaluation.ts`
- Error handling: TanStack Query mutations must have `onError` callback, not swallow errors
- File List must include ALL changed files (check `git diff` before marking done)
- Test assertions must be meaningful — no tautological tests
- Keep types in sync between `formConfig.ts` types and what the API returns

### Project Structure Notes

**New files to create:**

```
frontend/src/components/evaluation/forms/formConfig.ts           — Field definitions, types, benchmarks
frontend/src/components/evaluation/forms/NumberField.tsx          — Reusable number input with benchmark
frontend/src/components/evaluation/forms/NumberField.test.tsx     — Tests
frontend/src/components/evaluation/forms/CurrencyField.tsx       — IDR-formatted currency input
frontend/src/components/evaluation/forms/CurrencyField.test.tsx  — Tests
frontend/src/components/evaluation/forms/SelectField.tsx         — Dropdown component
frontend/src/components/evaluation/forms/SelectField.test.tsx    — Tests
frontend/src/components/evaluation/forms/OperationalForm.tsx     — 5 operational fields
frontend/src/components/evaluation/forms/OperationalForm.test.tsx
frontend/src/components/evaluation/forms/BusinessForm.tsx        — 7 business fields
frontend/src/components/evaluation/forms/BusinessForm.test.tsx
frontend/src/components/evaluation/forms/ContentForm.tsx         — 2 content fields
frontend/src/components/evaluation/forms/VisitorsForm.tsx        — 3 visitor fields
frontend/src/components/evaluation/forms/PromoToolsForm.tsx      — 11 promo tool fields
frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx
frontend/src/components/evaluation/forms/ProductsStatusForm.tsx  — product count + dropdown
frontend/src/components/evaluation/forms/ProductsStatusForm.test.tsx
frontend/src/components/evaluation/forms/AdsForm.tsx             — 2 ads fields
frontend/src/components/evaluation/forms/CampaignForm.tsx        — 2 campaign fields
frontend/src/components/evaluation/forms/CompetitionForm.tsx     — 3 product groups
frontend/src/components/evaluation/forms/CompetitionForm.test.tsx
frontend/src/components/evaluation/forms/SaveIndicator.tsx       — Auto-save status display
frontend/src/hooks/useAutoSaveForm.ts                            — Auto-save hook with debounce
```

**Existing files to modify:**

```
frontend/src/components/evaluation/EvaluationSections.tsx  ← MODIFY: replace SectionPlaceholders with real form components
frontend/src/pages/EvaluationPage.tsx                      ← MODIFY: wire React Hook Form + auto-save (if form state managed at page level)
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Story 3.3 ACs, FR8, FR11]
- [Source: _bmad-output/planning-artifacts/architecture.md — Frontend patterns, React Hook Form, TanStack Query, shadcn/ui]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md — Form patterns, auto-save, field layout, benchmarks]
- [Source: logic/scoring-system-template-sicu.md — All 75 rows, field mapping, benchmarks, score formulas]
- [Source: _bmad-output/implementation-artifacts/3-2-data-file-upload-and-parsing.md — Previous story patterns]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, testing patterns]
- [Source: frontend/src/hooks/useEvaluation.ts — Existing evaluation hooks API]
- [Source: frontend/src/components/evaluation/EvaluationSections.tsx — Current placeholder structure]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Radix UI Select requires `hasPointerCapture`, `setPointerCapture`, `releasePointerCapture`, and `scrollIntoView` mocks in jsdom test setup
- Pre-existing App.test.tsx Firebase API key error (not related to this story)

### Completion Notes List

- Task 1: Created formConfig.ts with ManualData TypeScript types matching JSONB schema, field definitions for all 9 categories with benchmarks, IDR formatting utilities (formatIDR/parseIDR), and EMPTY_MANUAL_DATA default. Added shadcn Select UI component.
- Task 2: Created NumberField (number input with benchmark), CurrencyField (IDR formatting on blur/focus), SelectField (wrapping Radix Select).
- Task 3: Created 9 category forms — OperationalForm (5 fields), BusinessForm (7 fields, Fashion-specific benchmark), ContentForm (2), VisitorsForm (3), PromoToolsForm (11 IDR fields), ProductsStatusForm (number + dropdown), AdsForm (2), CampaignForm (2), CompetitionForm (3 product groups with keyword + price).
- Task 4: Created useAutoSaveForm hook with 500ms debounce, local override state management, deep merge of ManualData categories, save/error/retry status. Created SaveIndicator component.
- Task 5: Replaced all SectionPlaceholder components with real form components in EvaluationSections. Wired useAutoSaveForm in EvaluationPage to manage form state and auto-save on blur. Section 4 (File Upload) and calculator/final score placeholders kept unchanged.
- Task 6: 9 test files with 149 total passing tests. Tests cover field rendering, IDR formatting, benchmarks, dropdown interaction, Fashion benchmark switching, pre-fill, auto-save trigger, and save indicator states.

### Change Log

- 2026-02-11: Implemented Story 3.3 — Manual Data Input Form. Created ~40 form controls across 9 scoring categories with benchmark helper text, IDR formatting, auto-save on blur with debounce, pre-fill from saved data, Status Toko dropdown, Fashion-specific benchmarks. 149 tests pass. 29 files changed.
- 2026-02-11: Code Review Fixes (10 issues: 3H/4M/3L). Fixed: AC #8 section progress in SectionNav, SelectField auto-save trigger, useAutoSaveForm deep merge + memoization + cleanup + tests, MANUAL_DATA_FIELDS competition category, story File List. 167 tests pass.

### Senior Developer Review (AI)

**Reviewer:** Mr. Door | **Date:** 2026-02-11

**Issues Found:** 3 High, 4 Medium, 3 Low — **ALL FIXED**

| # | Severity | Issue | Fix Applied |
|---|----------|-------|-------------|
| H1 | HIGH | AC #8 Section progress indication not implemented | Added `computeSectionProgress()` utility, `SectionNav` now shows filled/total counts + checkmark on completion |
| H2 | HIGH | SelectField dropdown doesn't trigger auto-save | `ProductsStatusForm` now calls `onBlur()` after `onChange` on select |
| H3 | HIGH | `useAutoSaveForm` hook has no unit tests | Created `useAutoSaveForm.test.ts` with 18 tests (pure functions + hook integration) |
| M1 | MEDIUM | Shallow merge of `initialData` loses nested defaults | Extracted `buildManualData()` for deep category-level merge |
| M2 | MEDIUM | `MANUAL_DATA_FIELDS` missing competition category | Added `COMPETITION_FIELDS` constant and competition to `MANUAL_DATA_FIELDS` |
| M3 | MEDIUM | `handleFieldChange` defeats `useCallback` memoization | Refactored to use `manualDataRef` — empty dependency array, stable identity |
| M4 | MEDIUM | Debounce timer not cleared on unmount | Added `useEffect` cleanup for `debounceRef` |
| L1 | LOW | Competition fields not in declarative config | Included via `COMPETITION_FIELDS` (flat key notation for nested fields) |
| L2 | LOW | `triggerSave` used setState hack to read state | Kept functional updater (correct pattern) but extracted `mergeWithOverrides` for clarity |
| L3 | LOW | `sprint-status.yaml` not in File List | Added to File List |

### File List

**New files:**
- frontend/src/components/evaluation/forms/formConfig.ts
- frontend/src/components/evaluation/forms/NumberField.tsx
- frontend/src/components/evaluation/forms/NumberField.test.tsx
- frontend/src/components/evaluation/forms/CurrencyField.tsx
- frontend/src/components/evaluation/forms/CurrencyField.test.tsx
- frontend/src/components/evaluation/forms/SelectField.tsx
- frontend/src/components/evaluation/forms/SelectField.test.tsx
- frontend/src/components/evaluation/forms/OperationalForm.tsx
- frontend/src/components/evaluation/forms/OperationalForm.test.tsx
- frontend/src/components/evaluation/forms/BusinessForm.tsx
- frontend/src/components/evaluation/forms/BusinessForm.test.tsx
- frontend/src/components/evaluation/forms/ContentForm.tsx
- frontend/src/components/evaluation/forms/VisitorsForm.tsx
- frontend/src/components/evaluation/forms/PromoToolsForm.tsx
- frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx
- frontend/src/components/evaluation/forms/ProductsStatusForm.tsx
- frontend/src/components/evaluation/forms/ProductsStatusForm.test.tsx
- frontend/src/components/evaluation/forms/AdsForm.tsx
- frontend/src/components/evaluation/forms/CampaignForm.tsx
- frontend/src/components/evaluation/forms/CompetitionForm.tsx
- frontend/src/components/evaluation/forms/CompetitionForm.test.tsx
- frontend/src/components/evaluation/forms/SaveIndicator.tsx
- frontend/src/components/evaluation/forms/EvaluationForms.test.tsx
- frontend/src/components/ui/select.tsx
- frontend/src/hooks/useAutoSaveForm.ts
- frontend/src/hooks/useAutoSaveForm.test.ts

**Modified files:**
- frontend/src/components/evaluation/EvaluationSections.tsx
- frontend/src/components/evaluation/SectionNav.tsx
- frontend/src/pages/EvaluationPage.tsx
- frontend/src/pages/EvaluationPage.test.tsx
- frontend/src/test/setup.ts
- _bmad-output/implementation-artifacts/sprint-status.yaml
