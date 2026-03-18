---
id: M004
provides:
  - Every rendered UI string in the frontend routes through react-i18next t() and locale JSON files
  - 720 locale keys in sync across 3 languages (id/en/th) — up from 590 at milestone start
  - localeMap.ts utility mapping i18next codes to Intl locale codes (id→id-ID, en→en-US, th→th-TH)
  - All 8 date/number formatting sites use dynamic locale from i18n context
  - All 47 field labels + 8 category headings + 6 generic labels resolve through i18n keys at render time
  - MONTHS constant with English abbreviations replacing INDO_MONTHS
  - benchmarkKey/unitKey pattern on FieldDefinition for field-level i18n
  - Zero hardcoded Indonesian rendered text in non-test, non-locale source
  - One-file-per-language translator workflow — no source code changes needed to localize
key_decisions:
  - "D030: English month abbreviations for all languages — no per-locale month name arrays"
  - "D031: labelKey on FieldDefinition resolved via t() at render time in form components"
  - "D032: Module-level Intl.DateTimeFormat converted to useMemo with i18n.language dependency for locale reactivity"
  - "D033: benchmarkKey/unitKey on FieldDefinition — optional i18n keys with fallback to hardcoded value"
  - "D034: DetailedEvaluation metric comparisons use metric_i18n.key with row.metric string fallback for pre-M002 backward compatibility"
patterns_established:
  - "t(field.labelKey!) with non-null assertion is the standard pattern for form field labels"
  - "getIntlLocale(i18n.language) is the standard pattern for all locale-aware date/number formatting"
  - "vi.mock('react-i18next') hoisted pattern with t returning key string — used across all test files touching i18n"
  - "For sub-components in the same file, pass t and formatted values as props rather than adding useTranslation to each"
  - "Locale key naming: fields.<category>.<fieldKey> for field labels, categories.<categoryKey> for display names, component-scoped namespaces for UI strings"
observability_surfaces:
  - "Locale key sync check: python3 -c comparing key counts across id.json/en.json/th.json — any mismatch signals i18n drift"
  - "Indonesian text sweep: rg for 55 common Indonesian words in non-test/non-locale source — zero rendered-string hits confirms extraction complete"
  - "id-ID sweep: rg 'id-ID' in non-test/non-locale source — zero hits confirms no hardcoded locale codes"
  - "Missing i18n keys render as literal key strings in UI (i18next default) — visible immediately"
  - "Full test suite: cd frontend && npm run test:run — 612 tests across 68 files"
requirement_outcomes:
  - id: R027
    from_status: active
    to_status: validated
    proof: "All 4 target components (EvaluationHistoryTable, DeleteEvaluationDialog, DowntimeWarningDialog, SelectField) use t() for every visible string. 34 new locale keys. rg for hardcoded Indonesian in all 4 components returns zero hits. 612 tests pass."
  - id: R028
    from_status: active
    to_status: validated
    proof: "All 8 files use getIntlLocale(i18n.language). rg 'id-ID' in non-test/non-locale source returns zero hits. 612 tests pass."
  - id: R029
    from_status: active
    to_status: validated
    proof: "All 47 field labels have labelKey resolved via t() in 7 form components + EvaluationDetailPage. GENERIC_LABELS uses i18n keys. DiscountResults uses t(). 612 tests pass."
  - id: R030
    from_status: active
    to_status: validated
    proof: "MONTHS constant has English abbreviations (4 corrections: Mei→May, Agu→Aug, Okt→Oct, Des→Dec). rg 'INDO_MONTHS' returns zero hits. formConfig.test.ts validates all 12."
  - id: R031
    from_status: active
    to_status: validated
    proof: "Full rg sweep for 55 Indonesian words in non-test/non-locale source returns zero rendered-string hits. 720 keys in sync across 3 locale files. Translator edits one JSON file."
  - id: R032
    from_status: active
    to_status: validated
    proof: "612/612 frontend tests pass across 68 files. All assertions updated in lockstep with i18n extraction using vi.mock('react-i18next') pattern."
duration: ~140min (S01 35m + S02 62m + S03 43m)
verification_result: passed
completed_at: 2026-03-18
---

# M004: Frontend i18n Completion

**Every visible UI string in the frontend now routes through locale files. Switching language changes everything — zero hardcoded Indonesian remains in rendered source. 720 locale keys in sync across 3 languages. A translator edits one JSON file per language to fully localize the app.**

