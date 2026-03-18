---
id: T01
parent: S02
milestone: M004
provides:
  - MONTHS constant with English abbreviations (locale-neutral month names)
  - GENERIC_LABELS with i18n key strings instead of hardcoded Indonesian
  - 6 generic.* locale keys in all 3 JSON files (id, en, th)
key_files:
  - frontend/src/components/evaluation/forms/fields.ts
  - frontend/src/components/evaluation/forms/formConfig.ts
  - frontend/src/components/evaluation/forms/formUtils.ts
  - frontend/src/components/evaluation/forms/formConfig.test.ts
  - frontend/src/components/evaluation/forms/BusinessForm.test.tsx
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
key_decisions:
  - GENERIC_LABELS stores raw i18n keys (e.g. "generic.thisMonth") that render as-is until wrapped in t() by T03
patterns_established:
  - i18n key strings in constants are resolved at render time via t(), not at definition time
observability_surfaces:
  - rg "INDO_MONTHS" frontend/src — zero hits confirms rename is complete
  - rg "generic\." frontend/src/locales/*.json — 18 lines confirms all locale keys present
duration: 12m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T01: Rename INDO_MONTHS to MONTHS and i18n GENERIC_LABELS

**Renamed INDO_MONTHS to MONTHS with English abbreviations, replaced GENERIC_LABELS with i18n key strings, added 6 generic.* locale keys to all 3 JSON files**

## What Happened

1. In `fields.ts`: renamed `INDO_MONTHS` to `MONTHS` and corrected 4 Indonesian month abbreviations to English (Mei→May, Agu→Aug, Okt→Oct, Des→Dec). Replaced `GENERIC_LABELS` hardcoded Indonesian strings with i18n key strings (`generic.thisMonth`, `generic.month1`…`generic.month5`).

2. Updated barrel export in `formConfig.ts` from `INDO_MONTHS` to `MONTHS`.

3. Updated import and reference in `formUtils.ts` from `INDO_MONTHS` to `MONTHS`.

4. Added 6 `generic.*` locale keys to all 3 JSON locale files: `id.json` (Indonesian), `en.json` (English), `th.json` (Thai). All files now have 630 keys each (up from 624).

5. Updated `formConfig.test.ts` assertions: month abbreviations changed from Indonesian to English (Des→Dec, Okt→Oct, Agu→Aug, Mei→May), generic fallback assertions changed from `"Bulan Ini"` etc. to `"generic.thisMonth"` etc.

6. Updated `BusinessForm.test.tsx` — 2 tests that asserted rendered label text `/Penjualan Bulan Bulan Ini/` now assert `/Penjualan Bulan generic\.thisMonth/`, matching the raw i18n key that renders until T03 wraps these in `t()`.

## Verification

- `cd frontend && npm run test:run -- formConfig.test` — 8/8 tests pass
- `cd frontend && npm run test:run` — 612/612 tests pass across 68 test files
- `rg "INDO_MONTHS" frontend/src` — zero hits (exit code 1 = no matches)
- `rg "Bulan Ini|Bulan -1" ... | grep -v test | grep -v locale` — only field `label` properties remain (scope of T02/T03)
- All 3 locale files at 630 keys each (in sync)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `cd frontend && npm run test:run -- formConfig.test` | 0 | ✅ pass | 3.8s |
| 2 | `cd frontend && npm run test:run` | 0 | ✅ pass | 19.3s |
| 3 | `rg "INDO_MONTHS" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src` | 1 (no matches) | ✅ pass | <1s |
| 4 | `rg "Bulan Ini\|Bulan -1" frontend/src ... \| grep -v test \| grep -v locale` | 0 | ⚠️ expected (field labels, T02 scope) | <1s |
| 5 | `rg "id-ID" frontend/src ... \| grep -v test \| grep -v locale \| grep -v localeMap` | 0 | ⚠️ expected (T04 scope) | <1s |
| 6 | Locale key counts: id=630, en=630, th=630 | 0 | ✅ pass | <1s |

## Diagnostics

- `rg "INDO_MONTHS" frontend/src` — should always return zero hits after this task
- `rg "generic\." frontend/src/locales/*.json` — should return 18 lines (6 keys × 3 files)
- If BusinessForm renders raw key strings like `"generic.thisMonth"` in the UI, that's expected until T03 wraps them in `t()`

## Deviations

- Updated `BusinessForm.test.tsx` (not listed in original plan) — 2 tests broke because they asserted rendered labels containing the old `"Bulan Ini"` text which now renders as `"generic.thisMonth"`. This is a direct consequence of the GENERIC_LABELS change.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/components/evaluation/forms/fields.ts` — renamed INDO_MONTHS→MONTHS, corrected 4 month abbreviations, replaced GENERIC_LABELS with i18n keys
- `frontend/src/components/evaluation/forms/formConfig.ts` — updated barrel export from INDO_MONTHS to MONTHS
- `frontend/src/components/evaluation/forms/formUtils.ts` — updated import and reference from INDO_MONTHS to MONTHS
- `frontend/src/components/evaluation/forms/formConfig.test.ts` — updated all month and generic label assertions
- `frontend/src/components/evaluation/forms/BusinessForm.test.tsx` — updated 2 generic fallback label assertions
- `frontend/src/locales/id.json` — added 6 generic.* keys (Indonesian translations)
- `frontend/src/locales/en.json` — added 6 generic.* keys (English translations)
- `frontend/src/locales/th.json` — added 6 generic.* keys (Thai translations)
- `.gsd/milestones/M004/slices/S02/S02-PLAN.md` — added Observability/Diagnostics section
- `.gsd/milestones/M004/slices/S02/tasks/T01-PLAN.md` — added Observability Impact section
