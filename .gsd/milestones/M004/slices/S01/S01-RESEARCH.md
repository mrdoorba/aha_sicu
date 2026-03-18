# S01 — Extract hardcoded strings from un-i18n'd components — Research

**Date:** 2026-03-18
**Depth:** Light — well-understood work applying the established `useTranslation` + locale JSON pattern already used by 10+ components in this codebase.

## Summary

S01 owns R027 (extract hardcoded strings from 4 components) and supports R031 (zero hardcoded Indonesian in source) and R032 (all tests pass after extraction).

The 4 target components contain ~40 hardcoded Indonesian strings total. The work is entirely mechanical: add `useTranslation()` hook, replace each hardcoded string with `t('key')`, add keys to all 3 locale JSON files, and update test assertions. Several existing keys can be reused (`common.cancel`, `common.retry`, `common.previous`, `common.next`, `common.pageOf`).

There is one boundary deliverable for downstream slices: `lib/localeMap.ts` providing `getIntlLocale(i18nLang)` — a trivial 3-mapping utility (id→id-ID, en→en-US, th→th-TH). S02 consumes this for date formatting. S01 itself needs it for the `dateFormatter` in EvaluationHistoryTable which currently hardcodes `'id-ID'`.

No DowntimeWarningDialog test exists — one should be added to prove the component renders i18n keys.

## Recommendation

Work component-by-component. Start with SelectField (smallest, 1 string) and DowntimeWarningDialog (small, no test to update — needs a new one) to prove the pattern, then DeleteEvaluationDialog (8 strings, straightforward test updates), then EvaluationHistoryTable last (largest at ~25 strings, most test assertions to update, plus the `dateFormatter` locale change needing `localeMap.ts`).

Create `localeMap.ts` as part of the EvaluationHistoryTable task since that's where it's first consumed.

## Implementation Landscape

### Key Files