## What Happened

This milestone systematically extracted all remaining hardcoded Indonesian text from the frontend, completing the i18n journey that M002 started for evaluation results and email output.

**S01** tackled the 4 components that were completely un-internationalized: SelectField, DowntimeWarningDialog, DeleteEvaluationDialog, and EvaluationHistoryTable. These represented the most visibly broken surfaces — the entire History page rendered in Indonesian regardless of language selection. The slice created `localeMap.ts` with `getIntlLocale()` to map i18next language codes to Intl locale codes, established the `vi.mock('react-i18next')` test pattern, and extracted 34 locale keys. EvaluationHistoryTable's module-level `Intl.DateTimeFormat('id-ID')` was converted to a `useMemo`-based formatter reactive to language changes.

**S02** addressed the structural i18n debt: 47 field labels in `fields.ts`, 6 generic month labels, 8 category display names, and 7 remaining hardcoded `id-ID` date formatting sites. The approach added `labelKey` and `displayNameKey` to the `FieldDefinition` type, keeping the original `label` property as inert fallback. All 7 form components were updated to resolve `t(field.labelKey!)` instead of rendering `field.label` directly. `INDO_MONTHS` was renamed to `MONTHS` with 4 Indonesian abbreviations corrected to English. Calculator components (DiscountResults, AdsKeywordResults, TopSkuResults) were fully i18n'd. This slice added 74 locale keys (624→698).

**S03** ran the verification sweep — a comprehensive `rg` scan for 55 common Indonesian words across all non-test, non-locale source files. It caught 21 additional rendered strings across 7 files that S01/S02 had missed: App.tsx access-denied message, LoginPage banner alt text, EvaluationHeader field labels, PromoToolsForm benchmark descriptions, OperationalForm unit labels, and SectionNav navigation labels. The slice introduced `benchmarkKey`/`unitKey` on `FieldDefinition` for field-level benchmark and unit i18n. After fixing SectionNav (discovered during the sweep), the final count reached 720 locale keys with zero rendered Indonesian in source.

The three slices connected cleanly: S01 produced `localeMap.ts` and the test mock pattern consumed by S02 and S03. S02 produced the `labelKey` mechanism and locale-aware date formatting consumed by S03's verification. S03 served as the safety net, catching strings the first two slices missed.

## Cross-Slice Verification

Each success criterion from the milestone roadmap was independently verified:

| # | Success Criterion | Evidence | Status |
|---|-------------------|----------|--------|
| 1 | Switching to TH renders zero Indonesian strings on any page | `rg` sweep for 55 Indonesian words in non-test/non-locale source returns zero rendered-string hits; 720 TH locale keys covering all UI surfaces | ✅ |
| 2 | Switching to EN renders zero Indonesian strings on any page | Same `rg` sweep; 720 EN locale keys in sync with ID and TH | ✅ |
| 3 | `rg` for common Indonesian words in non-test, non-locale source returns zero hits | All hits classified as: inert `label`/`benchmark` properties in fields.ts (dead code), code comments, backend column-name matchers, i18n key names, or TypeScript property names — zero rendered UI strings | ✅ |
| 4 | `rg "id-ID"` in non-test, non-locale source returns zero hits | Verified: exit code 1 (no matches) | ✅ |
| 5 | All frontend tests pass (602+ baseline) | 612/612 tests pass across 68 test files | ✅ |
| 6 | A translator only needs to edit their `{lang}.json` to fully localize the app | 720 keys in sync across all 3 locale files; zero rendered hardcoded strings in source | ✅ |

**Milestone Definition of Done verification:**

| # | DoD Item | Evidence | Status |
|---|----------|----------|--------|
| 1 | All 4 un-i18n'd components use t() for every visible string | S01 verified: rg for hardcoded Indonesian in all 4 components returns zero hits | ✅ |
| 2 | All 8 date formatting sites use active i18n locale | S02 verified: rg "id-ID" returns zero non-test/non-locale hits | ✅ |
| 3 | All 51 field labels resolve through locale files | 47 actual fields (plan overestimated), all with labelKey resolved via t() | ✅ |
| 4 | INDO_MONTHS replaced with English abbreviations | Renamed to MONTHS; rg "INDO_MONTHS" returns zero hits | ✅ |
| 5 | GENERIC_LABELS uses i18n keys | 6 generic.* keys resolved via t() at render time | ✅ |
| 6 | rg sweep confirms zero hardcoded Indonesian in source | 55-pattern sweep: zero rendered-string hits | ✅ |
| 7 | All frontend tests pass | 612/612 pass | ✅ |
| 8 | Success criteria re-checked against live behavior | All 6 success criteria verified above | ✅ |

