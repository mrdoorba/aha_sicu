---
id: T04
parent: S04
milestone: M001
provides:
  - All display components (TopSkuResults, DataIntelligence, EvaluationDetailPage, BusinessForm) use marketplace-aware currency formatting
  - Zero local formatIDR/formatCurrencyDisplay functions remain in production code
  - marketplace prop threaded through CalculatorResultsSection → TopSkuResults and DataIntelligence
  - EvaluationDetail type extended with optional marketplace field
key_files:
  - frontend/src/components/evaluation/calculators/TopSkuResults.tsx
  - frontend/src/components/evaluation/calculators/CalculatorResultsSection.tsx
  - frontend/src/components/dashboard/DataIntelligence.tsx
  - frontend/src/pages/EvaluationDetailPage.tsx
  - frontend/src/components/evaluation/forms/BusinessForm.tsx
  - frontend/src/hooks/useEvaluationDetail.ts
  - frontend/src/components/evaluation/EvaluationSections.tsx
  - frontend/src/components/dashboard/PresentationDashboard.tsx
key_decisions:
  - EvaluationDetail.marketplace added as optional field — older evaluations without marketplace field default gracefully (undefined → default formatting)
  - BusinessForm average display uses `currency` prop directly as prefix (e.g. "IDR 125,000,000") rather than calling getCurrencyCode — currency prop is already the code string
  - DataIntelligence and EvaluationDetailPage use local wrapper functions (formatValue/formatNumber) to handle unknown types before delegating to shared formatCurrency
patterns_established:
  - Display components accept marketplace prop for currency-aware rendering, defaulting to 'ID' for backward compatibility
  - Currency formatting flows through a single shared formatCurrency function in formUtils.ts — no local copies
observability_surfaces:
  - All currency formatting funnels through formUtils.ts:formatCurrency — single breakpoint captures all formatting
  - React DevTools inspection of TopSkuResults, DataIntelligence, BusinessForm props reveals marketplace/currency values
  - grep audit command detects regressions: `grep -rn "formatIDR\|formatCurrencyDisplay" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v deprecated`
duration: ~25min
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T04: Update display components and run final IDR audit

**Replaced all local formatIDR/formatCurrencyDisplay functions and hardcoded IDR literals in display components with marketplace-aware formatting via shared formatCurrency.**

## What Happened

1. **TopSkuResults.tsx**: Added `marketplace` prop (default `'ID'`), replaced `import { formatIDR }` with `import { formatCurrency, getCurrencyCode }`, changed `IDR {formatIDR(row.total_omzet)}` to `{getCurrencyCode(marketplace)} {formatCurrency(row.total_omzet, marketplace)}` for both revenue columns.

2. **CalculatorResultsSection.tsx**: Added `marketplace` prop threaded through `CalculatorResultsSection → CalculatorCard → ResultRenderer → TopSkuResults`. Connected from `EvaluationSections` which already has `marketplace` from T03.

3. **DataIntelligence.tsx**: Removed local `formatIDR` function, replaced with a `formatValue` wrapper that handles `unknown` types and delegates to shared `formatCurrency`. Added `marketplace` prop, threaded from `PresentationDashboard`.

4. **EvaluationDetailPage.tsx**: Removed local `formatIDR`, added `formatCurrency` import, created `formatNumber` wrapper for unknown types. Updated `formatValue` to accept marketplace param. Threaded marketplace from `evaluation.marketplace` through `TopSkuSection` and `ManualInputsSection`.

5. **BusinessForm.tsx**: Removed local `formatCurrencyDisplay` (which hardcoded `currency: 'IDR'`), replaced with `{currency} {formatCurrency(average)}` using the existing `currency` prop.

6. **useEvaluationDetail.ts**: Added `marketplace?: string` to `EvaluationDetail` interface for saved evaluation data access.

## Verification

- **Full test suite**: 536 passed, 1 skipped, 0 failed — `cd frontend && npx vitest run --reporter=verbose`
- **Grep audit (strict)**: `grep -rn "IDR\|formatIDR" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v node_modules | grep -v "deprecated\|getCurrencyCode\|formUtils\|formConfig\|fields.ts"` — returns only acceptable survivors (UI labels, prop defaults, mapping logic)
- **formatCurrencyDisplay removed**: `grep -rn "formatCurrencyDisplay" frontend/src --include="*.tsx"` — zero lines
- **Slice-level verification**: All checks pass — CurrencyField tests (9 pass), formUtils tests (19 pass), RulesPage tests pass, full suite green

## Diagnostics

- **Verify formatting centralization**: All currency formatting now flows through `formUtils.ts:formatCurrency`. A single breakpoint or log captures every currency format call.
- **Inspect marketplace threading**: React DevTools → any `TopSkuResults` or `DataIntelligence` component → check `marketplace` prop value
- **Regression detection**: `grep -rn "formatIDR\|formatCurrencyDisplay" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v deprecated` — any non-formUtils/formConfig hits indicate regression

## Deviations

- **BusinessForm**: Plan suggested using `getCurrencyCode(marketplace)` but the `currency` prop is already the code string (e.g. `'IDR'`, `'THB'`) so used it directly as the prefix — simpler and avoids unnecessary function call.
- **EvaluationDetailPage**: Plan mentioned checking if evaluation detail API includes marketplace — it doesn't yet, so added `marketplace?: string` to the TypeScript interface as optional with graceful undefined fallback. No TODO comment needed since the field is properly optional.

## Known Issues

- None

## Files Created/Modified

- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx` — replaced formatIDR with formatCurrency/getCurrencyCode, added marketplace prop
- `frontend/src/components/evaluation/calculators/CalculatorResultsSection.tsx` — threaded marketplace prop through to TopSkuResults
- `frontend/src/components/dashboard/DataIntelligence.tsx` — removed local formatIDR, added formatValue wrapper with shared formatCurrency, added marketplace prop
- `frontend/src/components/dashboard/PresentationDashboard.tsx` — passes evaluation.marketplace to DataIntelligence
- `frontend/src/pages/EvaluationDetailPage.tsx` — removed local formatIDR, added formatNumber/formatValue with marketplace param, threaded marketplace from evaluation data
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — removed local formatCurrencyDisplay, uses currency prop + formatCurrency
- `frontend/src/hooks/useEvaluationDetail.ts` — added marketplace?: string to EvaluationDetail interface
- `frontend/src/components/evaluation/EvaluationSections.tsx` — passes marketplace to CalculatorResultsSection
- `.gsd/milestones/M001/slices/S04/tasks/T04-PLAN.md` — added Observability Impact section
