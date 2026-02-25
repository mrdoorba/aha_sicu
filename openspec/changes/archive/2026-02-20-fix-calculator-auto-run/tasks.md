## 1. Post-upload cache invalidation

- [x] 1.1 Remove the `if (result.auto_calculated && result.auto_calculated.length > 0)` guard in `useUpload.ts` — always invalidate `calculatorResults` and `calculatorStatus` caches after successful upload
- [x] 1.2 Add test for unconditional cache invalidation in `useUpload.test.ts`

## 2. Manual Calculate button in ready state

- [x] 2.1 Add a "Calculate" button to the ready-but-no-result branch of `CalculatorCard` in `CalculatorResultsSection.tsx` that calls `useRunCalculator` for the specific calculator type, with loading and error states
- [x] 2.2 Change "Calculate All" / "Recalculate All" button visibility to show whenever any calculator has `status === "ready"` (not just when `hasAnyResult` is true). Label: "Calculate All" when no results exist, "Recalculate All" when some results exist.

## 3. Auto-calc error visibility

- [x] 3.1 After `processUpload` returns, extract any `auto_calculated` items with `status === "error"` and store them in a query cache key `['autoCalcErrors', brandId]` inside `useUpload.ts`
- [x] 3.2 Create a `useAutoCalcErrors(brandId)` hook in `useCalculator.ts` that reads from the `['autoCalcErrors', brandId]` cache key
- [x] 3.3 In `CalculatorCard`, read auto-calc errors via `useAutoCalcErrors` and show a warning banner when an error exists for the card's calculator type, with a "Calculate" button for manual retry
- [x] 3.4 Clear auto-calc errors for a brand when a new upload completes (set cache to empty array) or when a manual calculation succeeds

## 4. Tests

- [x] 4.1 Add frontend tests for `CalculatorCard` rendering: ready state with Calculate button, error banner from auto-calc, loading state during calculation
- [x] 4.2 Run full frontend test suite and fix any failures
