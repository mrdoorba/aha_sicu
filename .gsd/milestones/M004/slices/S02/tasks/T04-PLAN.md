---
estimated_steps: 7
estimated_files: 11
---

# T04: Replace 7 id-ID date formatting sites and extract calculator hardcoded strings

**Slice:** S02 — Locale-aware dates, field labels, and month constants
**Milestone:** M004

## Description

Replace all 7 remaining `id-ID` hardcoded date formatting sites with locale-aware formatting using `getIntlLocale()` from `@/lib/localeMap` (created in S01). Extract hardcoded strings from DiscountResults.tsx (7 strings) and AdsKeywordResults.tsx (1 string) into locale keys. After this task, zero `id-ID` hardcodes remain in non-test/non-locale source files.

**Relevant skills:** `test` (for vitest assertion updates)

## Steps

1. **EvaluationDetailPage.tsx — `formatDate()` function (~line 77-82):**
   - Currently: standalone function `function formatDate(dateStr: string): string` that uses `d.toLocaleDateString('id-ID', ...)`.
   - The component already has `useTranslation()`. Move the date formatting inline or make `formatDate` accept a locale parameter.
   - Recommended approach: change signature to `function formatDate(dateStr: string, locale: string): string` and replace `'id-ID'` with `locale`. At the call site (~line 599), pass `getIntlLocale(i18n.language)`.
   - Import `getIntlLocale` from `@/lib/localeMap`.

2. **AccountsPage.tsx — module-level `dateFormatter` (~line 38):**
   - Currently: `const dateFormatter = new Intl.DateTimeFormat('id-ID', ...)` at module level.
   - Cannot use hooks at module level. Convert to a `useMemo`-based formatter inside the component (same pattern S01 used for EvaluationHistoryTable):
     ```typescript
     const { t, i18n } = useTranslation();
     const dateFormatter = useMemo(
       () => new Intl.DateTimeFormat(getIntlLocale(i18n.language), { /* same options */ }),
       [i18n.language]
     );
     ```
   - Add `useTranslation` import from `react-i18next` if not present.
   - Add `useMemo` import from `react` if not present.
   - Import `getIntlLocale` from `@/lib/localeMap`.

3. **DashboardFooter.tsx (~line 21):**
   - Currently: `new Date(createdAt).toLocaleDateString('id-ID', ...)` inline in JSX.
   - Add `useTranslation` hook, import `getIntlLocale`, replace `'id-ID'` with `getIntlLocale(i18n.language)`.

4. **BusinessForm.tsx — monthOptions memo (~line 38):**
   - Currently: `d.toLocaleDateString('id-ID', { month: 'short', year: 'numeric' })`.
   - BusinessForm already has `useTranslation` and destructures `{ t }`. Add `i18n` to destructuring: `{ t, i18n }`.
   - Import `getIntlLocale` from `@/lib/localeMap`.
   - Replace `'id-ID'` with `getIntlLocale(i18n.language)`.
   - Add `i18n.language` to the `useMemo` dependency array: `useMemo(() => { ... }, [i18n.language])` (currently `[]`).

5. **Calculator components — `toLocaleString('id-ID')`:**
   - **DiscountResults.tsx (~line 21):** `new Date(result.calculated_at).toLocaleString('id-ID')` → `new Date(result.calculated_at).toLocaleString(getIntlLocale(i18n.language))`. This component does NOT have `useTranslation` yet — add it.
   - **TopSkuResults.tsx (~line 87):** Same pattern. Check if it already has `useTranslation` — if yes, just add `getIntlLocale`. If not, add the hook.
   - **AdsKeywordResults.tsx (~line 51):** Same pattern. Research says it already has `useTranslation`.

