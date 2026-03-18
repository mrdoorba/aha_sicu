---
estimated_steps: 7
estimated_files: 5
---

# T03: Extract strings from EvaluationHistoryTable and wire dynamic dateFormatter

**Slice:** S01 — Extract hardcoded strings from un-i18n'd components
**Milestone:** M004

## Description

EvaluationHistoryTable is the largest target component with ~25 hardcoded Indonesian strings and the most complex change: the `dateFormatter` on line ~21 is a **module-level const** that hardcodes `'id-ID'`. It must become dynamic, reading the current i18n language via `getIntlLocale()` from `lib/localeMap.ts` (created in T01). The `BrandAccordionRow` sub-component also calls `dateFormatter.format()` — both sites need the dynamic formatter. The test file has ~20 assertions to update.

**Critical pitfall:** The `dateFormatter` is `const dateFormatter = new Intl.DateTimeFormat('id-ID', ...)` at module scope. This runs once at import. You CANNOT just swap `'id-ID'` for `getIntlLocale(i18n.language)` at module scope — `i18n` isn't available there. You must move the formatter creation inside the component using `useMemo` keyed on `i18n.language`.

Relevant skill: `test` — for test update patterns.

## Steps

1. **Read the component and test file** to understand the full structure:
   - `frontend/src/components/evaluations/EvaluationHistoryTable.tsx`
   - `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx`
   - Understand how `dateFormatter` is used — which lines reference it, whether `BrandAccordionRow` is a separate component in the same file or a sub-component.

