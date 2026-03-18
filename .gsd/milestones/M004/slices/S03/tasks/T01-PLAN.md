---
estimated_steps: 10
estimated_files: 12
---

# T01: Extract residual hardcoded Indonesian from source and fix metric comparisons

**Slice:** S03 — Verification sweep and test hardening
**Milestone:** M004

## Description

S01 and S02 extracted ~170 hardcoded Indonesian strings to locale keys, but a systematic sweep found ~15 residual rendered Indonesian strings across 5 source files, plus Indonesian-string-based metric comparisons in DetailedEvaluation.tsx. This task extracts every remaining rendered Indonesian string and fixes the metric comparison logic. After this task, the only Indonesian text in non-test/non-locale source will be the inert `label` property in `fields.ts` (dead code, not rendered), code comments, and backend column name matchers — all of which are explicitly out of scope per the milestone constraints.

**Relevant skill:** Load the `test` skill if you need guidance on test pattern conventions.

## Steps

1. **Add `benchmarkKey` and `unitKey` to FieldDefinition type** in `frontend/src/components/evaluation/forms/types.ts`:
   - Add `benchmarkKey?: string;` after the existing `benchmark?: string;` property
   - Add `unitKey?: string;` after the existing `unit?: string;` property

2. **Add benchmarkKey to 10 PROMO_TOOLS_FIELDS entries** in `frontend/src/components/evaluation/forms/fields.ts`:
   - Each promo tool field with `benchmark: '>X% dari penjualan'` gets a `benchmarkKey` property with the pattern `'fields.promoTools.<fieldKey>.benchmark'`
   - Example: `{ key: 'promoToko', ..., benchmark: '>8% dari penjualan', benchmarkKey: 'fields.promoTools.promoToko.benchmark', ... }`
   - All 10 fields: promoToko, paketDiskon, komboHemat, flashSale, voucher, shopeeLive, gameToko, brandMembership, chatBroadcast, programAfiliasi

3. **Add unitKey to preparationTime field** in `fields.ts`:
   - The field at line ~61 has `unit: 'hari'`. Add `unitKey: 'common.days'`
   - Keep the original `unit: 'hari'` property (backward compatibility)

4. **Update PromoToolsForm to resolve benchmarkKey via t()** in `frontend/src/components/evaluation/forms/PromoToolsForm.tsx`:
   - The component already has `useTranslation` (from S02)
   - Line ~60: change `benchmark={field.benchmark}` to `benchmark={field.benchmarkKey ? t(field.benchmarkKey) : field.benchmark}`

5. **Update OperationalForm to resolve unitKey via t()** in `frontend/src/components/evaluation/forms/OperationalForm.tsx`:
   - The component already has `useTranslation` (from S02)
   - Find where `unit={field.unit}` is passed (line ~43) and change to `unit={field.unitKey ? t(field.unitKey) : field.unit}`

6. **Replace FIELD_LABELS in EvaluationHeader.tsx** with i18n resolution:
   - `frontend/src/components/evaluation/EvaluationHeader.tsx` already has `useTranslation` and `const { t } = useTranslation()`
   - Replace the `FIELD_LABELS` constant (lines 23-27) with a function or inline `t()` calls:
     ```typescript
     // Replace the static FIELD_LABELS map with a function that uses t()
     const getFieldLabel = (key: string): string => {
       const labelMap: Record<string, string> = {
         'Nama PIC/ Jabatan*': t('evaluationHeader.fieldLabel.namaPic'),
         'No WA*': t('evaluationHeader.fieldLabel.noWa'),
         'Link Shopee Mall / LazMall': t('evaluationHeader.fieldLabel.linkToko'),
       };
       return labelMap[key] ?? key;
     };
     ```
   - IMPORTANT: This function must be inside the component (after the `const { t } = useTranslation()` call), not at module level. Move `FIELD_LABELS` usage from `{FIELD_LABELS[key] ?? key}` to `{getFieldLabel(key)}`
   - VP_DISPLAY_FIELDS keys must NOT change — they match backend VP sheet column names

7. **Extract App.tsx accessDeniedMessage** in `frontend/src/App.tsx`:
   - Line 88: `accessDeniedMessage="Akses ditolak — halaman akun hanya untuk admin"`
   - The component that renders `RoleProtectedRoute` needs to pass a translated string. Check if App.tsx already has `useTranslation`. If not, you'll need to find where this prop is consumed. The simplest approach: if App.tsx has a React component function with hooks, add `useTranslation` and use `t('auth.accessDeniedAccounts')`. If not (e.g., it's just JSX in a router config), create a small wrapper component or use the `i18next` instance directly via `import i18next from 'i18next'; i18next.t('auth.accessDeniedAccounts')`.

8. **Extract LoginPage alt text** in `frontend/src/pages/LoginPage.tsx`:
   - Line 192: `alt="Garansi Omzet dan Profit Naik"`
   - LoginPage already has `useTranslation` — change to `alt={t('login.bannerAlt')}`