6. **Extract hardcoded strings from DiscountResults.tsx:**
   - Add `useTranslation` hook (being added in step 5 for date formatting).
   - Replace 7 hardcoded strings:
     - `"Invalid discount data"` → `t('discount.invalidData')`
     - `"Discount Check Calculator"` → `t('discount.title')`
     - `"% Diskon TOP SKU"` → `t('discount.topSkuDiscount')`
     - `"Range"` → `t('discount.range')`
     - `"Voucher"` → `t('discount.voucher')`
     - `"Paket Diskon"` → `t('discount.packageDiscount')`
     - `"Fake Discount Detected"` → `t('discount.fakeDiscountDetected')`
   - Extract 1 string from AdsKeywordResults.tsx:
     - `"Ads Keyword Calculator"` → `t('adsKeyword.title')`
   - Add locale keys to all 3 JSON files:
     - `discount.invalidData`: id="Data diskon tidak valid", en="Invalid discount data", th="ข้อมูลส่วนลดไม่ถูกต้อง"
     - `discount.title`: id="Kalkulator Pengecekan Diskon", en="Discount Check Calculator", th="เครื่องคำนวณตรวจสอบส่วนลด"
     - `discount.topSkuDiscount`: id="% Diskon TOP SKU", en="% Top SKU Discount", th="% ส่วนลด SKU ยอดนิยม"
     - `discount.range`: id="Rentang", en="Range", th="ช่วง"
     - `discount.voucher`: id="Voucher", en="Voucher", th="คูปอง"
     - `discount.packageDiscount`: id="Paket Diskon", en="Package Discount", th="แพ็คเกจส่วนลด"
     - `discount.fakeDiscountDetected`: id="Diskon Palsu Terdeteksi", en="Fake Discount Detected", th="ตรวจพบส่วนลดปลอม"
     - `adsKeyword.title`: id="Kalkulator Kata Kunci Iklan", en="Ads Keyword Calculator", th="เครื่องคำนวณคำค้นหาโฆษณา"

7. **Update tests and verify:**
   - **DiscountResults.test.tsx:** Add `vi.mock('react-i18next')` (same pattern from S01). Change assertions from hardcoded text to key strings (e.g. `"% Diskon TOP SKU"` → `"discount.topSkuDiscount"`).
   - Check if any other test files assert on date formatting with `id-ID` — if so, update those too.
   - Run full test suite: `cd frontend && npm run test:run` — all 612+ tests pass
   - Verify: `rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap` — zero hits

## Must-Haves

- [ ] All 7 `id-ID` date formatting sites replaced with `getIntlLocale(i18n.language)`
- [ ] AccountsPage `dateFormatter` converted from module-level to hook-based `useMemo`
- [ ] DiscountResults 7 hardcoded strings extracted to `t()` with locale keys
- [ ] AdsKeywordResults 1 hardcoded string extracted to `t()` with locale key
- [ ] 8 `discount.*` + `adsKeyword.*` locale keys in all 3 JSON files
- [ ] All tests pass (612+)
- [ ] Zero `id-ID` in non-test/non-locale/non-localeMap source

## Verification

- `cd frontend && npm run test:run` — all 612+ tests pass
- `rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap` — zero hits
- `rg "Fake Discount\|Paket Diskon\|Diskon TOP" frontend/src/components/evaluation/calculators/DiscountResults.tsx` — zero hits

## Inputs

- T01–T03 completed: MONTHS renamed, labels keyed, form components wired
- `frontend/src/lib/localeMap.ts` — `getIntlLocale()` utility from S01
- S01's `useMemo` pattern for `dateFormatter` (see `EvaluationHistoryTable.tsx` for reference)
- `vi.mock('react-i18next')` pattern from S01 test files

## Expected Output

- 7 source files updated to use `getIntlLocale()` instead of `'id-ID'`
- `DiscountResults.tsx` — fully i18n'd with `useTranslation` + `getIntlLocale`
- `AdsKeywordResults.tsx` — title string extracted
- `TopSkuResults.tsx` — date formatting locale-aware
- `DiscountResults.test.tsx` — updated with i18n mock and key-based assertions
- `frontend/src/locales/{id,en,th}.json` — 8 new keys under `discount.*` and `adsKeyword.*`
- Zero `id-ID` hardcodes in non-test/non-locale source

## Observability Impact

- **Signal changed:** All date/time formatting across 7 components now responds to the active i18n locale instead of being fixed to `id-ID`. Switching language in the UI changes date display format immediately.
- **Inspection:** `rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap` — zero hits confirms no hardcoded locale remains.
- **Failure state:** If a `discount.*` or `adsKeyword.*` locale key is missing from a JSON file, `react-i18next` returns the raw key string (e.g. `"discount.title"`) in the UI. This is the primary visual failure signal for missing translations.
- **Diagnostic command:** `python3 -c "import json; files=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; counts=[len(json.load(open(f))) for f in files]; print(dict(zip(files,counts))); assert len(set(counts))==1, f'Key count mismatch: {counts}'"` — verifies all 3 locale files have equal key counts.
