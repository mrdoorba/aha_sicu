---
id: S01
parent: M004
milestone: M004
provides:
  - localeMap.ts utility with getIntlLocale() mapping i18next codes to Intl locale codes (id→id-ID, en→en-US, th→th-TH)
  - 34 new locale keys across 3 JSON files (common.select, common.delete, downtime.*, deleteDialog.*, history.table.*)
  - All 4 target components (SelectField, DowntimeWarningDialog, DeleteEvaluationDialog, EvaluationHistoryTable) fully i18n'd
  - DowntimeWarningDialog test coverage (new file, 5 tests)
  - Established vi.mock('react-i18next') test pattern for i18n extraction
  - Dynamic dateFormatter in EvaluationHistoryTable via useMemo + getIntlLocale()
requires: []
affects:
  - S02
  - S03
key_files:
  - frontend/src/lib/localeMap.ts
  - frontend/src/lib/localeMap.test.ts
  - frontend/src/components/evaluation/forms/SelectField.tsx
  - frontend/src/components/evaluation/forms/SelectField.test.tsx
  - frontend/src/components/DowntimeWarningDialog.tsx
  - frontend/src/components/DowntimeWarningDialog.test.tsx
  - frontend/src/components/evaluations/DeleteEvaluationDialog.tsx
  - frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx
  - frontend/src/components/evaluations/EvaluationHistoryTable.tsx
  - frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
key_decisions:
  - Used Trans component with named <bold> for DowntimeWarningDialog description to preserve inline JSX formatting
  - Passed dateFormatter and t as props to BrandAccordionRow/SearchInput sub-components rather than adding useTranslation to each
  - useMemo keyed on i18n.language for Intl.DateTimeFormat recreation on language switch
patterns_established:
  - vi.mock('react-i18next') hoisted pattern with t returning key string and Trans returning i18nKey — used consistently across all 4 test files
  - For sub-components in the same file needing i18n, pass t and formatted values as props rather than adding useTranslation to each
  - Locale key naming convention: component-scoped namespaces (downtime.*, deleteDialog.*, history.table.*) with common.* for shared labels
observability_surfaces:
  - Missing i18n keys render as literal key strings in UI (i18next default) — visible = locale JSON missing the key
  - getIntlLocale('xx') for unknown codes returns 'id-ID' fallback silently — no error thrown
drill_down_paths:
  - .gsd/milestones/M004/slices/S01/tasks/T01-SUMMARY.md
  - .gsd/milestones/M004/slices/S01/tasks/T02-SUMMARY.md
  - .gsd/milestones/M004/slices/S01/tasks/T03-SUMMARY.md
duration: ~35min
verification_result: passed
completed_at: 2026-03-18
---

# S01: Extract hardcoded strings from un-i18n'd components

**All 4 un-i18n'd components (SelectField, DowntimeWarningDialog, DeleteEvaluationDialog, EvaluationHistoryTable) now route every visible string through `t()` with 34 new locale keys across 3 JSON files. EvaluationHistoryTable's dateFormatter uses dynamic locale via `getIntlLocale()` from new `localeMap.ts` utility. 612 tests pass.**

## What Happened

T01 established the foundation: created `localeMap.ts` with `getIntlLocale()` mapping 3 language codes (id→id-ID, en→en-US, th→th-TH) plus id-ID fallback, extracted 2 strings from SelectField (placeholder `"Pilih..."` → `t('common.select')`), extracted 3 strings from DowntimeWarningDialog using `useTranslation()` + `Trans` component for inline JSX formatting, and created a new DowntimeWarningDialog test file with 5 tests. Added 5 locale keys to all 3 JSON files.

T02 followed the pattern to extract 9 hardcoded strings from DeleteEvaluationDialog: title, description, confirmation prompt, placeholder, 2 aria-labels, a toast error, and 2 button labels (reusing `common.cancel` and `common.delete`). Added 7 `deleteDialog.*` keys. Updated 12 test assertions.

T03 tackled the largest component — EvaluationHistoryTable with ~25 hardcoded strings. Replaced the module-level `const dateFormatter = new Intl.DateTimeFormat('id-ID', ...)` with a `useMemo`-based formatter that reads `i18n.language` via `getIntlLocale()`, preserving the original options (day, month, year, hour, minute, timeZone: 'Asia/Jakarta'). Extracted all strings to `t()` calls with 22 `history.table.*` keys, reusing existing `common.previous`, `common.next`, `common.pageOf`, and `common.retry`. Sub-components `BrandAccordionRow` and `SearchInput` receive translated strings as props. Updated 17 test assertions.

All 3 locale files grew from 590 to 624 keys and remain in sync.

## Verification

All slice-plan verification checks pass:

| # | Check | Result |
|---|-------|--------|
| 1 | `npm run test:run` — full suite | ✅ 612/612 tests pass, 68 test files |
| 2 | `rg "Pilih\.\.\."` in non-test/non-locale source | ✅ no hits |
| 3 | `rg "Gagal memuat" EvaluationHistoryTable.tsx` | ✅ no hits |
| 4 | `rg "Hapus Evaluasi" DeleteEvaluationDialog.tsx` | ✅ no hits |
| 5 | `rg "Sistem Tidak" DowntimeWarningDialog.tsx` | ✅ no hits |
| 6 | `rg "id-ID" EvaluationHistoryTable.tsx` | ✅ no hits |
| 7 | localeMap.ts exists with getIntlLocale() | ✅ present |
| 8 | DowntimeWarningDialog.test.tsx exists | ✅ 5 tests |
| 9 | All 3 locale files have same key count (624) | ✅ in sync |

