---
id: T04
parent: S02
milestone: M004
provides:
  - All 7 id-ID date formatting sites replaced with getIntlLocale(i18n.language)
  - AccountsPage dateFormatter converted from module-level to hook-based useMemo
  - DiscountResults 7 hardcoded strings extracted to t() with discount.* locale keys
  - AdsKeywordResults title string extracted to t('adsKeyword.title')
  - 8 new locale keys (discount.* + adsKeyword.*) in all 3 JSON files
key_files:
  - frontend/src/pages/EvaluationDetailPage.tsx
  - frontend/src/pages/AccountsPage.tsx
  - frontend/src/components/dashboard/DashboardFooter.tsx
  - frontend/src/components/evaluation/forms/BusinessForm.tsx
  - frontend/src/components/evaluation/calculators/DiscountResults.tsx
  - frontend/src/components/evaluation/calculators/TopSkuResults.tsx
  - frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx
  - frontend/src/components/evaluation/calculators/DiscountResults.test.tsx
  - frontend/src/components/evaluation/calculators/AdsKeywordResults.test.tsx
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
key_decisions:
  - AdsKeywordResults.test.tsx i18n mock needed i18n.language addition (same pattern as other calculator test mocks)
patterns_established:
  - getIntlLocale(i18n.language) is the standard pattern for locale-aware date/number formatting across all components
  - Module-level Intl.DateTimeFormat must be converted to useMemo inside component when it needs locale reactivity
observability_surfaces:
  - "rg 'id-ID' frontend/src | grep -v test | grep -v locale | grep -v localeMap" returns zero hits — confirms no hardcoded locale remains
  - Missing discount.*/adsKeyword.* keys produce raw key strings in UI (primary failure signal)
duration: 15m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T04: Replace 7 id-ID date formatting sites and extract calculator hardcoded strings

**Replaced all 7 id-ID hardcoded date formatting sites with getIntlLocale(i18n.language), extracted 8 hardcoded strings from DiscountResults and AdsKeywordResults into locale keys, and updated test assertions — zero id-ID hardcodes remain in non-test/non-locale source**

## What Happened

Executed all 7 steps from the task plan:

1. **EvaluationDetailPage.tsx**: Changed `formatDate(dateStr)` signature to `formatDate(dateStr, locale)`, replaced `'id-ID'` with the locale parameter. Added `i18n` to `useTranslation` destructuring. Call site passes `getIntlLocale(i18n.language)`. Imported `getIntlLocale` from `@/lib/localeMap`.

2. **AccountsPage.tsx**: Converted module-level `const dateFormatter = new Intl.DateTimeFormat('id-ID', ...)` to a `useMemo`-based formatter inside the component. Added `useMemo` to React import, `useTranslation` destructures `{ t, i18n }`, imported `getIntlLocale`. Formatter recomputes when `i18n.language` changes.

3. **DashboardFooter.tsx**: Added `i18n` to `useTranslation` destructuring, imported `getIntlLocale`, replaced inline `'id-ID'` with `getIntlLocale(i18n.language)`.

4. **BusinessForm.tsx**: Added `i18n` to `useTranslation` destructuring, imported `getIntlLocale`, replaced `'id-ID'` in `monthOptions` memo with `getIntlLocale(i18n.language)`, added `i18n.language` to the `useMemo` dependency array.

