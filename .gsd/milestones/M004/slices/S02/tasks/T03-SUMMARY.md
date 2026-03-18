---
id: T03
parent: S02
milestone: M004
provides:
  - All 7 form components resolve field labels via t(field.labelKey!) instead of field.label
  - EvaluationDetailPage resolves category headings via t(displayNameKey) and field labels via t(labelKey)
  - EvaluationDetailPage hardcoded strings (competitor product labels, sales month labels, "Lihat di Shopee") extracted to t() calls
  - 5 new evaluation.* locale keys in all 3 JSON files
key_files:
  - frontend/src/components/evaluation/forms/OperationalForm.tsx
  - frontend/src/components/evaluation/forms/BusinessForm.tsx
  - frontend/src/components/evaluation/forms/VisitorsForm.tsx
  - frontend/src/components/evaluation/forms/PromoToolsForm.tsx
  - frontend/src/components/evaluation/forms/AdsForm.tsx
  - frontend/src/components/evaluation/forms/CampaignForm.tsx
  - frontend/src/components/evaluation/forms/ProductsStatusForm.tsx
  - frontend/src/pages/EvaluationDetailPage.tsx
key_decisions:
  - EvaluationDetailPage test keeps real i18n (not mocked) since locale values match original hardcoded text — zero assertion changes needed
  - shortLabel regex in EvaluationDetailPage intentionally retained (operates on resolved translated text, not hardcoded UI string)
patterns_established:
  - Form component tests that mock react-i18next use key-based assertions; page-level tests that use real i18n verify end-to-end resolution
  - t(field.labelKey!) with non-null assertion is the standard pattern for form field labels (all 47 fields have labelKey)
observability_surfaces:
  - Raw i18n key strings (e.g. "fields.operational.unfulfilledOrderRate") appearing in the UI = missing locale key
  - rg "Tingkat Pesanan|Penjualan dari" in form .tsx files should return zero non-test hits
duration: 25m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T03: Wire t(field.labelKey) into 7 form components and EvaluationDetailPage

**Replaced all field.label usages with t(field.labelKey!) in 7 form components and EvaluationDetailPage, extracted 5 hardcoded strings to locale keys, updated 4 test files with i18n mocks**

## What Happened

Wired i18n translation through all form field labels and the EvaluationDetailPage in a uniform pass:

1. **6 simple form components** (Operational, Visitors, PromoTools, Ads, Campaign, ProductsStatus): Changed `label={field.label}` → `label={t(field.labelKey!)}`. All already had `useTranslation` from S01 section title work. ProductsStatusForm had 2 label usages (NumberField + SelectField), both updated.

2. **BusinessForm**: Changed `getFieldLabel()` fallback from `return field.label` to `return t(field.labelKey!)`. Pre-resolved GENERIC_LABELS i18n keys in month label interpolation: `t('forms.business.salesMonth', { month: t(monthLabels[index]) })` — this handles both real month strings (e.g. `"Jan 2026"` passes through `t()` unchanged) and generic label keys (e.g. `"generic.thisMonth"` resolves to translated text).

3. **EvaluationDetailPage — categories**: Added `displayNameKey` to the `CATEGORY_LOOKUP` Map and changed render-time resolution to `t(categoryInfo.displayNameKey)` with `capitalize(category)` fallback.

4. **EvaluationDetailPage — field labels**: Changed both field label display sites (competition section and regular sections) from `fieldDef?.label` to `fieldDef?.labelKey ? t(fieldDef.labelKey) : (fieldDef?.label ?? key)`.

5. **EvaluationDetailPage — hardcoded strings**: Replaced `"Penjualan ${monthLabels[idx]}"` → `t('evaluation.salesMonthLabel', { month: t(monthLabels[idx]) })`, `productLabels` array → 3 `t()` calls, `"Lihat di Shopee"` → `t('evaluation.viewOnShopee')`.

6. **Locale files**: Added 5 new `evaluation.*` keys to all 3 JSON files (id/en/th), bringing total from 685 → 690 keys each.

7. **Test files**: Added `vi.mock('react-i18next')` with key-returning mock to 4 form test files (OperationalForm, BusinessForm, PromoToolsForm, ProductsStatusForm) and updated all label assertions to use i18n key patterns. EvaluationDetailPage test kept real i18n — since id.json locale values exactly match the original hardcoded Indonesian text, all assertions pass without changes.

## Verification