## Requirements Advanced

- R027 — All 4 target components (EvaluationHistoryTable, DeleteEvaluationDialog, DowntimeWarningDialog, SelectField) now use `t()` for every visible string. ~34 new locale keys added. Zero hardcoded Indonesian remains in these components.
- R032 — All existing frontend tests updated in lockstep with string extraction. Test assertions changed from hardcoded Indonesian text to i18n key patterns. 612 tests pass (above 602+ baseline).
- R031 — Partially advanced. 4 components cleared of hardcoded Indonesian. Remaining work (fields.ts labels, date formatting, month constants) deferred to S02/S03.

## Requirements Validated

- R027 — All 6 grep checks confirm zero hardcoded Indonesian in the 4 target components. 612 tests pass with key-based assertions.

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- none

## Deviations

- DowntimeWarningDialog description used `Trans` component with named `<bold>` instead of string interpolation `{{timeRange}}`, because the original had `<strong>` wrapping operating hours. The `Trans` approach preserves inline JSX formatting naturally.
- DowntimeWarningDialog operating hours text was "08:00 – 18:30 WIB" (not "00:00 - 08:00 WIB (UTC+7)" as plan anticipated) — matched actual component content.
- T03 extracted 22 unique keys (not ~25 as plan estimated) because some strings mapped to reused `common.*` keys. 17 test assertions updated (not ~20) — test file had 17 tests total.

## Known Limitations

- Locale values for `en.json` and `th.json` are developer-provided translations, not professional. Accuracy should be verified by native speakers.
- `getIntlLocale()` fallback is `id-ID` for unknown language codes — adding a 4th language requires updating the mapping.

## Follow-ups

- none — all planned work delivered. S02 consumes `localeMap.ts` for date formatting across 8 files.

## Files Created/Modified

- `frontend/src/lib/localeMap.ts` — new: exports `getIntlLocale()` with 3 mappings + id-ID fallback
- `frontend/src/lib/localeMap.test.ts` — new: 4 tests covering all mappings + unknown fallback
- `frontend/src/components/evaluation/forms/SelectField.tsx` — added useTranslation, replaced "Pilih..." with t('common.select')
- `frontend/src/components/evaluation/forms/SelectField.test.tsx` — added vi.mock('react-i18next'), updated placeholder assertion
- `frontend/src/components/DowntimeWarningDialog.tsx` — added useTranslation + Trans, extracted 3 strings to i18n keys
- `frontend/src/components/DowntimeWarningDialog.test.tsx` — new: 5 tests covering open/closed/dismiss/description states
- `frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` — added useTranslation, replaced 9 hardcoded strings with t() calls
- `frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx` — added vi.mock('react-i18next'), updated 12 assertions
- `frontend/src/components/evaluations/EvaluationHistoryTable.tsx` — added useTranslation + useMemo dateFormatter, replaced ~25 strings with t() calls
- `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx` — added vi.mock('react-i18next'), updated 17 assertions
- `frontend/src/locales/id.json` — added 34 keys: common.select, common.delete, downtime.*, deleteDialog.*, history.table.*
- `frontend/src/locales/en.json` — added 34 keys with English translations
- `frontend/src/locales/th.json` — added 34 keys with Thai translations

## Forward Intelligence

### What the next slice should know
- The `vi.mock('react-i18next')` pattern is established and identical across all 4 test files. Copy from any of them when updating additional test files in S02.
- `localeMap.ts` exports `getIntlLocale(lang)` — import from `@/lib/localeMap` or relative `../../lib/localeMap`. S02 needs this for 8 date formatting sites.
- Locale files are now at 624 keys. S02 will add ~60 more for fields/generic/discount namespaces.
- The mock `t` function returns the key as-is (e.g. `t('common.select')` → `"common.select"`). Tests assert against key strings, not translated text.

### What's fragile
- `BrandAccordionRow` and `SearchInput` receive i18n strings as props from EvaluationHistoryTable — if someone refactors them to standalone components, they'll need their own `useTranslation()` hook.
- The `useMemo` dateFormatter in EvaluationHistoryTable depends on `i18n.language` from the `useTranslation()` hook — if the hook is removed or the destructured `i18n` object changes, the formatter breaks silently (falls back to browser default locale).

### Authoritative diagnostics
- `cd frontend && npm run test:run -- --reporter=verbose` — 612 tests, 68 files. Any regression from S02 changes shows here immediately.
- `rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap` — should return only the remaining 8 date formatting sites that S02 will address.

### What assumptions changed
- Plan estimated ~40 new locale keys; actual count is 34. The gap is due to reusing existing `common.*` keys more than anticipated.
- Plan estimated ~25 strings + ~20 test assertions for EvaluationHistoryTable; actual was 22 keys + 17 test updates. Some strings consolidated into shared keys.
