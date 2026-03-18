# S03: Verification sweep and test hardening — Research

**Date:** 2026-03-18
**Depth:** Light-to-Targeted

## Summary

S03 is a verification and cleanup slice. After S01 and S02, the bulk of i18n extraction is complete — 698 locale keys across 3 synced JSON files, 612 tests passing, zero `id-ID` hardcodes in non-test/non-locale source. However, a systematic sweep reveals **several residual hardcoded Indonesian strings** that S01/S02 missed, plus test files still asserting hardcoded Indonesian text that happens to pass today but would break under a different default locale.

The residual rendered Indonesian falls into 3 categories: (1) two small source files with 1-3 hardcoded strings each (App.tsx, LoginPage.tsx, EvaluationHeader.tsx), (2) `fields.ts` benchmark strings containing `"dari penjualan"` (10 instances) rendered by PromoToolsForm, and (3) one `unit: 'hari'` rendered by NumberField. There are also ~3 files where Indonesian strings exist only for backend data matching (not rendered) and ~47 inert `label` properties that are no longer rendered. The approach should be: extract the rendered strings to locale keys, convert the backend-data comparisons to use `metric_i18n.key` instead of Indonesian string matching, and leave the inert `label` properties as-is (dead code cleanup is out of scope).

For tests, `EvaluationForms.test.tsx` was specifically flagged by S02 but actually passes today because it uses real i18n (not mocked) and `id.json` values match the original hardcoded text. One pre-existing test in `RulesPage.test.tsx` has a 5s timeout flake unrelated to i18n.

## Recommendation

Execute in two tasks:

**T01: Extract residual hardcoded Indonesian from source + clean up backend metric comparisons.** This covers all Category 1 (rendered) and Category 2 (backend-data logic) items. Small, mechanical changes across 5 files with ~15 new locale keys. This is the "sweep" part.

**T02: Verification gate — run final `rg` sweep + full test suite + locale sync check.** This is the "hardening" part. Run the full set of milestone DoD checks, confirm zero Indonesian in non-test/non-locale source (excluding inert `label` property and code comments), confirm all 612+ tests pass, confirm locale files stay in sync. Document any remaining known exceptions with justification.

## Implementation Landscape

### Key Files

**Files needing string extraction (T01):**

- `frontend/src/App.tsx:88` — `accessDeniedMessage="Akses ditolak — halaman akun hanya untuk admin"` → extract to `t('auth.accessDeniedAccounts')` locale key. App.tsx already has `useTranslation` indirectly available (the component rendering this is `RoleProtectedRoute` which accepts the string as a prop). Need to extract the prop value at the call site using `t()`.
- `frontend/src/pages/LoginPage.tsx:192` — `alt="Garansi Omzet dan Profit Naik"` → extract to `t('login.bannerAlt')` locale key. LoginPage already has `useTranslation`.
- `frontend/src/components/evaluation/EvaluationHeader.tsx:24-27` — `FIELD_LABELS` map has `'Nama PIC'`, `'No WA'`, `'Link Toko'` as rendered display values. These are displayed as field header labels. The keys (`'Nama PIC/ Jabatan*'` etc.) must stay as-is (they match backend VP sheet column names). Move display values to locale keys, resolve with `t()` at render time. EvaluationHeader already has `useTranslation`.
- `frontend/src/components/evaluation/forms/fields.ts` — 10 `benchmark` strings containing `"dari penjualan"` in PROMO_TOOLS_FIELDS. Add `benchmarkKey` to FieldDefinition (similar to `labelKey` pattern). Pattern: `benchmarkKey: 'fields.promoTools.promoToko.benchmark'` → resolved via `t()` in PromoToolsForm. Also: `unit: 'hari'` (1 instance on `preparationTime`) — could add `unitKey` or just use a simple locale key inline.
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — change `benchmark={field.benchmark}` to `benchmark={field.benchmarkKey ? t(field.benchmarkKey) : field.benchmark}` (or equivalent).

**Files needing backend-data logic cleanup (T01):**

- `frontend/src/components/dashboard/DetailedEvaluation.tsx:77,86` — comparisons `row.metric === 'Biaya (iklan)'` and `row.metric.startsWith('Rata² Penjualan')` and `row.metric === 'Program Afiliasi'` use Indonesian backend metric strings for layout decisions (adding separators between card groups). Replace with `row.metric_i18n?.key` comparisons: `row.metric_i18n?.key === 'scoring.adCost'`, `row.metric_i18n?.key?.startsWith('scoring.monthlySales')` or `row.metric_i18n?.key === 'scoring.avgSales6mo'`, `row.metric_i18n?.key === 'scoring.promo.programAfiliasi'`. Must keep `row.metric` as fallback for old evaluations without `metric_i18n`.

**Files that are fine as-is (no changes needed):**

- `frontend/src/components/evaluation/forms/fields.ts` — the 47 `label:` properties are dead code (all form components use `labelKey` now). Removing them is cleanup, not i18n extraction. Out of scope.
- `frontend/src/components/evaluation/forms/CompetitionForm.tsx:92` — `{/* Kata kunci pencarian */}` is a code comment, not rendered UI text. Leave as-is.
- `frontend/src/components/evaluation/forms/benchmarkUtils.ts:66` — JSDoc mentioning `'hari'`. Leave as-is.
- `frontend/src/pages/EvaluationDetailPage.tsx:116` — `key.includes('omzet')` matches database column names, not UI text. Leave as-is.
- `frontend/src/components/evaluation/EvaluationHeader.tsx:16-21` — `VP_DISPLAY_FIELDS` array values like `'Nama PIC/ Jabatan*'` are backend column name matchers. Leave as-is.

