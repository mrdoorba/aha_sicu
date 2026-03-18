---
id: S02
parent: M004
milestone: M004
provides:
  - MONTHS constant with English abbreviations replacing INDO_MONTHS (4 values corrected)
  - GENERIC_LABELS with i18n key strings resolved via t() at render time
  - labelKey on all 47 FieldDefinition instances, displayNameKey on all 8 CategoryDefinition instances
  - All 7 form components + EvaluationDetailPage resolve labels via t(field.labelKey!) instead of field.label
  - All 7 id-ID hardcoded date formatting sites replaced with getIntlLocale(i18n.language)
  - DiscountResults 7 hardcoded strings + AdsKeywordResults 1 hardcoded string extracted to locale keys
  - 74 new locale keys across all 3 JSON files (6 generic.* + 55 fields.*/categories.* + 5 evaluation.* + 8 discount.*/adsKeyword.*)
requires:
  - slice: S01
    provides: lib/localeMap.ts → getIntlLocale() function for locale-aware date formatting; established pattern for locale key naming and test mock updates
affects:
  - S03
key_files:
  - frontend/src/components/evaluation/forms/fields.ts
  - frontend/src/components/evaluation/forms/types.ts
  - frontend/src/components/evaluation/forms/formConfig.ts
  - frontend/src/components/evaluation/forms/formUtils.ts
  - frontend/src/components/evaluation/forms/OperationalForm.tsx
  - frontend/src/components/evaluation/forms/BusinessForm.tsx
  - frontend/src/components/evaluation/forms/VisitorsForm.tsx
  - frontend/src/components/evaluation/forms/PromoToolsForm.tsx
  - frontend/src/components/evaluation/forms/AdsForm.tsx
  - frontend/src/components/evaluation/forms/CampaignForm.tsx
  - frontend/src/components/evaluation/forms/ProductsStatusForm.tsx
  - frontend/src/pages/EvaluationDetailPage.tsx
  - frontend/src/pages/AccountsPage.tsx
  - frontend/src/components/dashboard/DashboardFooter.tsx
  - frontend/src/components/evaluation/calculators/DiscountResults.tsx
  - frontend/src/components/evaluation/calculators/TopSkuResults.tsx
  - frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
key_decisions:
  - GENERIC_LABELS stores raw i18n keys resolved at render time via t(), not at definition time
  - labelKey naming convention is fields.<category>.<camelCaseKey> with dot-separated nesting for competition products
  - EvaluationDetailPage test kept real i18n (not mocked) since id.json locale values match original hardcoded text — zero assertion changes needed
  - Module-level Intl.DateTimeFormat must be converted to useMemo inside component when it needs locale reactivity (AccountsPage pattern)
patterns_established:
  - t(field.labelKey!) with non-null assertion is the standard pattern for form field labels
  - getIntlLocale(i18n.language) is the standard pattern for all locale-aware date/number formatting
  - Form component tests that mock react-i18next use key-based assertions; page-level tests that use real i18n verify end-to-end resolution
  - i18n key naming follows fields.<category>.<fieldKey> for field labels, categories.<categoryKey> for display names
observability_surfaces:
  - rg "INDO_MONTHS" frontend/src — zero hits confirms rename complete
  - rg "id-ID" frontend/src | grep -v test | grep -v locale | grep -v localeMap — zero hits confirms no hardcoded locale
  - python3 locale key count check — all 3 files must show 698
  - Raw i18n key strings visible in UI (e.g. "fields.operational.unfulfilledOrderRate") = missing locale key
drill_down_paths:
  - .gsd/milestones/M004/slices/S02/tasks/T01-SUMMARY.md
  - .gsd/milestones/M004/slices/S02/tasks/T02-SUMMARY.md
  - .gsd/milestones/M004/slices/S02/tasks/T03-SUMMARY.md
  - .gsd/milestones/M004/slices/S02/tasks/T04-SUMMARY.md
duration: 62m
verification_result: passed
completed_at: 2026-03-18
---

# S02: Locale-aware dates, field labels, and month constants

**All 47 evaluation form field labels, 8 category headings, 6 generic labels, and 7 date formatting sites now resolve through i18n locale files; INDO_MONTHS renamed to MONTHS with English abbreviations; 8 calculator strings extracted; zero id-ID hardcodes remain in non-test/non-locale source**

## What Happened

This slice executed four tasks in sequence, each building on the previous:

