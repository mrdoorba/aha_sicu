# S02: Locale-aware dates, field labels, and month constants — UAT

**Milestone:** M004
**Written:** 2026-03-18

## UAT Type

- UAT mode: artifact-driven
- Why this mode is sufficient: All changes are UI label strings, date formatting, and locale file keys. Correctness is verifiable through test suite (612 tests), TypeScript compilation, `rg` sweeps, and locale key count checks. No runtime server or live data needed.

## Preconditions

- Working directory: `.gsd/worktrees/M004/`
- Node modules installed: `cd frontend && npm install` (if not already)
- All 612 frontend tests passing as baseline

## Smoke Test

Run `cd frontend && npm run test:run` — all 612 tests pass. This confirms no regressions from the 74 new locale keys, 47 labelKey wirings, and 7 date format changes.

## Test Cases

### 1. INDO_MONTHS fully renamed to MONTHS

1. `rg "INDO_MONTHS" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src`
2. **Expected:** Zero hits (exit code 1). The constant name `INDO_MONTHS` must not appear anywhere in source.
3. `grep "MONTHS" frontend/src/components/evaluation/forms/fields.ts | head -1`
4. **Expected:** Shows `export const MONTHS = [` with English abbreviations.
5. Verify the 4 corrected values: `grep -E "May|Aug|Oct|Dec" frontend/src/components/evaluation/forms/fields.ts`
6. **Expected:** `May`, `Aug`, `Oct`, `Dec` present (were `Mei`, `Agu`, `Okt`, `Des`).

### 2. GENERIC_LABELS uses i18n keys

1. `grep "generic\." frontend/src/components/evaluation/forms/fields.ts | head -10`
2. **Expected:** Shows entries like `'generic.thisMonth'`, `'generic.month1'`, etc. — raw i18n key strings, not Indonesian text.
3. `rg "generic\." frontend/src/locales/id.json`
4. **Expected:** 6 entries with Indonesian translations (e.g. `"generic.thisMonth": "Bulan Ini"`).
5. `rg "generic\." frontend/src/locales/en.json`
6. **Expected:** 6 entries with English translations (e.g. `"generic.thisMonth": "This Month"`).

### 3. All 47 fields have labelKey, all 8 categories have displayNameKey

1. `grep -c "labelKey" frontend/src/components/evaluation/forms/fields.ts`
2. **Expected:** 47
3. `grep -c "displayNameKey" frontend/src/components/evaluation/forms/fields.ts`
4. **Expected:** 8
5. `rg "fields\." frontend/src/locales/id.json | wc -l`
6. **Expected:** 47 lines (one per field definition)
7. `rg "categories\." frontend/src/locales/id.json | wc -l`
8. **Expected:** 8 lines (one per category)

### 4. Form components use t(field.labelKey!) instead of field.label

1. `rg "field\.label[^K]" frontend/src/components/evaluation/forms/OperationalForm.tsx frontend/src/components/evaluation/forms/BusinessForm.tsx frontend/src/components/evaluation/forms/VisitorsForm.tsx frontend/src/components/evaluation/forms/PromoToolsForm.tsx frontend/src/components/evaluation/forms/AdsForm.tsx frontend/src/components/evaluation/forms/CampaignForm.tsx frontend/src/components/evaluation/forms/ProductsStatusForm.tsx`
2. **Expected:** Zero hits. All 7 form components use `field.labelKey`, not `field.label`.
3. `rg "t\(field\.labelKey" frontend/src/components/evaluation/forms/*.tsx | wc -l`
4. **Expected:** At least 7 hits (one per form component, some have multiple).

### 5. EvaluationDetailPage uses i18n for categories and field labels

1. `rg "displayNameKey" frontend/src/pages/EvaluationDetailPage.tsx`
2. **Expected:** At least 1 hit — `t(categoryInfo.displayNameKey)` or similar.
3. `rg "Tingkat Pesanan|Penjualan dari|Pengunjung Lama|Bisnis Analisis|Kesehatan Operasional" frontend/src/pages/EvaluationDetailPage.tsx`
4. **Expected:** Zero hits (no hardcoded Indonesian category/field labels in rendered code).

### 6. Zero id-ID hardcodes in non-test/non-locale source

1. `rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap`
2. **Expected:** Zero hits (exit code 1). All date/number formatting uses `getIntlLocale(i18n.language)`.

### 7. All 3 locale files have matching key counts

1. `python3 -c "import json; files=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; counts=[len(json.load(open(f))) for f in files]; print(dict(zip(files,counts))); assert len(set(counts))==1, f'Mismatch: {counts}'"`
2. **Expected:** All 3 files show 698 keys. Assertion passes.

### 8. TypeScript compilation clean

1. `cd frontend && npx tsc --noEmit 2>&1 | head -5`
2. **Expected:** Zero errors. No broken imports from INDO_MONTHS→MONTHS rename, no type errors from labelKey/displayNameKey additions.

