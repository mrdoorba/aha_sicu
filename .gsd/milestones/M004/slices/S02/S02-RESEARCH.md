# S02: Locale-aware dates, field labels, and month constants — Research

**Date:** 2026-03-18
**Depth:** Targeted

## Summary

S02 covers three related workstreams: (1) replacing 7 remaining `id-ID` hardcoded date formatting sites with locale-aware formatting using `getIntlLocale()` from S01, (2) extracting 51 field labels + 8 category `displayName` values + `GENERIC_LABELS` from `fields.ts` into locale keys resolved at render time via `t()`, and (3) renaming `INDO_MONTHS` to `MONTHS` with 4 values corrected to English abbreviations (Mei→May, Agu→Aug, Okt→Oct, Des→Dec). Additionally, DiscountResults.tsx and AdsKeywordResults.tsx have ~9 hardcoded display strings that need extraction.

The work is mechanical — all patterns (locale mapping, `t()` extraction, test mock updates) were established in S01. The riskiest part is the `field.label` → `labelKey` mechanism change because it touches 7 form components and EvaluationDetailPage, but the pattern is uniform: every form component renders `field.label` in exactly the same way via `label={field.label}`, making the change systematic.

## Recommendation

Execute in three phases ordered by dependency and risk:

1. **MONTHS + GENERIC_LABELS first** — rename `INDO_MONTHS` → `MONTHS`, fix 4 values, replace `GENERIC_LABELS` hardcoded Indonesian with English generic keys (or i18n keys). Update `formConfig.test.ts` assertions. This is the foundation — `generateMonthLabels()` output changes propagate to BusinessForm labels.

2. **Field labels + category displayNames second** — add `labelKey` to `FieldDefinition`, add `displayNameKey` to `CategoryDefinition`, populate all 51 `labelKey` values and 8 `displayNameKey` values, update 7 form components and EvaluationDetailPage to resolve via `t()`. Update form test assertions.

3. **Date formatting + calculator strings last** — replace 7 remaining `id-ID` sites with `getIntlLocale()`, extract DiscountResults/AdsKeywordResults hardcoded strings. These are isolated components with minimal cross-cutting risk.

## Implementation Landscape

### Key Files

#### Month constants & utilities
- `frontend/src/components/evaluation/forms/fields.ts` — `INDO_MONTHS` (line ~59) needs renaming to `MONTHS` with 4 values corrected. `GENERIC_LABELS` (line ~60) has 6 hardcoded Indonesian strings ("Bulan Ini", "Bulan -1", …). 51 field `label` properties need `labelKey` additions. 8 `MANUAL_DATA_FIELDS` entries need `displayNameKey` additions.
- `frontend/src/components/evaluation/forms/formUtils.ts` — imports `GENERIC_LABELS` and `INDO_MONTHS`. `generateMonthLabels()` uses both. After rename, import changes trivially. `GENERIC_LABELS` needs to become i18n keys.
- `frontend/src/components/evaluation/forms/formConfig.ts` — barrel re-export file. Must update export names `INDO_MONTHS` → `MONTHS`.
- `frontend/src/components/evaluation/forms/types.ts` — `FieldDefinition` interface needs `labelKey?: string` added. `CategoryDefinition` needs `displayNameKey?: string` added.

#### Form components consuming `field.label` (7 components)
- `frontend/src/components/evaluation/forms/OperationalForm.tsx` — passes `label={field.label}` to `NumberField`. Needs `label={t(field.labelKey!)}`.
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — `getFieldLabel()` already uses `t()` for salesMonth/conversionRate but falls back to `field.label` for others. Fallback needs to become `t(field.labelKey!)`.
- `frontend/src/components/evaluation/forms/VisitorsForm.tsx` — passes `label={field.label}` to `NumberField`.
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — passes `label={field.label}` to `CurrencyField`.
- `frontend/src/components/evaluation/forms/AdsForm.tsx` — passes `label={field.label}` to `CurrencyField`.
- `frontend/src/components/evaluation/forms/CampaignForm.tsx` — passes `label={field.label}` to `NumberField`.
- `frontend/src/components/evaluation/forms/ProductsStatusForm.tsx` — passes `label={field.label}` to `NumberField` and `SelectField`.