9. **Fix DetailedEvaluation.tsx metric comparisons** in `frontend/src/components/dashboard/DetailedEvaluation.tsx`:
   - Line 77: `row.metric === 'Biaya (iklan)'` → `(row.metric_i18n?.key === 'scoring.adCost' || row.metric === 'Biaya (iklan)')`
   - Line 86: `row.metric.startsWith('Rata² Penjualan')` → `(row.metric_i18n?.key?.startsWith('scoring.avgSales') || row.metric.startsWith('Rata² Penjualan'))`
   - Line 86: `row.metric === 'Program Afiliasi'` → `(row.metric_i18n?.key === 'scoring.promo.programAfiliasi' || row.metric === 'Program Afiliasi')`
   - Line 86: `row.metric === 'ROI'` — this is English, leave as-is
   - CRITICAL: Keep the `row.metric` fallback for old evaluations without `metric_i18n` (pre-M002 data). Use `||` not replacement.
   - Verify the actual `metric_i18n.key` values by checking the backend scoring code or locale files. The keys used above are examples — check `frontend/src/locales/id.json` for the actual `scoring.*` keys to confirm the right key names.

10. **Add locale keys to all 3 JSON files** (`frontend/src/locales/id.json`, `en.json`, `th.json`):
    - `auth.accessDeniedAccounts`: id="Akses ditolak — halaman akun hanya untuk admin", en="Access denied — accounts page is admin only", th="การเข้าถึงถูกปฏิเสธ — หน้าบัญชีสำหรับผู้ดูแลระบบเท่านั้น"
    - `login.bannerAlt`: id="Garansi Omzet dan Profit Naik", en="Revenue and Profit Growth Guarantee", th="การรับประกันรายได้และกำไรเพิ่มขึ้น"
    - `evaluationHeader.fieldLabel.namaPic`: id="Nama PIC", en="PIC Name", th="ชื่อ PIC"
    - `evaluationHeader.fieldLabel.noWa`: id="No WA", en="WA Number", th="เบอร์ WA"
    - `evaluationHeader.fieldLabel.linkToko`: id="Link Toko", en="Store Link", th="ลิงก์ร้านค้า"
    - `common.days`: id="hari", en="days", th="วัน"
    - 10× benchmark keys with pattern `fields.promoTools.<key>.benchmark`:
      - `fields.promoTools.promoToko.benchmark`: id=">8% dari penjualan", en=">8% of sales", th=">8% ของยอดขาย"
      - `fields.promoTools.paketDiskon.benchmark`: id=">16% dari penjualan", en=">16% of sales", th=">16% ของยอดขาย"
      - `fields.promoTools.komboHemat.benchmark`: id=">1% dari penjualan", en=">1% of sales", th=">1% ของยอดขาย"
      - `fields.promoTools.flashSale.benchmark`: id=">1% dari penjualan", en=">1% of sales", th=">1% ของยอดขาย"
      - `fields.promoTools.voucher.benchmark`: id=">84% dari penjualan", en=">84% of sales", th=">84% ของยอดขาย"
      - `fields.promoTools.shopeeLive.benchmark`: id=">15% dari penjualan", en=">15% of sales", th=">15% ของยอดขาย"
      - `fields.promoTools.gameToko.benchmark`: id=">1% dari penjualan", en=">1% of sales", th=">1% ของยอดขาย"
      - `fields.promoTools.brandMembership.benchmark`: id=">1% dari penjualan", en=">1% of sales", th=">1% ของยอดขาย"
      - `fields.promoTools.chatBroadcast.benchmark`: id=">1% dari penjualan", en=">1% of sales", th=">1% ของยอดขาย"
      - `fields.promoTools.programAfiliasi.benchmark`: id=">18% dari penjualan", en=">18% of sales", th=">18% ของยอดขาย"
    - Total: 16 new keys (auth.accessDeniedAccounts, login.bannerAlt, 3 evaluationHeader.fieldLabel.*, common.days, 10 fields.promoTools.*.benchmark)
    - Add keys in alphabetical order within their namespace sections

11. **Update PromoToolsForm.test.tsx** in `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx`:
    - The test already has `vi.mock('react-i18next')` (from S02) where mock `t` returns the key string
    - Line ~51-55: 5 benchmark assertions like `expect(screen.getByText('Benchmark: >8% dari penjualan'))` need to change to `expect(screen.getByText('Benchmark: fields.promoTools.promoToko.benchmark'))` (because mock `t` returns the key, and CurrencyField renders `"Benchmark: {benchmark}"`)
    - Check if there are any other test files that assert `dari penjualan` text: `rg "dari penjualan" frontend/src --glob '*.test.*'`

12. **Check for any other test files needing updates:**
    - Run `rg "hari" frontend/src --glob '*.test.*' | grep -v node_modules` to see if any tests assert the `hari` unit text
    - Run `rg "Akses ditolak\|Garansi Omzet\|Nama PIC\|No WA\|Link Toko" frontend/src --glob '*.test.*'` to check for affected test assertions
    - Update any broken assertions to use key strings