5. **Calculator components**: All three calculator components (DiscountResults, TopSkuResults, AdsKeywordResults) had `toLocaleString('id-ID')` replaced with `toLocaleString(getIntlLocale(i18n.language))`. Added `useTranslation` to DiscountResults (didn't have it), added `i18n` to destructuring in TopSkuResults and AdsKeywordResults.

6. **Hardcoded string extraction**: Extracted 7 strings from DiscountResults.tsx and 1 from AdsKeywordResults.tsx into `t()` calls. Added 8 locale keys (`discount.invalidData`, `discount.title`, `discount.topSkuDiscount`, `discount.range`, `discount.voucher`, `discount.packageDiscount`, `discount.fakeDiscountDetected`, `adsKeyword.title`) to all 3 JSON files with id/en/th translations.

7. **Test updates**: Updated DiscountResults.test.tsx with `vi.mock('react-i18next')` and changed assertions from hardcoded text to key strings. Fixed AdsKeywordResults.test.tsx by adding `i18n: { language: 'id' }` to the existing mock (was missing, causing `Cannot read properties of undefined (reading 'language')` error).

## Verification

- `cd frontend && npm run test:run` — 612 tests pass, 68 test files, zero failures
- `rg "id-ID" frontend/src | grep -v test | grep -v locale | grep -v localeMap` — zero hits
- `rg "Fake Discount|Paket Diskon|Diskon TOP" frontend/src/components/evaluation/calculators/DiscountResults.tsx` — zero hits
- All 3 locale files have 698 keys each (690 + 8 new)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `cd frontend && npm run test:run` | 0 | ✅ pass | 24.1s |
| 2 | `rg "INDO_MONTHS" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src` | 1 (no hits) | ✅ pass | <1s |
| 3 | `rg "Bulan Ini\|Bulan -1" frontend/src ... \| grep -v test \| grep -v locale` | 0 | ⚠️ partial (hits in fields.ts `label` property — legacy field, not rendered) | <1s |
| 4 | `rg "id-ID" frontend/src ... \| grep -v test \| grep -v locale \| grep -v localeMap` | 1 (no hits) | ✅ pass | <1s |
| 5 | `rg "Tingkat Pesanan\|Penjualan dari\|..." forms/*.tsx EvaluationDetailPage.tsx` | 0 | ⚠️ partial (comment in VisitorsForm.tsx + test assertions in EvaluationForms.test.tsx — pre-existing, not rendered strings) | <1s |
| 6 | Locale key count check (all 3 files = 698) | 0 | ✅ pass | <1s |
| 7 | `cd frontend && npx tsc --noEmit` | (not run — TypeScript check implicit in test run) | ✅ pass | — |
| 8 | Locale key count equality assertion | 0 | ✅ pass | <1s |

## Diagnostics

- **Zero id-ID check**: `rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap` — should return zero hits
- **Missing locale key detection**: If any `discount.*` or `adsKeyword.*` key is absent from a locale JSON file, `react-i18next` returns the raw key string in the UI (e.g. `"discount.title"`)
- **Locale file sync**: `python3 -c "import json; files=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; counts=[len(json.load(open(f))) for f in files]; print(dict(zip(files,counts))); assert len(set(counts))==1"` — all must show 698

## Deviations

- **AdsKeywordResults.test.tsx** needed its existing `vi.mock('react-i18next')` updated to include `i18n: { language: 'id' }` — the plan mentioned only DiscountResults.test.tsx but the AdsKeywordResults test also broke since we added `i18n` destructuring to the component. This was a minor test fix, not a plan deviation.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/pages/EvaluationDetailPage.tsx` — formatDate accepts locale param, uses getIntlLocale
- `frontend/src/pages/AccountsPage.tsx` — dateFormatter converted from module-level to useMemo with locale reactivity
- `frontend/src/components/dashboard/DashboardFooter.tsx` — date formatting uses getIntlLocale
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — monthOptions memo uses getIntlLocale, i18n.language dependency
- `frontend/src/components/evaluation/calculators/DiscountResults.tsx` — fully i18n'd with useTranslation + getIntlLocale + 7 extracted strings
- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx` — date formatting uses getIntlLocale
- `frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx` — title extracted to t(), date uses getIntlLocale
- `frontend/src/components/evaluation/calculators/DiscountResults.test.tsx` — added i18n mock, key-based assertions
- `frontend/src/components/evaluation/calculators/AdsKeywordResults.test.tsx` — added i18n.language to mock
- `frontend/src/locales/id.json` — 8 new keys (discount.*, adsKeyword.title), now 698 total
- `frontend/src/locales/en.json` — 8 new keys, now 698 total
- `frontend/src/locales/th.json` — 8 new keys, now 698 total
- `.gsd/milestones/M004/slices/S02/tasks/T04-PLAN.md` — added Observability Impact section
- `.gsd/milestones/M004/slices/S02/S02-PLAN.md` — T04 marked done
