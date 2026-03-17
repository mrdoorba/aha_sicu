---
estimated_steps: 6
estimated_files: 5
---

# T01: Add shared currency utilities and extend CurrencyField

**Slice:** S04 — Frontend Currency and Marketplace UI
**Milestone:** M001

## Description

Create the shared `formatCurrency(value, marketplace)` and `parseCurrency(formatted, marketplace)` utility functions that all downstream tasks depend on, and extend `CurrencyField` to accept a `currency` prop driving the label and formatting. This is the foundation layer — every other task in S04 imports from these files.

Both IDR and THB use identical number formatting (comma-separated thousands via `Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })`). The marketplace parameter only determines which currency code label to display. `formatIDR`/`parseIDR` must remain as deprecated re-exports for backward compatibility during the migration.

**Relevant skill**: `test` — vitest with jsdom, colocated test files.

## Steps

1. **Add `formatCurrency` and `parseCurrency` to `formUtils.ts`**:
   - `formatCurrency(value: number | null | undefined, marketplace?: string): string` — same body as `formatIDR`, marketplace param is unused for now (formatting identical). Keep `formatIDR` as a one-liner calling `formatCurrency`.
   - `parseCurrency(formatted: string, marketplace?: string): number | null` — same body as `parseIDR`, marketplace param unused. Keep `parseIDR` as a one-liner calling `parseCurrency`.
   - Add a `getCurrencyCode(marketplace?: string): string` helper: returns `'THB'` for `'TH'`, `'IDR'` for `'ID'` (default). For unknown marketplace, return the marketplace string itself uppercased as fallback.

2. **Update barrel exports in `formConfig.ts`**:
   - Add `formatCurrency`, `parseCurrency`, `getCurrencyCode` to the exports from `formUtils`.

3. **Extend `CurrencyField` with `currency` prop**:
   - Add `currency?: 'IDR' | 'THB' | string` to `CurrencyFieldProps` (default `'IDR'`).
   - Change `<span className="ml-1 text-xs font-normal text-muted-foreground">(IDR)</span>` to `<span ...>({currency})</span>`.
   - Replace `formatIDR(value)` with `formatCurrency(value)` in the display logic.
   - Replace `parseIDR(e.target.value)` with `parseCurrency(e.target.value)` in the onChange handler.
   - Update import from `formConfig` to use `formatCurrency`, `parseCurrency`.

4. **Create `formUtils.test.ts`** with tests:
   - `formatCurrency` with positive number, zero, null, undefined, NaN → correct output
   - `parseCurrency` with formatted string, empty string, non-numeric → correct output
   - `getCurrencyCode('TH')` → `'THB'`, `getCurrencyCode('ID')` → `'IDR'`, `getCurrencyCode()` → `'IDR'`, `getCurrencyCode('XX')` → `'XX'`
   - `formatIDR` backward compat — still works identically

5. **Add THB variant test + fallback test to `CurrencyField.test.tsx`**:
   - Test: renders `(THB)` label when `currency="THB"` is passed
   - Test: renders `(XX)` label when `currency="XX"` is passed (unknown currency fallback — does not crash)

6. **Run tests**: `cd frontend && npx vitest run src/components/evaluation/forms/ --reporter=verbose`

## Must-Haves

- [ ] `formatCurrency(value, marketplace)` and `parseCurrency(formatted, marketplace)` exist in `formUtils.ts`
- [ ] `getCurrencyCode(marketplace)` maps `'TH'` → `'THB'`, `'ID'` → `'IDR'`, defaults to `'IDR'`
- [ ] `formatIDR`/`parseIDR` remain as deprecated re-exports (call through to new functions)
- [ ] `CurrencyField` accepts `currency` prop and renders the correct label
- [ ] `CurrencyField` with no `currency` prop renders `(IDR)` (backward compat)
- [ ] All 7 existing CurrencyField tests pass
- [ ] New THB variant test passes
- [ ] New unknown currency fallback test passes (no crash)
- [ ] `formUtils.test.ts` covers formatCurrency, parseCurrency, getCurrencyCode

## Verification

- `cd frontend && npx vitest run src/components/evaluation/forms/formUtils.test.ts --reporter=verbose` — all formatCurrency/parseCurrency/getCurrencyCode tests pass
- `cd frontend && npx vitest run src/components/evaluation/forms/CurrencyField.test.tsx --reporter=verbose` — all 7 existing + 2 new tests pass
- `cd frontend && npx vitest run src/components/evaluation/forms/ --reporter=verbose` — full forms directory passes

## Inputs

- `frontend/src/components/evaluation/forms/formUtils.ts` — existing `formatIDR`/`parseIDR` functions (lines 26-35)
- `frontend/src/components/evaluation/forms/CurrencyField.tsx` — existing component with hardcoded `(IDR)` label
- `frontend/src/components/evaluation/forms/formConfig.ts` — barrel re-exports for `formatIDR`/`parseIDR`
- `frontend/src/components/evaluation/forms/CurrencyField.test.tsx` — existing 7 tests to preserve

## Expected Output

- `frontend/src/components/evaluation/forms/formUtils.ts` — gains `formatCurrency`, `parseCurrency`, `getCurrencyCode`; `formatIDR`/`parseIDR` now delegate to new functions
- `frontend/src/components/evaluation/forms/formUtils.test.ts` — **created** — tests for all 3 new utilities + backward compat
- `frontend/src/components/evaluation/forms/formConfig.ts` — gains `formatCurrency`, `parseCurrency`, `getCurrencyCode` exports
- `frontend/src/components/evaluation/forms/CurrencyField.tsx` — gains `currency` prop, uses `formatCurrency`/`parseCurrency`
- `frontend/src/components/evaluation/forms/CurrencyField.test.tsx` — gains 2 new tests (THB variant, unknown currency fallback)

## Observability Impact

- **Signals changed**: `CurrencyField` now renders a dynamic `(currency)` label instead of hardcoded `(IDR)`. Inspect via React DevTools: the `currency` prop is visible on any `CurrencyField` instance. If omitted, defaults to `'IDR'` — existing behavior preserved.
- **Inspection surface**: `getCurrencyCode(marketplace)` is a pure function — test coverage is the primary inspection surface. Run `npx vitest run src/components/evaluation/forms/formUtils.test.ts` to verify mapping correctness.
- **Failure visibility**: If a downstream task passes an invalid marketplace code to `getCurrencyCode`, it returns the code uppercased (graceful fallback, not a crash). The `CurrencyField` renders whatever currency string it receives — visually obvious if wrong (e.g. `(XX)` instead of `(THB)`). No silent failures.
- **Deprecation tracking**: `formatIDR`/`parseIDR` are marked `@deprecated` in JSDoc. IDE tooling surfaces deprecation warnings at call sites. Grep for remaining usage: `grep -rn "formatIDR\|parseIDR" frontend/src --include="*.ts" --include="*.tsx" | grep -v test | grep -v "deprecated"`.