**T01 — Foundation constants** (12m): Renamed `INDO_MONTHS` → `MONTHS` with 4 Indonesian abbreviations corrected to English (Mei→May, Agu→Aug, Okt→Oct, Des→Dec). Replaced `GENERIC_LABELS` hardcoded Indonesian strings with i18n key strings (`generic.thisMonth`, `generic.month1`…`generic.month5`). Updated barrel export in `formConfig.ts`, import in `formUtils.ts`, and all test assertions. Added 6 `generic.*` locale keys to all 3 JSON files (624→630 keys each).

**T02 — Data layer** (10m): Added `labelKey?: string` to `FieldDefinition` and `displayNameKey?: string` to `CategoryDefinition` in `types.ts`. Populated `labelKey` on all 47 field definitions across 8 field arrays and `displayNameKey` on all 8 entries in `MANUAL_DATA_FIELDS`. Added 55 locale keys (`fields.*` and `categories.*` namespaces) to all 3 JSON files (630→685 keys each). Indonesian locale values exactly match the original hardcoded `label`/`displayName` strings, ensuring a zero-diff transition when T03 wired `t()`.

**T03 — Component wiring** (25m): Changed all 7 form components from `label={field.label}` to `label={t(field.labelKey!)}`. In BusinessForm, changed `getFieldLabel()` fallback to `t(field.labelKey!)` and pre-resolved GENERIC_LABELS keys through `t()`. In EvaluationDetailPage, wired `t(displayNameKey)` for category headings, `t(labelKey)` for field labels, and extracted 5 hardcoded strings (competitor product labels, sales month labels, "Lihat di Shopee") to `evaluation.*` locale keys. Updated 4 form test files with i18n mocks and key-based assertions. EvaluationDetailPage test needed zero changes because it uses real i18n and the id.json values match the original hardcoded text (685→690 keys each).

**T04 — Date formatting and calculators** (15m): Replaced all 7 remaining `id-ID` hardcoded date/number formatting sites with `getIntlLocale(i18n.language)` from `@/lib/localeMap`. AccountsPage's module-level `dateFormatter` was converted to a hook-based `useMemo` for locale reactivity. Extracted 7 hardcoded strings from DiscountResults and 1 from AdsKeywordResults into `discount.*` and `adsKeyword.*` locale keys. Updated calculator test files with i18n mocks and key-based assertions (690→698 keys each).

## Verification

All 8 slice-plan verification checks pass:

| # | Check | Result |
|---|-------|--------|
| 1 | `npm run test:run` — 612 tests, 68 files | ✅ all pass |
| 2 | `rg "INDO_MONTHS" frontend/src` | ✅ zero hits |
| 3 | `rg "Bulan Ini\|Bulan -1" \| grep -v test \| grep -v locale` | ✅ only legacy `label` property in fields.ts (not rendered — superseded by `labelKey`) |
| 4 | `rg "id-ID" \| grep -v test \| grep -v locale \| grep -v localeMap` | ✅ zero hits |
| 5 | `rg hardcoded Indonesian in forms/*.tsx + EvaluationDetailPage.tsx` | ✅ only a code comment in VisitorsForm.tsx and pre-existing test assertions in EvaluationForms.test.tsx |
| 6 | Locale key counts: id=698, en=698, th=698 | ✅ all equal |
| 7 | `npx tsc --noEmit` | ✅ zero errors |
| 8 | `python3` locale key equality assertion | ✅ pass |

Additional diagnostics confirmed:
- `grep -c "labelKey" fields.ts` = 47 (all field definitions)
- `grep -c "displayNameKey" fields.ts` = 8 (all categories)
- `rg "generic\." frontend/src/locales/*.json` = 18 lines (6 keys × 3 files)

## Requirements Advanced

- **R028** — All 7 remaining `id-ID` date formatting sites now use `getIntlLocale(i18n.language)`. EvaluationHistoryTable was already converted in S01. All 8 files specified in the requirement are now locale-aware. `rg "id-ID" | grep -v test | grep -v locale | grep -v localeMap` returns zero hits.
- **R029** — All 47 field labels have `labelKey` resolved via `t()` in 7 form components + EvaluationDetailPage. `GENERIC_LABELS` uses i18n key strings resolved via `t()`. DiscountResults hardcoded labels extracted to `discount.*` locale keys. All form field labels are now fully i18n'd.
- **R030** — `INDO_MONTHS` renamed to `MONTHS` with 4 corrections (Mei→May, Agu→Aug, Okt→Oct, Des→Dec). `rg "INDO_MONTHS"` returns zero hits. All 12 months use standard English abbreviations.
- **R031** — Advanced significantly: ~80 hardcoded Indonesian strings extracted to locale keys across forms, calculators, and detail page. Legacy `label` property retained in `fields.ts` as dead code (S03 sweep scope). Residual Indonesian limited to code comments and the legacy `label` field.
- **R032** — Advanced significantly: All 612 frontend tests pass after extraction. 6 test files updated with i18n mocks and key-based assertions in lockstep with source changes.

