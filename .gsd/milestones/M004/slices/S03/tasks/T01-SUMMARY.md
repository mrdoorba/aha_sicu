---
id: T01
parent: S03
milestone: M004
provides:
  - All residual hardcoded Indonesian UI strings extracted to i18n locale keys
  - benchmarkKey/unitKey added to FieldDefinition type and populated on promo/operational fields
  - DetailedEvaluation metric comparisons use metric_i18n.key with row.metric fallback
  - 16 new locale keys added to all 3 JSON files (id, en, th) — now at 714 keys each
key_files:
  - frontend/src/components/evaluation/forms/types.ts
  - frontend/src/components/evaluation/forms/fields.ts
  - frontend/src/components/evaluation/forms/PromoToolsForm.tsx
  - frontend/src/components/evaluation/forms/OperationalForm.tsx
  - frontend/src/components/evaluation/EvaluationHeader.tsx
  - frontend/src/App.tsx
  - frontend/src/pages/LoginPage.tsx
  - frontend/src/components/dashboard/DetailedEvaluation.tsx
  - frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
key_decisions:
  - Used useTranslation() directly in App.tsx since i18n is initialized globally before render
  - DetailedEvaluation metric comparisons use || fallback to preserve backward compatibility with pre-M002 evaluations
patterns_established:
  - benchmarkKey/unitKey pattern on FieldDefinition: optional i18n key resolved via t() with fallback to original hardcoded value
  - getFieldLabel() function inside component for FIELD_LABELS that need i18n but have backend-matched keys that must not change
observability_surfaces:
  - Locale key sync check: python3 one-liner verifying all 3 files have equal key count (714)
  - Residual Indonesian sweep: rg commands confirming zero rendered Indonesian strings remain
duration: 25m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T01: Extract residual hardcoded Indonesian from source and fix metric comparisons

**Extracted 15 residual hardcoded Indonesian strings from 5 source files to i18n locale keys, added benchmarkKey/unitKey to FieldDefinition, and fixed DetailedEvaluation metric comparisons to use metric_i18n.key with row.metric fallback**

## What Happened

Executed all 12 steps from the task plan:

1. Added `benchmarkKey?: string` and `unitKey?: string` to FieldDefinition type in `types.ts`.
2. Added `benchmarkKey` to 10 PROMO_TOOLS_FIELDS entries in `fields.ts` (not `gratisOngkir` — it uses absolute benchmark `>0`, not a percentage string).
3. Added `unitKey: 'common.days'` to the `preparationTime` field.
4. Updated `PromoToolsForm.tsx` to resolve `benchmarkKey` via `t()` when present, falling back to `field.benchmark`.
5. Updated `OperationalForm.tsx` to resolve `unitKey` via `t()` when present, falling back to `field.unit`.
6. Replaced static `FIELD_LABELS` map in `EvaluationHeader.tsx` with a `getFieldLabel()` function inside the component that uses `t()`. VP_DISPLAY_FIELDS keys unchanged (backend matchers).
7. Extracted `accessDeniedMessage` in `App.tsx` to `t('auth.accessDeniedAccounts')` — added `useTranslation` import and hook call.
8. Extracted LoginPage banner `alt` text to `t('login.bannerAlt')`.
9. Fixed DetailedEvaluation metric comparisons to check `row.metric_i18n?.key` first with `row.metric` fallback (verified actual keys from backend: `scoring.adCost`, `scoring.avgSales6mo`, `scoring.promo.programAfiliasi`).
10. Added 16 new locale keys to all 3 JSON files (id, en, th), now at 714 keys each.
11. Updated PromoToolsForm.test.tsx benchmark assertions to expect key strings (mock `t` returns key as-is).
12. Checked other test files — CurrencyField.test.tsx passes benchmark directly as prop (not through t()), EvaluationHeader.test.tsx uses real i18n so id.json values match existing assertions. No other tests needed updating.

## Verification

