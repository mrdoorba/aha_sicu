# S02: Locale-aware dates, field labels, and month constants

**Goal:** Every evaluation form field label, category heading, month abbreviation, and date format respects the active i18n locale. No hardcoded `id-ID` remains in non-test/non-locale source. `INDO_MONTHS` renamed to `MONTHS` with English abbreviations.
**Demo:** Switch to TH → all evaluation form labels render in Thai, dates show Thai locale formatting, month abbreviations are English (Jan, Feb, …, Dec). Switch to EN → same, in English. All 612+ frontend tests pass.

## Must-Haves

- `INDO_MONTHS` renamed to `MONTHS` with 4 values corrected: Mei→May, Agu→Aug, Okt→Oct, Des→Dec
- `GENERIC_LABELS` replaced with i18n key strings resolved via `t()` at render time
- All 51 field definitions have `labelKey` populated; all 8 category definitions have `displayNameKey` populated
- 7 form components + EvaluationDetailPage resolve labels via `t(field.labelKey!)` instead of `field.label`
- All 7 remaining `id-ID` hardcoded date formatting sites use `getIntlLocale()` from `@/lib/localeMap`
- DiscountResults hardcoded strings extracted to locale keys
- ~80 new locale keys added to all 3 JSON files (id, en, th) in sync
- All frontend tests pass (612+ baseline) with assertions updated in lockstep

## Verification

1. `cd frontend && npm run test:run` — all 612+ tests pass
2. `rg "INDO_MONTHS" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src` — zero hits (only `MONTHS` remains)
3. `rg "Bulan Ini|Bulan -1" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale` — zero hits
4. `rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap` — zero hits
5. `rg "Tingkat Pesanan|Penjualan dari|Pengunjung Lama|Bisnis Analisis|Kesehatan Operasional" frontend/src/components/evaluation/forms/*.tsx frontend/src/pages/EvaluationDetailPage.tsx` — zero hits
6. All 3 locale files have matching key counts (700+)

## Observability / Diagnostics

- **Runtime signals:** When a `generic.*` or `fields.*` or `categories.*` locale key is missing from a JSON file, `react-i18next` returns the raw key string (e.g. `"generic.thisMonth"`) instead of translated text. This is the primary failure signal — raw key strings visible in the UI mean a locale file is out of sync.
- **Inspection surfaces:** `rg "generic\." frontend/src/locales/*.json | wc -l` should return 18 (6 keys × 3 files). `python3 -c "import json; [print(f'{f}: {len(json.load(open(f)))}') for f in ['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']]"` confirms all 3 files have equal key counts.
- **Failure visibility:** TypeScript compilation (`npx tsc --noEmit`) catches any broken import after the `INDO_MONTHS` → `MONTHS` rename. Vitest test failures catch month abbreviation or generic label regressions. `rg "INDO_MONTHS"` returning any hit means the rename is incomplete.
- **Redaction constraints:** No secrets or PII involved in this slice — all changes are UI label strings and locale translations.

## Verification — Diagnostic / Failure-Path Check

7. `cd frontend && npx tsc --noEmit 2>&1 | head -20` — zero TypeScript errors (catches broken imports/references after rename)
8. `python3 -c "import json; files=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; counts=[len(json.load(open(f))) for f in files]; print(dict(zip(files,counts))); assert len(set(counts))==1, f'Key count mismatch: {counts}'"` — all 3 locale files have equal key counts (detects missing/extra keys)

## Integration Closure

- Upstream surfaces consumed: `frontend/src/lib/localeMap.ts` → `getIntlLocale()` from S01
- New wiring introduced: `labelKey`/`displayNameKey` fields on `FieldDefinition`/`CategoryDefinition`, `t()` resolution in 7 form components and EvaluationDetailPage
- What remains before milestone is truly usable end-to-end: S03 verification sweep to confirm zero hardcoded Indonesian anywhere in source

## Tasks

