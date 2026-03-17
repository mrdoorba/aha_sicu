# S04: Frontend Currency and Marketplace UI — UAT

**Milestone:** M001
**Written:** 2026-03-17

## UAT Type

- UAT mode: mixed (artifact-driven for test verification + live-runtime for visual/network checks)
- Why this mode is sufficient: Core logic verified by 536 vitest tests (artifact-driven). Visual layout and API contract require browser Network tab and UI inspection (live-runtime). No external integration or production deployment needed.

## Preconditions

- Frontend dev server running: `cd frontend && npm run dev` (typically http://localhost:5173)
- Backend API running: `cd backend && uvicorn app.main:app` (typically http://localhost:8000)
- Database migrated through migration 027 (THB rules seeded)
- At least one brand exists in the system for evaluation flow testing

## Smoke Test

Navigate to the Rules page → confirm two tabs appear: "🇮🇩 Indonesia (IDR)" and "🇹🇭 Thailand (THB)". Click the Thailand tab → confirm the page re-fetches and shows THB threshold values.

## Test Cases

### 1. Currency Formatting Utilities

1. Run `cd frontend && npx vitest run src/components/evaluation/forms/formUtils.test.ts --reporter=verbose`
2. **Expected:** 19/19 tests pass — formatCurrency handles both marketplaces, parseCurrency round-trips correctly, getCurrencyCode maps TH→THB and ID→IDR, deprecated formatIDR/parseIDR still work

### 2. CurrencyField Component Variants

1. Run `cd frontend && npx vitest run src/components/evaluation/forms/CurrencyField.test.tsx --reporter=verbose`
2. **Expected:** 9/9 tests pass — existing 7 tests + THB variant renders "(THB)" label + unknown currency "XX" renders "(XX)" without crash

### 3. Rules Page Marketplace Tabs — Default State

1. Navigate to Rules page (e.g. http://localhost:5173/rules)
2. **Expected:** Two tabs visible: "🇮🇩 Indonesia (IDR)" (active) and "🇹🇭 Thailand (THB)". Rule values shown are IDR thresholds.

### 4. Rules Page Marketplace Tabs — Tab Switch

1. On Rules page, click "🇹🇭 Thailand (THB)" tab
2. Open browser Network tab
3. **Expected:** GET request fires to `/api/v1/rules?marketplace=TH`. Page shows THB threshold values (e.g. six_month_avg_threshold ≈ 190,000 vs IDR 100,000,000).

### 5. Rules Page — Edit Cancellation on Tab Switch

1. On Rules page with IDR tab active, click Edit button
2. Change a threshold value (do NOT save)
3. Click "🇹🇭 Thailand (THB)" tab
4. **Expected:** Edit mode is cancelled — Save/Cancel buttons disappear, unsaved edits are discarded. The Thailand tab shows its own values.

### 6. Rules Page — THB Rule Editing

1. On Rules page, switch to Thailand tab
2. Click Edit, change a threshold value, click Save
3. Open Network tab
4. **Expected:** PUT request fires to `/api/v1/rules/default?marketplace=TH`. After save, the updated value persists when switching away and back to TH tab.

### 7. Evaluation Page — Marketplace Selector

1. Navigate to an evaluation page for any brand
2. **Expected:** Marketplace radio selector visible above the Fashion/Non-Fashion selector. "🇮🇩 Indonesia" is selected by default.

### 8. Evaluation Page — Switch to Thailand

1. On evaluation page, select "🇹🇭 Thailand" radio option
2. **Expected:** All CurrencyField labels change from "(IDR)" to "(THB)". Marketplace badge in header shows "🇹🇭 TH".

### 9. Evaluation Auto-Save Includes Marketplace

1. On evaluation page with Thailand selected, edit any currency field value
2. Wait for auto-save to trigger
3. Open browser Network tab, inspect the PUT request body
4. **Expected:** PUT request to `/api/v1/evaluations/brands/{id}` body contains `"marketplace": "TH"` alongside the form data.

### 10. Evaluation Save Includes Marketplace

1. On evaluation page with Thailand selected, click Save Evaluation
2. Open browser Network tab, inspect the POST request body
3. **Expected:** POST request to `/api/v1/evaluations/brands/{id}/save` body contains `"marketplace": "TH"`.

### 11. Evaluation Detail Page — Marketplace-Aware Display

1. Open an evaluation detail page for a previously saved evaluation
2. **Expected:** Currency values are formatted using the evaluation's marketplace. If marketplace field is absent (older evaluations), defaults to IDR formatting.

### 12. Top SKU Results — Marketplace Currency

1. On evaluation page with Thailand selected, trigger calculator that shows TopSkuResults
2. **Expected:** Revenue columns show "THB" prefix instead of "IDR" with marketplace-aware number formatting.

### 13. Data Intelligence — Marketplace Currency

1. Navigate to a presentation dashboard with Data Intelligence section
2. **Expected:** Revenue values use marketplace-aware formatting from the evaluation's marketplace field.

### 14. Business Form Average Display

1. On evaluation page, fill in at least 2 monthly sales values in the Business section
2. **Expected:** Computed average displays with correct currency prefix (e.g. "THB 125,000" when Thailand selected, "IDR 125,000" when Indonesia selected).

### 15. Full Test Suite Regression Check

1. Run `cd frontend && npx vitest run --reporter=verbose`
2. **Expected:** 63 test files, 536 tests passed, 1 skipped, 0 failures.

### 16. IDR Grep Audit

1. Run `grep -rn "formatIDR\|formatCurrencyDisplay" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v deprecated`
2. **Expected:** Only formUtils.ts and formConfig.ts barrel export lines. Zero hits in any component or page file.

## Edge Cases

### Unknown Currency Code

1. (Developer test) Render `<CurrencyField currency="XX" />` in isolation
2. **Expected:** Renders "(XX)" as the label, uses default number formatting, no crash. Verified by `CurrencyField.test.tsx` test case.

### Rapid Tab Switching on Rules Page

1. Click between IDR and THB tabs rapidly (5+ times in 2 seconds)
2. **Expected:** No stale data displayed. Final state matches whichever tab is active. React Query handles request cancellation/deduplication.

### Evaluation Page — Save Without Marketplace Change

1. On evaluation page with default Indonesia selected, save evaluation
2. **Expected:** POST body contains `"marketplace": "ID"`. No regression from adding marketplace to the flow.

### Older Evaluations Without Marketplace Field

1. Open an evaluation detail page for an evaluation saved before M001 (no marketplace column)
2. **Expected:** Page renders without error. Currency values display with default IDR formatting (graceful fallback for undefined marketplace).

## Failure Signals

- Any of the 536 tests failing — indicates regression in formatting, component rendering, or hook wiring
- `formatCurrencyDisplay` or local `formatIDR` appearing in grep audit outside formUtils/formConfig — indicates incomplete migration
- PUT/POST request bodies missing `marketplace` field — evaluation will be scored with wrong rules (backend defaults to ID)
- React Query devtools showing only `['rules']` without marketplace dimension — indicates cache key regression, risk of stale cross-marketplace data
- CurrencyField labels showing "(IDR)" after selecting Thailand marketplace — indicates currency prop not threaded correctly
- Console errors or blank page on marketplace switch — indicates missing prop or type error

## Requirements Proved By This UAT

- DATA-01 — Test cases 9, 10 prove marketplace is stored via PUT/POST request bodies
- RULES-01 — Test cases 3, 4 prove marketplace tabs exist and work
- RULES-02 — Test cases 5, 6 prove independent THB editing with cross-marketplace protection
- EVAL-01 — Test cases 7, 8 prove marketplace selector exists and is functional
- EVAL-02 — Test cases 8, 12, 14 prove currency code prefix changes with marketplace
- EVAL-03 — Test cases 11, 12, 13, 14 prove display components use correct formatting

## Not Proven By This UAT

- SCORE-03 (full end-to-end) — This UAT does not verify that selecting TH marketplace on the evaluation page actually causes the backend to score with THB thresholds and return THB-specific results. That requires a live evaluation with calculator execution, which crosses the frontend boundary into backend scoring logic (covered by S02 backend tests, but not by an integrated E2E test).
- Exchange rate accuracy — THB seed values were set by S01 migration; this UAT does not verify the conversion math is correct.
- Multi-user concurrency — No test for two admins editing IDR and THB rules simultaneously.

## Notes for Tester

- The "1 skipped" test in the full suite is an existing pre-S04 test — not related to marketplace changes.
- `fields.ts` still has `unit: 'IDR'` on ~25 field definitions. This is cosmetic — the render layer overrides with the `currency` prop. Don't flag these as bugs.
- The marketplace selector defaults to Indonesia on page load every time. There is no persistence of marketplace selection per brand — this is by design for M001. A future enhancement could auto-select based on brand metadata.
- The backend evaluation detail API may not return a `marketplace` field for evaluations saved before M001. The frontend handles this gracefully — it renders with IDR formatting as default.