2. **Fix the `dateFormatter` to use dynamic locale**:
   - Remove the module-level `const dateFormatter = new Intl.DateTimeFormat('id-ID', ...)` declaration.
   - Import `getIntlLocale` from `@/lib/localeMap` (or `../../lib/localeMap` — match the project's import style).
   - Inside the main `EvaluationHistoryTable` component, after getting `{ t, i18n }` from `useTranslation()`, create the formatter with `useMemo`:
     ```tsx
     const dateFormatter = useMemo(
       () => new Intl.DateTimeFormat(getIntlLocale(i18n.language), { day: 'numeric', month: 'short', year: 'numeric' }),
       [i18n.language]
     );
     ```
   - Check the exact format options used in the original `dateFormatter` — preserve them exactly.
   - If `BrandAccordionRow` is a separate component in the same file, pass `dateFormatter` as a prop. If it's defined inside `EvaluationHistoryTable`, it can capture `dateFormatter` from closure.
   - Make sure `useMemo` is imported from React.

3. **Add `useTranslation()` and extract all ~25 hardcoded strings**:
   - Add `import { useTranslation } from 'react-i18next';` (if not already added in step 2).
   - Add `const { t, i18n } = useTranslation();` inside the component.
   - Replace strings with `t()` calls. Key mapping:
     - Column headers: `"Brand"` → `t('history.table.brand')`, `"Evaluasi"` → `t('history.table.evaluations')`, `"Skor Tertinggi"` → `t('history.table.topScore')`, `"Terbaru"` → `t('history.table.latest')`
     - Evaluation count: `` `${count} evaluasi` `` → `t('history.table.evaluationCount', { count })`
     - Error messages: `"Gagal memuat evaluasi"` → `t('history.table.failedLoadEvaluations')`, `"Gagal memuat riwayat evaluasi"` → `t('history.table.failedLoadHistory')`
     - Show all: `` `Tampilkan semua (${count})` `` → `t('history.table.showAll', { count })`
     - Empty states: `"Belum ada riwayat evaluasi"` → `t('history.table.emptyState')`, `"Mulai evaluasi brand..."` → `t('history.table.emptyStateHint')`
     - Filter states: `"Tidak ada evaluasi yang cocok dengan filter"` → `t('history.table.noMatchFilter')`, search-specific → `t('history.table.noMatchSearch', { search })`, date-specific → `t('history.table.noMatchDate')`
     - Brand count: `` `${count} brand` `` → `t('history.table.brandCount', { count })`
     - **Reuse existing keys**: `"Sebelumnya"` → `t('common.previous')`, `"Berikutnya"` → `t('common.next')`, `` `Halaman ${page} dari ${pages}` `` → `t('common.pageOf', { page, totalPages: pages })` (note: variable is `totalPages` not `pages` in the existing key), `"Coba Lagi"` → `t('common.retry')`
     - Aria labels: `"Riwayat evaluasi"` → `t('history.table.aria.table')`, search label/placeholder/clear, date from/to/clear labels — use `history.table.aria.*` keys
   - Read the component line-by-line — the research found ~25 strings but there may be slight variations. Extract EVERY visible string.

4. **Add `history.table.*` keys to all 3 locale JSON files** (`id.json`, `en.json`, `th.json`):
   - Add all `history.table.*` keys with proper translations.
   - Indonesian values should match the original hardcoded strings exactly.
   - English and Thai translations should be natural equivalents.
   - Keys with interpolation (e.g., `{{count}}`, `{{search}}`) must use the same variable names as the `t()` calls.
   - IMPORTANT: Use **flat dot-notation keys** — `"history.table.brand"` not nested objects.

5. **Update `EvaluationHistoryTable.test.tsx`**:
   - Add `vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string, params?: Record<string, unknown>) => params ? \`\${key}\` : key, i18n: { language: 'id', changeLanguage: vi.fn() } }) }))` at the **top level**. Note: if tests check interpolated strings like "5 evaluasi", the mock `t` function must handle params. The simplest approach: `t: (key: string) => key` — then assertions just check the key. But if tests check for interpolated output, the mock must format params into the key string. Check what the existing tests assert.
   - Also mock or ensure `getIntlLocale` works in the test environment. Since `localeMap.ts` is pure (no side effects), it may not need mocking — it'll return `'id-ID'` when called with `'id'` from the mocked `i18n.language`.
   - Update all ~20 assertions:
     - `getByText('Evaluasi')` → `getByText('history.table.evaluations')`
     - `getByText('Skor Tertinggi')` → `getByText('history.table.topScore')`
     - Any `queryByText('Gagal memuat...')` → `queryByText('history.table.failedLoadHistory')`
     - Assertions on "Halaman X dari Y" → check for `'common.pageOf'` (or the interpolated form, depending on mock)
     - All `aria-label` attribute assertions: update from Indonesian to i18n keys
   - Read the test file carefully — it has the most assertions of all 3 test files.

6. **Run the full test suite** for this component:
   ```bash
   cd frontend && npm run test:run -- EvaluationHistoryTable --reporter=verbose
   ```

7. **Run the full S01 verification sweep**:
   ```bash
   cd frontend && npm run test:run -- --reporter=verbose 2>&1 | tail -30
   rg "id-ID" frontend/src/components/evaluations/EvaluationHistoryTable.tsx
   rg "Gagal memuat" frontend/src/components/evaluations/EvaluationHistoryTable.tsx
   rg "Pilih\.\.\." frontend/src/components/evaluation/forms/SelectField.tsx
   rg "Hapus Evaluasi" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx
   rg "Sistem Tidak" frontend/src/components/DowntimeWarningDialog.tsx
   ```

## Must-Haves

- [ ] `dateFormatter` moved from module-level const into component body using `useMemo` keyed on `i18n.language`
- [ ] `dateFormatter` uses `getIntlLocale(i18n.language)` instead of hardcoded `'id-ID'`
- [ ] `BrandAccordionRow` receives or accesses the dynamic `dateFormatter` (not the old module-level const)
- [ ] All ~25 hardcoded strings replaced with `t()` calls
- [ ] Existing keys reused: `common.previous`, `common.next`, `common.pageOf` (with `{ page, totalPages: pages }`), `common.retry`
- [ ] `common.pageOf` called with `totalPages` not `pages` — matches existing key signature
- [ ] All `history.table.*` keys added to id.json, en.json, th.json
- [ ] All ~20 test assertions updated from Indonesian text to i18n keys
- [ ] `vi.mock('react-i18next')` at top level of test file
- [ ] All EvaluationHistoryTable tests pass
- [ ] `rg "id-ID" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` returns no hits

## Verification

- `cd frontend && npm run test:run -- EvaluationHistoryTable --reporter=verbose` — all tests pass
- `rg "id-ID" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — no hits
- `rg "Gagal memuat" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — no hits
- `rg "Belum ada" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — no hits
- `cd frontend && npm run test:run -- --reporter=verbose 2>&1 | tail -5` — full suite passes (602+ tests)

## Inputs

- `frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — largest target component, ~25 hardcoded strings + module-level `dateFormatter`
- `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx` — test file with ~20 assertions against Indonesian text
- `frontend/src/lib/localeMap.ts` — created in T01, provides `getIntlLocale()`
- `frontend/src/locales/id.json`, `en.json`, `th.json` — locale files already extended in T01 and T02
- T01/T02 output: the `vi.mock('react-i18next')` pattern — match it exactly
- Existing keys to reuse: `common.previous`, `common.next`, `common.pageOf` (uses `{{page}}` and `{{totalPages}}`), `common.retry`, `common.cancel`

## Expected Output

- `frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — modified: `useTranslation()` added, all strings use `t()`, `dateFormatter` is dynamic via `useMemo` + `getIntlLocale()`
- `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx` — modified: mocks i18next, ~20 assertions updated
- `frontend/src/locales/id.json` — ~22 new `history.table.*` keys
- `frontend/src/locales/en.json` — ~22 new `history.table.*` keys
- `frontend/src/locales/th.json` — ~22 new `history.table.*` keys

## Observability Impact

- **Runtime signal:** When language is switched via `LanguageToggle`, EvaluationHistoryTable re-renders all column headers, empty states, filter labels, pagination controls, and aria labels with translated text. The `dateFormatter` re-creates via `useMemo` with the new locale, so dates also reformat.
- **Inspection surface:** Open React DevTools → filter by `EvaluationHistoryTable` → inspect `dateFormatter` in hooks panel to verify it was created with the correct locale. Or switch language and visually confirm that column headers, empty states, and date formats change.
- **Failure visibility:** Missing i18n keys render as literal key strings (e.g., `"history.table.brand"` appears on screen). A hardcoded `'id-ID'` remaining in the component would be caught by `rg "id-ID"` verification. A stale module-level `dateFormatter` would ignore language changes — testable by switching language and observing if dates stay in Indonesian format.
- **Test signal:** The `vi.mock('react-i18next')` mock returns keys as-is. Any key rename in the component without a matching locale file update causes the raw key to appear visually. Any assertion mismatch in tests causes immediate failure.