- [x] **T01: Rename INDO_MONTHS to MONTHS and i18n GENERIC_LABELS** `est:20m`
  - Why: Foundation — month constants and generic labels are consumed by `generateMonthLabels()` which feeds BusinessForm and EvaluationDetailPage. Must be correct before field label work begins.
  - Files: `frontend/src/components/evaluation/forms/fields.ts`, `frontend/src/components/evaluation/forms/formConfig.ts`, `frontend/src/components/evaluation/forms/formUtils.ts`, `frontend/src/components/evaluation/forms/formConfig.test.ts`, `frontend/src/locales/id.json`, `frontend/src/locales/en.json`, `frontend/src/locales/th.json`
  - Do: Rename `INDO_MONTHS` → `MONTHS` with 4 values corrected (Mei→May, Agu→Aug, Okt→Oct, Des→Dec). Replace `GENERIC_LABELS` hardcoded Indonesian strings with i18n key strings (`generic.thisMonth`, `generic.month1`…`generic.month5`). Update barrel export in `formConfig.ts`. Update import in `formUtils.ts`. Add 6 `generic.*` locale keys to all 3 JSON files. Update `formConfig.test.ts` assertions for new month abbreviations and generic label keys.
  - Verify: `cd frontend && npm run test:run -- formConfig.test` passes; `rg "INDO_MONTHS" frontend/src` returns zero hits
  - Done when: `MONTHS` has English abbreviations, `GENERIC_LABELS` contains i18n key strings, all formConfig tests pass, barrel export updated

- [x] **T02: Add labelKey to all 51 field definitions and displayNameKey to all 8 categories** `est:25m`
  - Why: Data layer — populates the i18n key strings that form components will consume in T03. Also adds all ~60 new locale keys to JSON files. Separated from component wiring to keep each task focused and independently verifiable.
  - Files: `frontend/src/components/evaluation/forms/types.ts`, `frontend/src/components/evaluation/forms/fields.ts`, `frontend/src/locales/id.json`, `frontend/src/locales/en.json`, `frontend/src/locales/th.json`
  - Do: Add `labelKey?: string` to `FieldDefinition` and `displayNameKey?: string` to `CategoryDefinition` in `types.ts`. Populate `labelKey` on all 51 field definitions (OPERATIONAL_FIELDS, BUSINESS_FIELDS, VISITORS_FIELDS, PROMO_TOOLS_FIELDS, PRODUCTS_FIELDS, ADS_FIELDS, CAMPAIGN_FIELDS, COMPETITION_FIELDS) and `displayNameKey` on all 8 entries in `MANUAL_DATA_FIELDS`. Add corresponding locale keys to all 3 JSON files using namespaced convention: `fields.operational.*`, `fields.business.*`, etc. for labels; `categories.*` for displayNames.
  - Verify: `cd frontend && npm run test:run` passes (no runtime breakage — labelKey is additive); TypeScript build check passes
  - Done when: All 51 fields have `labelKey`, all 8 categories have `displayNameKey`, all 3 locale files have matching new keys, tests still pass

- [x] **T03: Wire t(field.labelKey) into 7 form components and EvaluationDetailPage** `est:40m`
  - Why: Core delivery — this is where field labels actually become locale-aware in the UI. The riskiest task because it touches 8 source files and their tests, but the pattern is uniform.
  - Files: `frontend/src/components/evaluation/forms/OperationalForm.tsx`, `frontend/src/components/evaluation/forms/BusinessForm.tsx`, `frontend/src/components/evaluation/forms/VisitorsForm.tsx`, `frontend/src/components/evaluation/forms/PromoToolsForm.tsx`, `frontend/src/components/evaluation/forms/AdsForm.tsx`, `frontend/src/components/evaluation/forms/CampaignForm.tsx`, `frontend/src/components/evaluation/forms/ProductsStatusForm.tsx`, `frontend/src/pages/EvaluationDetailPage.tsx`, plus test files: `BusinessForm.test.tsx`, `OperationalForm.test.tsx`, `PromoToolsForm.test.tsx`, `ProductsStatusForm.test.tsx`, `EvaluationDetailPage.test.tsx`
  - Do: In 6 simple form components, change `label={field.label}` → `label={t(field.labelKey!)}`, adding `useTranslation` where missing. In BusinessForm, change `getFieldLabel()` fallback from `return field.label` to `return t(field.labelKey!)` and pre-resolve GENERIC_LABELS keys: `t('forms.business.salesMonth', { month: t(monthLabels[index]) })`. In EvaluationDetailPage, use `t(categoryInfo.displayNameKey)` for headings, `t(fieldDef.labelKey)` for field labels, replace hardcoded `productLabels` and `"Penjualan ${monthLabels[idx]}"` and `"Lihat di Shopee"` with `t()` calls. Update all affected test files: add `vi.mock('react-i18next')` where missing, change label assertions from Indonesian text to key strings.
  - Verify: `cd frontend && npm run test:run` — all 612+ tests pass; `rg "Tingkat Pesanan|Penjualan dari|Pengunjung Lama|Bisnis Analisis" frontend/src/components/evaluation/forms/*.tsx frontend/src/pages/EvaluationDetailPage.tsx` returns zero hits
  - Done when: All 7 form components + EvaluationDetailPage render labels via `t()`, zero hardcoded Indonesian labels in those files, all tests pass