**Note:** CompetitionForm.tsx is already fully i18n'd — it doesn't use `field.label` at all. It uses inline `t('forms.competition.*')` keys.

#### EvaluationDetailPage consuming `field.label` + `displayName`
- `frontend/src/pages/EvaluationDetailPage.tsx` — builds module-level `CATEGORY_LOOKUP` from `MANUAL_DATA_FIELDS` (line ~63). Uses `categoryInfo?.displayName` (line ~351), `fieldDef?.label` (lines ~427, ~461), hardcoded `"Penjualan ${monthLabels[idx]}"` (line ~393), hardcoded `productLabels = ['Produk Kompetitor 1', 'Produk Kompetitor 2', 'Produk Kompetitor 3']` (line ~405), hardcoded `"Lihat di Shopee"` (line ~436). The `formatDate()` function (line ~78) uses `id-ID`.

#### Date formatting sites (7 remaining after S01)
1. `frontend/src/pages/EvaluationDetailPage.tsx` line ~79 — `toLocaleDateString('id-ID', ...)` in `formatDate()`
2. `frontend/src/pages/AccountsPage.tsx` line ~38 — `new Intl.DateTimeFormat('id-ID', ...)` module-level constant
3. `frontend/src/components/dashboard/DashboardFooter.tsx` line ~21 — `toLocaleDateString('id-ID', ...)`
4. `frontend/src/components/evaluation/forms/BusinessForm.tsx` line ~38 — `toLocaleDateString('id-ID', ...)` in `monthOptions` memo
5. `frontend/src/components/evaluation/calculators/DiscountResults.tsx` line ~21 — `toLocaleString('id-ID')`
6. `frontend/src/components/evaluation/calculators/TopSkuResults.tsx` line ~87 — `toLocaleString('id-ID')`
7. `frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx` line ~51 — `toLocaleString('id-ID')`

#### Calculator components with hardcoded strings
- `frontend/src/components/evaluation/calculators/DiscountResults.tsx` — 7 hardcoded strings: "Invalid discount data", "Discount Check Calculator", "% Diskon TOP SKU", "Range", "Voucher", "Paket Diskon", "Fake Discount Detected". No `useTranslation` hook yet.
- `frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx` — 1 hardcoded string: "Ads Keyword Calculator". Already has `useTranslation`.

#### Test files that will break
- `frontend/src/components/evaluation/forms/formConfig.test.ts` — 6 tests assert `generateMonthLabels()` output with Indonesian month abbreviations ("Des", "Okt", "Agu", "Mei") and `GENERIC_LABELS` strings ("Bulan Ini", "Bulan -1", …). All 6 assertions need updating.
- `frontend/src/components/evaluation/forms/BusinessForm.test.tsx` — ~10 assertions against Indonesian labels: "Penjualan Bulan", "Tingkat Konversi", "Bisnis Analisis", "Bulan Awal Penjualan", "Rata-rata Penjualan 6 Bulan Terakhir", "Bulan Ini". Needs `vi.mock('react-i18next')` and assertions changed to key strings.
- `frontend/src/components/evaluation/forms/OperationalForm.test.tsx` — 7 assertions against Indonesian labels. Needs `vi.mock('react-i18next')` and key-based assertions.
- `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx` — 12 assertions against Indonesian labels. Needs `vi.mock('react-i18next')` and key-based assertions.
- `frontend/src/components/evaluation/forms/ProductsStatusForm.test.tsx` — 1 assertion against "Jumlah Produk". Needs mock + key assertion.
- `frontend/src/components/evaluation/calculators/DiscountResults.test.tsx` — assertions against "% Diskon TOP SKU", "Paket Diskon", "Fake Discount Detected". Needs `vi.mock('react-i18next')` and key assertions.
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — ~12 assertions against Indonesian category names and field labels. Needs key-based assertions.

