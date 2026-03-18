---
id: T03
parent: S01
milestone: M004
provides:
  - EvaluationHistoryTable fully i18n'd with 22 new history.table.* keys across 3 locales
  - Dynamic dateFormatter via useMemo + getIntlLocale(i18n.language) replacing hardcoded 'id-ID'
  - BrandAccordionRow receives dateFormatter and t as props for i18n support
key_files:
  - frontend/src/components/evaluations/EvaluationHistoryTable.tsx
  - frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
key_decisions:
  - Passed dateFormatter and t as props to BrandAccordionRow rather than calling useTranslation inside it, since it's a sub-component in the same file and avoids a second hook call
  - Passed ariaLabel, placeholder, and clearLabel as props to SearchInput rather than calling useTranslation inside it
  - Preserved exact dateFormatter options (day, month, year, hour, minute, timeZone) from original module-level const
patterns_established:
  - For sub-components in the same file that need i18n, pass t and formatted values as props rather than adding useTranslation to each sub-component
  - useMemo keyed on i18n.language for Intl.DateTimeFormat recreation on language change
observability_surfaces:
  - Runtime: language switch causes dateFormatter recreation and all text re-render via useTranslation
  - Test: vi.mock('react-i18next') returns keys as-is — any key mismatch causes visible literal key strings
duration: 12min
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T03: Extract strings from EvaluationHistoryTable and wire dynamic dateFormatter

**Extract ~25 hardcoded Indonesian strings from EvaluationHistoryTable, add 22 history.table.* keys to 3 locale files, move dateFormatter from module-level const into useMemo with dynamic locale via getIntlLocale(), update 17 test assertions**

## What Happened

Removed the module-level `const dateFormatter = new Intl.DateTimeFormat('id-ID', ...)` and replaced it with a `useMemo`-based formatter inside EvaluationHistoryTable that reads `i18n.language` via `getIntlLocale()` from `localeMap.ts` (created in T01). The formatter preserves the original options: day, month, year, hour, minute, and Asia/Jakarta timeZone.

Added `useTranslation()` to the main component and extracted all ~25 hardcoded Indonesian strings to `t()` calls. Sub-components `BrandAccordionRow` and `SearchInput` receive translated strings via props rather than calling `useTranslation()` themselves — this keeps hook usage minimal and follows the pattern of the existing code.

Added 22 new `history.table.*` keys (including 7 `history.table.aria.*` keys) to all 3 locale files. Indonesian values match the original hardcoded strings exactly. Reused existing keys: `common.previous`, `common.next`, `common.pageOf` (with `{ page, totalPages: pages }`), `common.retry`.

Updated the test file with `vi.mock('react-i18next')` at top level (matching T01/T02 pattern) and updated all 17 assertions from Indonesian text to i18n key strings.

## Verification

- `npm run test:run -- EvaluationHistoryTable --reporter=verbose` — 17/17 tests pass
- `npm run test:run -- --reporter=verbose` — 612/612 tests pass (68 test files)
- `rg "id-ID" EvaluationHistoryTable.tsx` — no hits
- `rg "Gagal memuat" EvaluationHistoryTable.tsx` — no hits
- `rg "Belum ada" EvaluationHistoryTable.tsx` — no hits
- All slice verification greps pass (SelectField, DeleteEvaluationDialog, DowntimeWarningDialog)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `cd frontend && npm run test:run -- EvaluationHistoryTable --reporter=verbose` | 0 | ✅ pass | 4.1s |
| 2 | `cd frontend && npm run test:run -- --reporter=verbose` | 0 | ✅ pass | 20.3s |
| 3 | `rg "id-ID" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` | 1 | ✅ pass (no hits) | <1s |
| 4 | `rg "Gagal memuat" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` | 1 | ✅ pass (no hits) | <1s |
| 5 | `rg "Belum ada" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` | 1 | ✅ pass (no hits) | <1s |
| 6 | `rg "Pilih\.\.\." frontend/src/components/evaluation/forms/SelectField.tsx` | 1 | ✅ pass (no hits) | <1s |
| 7 | `rg "Hapus Evaluasi" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` | 1 | ✅ pass (no hits) | <1s |
| 8 | `rg "Sistem Tidak" frontend/src/components/DowntimeWarningDialog.tsx` | 1 | ✅ pass (no hits) | <1s |

## Diagnostics

- **Runtime:** Switch language via LanguageToggle → all EvaluationHistoryTable text (column headers, empty states, filter labels, pagination, aria-labels) re-renders. Dates reformat based on new locale. Missing keys render as literal key strings.
- **Test:** Mock `t` returns keys as-is. Any key rename without matching test update causes immediate test failure. `getIntlLocale` doesn't need mocking — it's a pure function that returns `'id-ID'` for `'id'` input from mocked `i18n.language`.

## Deviations

- Plan noted ~25 hardcoded strings and ~20 test assertions. Actual count: 22 unique i18n keys extracted, 17 test assertions updated. The discrepancy is because some plan-listed strings mapped to reused common.* keys rather than new keys, and the test file had 17 tests total (not 20 assertions to update).
- Plan suggested `t('history.table.evaluationCount', { count })` — implemented exactly but the test mock returns just the key string since the mock `t` ignores params. Tests assert against the key name, which is sufficient for verifying key wiring.
- The original dateFormatter included `hour: '2-digit'`, `minute: '2-digit'`, and `timeZone: 'Asia/Jakarta'` — the plan only mentioned `day`, `month`, `year`. Preserved all original options in the useMemo.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — Added useTranslation + useMemo dateFormatter, replaced all hardcoded strings with t() calls, passed dateFormatter/t as props to BrandAccordionRow, passed translated strings as props to SearchInput
- `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx` — Added vi.mock('react-i18next'), updated 17 assertions from Indonesian text to i18n key strings
- `frontend/src/locales/id.json` — Added 22 history.table.* keys with Indonesian translations
- `frontend/src/locales/en.json` — Added 22 history.table.* keys with English translations
- `frontend/src/locales/th.json` — Added 22 history.table.* keys with Thai translations
- `.gsd/milestones/M004/slices/S01/tasks/T03-PLAN.md` — Added Observability Impact section (pre-flight fix)