- [x] **T04: Replace 7 id-ID date formatting sites and extract calculator hardcoded strings** `est:25m`
  - Why: Closes the last two workstreams — locale-aware date formatting and calculator string extraction. After this, zero `id-ID` hardcodes remain in non-test/non-locale source.
  - Files: `frontend/src/pages/EvaluationDetailPage.tsx`, `frontend/src/pages/AccountsPage.tsx`, `frontend/src/components/dashboard/DashboardFooter.tsx`, `frontend/src/components/evaluation/forms/BusinessForm.tsx`, `frontend/src/components/evaluation/calculators/DiscountResults.tsx`, `frontend/src/components/evaluation/calculators/TopSkuResults.tsx`, `frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx`, `frontend/src/components/evaluation/calculators/DiscountResults.test.tsx`, `frontend/src/locales/id.json`, `frontend/src/locales/en.json`, `frontend/src/locales/th.json`
  - Do: Replace all 7 `id-ID` sites with `getIntlLocale(i18n.language)` from `@/lib/localeMap`. AccountsPage: convert module-level `dateFormatter` to hook-based `useMemo` inside component. EvaluationDetailPage: make `formatDate()` accept locale param or move inline. DashboardFooter: use `useTranslation` + `getIntlLocale`. BusinessForm `monthOptions`: use `getIntlLocale`. Calculator components (DiscountResults, TopSkuResults, AdsKeywordResults): use `getIntlLocale` for `toLocaleString`. Additionally, extract DiscountResults' 7 hardcoded strings and AdsKeywordResults' 1 hardcoded string into locale keys. Add `discount.*` and `adsKeyword.*` keys to locale files. Update DiscountResults.test.tsx assertions.
  - Verify: `cd frontend && npm run test:run` — all tests pass; `rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap` returns zero hits
  - Done when: Zero `id-ID` hardcodes in non-test/non-locale source, all calculator strings extracted to locale keys, all tests pass

## Files Likely Touched

- `frontend/src/components/evaluation/forms/types.ts`
- `frontend/src/components/evaluation/forms/fields.ts`
- `frontend/src/components/evaluation/forms/formConfig.ts`
- `frontend/src/components/evaluation/forms/formUtils.ts`
- `frontend/src/components/evaluation/forms/formConfig.test.ts`
- `frontend/src/components/evaluation/forms/OperationalForm.tsx`
- `frontend/src/components/evaluation/forms/OperationalForm.test.tsx`
- `frontend/src/components/evaluation/forms/BusinessForm.tsx`
- `frontend/src/components/evaluation/forms/BusinessForm.test.tsx`
- `frontend/src/components/evaluation/forms/VisitorsForm.tsx`
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx`
- `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx`
- `frontend/src/components/evaluation/forms/AdsForm.tsx`
- `frontend/src/components/evaluation/forms/CampaignForm.tsx`
- `frontend/src/components/evaluation/forms/ProductsStatusForm.tsx`
- `frontend/src/components/evaluation/forms/ProductsStatusForm.test.tsx`
- `frontend/src/pages/EvaluationDetailPage.tsx`
- `frontend/src/pages/EvaluationDetailPage.test.tsx`
- `frontend/src/pages/AccountsPage.tsx`
- `frontend/src/components/dashboard/DashboardFooter.tsx`
- `frontend/src/components/evaluation/calculators/DiscountResults.tsx`
- `frontend/src/components/evaluation/calculators/DiscountResults.test.tsx`
- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx`
- `frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx`
- `frontend/src/locales/id.json`
- `frontend/src/locales/en.json`
- `frontend/src/locales/th.json`
