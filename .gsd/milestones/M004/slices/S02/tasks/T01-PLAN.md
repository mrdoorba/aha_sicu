---
estimated_steps: 6
estimated_files: 7
---

# T01: Rename INDO_MONTHS to MONTHS and i18n GENERIC_LABELS

**Slice:** S02 — Locale-aware dates, field labels, and month constants
**Milestone:** M004

## Description

Rename the `INDO_MONTHS` constant to `MONTHS` and correct 4 Indonesian month abbreviations to English (Mei→May, Agu→Aug, Okt→Oct, Des→Dec). Replace the `GENERIC_LABELS` array of hardcoded Indonesian strings ("Bulan Ini", "Bulan -1", …) with i18n key strings ("generic.thisMonth", "generic.month1", …) that will be resolved with `t()` at render time. Update the barrel export and imports. Add 6 `generic.*` locale keys to all 3 JSON files. Update test assertions.

**Relevant skills:** `test` (for vitest test pattern matching)

## Steps

1. **In `frontend/src/components/evaluation/forms/fields.ts`:**
   - Rename `INDO_MONTHS` to `MONTHS`
   - Change the 4 values: `"Mei"` → `"May"`, `"Agu"` → `"Aug"`, `"Okt"` → `"Oct"`, `"Des"` → `"Dec"`
   - Final array: `["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]`
   - Replace `GENERIC_LABELS` content from `["Bulan Ini", "Bulan -1", "Bulan -2", "Bulan -3", "Bulan -4", "Bulan -5"]` to `["generic.thisMonth", "generic.month1", "generic.month2", "generic.month3", "generic.month4", "generic.month5"]`

2. **In `frontend/src/components/evaluation/forms/formConfig.ts`:**
   - Change barrel export from `INDO_MONTHS` to `MONTHS`

3. **In `frontend/src/components/evaluation/forms/formUtils.ts`:**
   - Change import from `import { GENERIC_LABELS, INDO_MONTHS } from './fields'` to `import { GENERIC_LABELS, MONTHS } from './fields'`
   - Change reference inside `generateMonthLabels()` from `INDO_MONTHS[monthIndex]` to `MONTHS[monthIndex]`

4. **Add 6 locale keys to all 3 JSON files** (`frontend/src/locales/{id,en,th}.json`):
   - `"generic.thisMonth"`: id="Bulan Ini", en="This Month", th="เดือนนี้"
   - `"generic.month1"`: id="Bulan -1", en="Month -1", th="เดือน -1"
   - `"generic.month2"`: id="Bulan -2", en="Month -2", th="เดือน -2"
   - `"generic.month3"`: id="Bulan -3", en="Month -3", th="เดือน -3"
   - `"generic.month4"`: id="Bulan -4", en="Month -4", th="เดือน -4"
   - `"generic.month5"`: id="Bulan -5", en="Month -5", th="เดือน -5"
   - Place these in a `"generic"` namespace block in each JSON file, near existing keys.

5. **Update `frontend/src/components/evaluation/forms/formConfig.test.ts`:**
   - Assertions testing `generateMonthLabels('2025-12')` currently expect `["Des 2025", ...]` — must become `["Dec 2025", ...]`. Similarly "Okt" → "Oct", "Agu" → "Aug", "Mei" → "May".
   - Assertions testing `generateMonthLabels(null)` and invalid input currently expect `["Bulan Ini", "Bulan -1", ...]` — must become `["generic.thisMonth", "generic.month1", ...]`.
   - Read the test file first to identify all specific assertions that need updating.

6. **Run tests and verify:**
   - `cd frontend && npm run test:run -- formConfig.test` — all tests pass
   - `rg "INDO_MONTHS" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src` — zero hits
   - `rg "Bulan Ini" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale` — zero hits

## Must-Haves

- [ ] `INDO_MONTHS` renamed to `MONTHS` everywhere (fields.ts, formConfig.ts barrel, formUtils.ts import)
- [ ] 4 month abbreviations corrected: Mei→May, Agu→Aug, Okt→Oct, Des→Dec
- [ ] `GENERIC_LABELS` contains i18n key strings, not hardcoded Indonesian
- [ ] 6 `generic.*` locale keys added to all 3 JSON files with correct translations
- [ ] `formConfig.test.ts` assertions updated and all tests pass

## Verification

- `cd frontend && npm run test:run -- formConfig.test` — all formConfig tests pass
- `cd frontend && npm run test:run` — full suite still passes (612+)
- `rg "INDO_MONTHS" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src` — zero hits

## Observability Impact

- **What changes:** `MONTHS` now contains English abbreviations (locale-neutral), and `GENERIC_LABELS` contains i18n key strings instead of hardcoded Indonesian. This means any downstream consumer that was previously rendering `"Mei"` will now render `"May"`, and any consumer that was rendering `"Bulan Ini"` will now render the raw key `"generic.thisMonth"` until it's wrapped in `t()` (which happens in T03).
- **How to inspect:** `rg "INDO_MONTHS" frontend/src` should return zero hits after this task. `rg "generic\." frontend/src/locales/*.json` should return 18 lines (6 keys × 3 files).
- **Failure visibility:** If the rename is incomplete, TypeScript compilation fails on broken imports. If month abbreviations are wrong, `formConfig.test.ts` assertions fail. If GENERIC_LABELS keys are wrong, fallback label tests fail.

## Inputs

- `frontend/src/components/evaluation/forms/fields.ts` — contains `INDO_MONTHS` and `GENERIC_LABELS` to modify
- `frontend/src/components/evaluation/forms/formConfig.ts` — barrel export to update
- `frontend/src/components/evaluation/forms/formUtils.ts` — imports `INDO_MONTHS` and `GENERIC_LABELS`
- `frontend/src/components/evaluation/forms/formConfig.test.ts` — test assertions to update
- S01 established locale key pattern (nested JSON namespaces, all 3 files in sync at 624 keys)

## Expected Output

- `frontend/src/components/evaluation/forms/fields.ts` — `MONTHS` with English abbreviations, `GENERIC_LABELS` with i18n key strings
- `frontend/src/components/evaluation/forms/formConfig.ts` — exports `MONTHS` instead of `INDO_MONTHS`
- `frontend/src/components/evaluation/forms/formUtils.ts` — imports and uses `MONTHS`
- `frontend/src/components/evaluation/forms/formConfig.test.ts` — updated assertions passing
- `frontend/src/locales/{id,en,th}.json` — 6 new `generic.*` keys each
