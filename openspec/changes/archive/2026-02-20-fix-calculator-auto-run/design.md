## Context

After a file upload, the backend calls `run_calculators_for_upload()` to auto-execute affected calculators. If this fails, the error is caught in a `try/except` in `upload/service.py` and `auto_calc_raw` is set to `[]`. The frontend only invalidates calculator caches when `auto_calculated.length > 0`, so on silent failure the UI shows stale state. Additionally, the "Ready to calculate" state in `CalculatorResultsSection.tsx` renders only text with no action button, and "Recalculate All" only appears when `hasAnyResult` is true — creating a dead-end when all calculators have no results.

## Goals / Non-Goals

**Goals:**
- Users can always manually trigger any calculator that is in "ready" state
- Users can see when auto-calculation failed after an upload
- Calculator caches are always fresh after a successful upload

**Non-Goals:**
- Fixing the root cause of auto-calc failures (data issues, backend errors) — those are separate investigations
- Changing the auto-calc backend logic itself
- Adding retry logic for auto-calc on the backend

## Decisions

### 1. Always invalidate calculator caches after upload

**Decision**: Remove the `if (result.auto_calculated.length > 0)` guard in `useUpload.ts` and always invalidate `calculatorResults` and `calculatorStatus` caches after a successful upload.

**Rationale**: `clear_dependent_results` runs before auto-calc, so old results are already deleted in the DB. Even if auto-calc fails, the frontend cache is now stale. Unconditional invalidation ensures the UI reflects the actual DB state. The cost of an extra cache invalidation is negligible.

### 2. Add Calculate button to "Ready to calculate" state

**Decision**: In the "Ready to calculate" branch of `CalculatorCard`, add a Button that calls `useRunCalculator` for that calculator type.

**Rationale**: This is the simplest escape hatch. The hook and endpoint already exist — we're just surfacing them in a state that previously had no action.

### 3. Show "Calculate All" button whenever any calculator is ready-but-no-result

**Decision**: Change the `hasAnyResult` check for the "Recalculate All" / "Calculate All" button to also include cases where any calculator has `status === "ready"` and no result.

**Rationale**: Users need a bulk action even when starting fresh (no results yet). The `run-all` endpoint already handles this correctly — it skips non-ready calculators.

### 4. Surface auto-calc errors from upload response

**Decision**: Store `auto_calculated` items with `status === "error"` in a lightweight React context or query cache entry, and display a warning banner in the calculator card when an auto-calc error exists for that calculator type.

**Alternative considered**: Storing errors in component state — rejected because the upload and calculator display are separate components/pages. Using query cache is simpler and stays consistent with existing patterns.

**Implementation**: After `processUpload` returns, if any `auto_calculated` item has `status === "error"`, store the error entries in a React Query cache key like `['autoCalcErrors', brandId]`. The `CalculatorCard` component reads from this cache and shows a warning when relevant.

## Risks / Trade-offs

- **Extra network requests**: Always invalidating calculator caches means 2 extra GET requests after every upload. → Acceptable for correctness; these are lightweight queries.
- **Auto-calc error state is transient**: The error entries in query cache will be cleared on page reload. → Acceptable because the "Calculate" button provides a permanent escape hatch regardless of error visibility.
