---
id: T02
parent: S01
milestone: M004
provides:
  - DeleteEvaluationDialog fully i18n'd with 7 new deleteDialog.* keys across 3 locales
  - Reuses common.cancel and common.delete keys from T01
key_files:
  - frontend/src/components/evaluations/DeleteEvaluationDialog.tsx
  - frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
key_decisions:
  - Used common.delete for the "Hapus" button (reuse over deleteDialog.confirmButton) since the label is generic
  - Kept description as a single key (deleteDialog.description) combining both Indonesian sentences
patterns_established:
  - Same vi.mock('react-i18next') hoisted pattern as T01 for test file updates
observability_surfaces:
  - Missing i18n keys render as raw key strings in UI (i18next default behavior)
  - Toast error path (deleteDialog.toast.copyFailed) only fires on clipboard API failure
duration: ~8 minutes
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T02: Extract strings from DeleteEvaluationDialog

**Extract 9 hardcoded Indonesian strings from DeleteEvaluationDialog to i18n keys, add deleteDialog.* keys to all 3 locale files, and update 9 test assertions to verify key wiring**

## What Happened

Replaced all hardcoded Indonesian strings in DeleteEvaluationDialog.tsx with `t()` calls from `useTranslation()`. The component had 9 strings: title, description (two sentences kept as one key), confirmation prompt, placeholder, two aria-labels, a toast error message, and two button labels (cancel and delete). The cancel and delete buttons reuse `common.cancel` and `common.delete` respectively.

Added 7 new `deleteDialog.*` flat dot-notation keys to all three locale files (id.json, en.json, th.json) with proper translations.

Updated the test file with the same `vi.mock('react-i18next')` pattern from T01, and changed all 12 assertion points (across 9 tests) from Indonesian text matching to i18n key matching.

## Verification

- `cd frontend && npm run test:run -- DeleteEvaluationDialog --reporter=verbose` — 9/9 tests pass
- `rg "Hapus Evaluasi" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` — no hits (exit 1)
- `rg "Ketik nama" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` — no hits (exit 1)
- Full test suite: 612 tests pass (68 files), above 602+ baseline

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `cd frontend && npm run test:run -- DeleteEvaluationDialog --reporter=verbose` | 0 | ✅ pass | 3.5s |
| 2 | `rg "Hapus Evaluasi" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` | 1 | ✅ pass (no hits) | <1s |
| 3 | `rg "Ketik nama" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` | 1 | ✅ pass (no hits) | <1s |
| 4 | `cd frontend && npm run test:run -- --reporter=verbose` (full suite) | 0 | ✅ pass (612 tests) | 28.7s |
| 5 | `rg "Pilih\.\.\." frontend/src (excl test/locale)` | 1 | ✅ pass (no hits) | <1s |
| 6 | `rg "Hapus Evaluasi" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` | 1 | ✅ pass (no hits) | <1s |
| 7 | `rg "Sistem Tidak" frontend/src/components/DowntimeWarningDialog.tsx` | 1 | ✅ pass (no hits) | <1s |
| 8 | `rg "Gagal memuat" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` | 0 | ⏳ expected (T03 work) | <1s |
| 9 | `rg "id-ID" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` | 0 | ⏳ expected (T04 work) | <1s |

## Diagnostics

- **Runtime:** Switch language in app → DeleteEvaluationDialog title, description, confirmation prompt, placeholder, button labels, and aria-labels all re-render with translated text. Missing keys render as literal key strings.
- **Test:** Mock `t` returns keys as-is. Any key rename in component without matching test update causes immediate test failure.
- **Toast path:** `deleteDialog.toast.copyFailed` fires only on clipboard API failure — verifiable through Sonner toast or mocked `toast.error` in tests.

## Deviations

None.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` — added useTranslation import, replaced 9 hardcoded strings with t() calls
- `frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx` — added vi.mock('react-i18next'), updated 12 assertion points from Indonesian text to i18n keys
- `frontend/src/locales/id.json` — added 7 deleteDialog.* keys (Indonesian)
- `frontend/src/locales/en.json` — added 7 deleteDialog.* keys (English)
- `frontend/src/locales/th.json` — added 7 deleteDialog.* keys (Thai)
- `.gsd/milestones/M004/slices/S01/tasks/T02-PLAN.md` — added Observability Impact section
