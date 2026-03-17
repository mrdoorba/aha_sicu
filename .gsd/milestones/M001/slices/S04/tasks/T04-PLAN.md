---
estimated_steps: 6
estimated_files: 5
---

# T04: Update display components and run final IDR audit

**Slice:** S04 — Frontend Currency and Marketplace UI
**Milestone:** M001

## Description

Replace all remaining local `formatIDR` functions and hardcoded `IDR` string literals in display components with marketplace-aware formatting. This is the cleanup pass that ensures every currency value in the UI reflects the selected marketplace. After this task, a grep audit of the codebase should show zero `IDR`/`formatIDR` references in production code (excluding deprecated re-exports and `fields.ts` static config).

**Relevant skill**: `test` — vitest with jsdom.

## Steps

1. **Update `TopSkuResults.tsx`**:
   - Add `marketplace?: string` prop (default `'ID'`).
   - Import `formatCurrency` and `getCurrencyCode` from `../forms/formConfig`.
   - Replace line ~145: `IDR {formatIDR(row.total_omzet)}` → `{getCurrencyCode(marketplace)} {formatCurrency(row.total_omzet, marketplace)}`.
   - Replace line ~146: `IDR {formatIDR(row.rata2_harga_jual)}` → same pattern.
   - Remove the `import { formatIDR } from '../forms/formConfig'` import.
   - Thread `marketplace` from parent component. Check `CalculatorResultsSection` (or wherever `TopSkuResults` is rendered) and add marketplace prop there too. Trace the prop source up to `EvaluationSections` where marketplace is available from T03.

2. **Update `DataIntelligence.tsx`**:
   - This file has its own local `formatIDR(value: unknown): string` function (line 16).
   - Add `marketplace?: string` prop to the component's props interface.
   - Import `formatCurrency` from the shared forms formConfig.
   - Replace the local `formatIDR` with a wrapper that handles the `unknown` type: `function formatValue(value: unknown, mp?: string): string { ... }` that safely converts to number then calls `formatCurrency`.
   - Update all 3 usage sites (~lines 78, 99, 124) to use the new function with marketplace.
   - Thread marketplace from the parent component that renders `DataIntelligence`.

3. **Update `EvaluationDetailPage.tsx`**:
   - This file has its own local `formatIDR(value: unknown): string` function (line 58).
   - The evaluation detail page shows saved evaluation data. The saved evaluation record should include `marketplace` — check the evaluation detail API response type and extract marketplace from it.
   - Import `formatCurrency` from shared formConfig.
   - Replace the local `formatIDR` with a marketplace-aware version.
   - Update all usage sites (~lines 84, 188, 189, 214) to pass marketplace.
   - If the evaluation detail response doesn't include marketplace, default to `'ID'` and add a TODO comment.

4. **Update `BusinessForm.tsx` formatCurrencyDisplay**:
   - Line 20 has `function formatCurrencyDisplay(value: number): string` with hardcoded `currency: 'IDR'`.
   - Replace with imported `formatCurrency` from `formConfig`: `formatCurrency(average)` (number formatting is identical — no currency code needed in the average display, just the formatted number).
   - Or use `getCurrencyCode(marketplace)` to prefix the formatted number if the current display includes the currency symbol.
   - Investigate the current usage: it's used in the "computed average" display area. The current format uses `Intl.NumberFormat` with `style: 'currency', currency: 'IDR'` which produces `IDR 125,000,000`. Replace with `{getCurrencyCode(currency)} {formatCurrency(average)}` where `currency` comes from the prop added in T03.
   - Remove the local `formatCurrencyDisplay` function.

5. **Run final grep audit**:
   - Execute: `grep -rn "IDR\|formatIDR" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v node_modules`
   - **Acceptable survivors**: 
     - `formUtils.ts` — deprecated `formatIDR`/`parseIDR` function definitions (now delegating to `formatCurrency`/`parseCurrency`)
     - `formConfig.ts` — barrel re-exports of `formatIDR`/`parseIDR`
     - `fields.ts` — `unit: 'IDR'` on ~16 field definitions (static config; render layer overrides via currency prop)
     - `getCurrencyCode` function body containing the string `'IDR'` as a return value
   - **Must NOT appear**: any standalone `IDR` string literal used for display, any local `formatIDR` function, any `import { formatIDR }` (except in test files).
   - Fix any remaining hits before proceeding.

6. **Run full test suite**:
   - `cd frontend && npx vitest run --reporter=verbose`
   - All tests must pass. If any test fails due to changed formatIDR imports, update the test to use the new function names while preserving the assertion logic.

## Must-Haves

- [ ] `TopSkuResults.tsx` uses marketplace-aware formatting (no hardcoded `IDR` prefix)
- [ ] `DataIntelligence.tsx` local `formatIDR` removed, uses shared `formatCurrency`
- [ ] `EvaluationDetailPage.tsx` local `formatIDR` removed, uses shared `formatCurrency`
- [ ] `BusinessForm.tsx` local `formatCurrencyDisplay` removed, uses shared `formatCurrency`
- [ ] Grep audit passes — zero non-test production `IDR`/`formatIDR` hits (excluding acceptable survivors)
- [ ] Full test suite passes

## Verification

- `cd frontend && npx vitest run --reporter=verbose` — full suite passes
- `grep -rn "IDR\|formatIDR" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v node_modules | grep -v "deprecated\|getCurrencyCode\|formUtils\|formConfig\|fields.ts"` — returns zero lines
- `grep -rn "formatCurrencyDisplay" frontend/src --include="*.tsx"` — returns zero lines (local function removed)

## Inputs

- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx` — lines 13, 145-146 use `formatIDR` and `IDR` string literal
- `frontend/src/components/dashboard/DataIntelligence.tsx` — line 16 has local `formatIDR`, lines 78, 99, 124 use it
- `frontend/src/pages/EvaluationDetailPage.tsx` — line 58 has local `formatIDR`, lines 84, 188, 189, 214 use it
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — line 20 has local `formatCurrencyDisplay` with hardcoded IDR
- T01 output: `formatCurrency`/`getCurrencyCode` available in `formConfig.ts`
- T03 output: `marketplace`/`currency` props threaded through `EvaluationSections` to form components

## Expected Output

- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx` — uses `formatCurrency` and `getCurrencyCode(marketplace)` instead of `formatIDR` and `IDR` literal
- `frontend/src/components/dashboard/DataIntelligence.tsx` — local `formatIDR` removed, uses imported `formatCurrency` with marketplace
- `frontend/src/pages/EvaluationDetailPage.tsx` — local `formatIDR` removed, uses imported `formatCurrency` with marketplace
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — local `formatCurrencyDisplay` removed, uses imported `formatCurrency`/`getCurrencyCode`
- Grep audit clean: only acceptable survivors remain
