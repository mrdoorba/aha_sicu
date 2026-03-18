# S01: Extract hardcoded strings from un-i18n'd components — UAT

**Milestone:** M004
**Written:** 2026-03-18

## UAT Type

- UAT mode: artifact-driven
- Why this mode is sufficient: All changes are source-level i18n string extraction verified by automated tests and grep checks. No runtime server or database required — i18next mock returns keys, confirming wiring. Visual language-switch verification is deferred to S03 end-to-end UAT.

## Preconditions

- Working directory: `frontend/` within the M004 worktree
- Node modules installed (`npm install` completed)
- All 612 tests passing (`npm run test:run` exits 0)

## Smoke Test

Run `cd frontend && npm run test:run -- SelectField DowntimeWarningDialog DeleteEvaluationDialog EvaluationHistoryTable localeMap --reporter=verbose` — all component-specific tests pass (14 + 5 + 9 + 17 + 4 = 49 tests).

## Test Cases

### 1. localeMap.ts returns correct Intl locale codes

1. Open `frontend/src/lib/localeMap.ts`
2. Verify `getIntlLocale('id')` → `'id-ID'`, `getIntlLocale('en')` → `'en-US'`, `getIntlLocale('th')` → `'th-TH'`
3. Verify `getIntlLocale('xx')` → `'id-ID'` (fallback)
4. Run `npm run test:run -- localeMap --reporter=verbose`
5. **Expected:** 4/4 tests pass

### 2. SelectField has no hardcoded Indonesian placeholder

1. Open `frontend/src/components/evaluation/forms/SelectField.tsx`
2. Search for `"Pilih"` — should not appear
3. Verify component imports `useTranslation` from `react-i18next`
4. Verify placeholder uses `t('common.select')`
5. Run `rg "Pilih\.\.\." frontend/src/components/evaluation/forms/SelectField.tsx`
6. **Expected:** No matches (exit code 1)

### 3. SelectField tests assert on i18n keys

1. Open `frontend/src/components/evaluation/forms/SelectField.test.tsx`
2. Verify `vi.mock('react-i18next')` is present at the top level
3. Verify placeholder assertions use `'common.select'` instead of `'Pilih...'`
4. Run `npm run test:run -- SelectField --reporter=verbose`
5. **Expected:** All 5 SelectField tests pass

### 4. DowntimeWarningDialog has no hardcoded Indonesian

1. Open `frontend/src/components/DowntimeWarningDialog.tsx`
2. Search for `"Sistem Tidak"`, `"Maaf"`, `"Tutup"` — none should appear
3. Verify component imports `useTranslation` and `Trans` from `react-i18next`
4. Verify title uses `t('downtime.title')`, dismiss button uses `t('downtime.dismiss')`
5. Verify description uses `<Trans i18nKey="downtime.description" ...>`
6. Run `rg "Sistem Tidak" frontend/src/components/DowntimeWarningDialog.tsx`
7. **Expected:** No matches (exit code 1)

### 5. DowntimeWarningDialog test file exists with passing tests

1. Verify file exists: `frontend/src/components/DowntimeWarningDialog.test.tsx`
2. Run `npm run test:run -- DowntimeWarningDialog --reporter=verbose`
3. **Expected:** 5/5 tests pass (renders when open, hidden when closed, dismiss callback, description content, title content)

### 6. DeleteEvaluationDialog has no hardcoded Indonesian

1. Open `frontend/src/components/evaluations/DeleteEvaluationDialog.tsx`
2. Search for `"Hapus Evaluasi"`, `"Batal"`, `"Ketik nama"`, `"Anda yakin"` — none should appear
3. Verify component imports `useTranslation` from `react-i18next`
4. Verify 9 strings replaced with `t()` calls using `deleteDialog.*` and `common.*` keys
5. Run `rg "Hapus Evaluasi" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx`
6. **Expected:** No matches (exit code 1)

### 7. DeleteEvaluationDialog tests assert on i18n keys

1. Open `frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx`
2. Verify `vi.mock('react-i18next')` is present
3. Verify assertions use key strings (e.g. `'deleteDialog.title'`) instead of Indonesian
4. Run `npm run test:run -- DeleteEvaluationDialog --reporter=verbose`
5. **Expected:** 9/9 tests pass

### 8. EvaluationHistoryTable has no hardcoded Indonesian or id-ID