- `npx tsc --noEmit` — zero type errors
- `npm run test:run` — 612/612 tests pass (68 test files)
- Locale sync check — all 3 files at 714 keys
- `rg "dari penjualan" PromoToolsForm.tsx` — zero hits
- `rg "Akses ditolak" App.tsx` — zero hits
- `rg "Garansi Omzet" LoginPage.tsx` — zero hits
- `grep "Nama PIC'" EvaluationHeader.tsx` — zero hits
- `rg "id-ID"` sweep — zero hits (slice-level check)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `cd frontend && npx tsc --noEmit` | 0 | ✅ pass | 45s |
| 2 | `cd frontend && npm run test:run` | 0 | ✅ pass (612/612) | 44s |
| 3 | `python3 -c "import json; ..." (locale sync)` | 0 | ✅ pass [714, 714, 714] | <1s |
| 4 | `rg "dari penjualan" PromoToolsForm.tsx` | 1 (no match) | ✅ pass | <1s |
| 5 | `rg "Akses ditolak" App.tsx` | 1 (no match) | ✅ pass | <1s |
| 6 | `rg "Garansi Omzet" LoginPage.tsx` | 1 (no match) | ✅ pass | <1s |
| 7 | `grep "Nama PIC'" EvaluationHeader.tsx` | 1 (no match) | ✅ pass | <1s |
| 8 | `rg "id-ID" (filtered sweep)` | 1 (no match) | ✅ pass | <1s |

## Diagnostics

- **Locale key count:** `python3 -c "import json; fs=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; cs=[len(json.load(open(f))) for f in fs]; print(cs)"` — should print `[714, 714, 714]`
- **Residual Indonesian:** `rg "dari penjualan|Akses ditolak|Garansi Omzet" frontend/src --glob '!*.test.*' --glob '!locales/*'` — should return only `fields.ts` inert `benchmark` properties
- **metric_i18n fallback:** Old evaluations without `metric_i18n` continue to work via `|| row.metric === '...'` fallback — testable by viewing pre-M002 evaluation dashboards in browser

## Deviations

None — all 12 steps executed as planned.

## Known Issues

- `CurrencyField.test.tsx` still references `>8% dari penjualan` in a direct benchmark prop test — this is correct since CurrencyField receives an already-resolved string, not a key.
- `benchmarkUtils.test.ts` still references `'hari'` in the unit parameter to `getBenchmarkFromRules` — this tests the benchmark utility function which operates on raw unit strings, not i18n-resolved values.

## Files Created/Modified

- `frontend/src/components/evaluation/forms/types.ts` — Added `benchmarkKey?: string` and `unitKey?: string` to FieldDefinition
- `frontend/src/components/evaluation/forms/fields.ts` — Added `benchmarkKey` to 10 PROMO_TOOLS_FIELDS, `unitKey` to preparationTime
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — Resolve benchmarkKey via t() when present
- `frontend/src/components/evaluation/forms/OperationalForm.tsx` — Resolve unitKey via t() when present
- `frontend/src/components/evaluation/EvaluationHeader.tsx` — Replaced static FIELD_LABELS with getFieldLabel() using t()
- `frontend/src/App.tsx` — Added useTranslation, extracted accessDeniedMessage to t('auth.accessDeniedAccounts')
- `frontend/src/pages/LoginPage.tsx` — Extracted banner alt text to t('login.bannerAlt')
- `frontend/src/components/dashboard/DetailedEvaluation.tsx` — Fixed metric comparisons to use metric_i18n.key with fallback
- `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx` — Updated benchmark assertions to expect key strings
- `frontend/src/locales/id.json` — Added 16 new keys (698 → 714)
- `frontend/src/locales/en.json` — Added 16 new keys (698 → 714)
- `frontend/src/locales/th.json` — Added 16 new keys (698 → 714)
- `.gsd/milestones/M004/slices/S03/S03-PLAN.md` — Added Observability section, marked T01 done
- `.gsd/milestones/M004/slices/S03/tasks/T01-PLAN.md` — Added Observability Impact section