- `cd frontend && npm run test:run` — all 612 tests pass across 68 files
- `rg "Tingkat Pesanan|Penjualan dari|Pengunjung Lama"` on form .tsx + EvaluationDetailPage — zero hits (excluding test files and comments)
- `rg "Bisnis Analisis|Kesehatan Operasional|Alat Promosi|Tinjauan Pengunjung"` — zero hits
- `rg "Produk Kompetitor|Lihat di Shopee" EvaluationDetailPage.tsx` — only the `shortLabel` regex (code, not displayed text)
- TypeScript `tsc --noEmit` — zero errors
- All 3 locale files have 690 matching keys

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `cd frontend && npm run test:run` | 0 | ✅ pass | 28s |
| 2 | `rg "Tingkat Pesanan\|Penjualan dari\|Pengunjung Lama" ...tsx ...EvaluationDetailPage.tsx \| grep -v test` | 1 (no matches except comment) | ✅ pass | <1s |
| 3 | `rg "Bisnis Analisis\|Kesehatan Operasional\|Alat Promosi\|Tinjauan Pengunjung" ...tsx` | 1 (no matches) | ✅ pass | <1s |
| 4 | `rg "Produk Kompetitor\|Lihat di Shopee" EvaluationDetailPage.tsx` | 0 (only shortLabel regex) | ✅ pass | <1s |
| 5 | `npx tsc --noEmit` | 0 | ✅ pass | 7s |
| 6 | `python3 locale key count check` | 0 (690 = 690 = 690) | ✅ pass | <1s |
| S-1 | `rg "INDO_MONTHS" frontend/src` | 1 (zero hits) | ✅ pass | <1s |
| S-2 | `rg "Bulan Ini\|Bulan -1" frontend/src \| grep -v test \| grep -v locale` | 0 (fields.ts label property only) | ✅ pass | <1s |
| S-5 | `rg "Tingkat Pesanan..." on forms + detail page` | same as #2 | ✅ pass | <1s |

## Diagnostics

- **Missing locale key detection**: If a `fields.*`, `categories.*`, or `evaluation.*` key is absent from a locale JSON file, `react-i18next` returns the raw key string in the UI. This is the primary failure signal.
- **Verification command**: `rg "Tingkat Pesanan|Penjualan dari|Bisnis Analisis|Kesehatan Operasional" frontend/src/components/evaluation/forms/*.tsx frontend/src/pages/EvaluationDetailPage.tsx | grep -v test` — should return zero hits. Any hit means a form component still uses hardcoded Indonesian.
- **Locale key count**: `python3 -c "import json; [print(f'{f}: {len(json.load(open(f)))}') for f in ['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']]"` — all must show 690.

## Deviations

- **EvaluationDetailPage test not updated**: Plan expected ~12 assertion changes in EvaluationDetailPage.test.tsx. In practice, zero changes were needed because the test uses the real i18n module (loaded via test setup's `import '../i18n'`) and the id.json locale values exactly match the original hardcoded Indonesian text. This is a positive deviation — it validates that the locale file values are correct.
- **4 test files updated instead of 5**: Only OperationalForm, BusinessForm, PromoToolsForm, and ProductsStatusForm tests needed `vi.mock('react-i18next')` + assertion updates. EvaluationDetailPage test was unchanged.

## Known Issues

- `shortLabel` regex in EvaluationDetailPage still matches the Indonesian pattern `Produk Kompetitor \d — `. This works correctly because the id.json locale values contain this prefix. When switching to EN/TH locales, the regex will not match and labels will show the full translated text (e.g. "Competitor Product 1 — Product Name" instead of just "Product Name"). This is a minor UX inconsistency for T04 or a follow-up to address with a locale-aware stripping approach.
- The `label` property on `FieldDefinition` is now effectively dead code in the 7 form components (all use `labelKey`). EvaluationDetailPage's `shortLabel` and `formatValue` functions still reference `fieldDef?.label` as fallback. A future cleanup task could remove `label` entirely.

## Files Created/Modified

- `frontend/src/components/evaluation/forms/OperationalForm.tsx` — Changed `label={field.label}` → `label={t(field.labelKey!)}`
- `frontend/src/components/evaluation/forms/VisitorsForm.tsx` — Same pattern
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — Same pattern
- `frontend/src/components/evaluation/forms/AdsForm.tsx` — Same pattern
- `frontend/src/components/evaluation/forms/CampaignForm.tsx` — Same pattern
- `frontend/src/components/evaluation/forms/ProductsStatusForm.tsx` — Same pattern for both NumberField and SelectField
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — Changed `getFieldLabel` fallback to `t(field.labelKey!)`, pre-resolved monthLabels with `t()`
- `frontend/src/pages/EvaluationDetailPage.tsx` — Added `displayNameKey` to CATEGORY_LOOKUP, changed category/field label resolution to `t()`, extracted hardcoded strings
- `frontend/src/components/evaluation/forms/OperationalForm.test.tsx` — Added `vi.mock('react-i18next')`, changed label assertions to key patterns
- `frontend/src/components/evaluation/forms/BusinessForm.test.tsx` — Added i18n mock, changed all label assertions to key patterns
- `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx` — Added i18n mock, changed label assertions to key patterns
- `frontend/src/components/evaluation/forms/ProductsStatusForm.test.tsx` — Added i18n mock, changed label assertions to key patterns
- `frontend/src/locales/id.json` — Added 5 `evaluation.*` keys (690 total)
- `frontend/src/locales/en.json` — Added 5 `evaluation.*` keys (690 total)
- `frontend/src/locales/th.json` — Added 5 `evaluation.*` keys (690 total)
- `.gsd/milestones/M004/slices/S02/tasks/T03-PLAN.md` — Added Observability Impact section
