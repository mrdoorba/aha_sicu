## Why

When calculators fail to auto-run after file upload, the error is silently swallowed and the UI shows "Ready to calculate" with no way for the user to manually trigger calculation. This creates a dead-end where the user has uploaded all required files but cannot get calculator results, which cascades into evaluation scores showing 0 for categories that depend on calculator data (e.g., Stok = 0 despite stock data being > 24).

## What Changes

- Add a "Calculate" button to the "Ready to calculate" state in each calculator card, so users can manually trigger individual calculators
- Show a "Calculate All" button whenever any calculator is in a ready-but-no-result state (currently only shows when results already exist)
- Always invalidate calculator query caches after upload completes, regardless of whether `auto_calculated` response is empty
- Surface auto-calc errors from the upload response in the calculator UI, so users know something went wrong instead of seeing a silent "Ready to calculate"

## Capabilities

### New Capabilities
- `calculator-run-ux`: Manual calculator trigger and auto-calc error feedback — ensures users can always trigger ready calculators and see why auto-calculation may have failed

### Modified Capabilities

## Impact

- `frontend/src/components/evaluation/calculators/CalculatorResultsSection.tsx` — Add Calculate button to ready state, adjust "Calculate All" visibility logic, show auto-calc errors
- `frontend/src/hooks/useUpload.ts` — Always invalidate calculator caches after successful upload
- `frontend/src/hooks/useCalculator.ts` — May need minor adjustments for error state tracking from auto-calc