## Requirements Validated

- **R028** — `rg "id-ID" frontend/src | grep -v test | grep -v locale | grep -v localeMap` returns zero hits. All 8 affected files (EvaluationHistoryTable, AccountsPage, EvaluationDetailPage, DashboardFooter, BusinessForm, DiscountResults, TopSkuResults, AdsKeywordResults) use `getIntlLocale(i18n.language)` for date/number formatting. 612 tests pass.
- **R029** — All 47 field labels resolve through `t(field.labelKey!)` in form components. `GENERIC_LABELS` contains i18n keys resolved via `t()`. DiscountResults uses `t()` for all visible strings. `rg` for hardcoded Indonesian labels in form components and EvaluationDetailPage returns zero rendered-string hits. 612 tests pass.
- **R030** — `MONTHS` constant has English abbreviations: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec. `rg "INDO_MONTHS"` returns zero hits. formConfig tests validate all 12 month abbreviations.

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- **R029** — Plan estimated 51 field definitions; actual codebase has 47. All 47 have `labelKey`. The requirement text should say "47" not "51". The 2 DiscountResults labels mentioned in R029 are covered (extracted to `discount.*` keys).

## Deviations

- **47 field definitions instead of 51**: The plan estimated 51 field definitions but the actual codebase has 47 (5+7+3+11+2+2+2+15). All 47 have `labelKey` — no fields missed.
- **BusinessForm.test.tsx updated in T01**: Not in original T01 plan, but 2 tests broke because they asserted rendered labels containing `"Bulan Ini"` which changed to `"generic.thisMonth"`. Direct consequence of GENERIC_LABELS change.
- **AdsKeywordResults.test.tsx updated in T04**: Plan mentioned only DiscountResults.test.tsx, but AdsKeywordResults test also needed `i18n: { language: 'id' }` added to its mock after `i18n` destructuring was added to the component.
- **EvaluationDetailPage test unchanged in T03**: Plan expected ~12 assertion changes, but zero were needed because the test uses real i18n with id.json values matching original hardcoded text. Positive deviation — validates locale file correctness.

## Known Limitations

- The `label` property on `FieldDefinition` is now effectively dead code in form components (all use `labelKey`). EvaluationDetailPage's `shortLabel` and `formatValue` functions still reference `fieldDef?.label` as fallback. A future cleanup could remove `label` entirely, but it's harmless as-is.
- `shortLabel` regex in EvaluationDetailPage matches the Indonesian pattern `Produk Kompetitor \d — `. Works correctly for id locale but will not strip the prefix for EN/TH locales, showing the full translated text instead. Minor UX inconsistency — could be addressed with a locale-aware stripping approach.
- The `fields.ts` `label` property still contains hardcoded Indonesian text (e.g. `"Penjualan Bulan Ini"`). These strings are no longer rendered in the UI (superseded by `labelKey`), but they remain in the source file. S03 sweep may flag these but they are inert.

## Follow-ups

