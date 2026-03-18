---
estimated_steps: 8
estimated_files: 12
---

# T03: Wire t(field.labelKey) into 7 form components and EvaluationDetailPage

**Slice:** S02 — Locale-aware dates, field labels, and month constants
**Milestone:** M004

## Description

Replace all `field.label` usage in 7 form components and EvaluationDetailPage with `t(field.labelKey!)` calls. This is the highest-risk task in the slice — it touches 8 source files and 5 test files — but the pattern is uniform across the simple form components. BusinessForm and EvaluationDetailPage require special attention due to dynamic label construction. Also extract remaining hardcoded strings from EvaluationDetailPage (product labels, "Lihat di Shopee", dynamic sales month labels).

**Relevant skills:** `test` (for vitest assertion updates)

## Steps

1. **Update 6 simple form components** (each has exactly 1 `label={field.label}` to change):
   - `OperationalForm.tsx` — change `label={field.label}` → `label={t(field.labelKey!)}`. Add `const { t } = useTranslation();` if not already present (check first — some forms may already have it from S01 work on section titles). Import `useTranslation` from `react-i18next` if needed.
   - `VisitorsForm.tsx` — same pattern
   - `PromoToolsForm.tsx` — same pattern
   - `AdsForm.tsx` — same pattern
   - `CampaignForm.tsx` — same pattern
   - `ProductsStatusForm.tsx` — has 2 `field.label` usages (one for NumberField, one for SelectField), change both

2. **Update BusinessForm.tsx:**
   - The `getFieldLabel()` function has a fallback `return field.label` on the last line. Change to `return t(field.labelKey!)`.
   - **Critical pitfall:** `getFieldLabel` calls `t('forms.business.salesMonth', { month: monthLabels[index] })`. After T01, `monthLabels[index]` may return a GENERIC_LABELS i18n key string like `"generic.thisMonth"` (when `data.salesStartMonth` is null/invalid). This key must be pre-resolved: change to `t('forms.business.salesMonth', { month: t(monthLabels[index]) })`. When `monthLabels[index]` is a real month string like `"Dec 2025"`, `t("Dec 2025")` returns it as-is (i18next returns the key when no translation exists for it — which is fine for literal month strings).
   - Similarly for conversionRate: `t('forms.business.conversionRate', { month: monthLabels[0] })` → `t('forms.business.conversionRate', { month: t(monthLabels[0]) })`.

3. **Update EvaluationDetailPage.tsx — category display names:**
   - The page builds a `CATEGORY_LOOKUP` Map from `MANUAL_DATA_FIELDS` at module level (~line 63). It uses `cat.displayName` (~line 67).
   - At render time (~line 351): `const categoryLabel = categoryInfo?.displayName ?? capitalize(category)`.
   - Change to use `displayNameKey`: `const categoryLabel = categoryInfo?.displayNameKey ? t(categoryInfo.displayNameKey) : capitalize(category)`.
   - The component already has `useTranslation()` (it uses `t()` for scoring breakdown). Verify this.

4. **Update EvaluationDetailPage.tsx — field labels:**
   - Line ~427 and ~461: uses `fieldDef?.label` to display field labels.
   - Change to `fieldDef?.labelKey ? t(fieldDef.labelKey) : fieldDef?.label`.

5. **Update EvaluationDetailPage.tsx — hardcoded strings:**
   - Line ~392: `dynamicLabel = \`Penjualan ${monthLabels[idx]}\`` — replace with `dynamicLabel = t('evaluation.salesMonthLabel', { month: t(monthLabels[idx]) })`. Add `evaluation.salesMonthLabel` key to locale files: id="Penjualan {{month}}", en="Sales {{month}}", th="ยอดขาย {{month}}".
   - Line ~403: `const productLabels = ['Produk Kompetitor 1', 'Produk Kompetitor 2', 'Produk Kompetitor 3']` — replace with `const productLabels = [t('evaluation.competitorProduct1'), t('evaluation.competitorProduct2'), t('evaluation.competitorProduct3')]`. Add 3 locale keys.
   - Line ~433: `"Lihat di Shopee"` — replace with `t('evaluation.viewOnShopee')`. Add locale key: id="Lihat di Shopee", en="View on Shopee", th="ดูบน Shopee".

6. **Add ~5 new locale keys to all 3 JSON files** for EvaluationDetailPage strings:
   - `evaluation.salesMonthLabel`: id="Penjualan {{month}}", en="Sales {{month}}", th="ยอดขาย {{month}}"
   - `evaluation.competitorProduct1`: id="Produk Kompetitor 1", en="Competitor Product 1", th="สินค้าคู่แข่ง 1"
   - `evaluation.competitorProduct2`: id="Produk Kompetitor 2", en="Competitor Product 2", th="สินค้าคู่แข่ง 2"
   - `evaluation.competitorProduct3`: id="Produk Kompetitor 3", en="Competitor Product 3", th="สินค้าคู่แข่ง 3"
   - `evaluation.viewOnShopee`: id="Lihat di Shopee", en="View on Shopee", th="ดูบน Shopee"

