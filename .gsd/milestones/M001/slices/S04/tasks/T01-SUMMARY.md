---
id: T01
parent: S04
milestone: M001
provides:
  - formatCurrency(value, marketplace) utility function
  - parseCurrency(formatted, marketplace) utility function
  - getCurrencyCode(marketplace) helper (TH→THB, ID→IDR)
  - CurrencyField currency prop for marketplace-aware labels
  - Backward-compatible formatIDR/parseIDR deprecated re-exports
key_files:
  - frontend/src/components/evaluation/forms/formUtils.ts
  - frontend/src/components/evaluation/forms/formConfig.ts
  - frontend/src/components/evaluation/forms/CurrencyField.tsx
  - frontend/src/components/evaluation/forms/formUtils.test.ts
  - frontend/src/components/evaluation/forms/CurrencyField.test.tsx
key_decisions:
  - formatIDR/parseIDR kept as deprecated one-liner re-exports rather than removed — allows incremental migration across downstream tasks without breaking existing callers
  - getCurrencyCode returns uppercased unknown codes as-is (graceful fallback) rather than throwing — prevents crash on bad data
patterns_established:
  - Currency formatting uses formatCurrency/parseCurrency with marketplace param (unused today, extensible for locale-specific formatting later)
  - CurrencyField accepts currency prop defaulting to 'IDR' — all downstream forms thread marketplace→getCurrencyCode→currency
observability_surfaces:
  - CurrencyField currency prop visible in React DevTools
  - Deprecated formatIDR/parseIDR usage trackable via grep or IDE deprecation warnings
duration: 15m
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T01: Add shared currency utilities and extend CurrencyField

**Added `formatCurrency`, `parseCurrency`, `getCurrencyCode` utilities and extended `CurrencyField` with a `currency` prop for marketplace-aware label rendering.**

## What Happened

Added three new functions to `formUtils.ts`:
- `getCurrencyCode(marketplace?)` — maps `'TH'→'THB'`, `'ID'→'IDR'`, defaults to `'IDR'`, unknown codes uppercased as fallback
- `formatCurrency(value, _marketplace?)` — identical formatting logic to former `formatIDR`, marketplace param reserved for future use
- `parseCurrency(formatted, _marketplace?)` — identical parsing logic to former `parseIDR`, marketplace param reserved for future use

Converted `formatIDR`/`parseIDR` to deprecated one-liner delegates calling through to the new functions. Updated barrel exports in `formConfig.ts` to include all three new functions.

Extended `CurrencyField` with a `currency?: 'IDR' | 'THB' | string` prop (default `'IDR'`). The component now renders `({currency})` dynamically instead of hardcoded `(IDR)`, and uses `formatCurrency`/`parseCurrency` instead of `formatIDR`/`parseIDR`.

Created `formUtils.test.ts` with 19 tests covering all three utilities plus backward compatibility. Added 2 new tests to `CurrencyField.test.tsx` for THB variant and unknown currency fallback.

## Verification

- `npx vitest run src/components/evaluation/forms/formUtils.test.ts` — **19/19 passed** (formatCurrency: 6, parseCurrency: 6, getCurrencyCode: 5, formatIDR compat: 1, parseIDR compat: 1)
- `npx vitest run src/components/evaluation/forms/CurrencyField.test.tsx` — **9/9 passed** (7 existing + 2 new: THB variant, XX unknown fallback)
- `npx vitest run src/components/evaluation/forms/` — **128/128 passed** across 13 test files, zero regressions

### Slice-level verification (intermediate — partial pass expected)
- ✅ `CurrencyField.test.tsx` — 7 existing + 2 new tests pass
- ✅ `formUtils.test.ts` — new test file passes with full coverage
- ⬜ `RulesPage.test.tsx` marketplace tabs — not yet (T02)
- ⬜ Grep audit for zero IDR hits — remaining callers in `DataIntelligence.tsx`, `TopSkuResults.tsx`, `EvaluationDetailPage.tsx` (T04)
- ✅ Failure-path check — `CurrencyField` with `currency="XX"` renders `(XX)` without crashing

## Diagnostics

- **Inspect currency prop**: React DevTools → find any `CurrencyField` instance → check `currency` prop value
- **Track deprecated usage**: `grep -rn "formatIDR\|parseIDR" frontend/src --include="*.ts" --include="*.tsx" | grep -v test | grep -v deprecated` — non-zero until T04 completes migration
- **Verify mapping**: `npx vitest run src/components/evaluation/forms/formUtils.test.ts -t getCurrencyCode`

## Deviations

None.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/components/evaluation/forms/formUtils.ts` — added `getCurrencyCode`, `formatCurrency`, `parseCurrency`; converted `formatIDR`/`parseIDR` to deprecated delegates
- `frontend/src/components/evaluation/forms/formConfig.ts` — added `formatCurrency`, `parseCurrency`, `getCurrencyCode` to barrel exports
- `frontend/src/components/evaluation/forms/CurrencyField.tsx` — added `currency` prop, switched to `formatCurrency`/`parseCurrency` imports
- `frontend/src/components/evaluation/forms/formUtils.test.ts` — **created** — 19 tests for all utilities + backward compat
- `frontend/src/components/evaluation/forms/CurrencyField.test.tsx` — added 2 new tests (THB variant, unknown currency fallback)