## Must-Haves

- [ ] `benchmarkKey` and `unitKey` added to FieldDefinition type
- [ ] 10 PROMO_TOOLS_FIELDS entries have `benchmarkKey` populated
- [ ] preparationTime field has `unitKey: 'common.days'`
- [ ] PromoToolsForm resolves `benchmarkKey` via `t()` when present
- [ ] OperationalForm resolves `unitKey` via `t()` when present
- [ ] EvaluationHeader FIELD_LABELS display values resolved via `t()`
- [ ] App.tsx accessDeniedMessage extracted to `t('auth.accessDeniedAccounts')`
- [ ] LoginPage banner alt extracted to `t('login.bannerAlt')`
- [ ] DetailedEvaluation metric comparisons use `metric_i18n.key` with `row.metric` fallback
- [ ] 16 new locale keys added to all 3 JSON files (id, en, th)
- [ ] PromoToolsForm.test.tsx benchmark assertions updated to expect key strings
- [ ] `npx tsc --noEmit` passes
- [ ] `npm run test:run` passes 612+
- [ ] All 3 locale files have equal key count (698 + 16 = 714)

## Verification

- `cd frontend && npx tsc --noEmit` — zero type errors
- `cd frontend && npm run test:run` — 612+ tests pass
- `python3 -c "import json; fs=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; cs=[len(json.load(open(f))) for f in fs]; print(cs); assert len(set(cs))==1"` — all 3 files have equal key count
- `rg "dari penjualan" frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — zero hits
- `rg "Akses ditolak" frontend/src/App.tsx` — zero hits
- `rg "Garansi Omzet" frontend/src/pages/LoginPage.tsx` — zero hits
- `grep "Nama PIC'" frontend/src/components/evaluation/EvaluationHeader.tsx` — zero hits (only the VP_DISPLAY_FIELDS backend matcher key remains, not the display label)

## Observability Impact

- **New locale keys:** 16 new keys added to all 3 locale JSON files. Verification: locale sync check confirms equal key counts. Any key mismatch causes `i18next` to show the raw key string in the UI, which is visually detectable.
- **`metric_i18n.key` comparisons:** DetailedEvaluation now checks `row.metric_i18n?.key` before falling back to `row.metric`. This makes the component resilient to both translated and untranslated API responses. Inspectable via browser DevTools → Network → evaluation API response to see whether `metric_i18n` is populated.
- **`benchmarkKey` / `unitKey` resolution:** PromoToolsForm and OperationalForm resolve these via `t()` when present, falling back to the original hardcoded value. This is testable by switching the browser language to English/Thai and confirming benchmark text changes.
- **No new runtime errors expected:** All changes are additive (`||` fallbacks, optional chaining), so pre-M002 data without `metric_i18n` continues to work.

## Inputs

- `frontend/src/components/evaluation/forms/types.ts` — FieldDefinition type with existing `benchmark?: string` and `unit?: string` properties (from S02)
- `frontend/src/components/evaluation/forms/fields.ts` — 47 field definitions with `labelKey` already populated (from S02); 10 PROMO_TOOLS_FIELDS with `benchmark: '>X% dari penjualan'`
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — already uses `t(field.labelKey!)` for labels (from S02); needs same pattern for benchmarks
- `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx` — already has `vi.mock('react-i18next')` with mock `t` returning key strings (from S02)
- `frontend/src/locales/id.json`, `en.json`, `th.json` — currently at 698 keys each, in sync
- S01 Forward Intelligence: mock `t` function returns the key as-is; tests assert against key strings, not translated text
- S02 Forward Intelligence: `EvaluationForms.test.tsx` still asserts hardcoded Indonesian field labels — it uses real i18n (not mocked), so id.json values match and it passes without changes. Do NOT modify it.

## Expected Output

- `frontend/src/components/evaluation/forms/types.ts` — FieldDefinition has `benchmarkKey?: string` and `unitKey?: string`
- `frontend/src/components/evaluation/forms/fields.ts` — 10 PROMO_TOOLS_FIELDS entries have `benchmarkKey`, preparationTime has `unitKey`
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — benchmark prop resolved via `t()` when `benchmarkKey` present
- `frontend/src/components/evaluation/forms/OperationalForm.tsx` — unit prop resolved via `t()` when `unitKey` present
- `frontend/src/components/evaluation/EvaluationHeader.tsx` — FIELD_LABELS display values resolved via `t()` inside component
- `frontend/src/App.tsx` — accessDeniedMessage uses `t('auth.accessDeniedAccounts')`
- `frontend/src/pages/LoginPage.tsx` — alt text uses `t('login.bannerAlt')`
- `frontend/src/components/dashboard/DetailedEvaluation.tsx` — metric comparisons use `metric_i18n.key` with `row.metric` fallback
- `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx` — benchmark assertions expect key strings
- `frontend/src/locales/*.json` — 714 keys each (698 + 16), all 3 in sync