### 9. Full test suite passes

1. `cd frontend && npm run test:run`
2. **Expected:** 612 tests pass, 68 test files, zero failures. This validates:
   - formConfig.test.ts: English month abbreviations and generic label keys
   - BusinessForm.test.tsx: i18n key-based label assertions
   - OperationalForm.test.tsx: i18n key-based label assertions
   - PromoToolsForm.test.tsx: i18n key-based label assertions
   - ProductsStatusForm.test.tsx: i18n key-based label assertions
   - DiscountResults.test.tsx: i18n key-based assertions
   - AdsKeywordResults.test.tsx: i18n mock with language
   - EvaluationDetailPage.test.tsx: real i18n resolving to Indonesian (unchanged assertions)

### 10. AccountsPage dateFormatter converted to hook-based

1. `rg "useMemo" frontend/src/pages/AccountsPage.tsx`
2. **Expected:** At least 1 hit — dateFormatter is wrapped in useMemo.
3. `rg "getIntlLocale" frontend/src/pages/AccountsPage.tsx`
4. **Expected:** At least 1 hit — uses locale mapping.

### 11. Calculator components use getIntlLocale

1. `rg "getIntlLocale" frontend/src/components/evaluation/calculators/DiscountResults.tsx frontend/src/components/evaluation/calculators/TopSkuResults.tsx frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx`
2. **Expected:** At least 3 hits (one per calculator file).
3. `rg "id-ID" frontend/src/components/evaluation/calculators/*.tsx`
4. **Expected:** Zero hits.

## Edge Cases

### Missing locale key renders raw key string

1. Temporarily remove a `fields.*` key from `en.json`, switch to EN locale.
2. **Expected:** The missing label renders as the raw key string (e.g. `"fields.operational.unfulfilledOrderRate"`) instead of translated text. This is the primary failure signal for missing locale keys — no crash, just visible raw keys.

### Pre-i18n evaluations still display correctly

1. Load an evaluation detail page for a pre-i18n evaluation (one without `_i18n` fields).
2. **Expected:** Falls back to raw Indonesian text via `renderTranslatable()`. No blank fields or errors. The `fieldDef?.labelKey ? t(fieldDef.labelKey) : (fieldDef?.label ?? key)` fallback chain handles missing labelKey gracefully.

### Non-id locale date formatting

1. Switch to TH locale in the UI.
2. View a page with date formatting (AccountsPage, EvaluationDetailPage, DashboardFooter).
3. **Expected:** Dates render in Thai locale format (th-TH), not Indonesian (id-ID).

## Failure Signals

- Any of the 612 tests failing = regression from i18n wiring
- `rg "INDO_MONTHS"` returning hits = incomplete rename
- `rg "id-ID" | grep -v test | grep -v locale | grep -v localeMap` returning hits = missed date formatting site
- Locale key count mismatch between files = missing translations in one language
- TypeScript errors = broken import or type mismatch from refactoring
- Raw i18n key strings (e.g. `"fields.business.salesMonth0"`) visible in UI = component not calling `t()` or key missing from locale file

## Requirements Proved By This UAT

- **R028** — Test case #6 proves zero id-ID hardcodes remain. Test case #10 and #11 prove locale-aware formatting.
- **R029** — Test cases #2, #3, #4, #5 prove field labels, generic labels, and calculator labels use t() with locale keys.
- **R030** — Test case #1 proves INDO_MONTHS renamed to MONTHS with English abbreviations.
- **R032** (partially) — Test case #9 proves all 612 tests pass after i18n extraction with updated assertions.

## Not Proven By This UAT

- **R031** (zero hardcoded Indonesian in source) — S02 extracted the bulk of strings but the `label` property in `fields.ts` still contains hardcoded Indonesian (inert/not rendered). S03 sweep will verify the residual is truly non-rendered.
- Live runtime visual verification — switching languages in a running browser is not tested here (artifact-driven only). S03 UAT or manual testing should cover this.
- Thai and English translation quality — locale files have professional translations but no native speaker review.

## Notes for Tester

- The `label` property in `fields.ts` still shows hardcoded Indonesian (e.g. `"Penjualan Bulan Ini"`). This is **expected** — it's now dead code superseded by `labelKey`. Form components use `t(field.labelKey!)`. Don't flag these as failures.
- `EvaluationForms.test.tsx` still asserts hardcoded Indonesian strings — this is a pre-existing integration test that was outside S02 scope. S03 will address it.
- The `shortLabel` regex in EvaluationDetailPage only strips Indonesian competition product prefixes. In EN/TH locales, competition product labels will show full text instead of stripped short names. This is a known cosmetic gap.
- The comment `{/* Computed: % Pengunjung Lama */}` in VisitorsForm.tsx is a code comment, not rendered UI text. Not a failure.