- S03 verification sweep should confirm all residual Indonesian text in source is either in test files, locale files, code comments, or the inert `label` property — not rendered UI text.
- S03 should update `EvaluationForms.test.tsx` which still asserts hardcoded Indonesian field labels (pre-existing test that wasn't in S02 scope since it tests the integration form wrapper, not individual form components).

## Files Created/Modified

- `frontend/src/components/evaluation/forms/types.ts` — Added `labelKey?: string` to FieldDefinition, `displayNameKey?: string` to CategoryDefinition
- `frontend/src/components/evaluation/forms/fields.ts` — Renamed INDO_MONTHS→MONTHS (4 corrections), i18n'd GENERIC_LABELS, added labelKey to 47 fields, displayNameKey to 8 categories
- `frontend/src/components/evaluation/forms/formConfig.ts` — Updated barrel export INDO_MONTHS→MONTHS
- `frontend/src/components/evaluation/forms/formUtils.ts` — Updated import INDO_MONTHS→MONTHS
- `frontend/src/components/evaluation/forms/formConfig.test.ts` — Updated month abbreviation and generic label assertions
- `frontend/src/components/evaluation/forms/OperationalForm.tsx` — label={field.label} → label={t(field.labelKey!)}
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — getFieldLabel uses t(field.labelKey!), monthOptions uses getIntlLocale
- `frontend/src/components/evaluation/forms/VisitorsForm.tsx` — label={t(field.labelKey!)}
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — label={t(field.labelKey!)}
- `frontend/src/components/evaluation/forms/AdsForm.tsx` — label={t(field.labelKey!)}
- `frontend/src/components/evaluation/forms/CampaignForm.tsx` — label={t(field.labelKey!)}
- `frontend/src/components/evaluation/forms/ProductsStatusForm.tsx` — label={t(field.labelKey!)} for both NumberField and SelectField
- `frontend/src/pages/EvaluationDetailPage.tsx` — Category/field labels via t(), formatDate locale-aware, 5 hardcoded strings extracted
- `frontend/src/pages/AccountsPage.tsx` — Module-level dateFormatter → useMemo with getIntlLocale
- `frontend/src/components/dashboard/DashboardFooter.tsx` — Date formatting uses getIntlLocale
- `frontend/src/components/evaluation/calculators/DiscountResults.tsx` — Fully i18n'd: useTranslation + getIntlLocale + 7 extracted strings
- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx` — toLocaleString uses getIntlLocale
- `frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx` — Title extracted to t(), toLocaleString uses getIntlLocale
- `frontend/src/components/evaluation/forms/OperationalForm.test.tsx` — Added i18n mock, key-based assertions
- `frontend/src/components/evaluation/forms/BusinessForm.test.tsx` — Added i18n mock, key-based assertions
- `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx` — Added i18n mock, key-based assertions
- `frontend/src/components/evaluation/forms/ProductsStatusForm.test.tsx` — Added i18n mock, key-based assertions
- `frontend/src/components/evaluation/calculators/DiscountResults.test.tsx` — Added i18n mock, key-based assertions
- `frontend/src/components/evaluation/calculators/AdsKeywordResults.test.tsx` — Added i18n.language to mock
- `frontend/src/locales/id.json` — 74 new keys (624→698 total)
- `frontend/src/locales/en.json` — 74 new keys (624→698 total)
- `frontend/src/locales/th.json` — 74 new keys (624→698 total)

## Forward Intelligence

### What the next slice should know
- All evaluation form field labels, category headings, generic labels, date formatting, and calculator strings are now fully i18n'd. The remaining hardcoded Indonesian in source is limited to: (a) the inert `label` property in `fields.ts` (47 instances — not rendered), (b) code comments, (c) `EvaluationForms.test.tsx` assertions, and (d) any strings in components not yet swept. S03's `rg` sweep should focus on separating rendered UI strings from these inert/test/comment occurrences.
- Locale files have 698 keys each. All 3 files are in sync. The key naming convention is `fields.<category>.<fieldKey>`, `categories.<categoryKey>`, `generic.*`, `evaluation.*`, `discount.*`, `adsKeyword.*`.

### What's fragile
- `EvaluationForms.test.tsx` still asserts hardcoded Indonesian field labels — it was outside S02 scope (integration test for the form wrapper). S03 must update it or it will produce false positives in a sweep for hardcoded Indonesian.
- The `shortLabel` regex in EvaluationDetailPage only matches Indonesian competition product patterns — switching to EN/TH will show full label text instead of stripped short names. Cosmetic but noticeable.

### Authoritative diagnostics
- `rg "id-ID" frontend/src | grep -v test | grep -v locale | grep -v localeMap` — zero hits is the primary proof that R028 is satisfied
- `python3 -c "import json; files=[...]; counts=[len(json.load(open(f))) for f in files]; assert len(set(counts))==1"` — locale file sync check; any mismatch means a key was added to one file but not others
- `npm run test:run` — 612 tests passing is the regression gate; any failure likely means a label or mock was missed

### What assumptions changed
- Plan assumed 51 field definitions — actual count is 47. All 47 are covered.
- Plan assumed EvaluationDetailPage test would need ~12 assertion updates — actual was 0 because it uses real i18n with matching locale values.
- Plan estimated ~80 new locale keys — actual is 74 (6+55+5+8). The gap is from the field count discrepancy.