**Test files (T02 scope — verify, not modify):**

- `frontend/src/components/evaluation/forms/EvaluationForms.test.tsx` — uses real i18n (not mocked). Asserts against rendered text which resolves through `id.json` locale values. Currently passes (9/9). S02 flagged this but it needs **zero changes** because the locale values match original text.
- ~40 other test files assert Indonesian text using real i18n — they all pass because `id.json` values match. No changes needed unless the default locale is changed.
- `frontend/src/components/rules/RulesPage.test.tsx:517` — pre-existing 5s timeout flake on "successful password confirmation triggers mutation". Unrelated to i18n. Consider extending timeout or skipping in the verification report.

### Build Order

1. **T01: Extract + clean** — all source file changes in one task. ~5 files modified, ~15 new locale keys. Depends on nothing. Approach:
   - Add locale keys for: `auth.accessDeniedAccounts`, `login.bannerAlt`, `evaluationHeader.fieldLabel.namaPic`, `evaluationHeader.fieldLabel.noWa`, `evaluationHeader.fieldLabel.linkToko`, 10× `fields.promoTools.*.benchmark` (pattern: `">X% of sales"`), 1× `fields.operational.preparationTime.unit` (or inline `t('common.days')`)
   - Add `benchmarkKey?: string` to `FieldDefinition` in `types.ts`
   - Update PromoToolsForm to resolve `benchmarkKey` via `t()`
   - Fix DetailedEvaluation.tsx metric comparisons to use `metric_i18n.key`
   - Update any test assertions broken by these changes (likely minimal — PromoToolsForm.test.tsx may need assertion updates)

2. **T02: Verification gate** — run all DoD checks, document results, update requirement statuses. Depends on T01.
   - `rg` sweep for common Indonesian words in non-test, non-locale `.tsx`/`.ts` — must return zero rendered hits
   - `rg "id-ID"` in non-test, non-locale source — already zero (confirmed)
   - `npm run test:run` — must be 612+ pass
   - Locale key sync check — all 3 files must have same count
   - `npx tsc --noEmit` — zero type errors
   - Document known exceptions: inert `label` property, code comments, backend column name matchers

### Verification Approach

**After T01:**
```bash
# 1. Type check
cd frontend && npx tsc --noEmit

# 2. Full test suite
npm run test:run

# 3. Locale sync
python3 -c "import json; fs=['src/locales/id.json','src/locales/en.json','src/locales/th.json']; cs=[len(json.load(open(f))) for f in fs]; print(cs); assert len(set(cs))==1"
```

**After T02 (full DoD check):**
```bash
# 4. Indonesian text sweep — rendered strings only
rg -n --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src -w -i \
  "Penjualan|Bulan|Evaluasi|Hapus|Gagal|Berhasil|Terjadi|Tidak|Pilih|Cari|Batal|Simpan|Kirim|Tambah|Ubah|Lihat|Kembali|Memuat|Riwayat|Konfirmasi|Tutup|Peringatan|Halaman|Berikutnya|Sebelumnya|Akses|ditolak|Rata|Afiliasi|Ongkir|Diskon|Iklan|Pesanan|Pengunjung|Tingkat|Sinkronisasi|Sistem|Garansi|Omzet|Pengemasan|Pengiriman|Dibalas|Penilaian|Konversi|Pengikut|Produk|Toko|Sesi|Dinominasikan|Tersedia" \
  frontend/src --glob '!*.test.*' --glob '!*locales*' --glob '!*locale*' --glob '!*localeMap*' \
  | grep -v "// " | grep -v "label:" | grep -v "displayName:" | grep -v "labelKey" | grep -v "displayNameKey"

# 5. id-ID sweep
rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src \
  | grep -v test | grep -v locale | grep -v localeMap

# Expected: only backend column name matchers (VP_DISPLAY_FIELDS keys) and inert label property
```

## Constraints

- The `fields.ts` `label` property (47 instances) must NOT be removed in this slice — it would be a breaking type change requiring a `FieldDefinition` type update and all consumers. It's dead code (not rendered) and is harmless. Cleanup belongs in a future housekeeping task.
- DetailedEvaluation.tsx metric comparisons must keep `row.metric` fallback for old evaluations that don't have `metric_i18n` (pre-M002 data).
- VP_DISPLAY_FIELDS keys in EvaluationHeader.tsx must match backend VP sheet column names exactly — they are NOT translatable.

## Common Pitfalls

- **PromoToolsForm.test.tsx already mocks i18n** — adding `benchmarkKey` resolution via `t()` means the mock `t` will return the key string (e.g., `"fields.promoTools.promoToko.benchmark"`). Test assertions must expect the key string, not the resolved translation.
- **DetailedEvaluation.tsx `metric_i18n` may be null** — old evaluations (pre-M002) don't have `metric_i18n`. The separator logic must use optional chaining: `row.metric_i18n?.key === 'scoring.adCost' || row.metric === 'Biaya (iklan)'`.
- **NumberField/CurrencyField `"Benchmark: "` prefix is hardcoded English** — extracting this to i18n is a nice-to-have but not required by R031 (which targets Indonesian text). Note it but don't block on it.
- **`rg` sweep false positives** — words like `Status`, `Regular`, `Email`, `Kategori` appear in code but are either English, proper nouns, or backend column names. The sweep must exclude these contextually. Focus on the grep patterns that match actual Indonesian UI text.