**Test files that will NOT break:** AdsForm, CampaignForm, VisitorsForm (no test files exist). CompetitionForm.test.tsx (already i18n'd). formUtils.test.ts (only tests formatCurrency/parseCurrency, not month labels directly — but `formConfig.test.ts` does test `generateMonthLabels`).

#### Locale files
- `frontend/src/locales/id.json` — needs ~80 new keys: 51 field labelKeys, 8 category displayNameKeys, 6 GENERIC_LABELS keys, ~9 discount/calculator strings, ~6 EvaluationDetailPage-specific strings
- `frontend/src/locales/en.json` — same keys with English translations
- `frontend/src/locales/th.json` — same keys with Thai translations

### Build Order

**Phase 1: MONTHS rename + GENERIC_LABELS i18n** (foundation, unblocks Phase 2)
1. In `fields.ts`: rename `INDO_MONTHS` → `MONTHS`, fix 4 values (Mei→May, Agu→Aug, Okt→Oct, Des→Dec)
2. In `formConfig.ts`: update barrel export name
3. In `formUtils.ts`: update import
4. For `GENERIC_LABELS`: change to i18n keys — replace `["Bulan Ini", "Bulan -1", ...]` with `["generic.thisMonth", "generic.month1", ...]` and add corresponding locale keys
5. Update `formConfig.test.ts` assertions (month names change, generic labels become keys)
6. Verify: `npm run test:run -- formConfig.test`

**Phase 2: Field labels + category displayNames** (highest risk, most files touched)
1. Add `labelKey?: string` to `FieldDefinition` and `displayNameKey?: string` to `CategoryDefinition` in `types.ts`
2. Add `labelKey` to all 51 field definitions and `displayNameKey` to all 8 category definitions in `fields.ts`
3. Add ~59 locale keys to all 3 JSON files
4. Update 7 form components: change `label={field.label}` → `label={t(field.labelKey!)}`
5. Update EvaluationDetailPage: use `t(categoryInfo.displayNameKey)` for headings, `t(fieldDef.labelKey)` for field labels, extract remaining hardcoded strings
6. Update all affected tests: add `vi.mock('react-i18next')` where missing, change label assertions to key strings
7. Verify: `npm run test:run`

**Phase 3: Date formatting + calculator strings** (isolated, lowest risk)
1. Replace 7 `id-ID` date sites with `getIntlLocale()` from `@/lib/localeMap`
2. Components needing `useTranslation` added: DiscountResults (needs hook + `t()` calls for 7 strings), EvaluationDetailPage `formatDate()` (needs locale param)
3. AccountsPage: change module-level `dateFormatter` to hook-based (like S01 did for EvaluationHistoryTable — useMemo pattern)
4. DashboardFooter: pass locale or use `useTranslation()` hook's `i18n.language`
5. BusinessForm `monthOptions`: already has `useTranslation`, just needs `getIntlLocale(i18n.language)` for the date label
6. Calculator results (DiscountResults, TopSkuResults, AdsKeywordResults): already have or need `useTranslation`, use `getIntlLocale()` for date formatting
7. Update DiscountResults.test.tsx assertions
8. Verify: `npm run test:run`

### Verification Approach

1. **Unit tests:** `cd frontend && npm run test:run` — all 612+ tests pass
2. **Month constant:** `rg "INDO_MONTHS" frontend/src` returns zero hits in non-test source (only `MONTHS` remains)
3. **GENERIC_LABELS:** `rg "Bulan Ini|Bulan -1" frontend/src` returns zero hits in non-test, non-locale source
4. **Date formatting:** `rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap` returns zero hits
5. **Field labels:** `rg "Tingkat Pesanan|Penjualan dari|Pengunjung Lama" frontend/src/components/evaluation/forms/*.tsx frontend/src/pages/EvaluationDetailPage.tsx` returns zero hits
6. **Locale sync:** all 3 locale files have identical key counts (~700+)
7. **Category displayNames:** `rg "Kesehatan Operasional|Bisnis Analisis|Tinjauan Pengunjung|Alat Promosi" frontend/src --type-add 'src:*.tsx' -t src | grep -v test | grep -v locale` returns zero hits

## Constraints

- `FieldDefinition.labelKey` must be optional (`labelKey?: string`) to avoid breaking the type everywhere at once — but in practice every field definition will have it populated. The `label` property must remain for backward compatibility with CompetitionForm's `COMPETITION_FIELDS` (used in EvaluationDetailPage's `CATEGORY_LOOKUP`).
- `generateMonthLabels()` return type stays `string[]` — when `GENERIC_LABELS` becomes i18n keys, the array returns key strings that get resolved via `t()` at the render site (BusinessForm already does this — `t('forms.business.salesMonth', { month: monthLabels[index] })`).
- AccountsPage has a module-level `dateFormatter` — must convert to a hook-based `useMemo` pattern inside the component (same as S01's EvaluationHistoryTable fix), since `useTranslation` can only be called inside components.
- EvaluationDetailPage's `formatDate()` is a standalone function outside the component — must either make it accept a locale parameter or move formatting inline where `i18n.language` is available.

## Common Pitfalls

- **BusinessForm `getFieldLabel` fallback** — The current fallback `return field.label` must become `return t(field.labelKey!)`. But BusinessForm also interpolates month labels via `t('forms.business.salesMonth', { month: monthLabels[index] })`. When `monthLabels[index]` returns a GENERIC_LABELS i18n key (e.g. `"generic.thisMonth"`), that key must be pre-resolved with `t()` before interpolation: `t('forms.business.salesMonth', { month: t(monthLabels[index]) })`.
- **EvaluationDetailPage hardcoded `productLabels` array** — Line ~405 has `['Produk Kompetitor 1', 'Produk Kompetitor 2', 'Produk Kompetitor 3']` as a local constant. Must replace with `t()` calls.
- **EvaluationDetailPage `"Penjualan ${monthLabels[idx]}"`** — Line ~393 constructs a dynamic label using string interpolation with `generateMonthLabels()` output. After GENERIC_LABELS becomes i18n keys, this interpolation must resolve the keys with `t()`.
- **EvaluationDetailPage test has scoring breakdown assertions** — Tests assert `{ category: 'Kesehatan Operasional Toko' }` in mock data for the scoring breakdown table. These are backend response values, NOT frontend display names — the rendering uses `CATEGORY_MAP` which already resolves via `t(mapped.labelKey)`. The mock data should keep its values; only the assertion on rendered text changes.
- **DiscountResults labels are a mix of Indonesian and English** — "% Diskon TOP SKU" is Indonesian, "Range" and "Voucher" are English, "Paket Diskon" is Indonesian, "Fake Discount Detected" is English. All should become i18n keys regardless.

## Open Risks

- **EvaluationDetailPage complexity** — This page has the most interleaved concerns: field labels from `CATEGORY_LOOKUP`, dynamic month labels, hardcoded product labels, date formatting, and `displayName` rendering. Any missed string will be caught by the S03 `rg` sweep, but the page warrants careful review.
- **~80 locale keys to add** — Large batch of keys across 3 files. Key naming consistency is important. Recommend `fields.operational.*`, `fields.business.*`, `fields.visitors.*`, `fields.promoTools.*`, `fields.products.*`, `fields.ads.*`, `fields.campaign.*`, `fields.competition.*` for field labels, `categories.*` for displayNames, `generic.*` for GENERIC_LABELS, `discount.*` for DiscountResults.