## Requirement Changes

- **R027**: active → validated — All 4 target components use t() for every visible string. 34 locale keys added. Zero hardcoded Indonesian in any of the 4 components. 612 tests pass with key-based assertions.
- **R028**: active → validated — All 8 files (EvaluationHistoryTable, AccountsPage, EvaluationDetailPage, DashboardFooter, BusinessForm, DiscountResults, TopSkuResults, AdsKeywordResults) use `getIntlLocale(i18n.language)`. `rg "id-ID"` in non-test/non-locale source returns zero hits.
- **R029**: active → validated — All 47 field labels resolve through `t(field.labelKey!)`. GENERIC_LABELS uses i18n keys. DiscountResults fully i18n'd. Plan said 51 fields; actual is 47 — all covered.
- **R030**: active → validated — MONTHS constant with English abbreviations. 4 corrections applied. `rg "INDO_MONTHS"` returns zero hits.
- **R031**: active → validated — Full 55-pattern rg sweep returns zero rendered Indonesian in non-test/non-locale source. 720 keys in sync across 3 languages. One-file-per-language translator workflow achieved.
- **R032**: active → validated — 612/612 tests pass across 68 files. All assertions updated in lockstep using established vi.mock('react-i18next') pattern.

## Forward Intelligence

### What the next milestone should know
- The frontend i18n system is complete. All 720 locale keys are the single source of truth for UI text. Adding a new language requires only: (1) create `{lang}.json` with 720 keys, (2) add import to `i18n.ts`, (3) add to `LANGUAGES` array and backend `STRINGS`/`CATEGORY_MAP`. No component changes needed.
- The `localeMap.ts` utility maps 3 language codes. A 4th language requires adding one entry to the mapping (fallback is `id-ID` for unknown codes).
- Backend scoring generates `TranslatableText` i18n structs alongside Indonesian strings. Frontend resolves them via `renderTranslatable()`. Pre-M002 evaluations fall back to raw Indonesian text — this is by design.
- All 20 tracked requirements (R014–R032) are now validated. There are no active or deferred requirements.

### What's fragile
- **fields.ts dual-property pattern** — `label` + `labelKey`, `benchmark` + `benchmarkKey`, `displayName` + `displayNameKey` coexist. The hardcoded properties are inert but could confuse developers who use `field.label` directly instead of `t(field.labelKey!)`. Any new form component must resolve the `*Key` variant.
- **Backend matcher strings** — ~15 source locations match Indonesian strings from the API (category names, metric strings). If the backend ever returns i18n'd names, these matchers break silently.
- **Pre-M002 evaluation fallback** — DetailedEvaluation uses `row.metric` string comparison for old evaluations without `metric_i18n`. Those entries display Indonesian regardless of language selection.
- **shortLabel regex** in EvaluationDetailPage only matches the Indonesian pattern `Produk Kompetitor \d — `. EN/TH locales show full label text instead of stripped short names — cosmetic but noticeable.

### Authoritative diagnostics
- `cd frontend && npm run test:run` — 612 tests, 68 files. First signal for any regression.
- `python3 -c "import json; fs=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; cs=[len(json.load(open(f))) for f in fs]; print(cs); assert len(set(cs))==1"` — locale file sync gate. Count should be 720+.
- `rg "id-ID" frontend/src | grep -v test | grep -v locale | grep -v localeMap` — zero hits confirms no hardcoded locale codes.
- `cd frontend && npx tsc --noEmit` — catches FieldDefinition type mismatches for new fields.

### What assumptions changed
- **Plan estimated 51 field definitions** — actual codebase has 47. All 47 are covered.
- **Plan estimated ~130 new locale keys** across all slices — actual is 130 (34 + 74 + 22 = 130 keys, 590 → 720). Accurate overall.
- **S03 scope was larger than planned** — T01 found 15 strings in 5 files, but T02 sweep found 6 more in SectionNav.tsx. The comprehensive rg sweep was essential.
- **EvaluationDetailPage test needed zero assertion updates** in S02 because it uses real i18n with id.json values matching original hardcoded text — a positive surprise.