7. **Update test files** — add `vi.mock('react-i18next')` and change assertions:
   - The established mock pattern from S01 (copy from any S01 test, e.g. `SelectField.test.tsx`):
     ```typescript
     vi.mock('react-i18next', () => ({
       useTranslation: () => ({
         t: (key: string, opts?: Record<string, string>) => {
           if (opts) return `${key}::${JSON.stringify(opts)}`;
           return key;
         },
         i18n: { language: 'id' },
       }),
       Trans: ({ i18nKey }: { i18nKey: string }) => i18nKey,
     }));
     ```
   - **BusinessForm.test.tsx** (~10 assertions): Change assertions from Indonesian text ("Penjualan Bulan", "Tingkat Konversi") to key patterns. The mock `t` returns the key, so `t('forms.business.salesMonth', { month: t('generic.thisMonth') })` returns `"forms.business.salesMonth::{"month":"generic.thisMonth"}"` — adjust assertions accordingly.
   - **OperationalForm.test.tsx** (~7 assertions): Change from Indonesian labels to `fields.operational.*` keys.
   - **PromoToolsForm.test.tsx** (~12 assertions): Change from Indonesian labels to `fields.promoTools.*` keys.
   - **ProductsStatusForm.test.tsx** (~1 assertion): Change from "Jumlah Produk" to key string.
   - **EvaluationDetailPage.test.tsx** (~12 assertions): Change category names and field labels from Indonesian to key strings. Be careful: mock data `{ category: 'Kesehatan Operasional Toko' }` in scoring breakdown is **backend data** — don't change it. Only change assertions on **rendered** display text.

8. **Run tests and verify:**
   - `cd frontend && npm run test:run` — all 612+ tests pass
   - `rg "Tingkat Pesanan|Penjualan dari|Pengunjung Lama|Bisnis Analisis|Kesehatan Operasional" frontend/src/components/evaluation/forms/*.tsx frontend/src/pages/EvaluationDetailPage.tsx` — zero hits

## Must-Haves

- [ ] All 7 form components use `t(field.labelKey!)` instead of `field.label`
- [ ] BusinessForm `getFieldLabel` fallback uses `t(field.labelKey!)` and pre-resolves `monthLabels` with `t()`
- [ ] EvaluationDetailPage uses `t(displayNameKey)` for category headings and `t(labelKey)` for field labels
- [ ] EvaluationDetailPage hardcoded strings (productLabels, "Penjualan ${monthLabels}", "Lihat di Shopee") extracted to `t()` calls
- [ ] ~5 new locale keys in all 3 JSON files for EvaluationDetailPage strings
- [ ] All affected test files have `vi.mock('react-i18next')` and updated assertions
- [ ] All 612+ tests pass

## Verification

- `cd frontend && npm run test:run` — all 612+ tests pass
- `rg "Tingkat Pesanan|Penjualan dari|Pengunjung Lama" frontend/src/components/evaluation/forms/*.tsx frontend/src/pages/EvaluationDetailPage.tsx` — zero hits
- `rg "Bisnis Analisis|Kesehatan Operasional|Alat Promosi|Tinjauan Pengunjung" frontend/src/components/evaluation/forms/*.tsx frontend/src/pages/EvaluationDetailPage.tsx` — zero hits
- `rg "Produk Kompetitor|Lihat di Shopee" frontend/src/pages/EvaluationDetailPage.tsx` — zero hits

## Inputs

- T01 completed: `MONTHS` has English abbreviations, `GENERIC_LABELS` has i18n key strings
- T02 completed: All 51 fields have `labelKey`, all 8 categories have `displayNameKey`, locale keys added
- `vi.mock('react-i18next')` pattern established in S01 (e.g. in `SelectField.test.tsx`, `DeleteEvaluationDialog.test.tsx`)
- Current test baseline: 612+ tests passing across 68 files

## Expected Output

- 7 form component files updated to use `t(field.labelKey!)` 
- `EvaluationDetailPage.tsx` updated with `t()` for category names, field labels, and hardcoded strings
- 5 test files updated with i18n mocks and key-based assertions
- `frontend/src/locales/{id,en,th}.json` — ~5 new `evaluation.*` keys each
- All tests passing

## Observability Impact

- **Signals changed:** Form field labels, category headings, competitor product labels, "Lihat di Shopee" text, and dynamic sales month labels now resolve at render time through `t()` instead of being hardcoded. Switching locale will change all these strings.
- **Inspection:** If a `fields.*`, `categories.*`, or `evaluation.*` locale key is missing from a JSON file, `react-i18next` returns the raw key string (e.g. `"fields.operational.unfulfilledOrderRate"`) instead of translated text. This is the primary visual failure signal.
- **Failure state:** `rg "Tingkat Pesanan|Penjualan dari|Pengunjung Lama" frontend/src/components/evaluation/forms/*.tsx frontend/src/pages/EvaluationDetailPage.tsx | grep -v test | grep -v comment` returning any hit means a form component still uses hardcoded Indonesian.
- **Test coverage:** 4 form test files (OperationalForm, BusinessForm, PromoToolsForm, ProductsStatusForm) now use `vi.mock('react-i18next')` with key-based assertions. EvaluationDetailPage test uses the real i18n module and verifies end-to-end locale resolution.