1. Open `frontend/src/components/evaluations/EvaluationHistoryTable.tsx`
2. Search for `"Gagal memuat"`, `"Belum ada"`, `"Cari"`, `'id-ID'` — none should appear
3. Verify component imports `useTranslation` from `react-i18next` and `getIntlLocale` from `lib/localeMap`
4. Verify dateFormatter is inside `useMemo` keyed on `i18n.language`, using `getIntlLocale(i18n.language)`
5. Run `rg "id-ID" frontend/src/components/evaluations/EvaluationHistoryTable.tsx`
6. **Expected:** No matches (exit code 1)
7. Run `rg "Gagal memuat" frontend/src/components/evaluations/EvaluationHistoryTable.tsx`
8. **Expected:** No matches (exit code 1)

### 9. EvaluationHistoryTable tests assert on i18n keys

1. Open `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx`
2. Verify `vi.mock('react-i18next')` is present
3. Verify assertions use key strings (e.g. `'history.table.title'`, `'history.table.errorMessage'`)
4. Run `npm run test:run -- EvaluationHistoryTable --reporter=verbose`
5. **Expected:** 17/17 tests pass

### 10. Locale files are in sync with correct keys

1. Run: `python3 -c "import json; [print(f'{f}: {len(json.load(open(f)))} keys') for f in ['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']]"`
2. **Expected:** All 3 files report 624 keys
3. Check `downtime.*` keys exist in all 3: `rg "downtime\." frontend/src/locales/id.json`
4. **Expected:** downtime.title, downtime.description, downtime.dismiss present
5. Check `deleteDialog.*` keys exist: `rg "deleteDialog\." frontend/src/locales/id.json`
6. **Expected:** 7 deleteDialog.* keys present
7. Check `history.table.*` keys exist: `rg "history\.table\." frontend/src/locales/id.json`
8. **Expected:** 22 history.table.* keys present (including history.table.aria.*)

### 11. Full test suite regression check

1. Run `cd frontend && npm run test:run -- --reporter=verbose`
2. **Expected:** 612 tests pass across 68 test files. Zero failures. Above the 602+ baseline.

## Edge Cases

### Unknown language code in localeMap

1. Call `getIntlLocale('zh')` or `getIntlLocale('')`
2. **Expected:** Returns `'id-ID'` as fallback — no error thrown

### Trans component with missing bold slot

1. If DowntimeWarningDialog renders with `Trans` but the locale key omits `<bold>` tags
2. **Expected:** i18next renders the content without formatting — no crash. The time range text appears unstyled.

### SelectField with no placeholder prop

1. SelectField with `showPlaceholder={false}` (or equivalent)
2. **Expected:** The `t('common.select')` placeholder is only rendered when the component logic requests it. No crash if skipped.

## Failure Signals

- Any of the 612 tests failing — indicates broken string extraction or test mock
- `rg` for Indonesian words (`Pilih`, `Gagal`, `Hapus`, `Sistem`) in target components returning hits — indicates missed extraction
- `rg "id-ID"` in EvaluationHistoryTable returning hits — indicates dateFormatter not converted
- Locale file key counts differing between id.json/en.json/th.json — indicates missed key in one language
- Literal key strings (e.g. "downtime.title") appearing in UI at runtime — indicates locale JSON missing the key

## Requirements Proved By This UAT

- R027 — Test cases 2-9 prove all 4 target components use `t()` for every visible string. Grep checks confirm zero hardcoded Indonesian remains.
- R032 — Test case 11 proves all frontend tests pass after extraction. Test cases 3, 5, 7, 9 prove assertions updated to key-based patterns.

## Not Proven By This UAT

- R031 (zero hardcoded Indonesian across ALL source) — only 4 components cleared; remaining components addressed in S02/S03
- Visual language switching — this UAT is artifact-driven. Live runtime verification of Thai/English rendering deferred to S03 UAT.
- Professional translation quality — en.json and th.json values are developer-provided, not professionally reviewed.

## Notes for Tester

- The `vi.mock('react-i18next')` mock makes `t()` return the key string as-is. This means tests verify key *wiring*, not translation *content*. Seeing `"common.select"` in test output is correct behavior, not a bug.
- The test count went from 602 baseline to 612 because 5 new DowntimeWarningDialog tests + 4 localeMap tests + 1 new test elsewhere were added.
- If running individual test files, use `npm run test:run -- <pattern>` not `npx vitest` to ensure correct config resolution.