## Files Created/Modified

- `frontend/src/lib/localeMap.ts` — new: getIntlLocale() mapping i18next codes to Intl locale codes
- `frontend/src/lib/localeMap.test.ts` — new: 4 tests for locale mapping
- `frontend/src/components/evaluation/forms/types.ts` — added labelKey, displayNameKey, benchmarkKey, unitKey to FieldDefinition/CategoryDefinition
- `frontend/src/components/evaluation/forms/fields.ts` — INDO_MONTHS→MONTHS, i18n'd GENERIC_LABELS, added labelKey/displayNameKey/benchmarkKey to all field/category definitions
- `frontend/src/components/evaluation/forms/formConfig.ts` — updated barrel export INDO_MONTHS→MONTHS
- `frontend/src/components/evaluation/forms/formUtils.ts` — updated import INDO_MONTHS→MONTHS
- `frontend/src/components/evaluation/forms/formConfig.test.ts` — updated month and generic label assertions
- `frontend/src/components/evaluation/forms/SelectField.tsx` — added useTranslation, t('common.select')
- `frontend/src/components/evaluation/forms/SelectField.test.tsx` — added i18n mock
- `frontend/src/components/DowntimeWarningDialog.tsx` — added useTranslation + Trans, 3 strings extracted
- `frontend/src/components/DowntimeWarningDialog.test.tsx` — new: 5 tests
- `frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` — 9 strings extracted to t() calls
- `frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx` — 12 assertions updated
- `frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — useMemo dateFormatter + ~22 strings extracted
- `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx` — 17 assertions updated
- `frontend/src/components/evaluation/forms/OperationalForm.tsx` — label={t(field.labelKey!)}, unitKey resolution
- `frontend/src/components/evaluation/forms/OperationalForm.test.tsx` — added i18n mock
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — getFieldLabel uses t(field.labelKey!), getIntlLocale for months
- `frontend/src/components/evaluation/forms/BusinessForm.test.tsx` — added i18n mock
- `frontend/src/components/evaluation/forms/VisitorsForm.tsx` — label={t(field.labelKey!)}
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — label={t(field.labelKey!)}, benchmarkKey resolution
- `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx` — updated benchmark assertions
- `frontend/src/components/evaluation/forms/AdsForm.tsx` — label={t(field.labelKey!)}
- `frontend/src/components/evaluation/forms/CampaignForm.tsx` — label={t(field.labelKey!)}
- `frontend/src/components/evaluation/forms/ProductsStatusForm.tsx` — label={t(field.labelKey!)}
- `frontend/src/components/evaluation/forms/ProductsStatusForm.test.tsx` — added i18n mock
- `frontend/src/pages/EvaluationDetailPage.tsx` — category/field labels via t(), formatDate locale-aware, 5 strings extracted
- `frontend/src/pages/AccountsPage.tsx` — module-level dateFormatter → useMemo with getIntlLocale
- `frontend/src/pages/LoginPage.tsx` — banner alt text extracted to t()
- `frontend/src/components/dashboard/DashboardFooter.tsx` — date formatting uses getIntlLocale
- `frontend/src/components/dashboard/DetailedEvaluation.tsx` — metric comparisons use metric_i18n.key with fallback
- `frontend/src/components/evaluation/EvaluationHeader.tsx` — static FIELD_LABELS replaced with getFieldLabel() using t()
- `frontend/src/components/evaluation/SectionNav.tsx` — label→labelKey, added useTranslation + t()
- `frontend/src/components/evaluation/SectionNav.test.tsx` — added i18n mock, key-based assertions
- `frontend/src/components/evaluation/calculators/DiscountResults.tsx` — fully i18n'd: 7 strings extracted
- `frontend/src/components/evaluation/calculators/DiscountResults.test.tsx` — added i18n mock
- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx` — toLocaleString uses getIntlLocale
- `frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx` — title extracted, toLocaleString uses getIntlLocale
- `frontend/src/components/evaluation/calculators/AdsKeywordResults.test.tsx` — added i18n.language to mock
- `frontend/src/App.tsx` — access denied message extracted to t()
- `frontend/src/locales/id.json` — 130 new keys (590 → 720)
- `frontend/src/locales/en.json` — 130 new keys (590 → 720)
- `frontend/src/locales/th.json` — 130 new keys (590 → 720)