**Components to change:**
- `frontend/src/components/evaluation/forms/SelectField.tsx` — 1 hardcoded string: placeholder `"Pilih..."`. Add `useTranslation()`, replace with `t('common.select')`.
- `frontend/src/components/DowntimeWarningDialog.tsx` — 5 hardcoded strings: title, description (with embedded bold text), button label. Add `useTranslation()`, add `downtime.*` keys.
- `frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` — 8 hardcoded strings: title, description, confirmation prompt, placeholder, button labels, toast, aria-labels. Add `useTranslation()`, add `deleteDialog.*` keys. Reuse `common.cancel` for "Batal".
- `frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — ~25 hardcoded strings: column headers, pagination, search, date pickers, empty/error states, "show all" button, evaluation count text, aria-labels. The `dateFormatter` on line 21 hardcodes `'id-ID'` — needs `getIntlLocale()`. Reuse `common.previous`/`common.next`/`common.pageOf`/`common.retry`.

**New file to create:**
- `frontend/src/lib/localeMap.ts` — exports `getIntlLocale(lang: string): string` mapping `id→id-ID`, `en→en-US`, `th→th-TH` with `id-ID` fallback. ~10 lines. Consumed by S02 across 8 files.

**Locale files to update (all 3 in lockstep):**
- `frontend/src/locales/id.json` — add ~35 new keys
- `frontend/src/locales/en.json` — add ~35 new keys
- `frontend/src/locales/th.json` — add ~35 new keys

**Test files to update:**
- `frontend/src/components/evaluation/forms/SelectField.test.tsx` — add `vi.mock('react-i18next')`, update assertion for placeholder (line 25: `'Pilih...'` → `'common.select'`). The label `'Status Toko'` comes from the test's own prop, not from the component — no change needed.
- `frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx` — add `vi.mock('react-i18next')`, update ~12 assertions from Indonesian text to i18n keys.
- `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx` — add `vi.mock('react-i18next')`, update ~20 assertions. This is the largest test change.

**New test file to create:**
- `frontend/src/components/DowntimeWarningDialog.test.tsx` — basic render test verifying i18n keys render. Follow established mock pattern.

### Existing Keys to Reuse (do NOT duplicate)

| Hardcoded string | Existing key |
|---|---|
| "Batal" (Cancel) | `common.cancel` |
| "Coba Lagi" (Retry) | `common.retry` |
| "Sebelumnya" (Previous) | `common.previous` |
| "Berikutnya" (Next) | `common.next` |
| "Halaman X dari Y" | `common.pageOf` (already has `{{page}}`/`{{totalPages}}` vars) |

### New Key Inventory (approximate)

**`common.*` (shared):**
- `common.select` — "Pilih..." / "Select..." / "เลือก..."
- `common.delete` — "Hapus" / "Delete" / "ลบ"

**`history.table.*` (EvaluationHistoryTable):**
- `history.table.brand` — column header "Brand"
- `history.table.evaluations` — column header "Evaluasi" / "Evaluations"
- `history.table.topScore` — "Skor Tertinggi" / "Top Score"
- `history.table.latest` — "Terbaru" / "Latest"
- `history.table.evaluationCount` — "{{count}} evaluasi" / "{{count}} evaluations"
- `history.table.failedLoadEvaluations` — "Gagal memuat evaluasi"
- `history.table.showAll` — "Tampilkan semua ({{count}})"
- `history.table.failedLoadHistory` — "Gagal memuat riwayat evaluasi"
- `history.table.emptyState` — "Belum ada riwayat evaluasi"
- `history.table.emptyStateHint` — "Mulai evaluasi brand..."
- `history.table.noMatchFilter` — "Tidak ada evaluasi yang cocok dengan filter"
- `history.table.noMatchSearch` — "Tidak ada evaluasi ditemukan untuk '{{search}}'"
- `history.table.noMatchDate` — "Tidak ada evaluasi ditemukan untuk rentang tanggal tersebut"
- `history.table.brandCount` — "{{count}} brand"
- `history.table.aria.table` — "Riwayat evaluasi" / "Evaluation history"
- `history.table.aria.searchLabel` — "Cari evaluasi berdasarkan nama brand"
- `history.table.aria.searchPlaceholder` — "Cari nama brand..."
- `history.table.aria.clearSearch` — "Hapus pencarian"
- `history.table.aria.dateFrom` — "Dari tanggal" / "From date"
- `history.table.aria.dateTo` — "Sampai tanggal" / "To date"
- `history.table.aria.clearDateFrom` — "Hapus dari tanggal"
- `history.table.aria.clearDateTo` — "Hapus sampai tanggal"

**`deleteDialog.*` (DeleteEvaluationDialog):**
- `deleteDialog.title` — "Hapus Evaluasi" / "Delete Evaluation"
- `deleteDialog.description` — permanent warning text
- `deleteDialog.confirmPrompt` — "Ketik nama brand untuk konfirmasi:"
- `deleteDialog.placeholder` — "Ketik nama brand di sini..."
- `deleteDialog.aria.confirmInput` — "Konfirmasi nama brand"
- `deleteDialog.aria.copyBrand` — "Salin nama brand"
- `deleteDialog.toast.copyFailed` — "Gagal menyalin nama brand"

**`downtime.*` (DowntimeWarningDialog):**
- `downtime.title` — "Sistem Tidak Tersedia"
- `downtime.description` — system hours message (with interpolation for time range)
- `downtime.dismiss` — "Mengerti" / "Understood" / "เข้าใจแล้ว"

### Build Order

1. **Create `localeMap.ts`** — trivial, unblocks S02 and the dateFormatter change in EvaluationHistoryTable. Write unit test.
2. **SelectField** — smallest component (1 string). Proves the mock pattern works. Updates 1 test file.
3. **DowntimeWarningDialog** — small component (5 strings), no existing test. Write new test file.
4. **DeleteEvaluationDialog** — medium component (8 strings). Updates 1 test file with ~12 assertion changes.
5. **EvaluationHistoryTable** — largest component (~25 strings). Updates 1 test file with ~20 assertion changes. Integrates `localeMap.ts` for `dateFormatter`. This is the riskiest piece — the `dateFormatter` is a module-level `const` that must become a function (or use `useMemo` inside the component) to read the current i18n language.
6. **Locale files** — add all new keys to id.json, en.json, th.json. Can be done incrementally per-component or all at once.

### Verification Approach

```bash
cd frontend && npm run test:run -- --reporter=verbose 2>&1 | tail -20
```

- All existing tests pass (602+ baseline)
- New DowntimeWarningDialog test passes
- `rg "Pilih\.\.\." frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v locale` returns no hits (SelectField cleaned)
- `rg "Gagal memuat" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` returns no hits
- `rg "Hapus Evaluasi" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` returns no hits
- `rg "Sistem Tidak" frontend/src/components/DowntimeWarningDialog.tsx` returns no hits

## Constraints

- The `dateFormatter` in EvaluationHistoryTable is a **module-level const** (`new Intl.DateTimeFormat('id-ID', ...)`). It cannot simply swap in a dynamic locale at the top level. It must move inside the component (or into a helper called with the current locale). The `BrandAccordionRow` sub-component also calls `dateFormatter.format()` — both sites need the dynamic formatter.
- The `deleteDialog.description` text in Indonesian contains two sentences. The translation must carry both — use a single key with the full text, not split keys.
- `SelectField` receives `label` as a prop from the parent form component. The `label` prop value is **not** this slice's concern (that's S02's `fields.ts` labelKey work). Only the `"Pilih..."` placeholder inside SelectField is S01 scope.
- Locale files use **flat dot-notation keys** (not nested objects) — except `emailBody` which uses nesting. New keys must follow the flat pattern.

## Common Pitfalls

- **Module-level dateFormatter** — The `new Intl.DateTimeFormat('id-ID', ...)` at module scope runs once at import time. If you just swap `'id-ID'` for `getIntlLocale(i18n.language)`, it captures the language at import, not at render. Must create the formatter inside the component or use a factory function called per-render/per-memo.
- **Test mock must be hoisted** — `vi.mock('react-i18next')` must be at the top level of the test file, not inside `describe`. The `t: (key) => key` pattern means assertions change from checking visible text (`'Hapus Evaluasi'`) to checking the key (`'deleteDialog.title'`). Some tests also check `aria-label` attributes which will similarly become i18n keys.
- **`common.pageOf` variable names** — The existing key uses `{{page}}` and `{{totalPages}}`. The component currently uses template literals `` `Halaman ${page} dari ${pages}` ``. The variable `pages` must be passed as `totalPages` to match the existing key signature: `t('common.pageOf', { page, totalPages: pages })`.
