---
id: T01
parent: S01
milestone: M004
provides:
  - localeMap.ts utility with getIntlLocale() for downstream date formatting
  - i18n extraction pattern established for SelectField and DowntimeWarningDialog
  - DowntimeWarningDialog test coverage (new file)
  - common.select, common.delete, downtime.* locale keys in all 3 JSON files
key_files:
  - frontend/src/lib/localeMap.ts
  - frontend/src/lib/localeMap.test.ts
  - frontend/src/components/evaluation/forms/SelectField.tsx
  - frontend/src/components/evaluation/forms/SelectField.test.tsx
  - frontend/src/components/DowntimeWarningDialog.tsx
  - frontend/src/components/DowntimeWarningDialog.test.tsx
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
key_decisions:
  - Used Trans component with named <bold> component for DowntimeWarningDialog description (inline JSX formatting)
patterns_established:
  - vi.mock('react-i18next') pattern with t returning key and Trans returning i18nKey for components using Trans
observability_surfaces:
  - Missing i18n keys render as literal key strings in UI (e.g. "downtime.title" visible = locale JSON missing the key)
duration: 15m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T01: Extract strings from SelectField and DowntimeWarningDialog, create localeMap.ts

**Created localeMap.ts utility, extracted hardcoded Indonesian strings from SelectField and DowntimeWarningDialog to i18n keys, added DowntimeWarningDialog test coverage**

## What Happened

Created `localeMap.ts` with `getIntlLocale()` mapping 3 language codes to Intl locales plus fallback. Replaced the hardcoded `"Pilih..."` placeholder in SelectField with `t('common.select')`. Extracted all 3 visible strings from DowntimeWarningDialog: title → `t('downtime.title')`, description → `Trans` component with `i18nKey="downtime.description"` and named `<bold>` component for the operating hours, dismiss button → `t('downtime.dismiss')`. Created a new test file for DowntimeWarningDialog with 5 tests covering open/closed/dismiss/description states. Added 5 new keys (`common.select`, `common.delete`, `downtime.title`, `downtime.description`, `downtime.dismiss`) to all 3 locale files (id, en, th). Updated SelectField test to mock `react-i18next` and assert i18n key instead of hardcoded text.

## Verification

- All 14 task-specific tests pass (localeMap: 4, SelectField: 5, DowntimeWarningDialog: 5)
- Full test suite: 612 tests pass across 68 files (baseline maintained)
- `rg "Pilih\.\.\."` in SelectField.tsx returns no hits
- `rg "Sistem Tidak"` in DowntimeWarningDialog.tsx returns no hits
- `rg "Pilih\.\.\."` in all non-test/non-locale .tsx/.ts files returns no hits

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `npx vitest run SelectField DowntimeWarningDialog localeMap --reporter=verbose` | 0 | ✅ pass | 1.24s |
| 2 | `rg "Pilih\.\.\." frontend/src/components/evaluation/forms/SelectField.tsx` | 1 (no match) | ✅ pass | <1s |
| 3 | `rg "Sistem Tidak" frontend/src/components/DowntimeWarningDialog.tsx` | 1 (no match) | ✅ pass | <1s |
| 4 | `npx vitest run --reporter=verbose` (full suite) | 0 | ✅ pass | 19.3s |
| 5 | `rg "Pilih\.\.\." frontend/src (non-test, non-locale)` | 1 (no match) | ✅ pass | <1s |
| 6 | `rg "Gagal memuat" EvaluationHistoryTable.tsx` | 0 (hits found) | ⏳ T03 scope | <1s |
| 7 | `rg "Hapus Evaluasi" DeleteEvaluationDialog.tsx` | 0 (hits found) | ⏳ T02 scope | <1s |
| 8 | `rg "id-ID" EvaluationHistoryTable.tsx` | 0 (hits found) | ⏳ T03 scope | <1s |

## Diagnostics

- **localeMap:** Pure function, no runtime logging. Test with `getIntlLocale('xx')` → returns `'id-ID'` fallback.
- **i18n wiring:** Switch language in app → SelectField placeholder and DowntimeWarningDialog text change. Missing keys render as literal key strings.
- **Trans component mock:** Tests mock `Trans` as a component that renders `i18nKey` as text. This is sufficient for verifying key wiring without full i18next runtime.

## Deviations

- DowntimeWarningDialog description used `Trans` with named `<bold>` component (not interpolation `{{timeRange}}`), because the original had `<strong>` wrapping the operating hours. The `Trans` approach preserves inline JSX formatting more naturally than string interpolation.
- The description text mentions operating hours "08:00 – 18:30 WIB" (not "00:00 - 08:00 WIB (UTC+7)" as the plan anticipated) — matched actual component content.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/lib/localeMap.ts` — new: exports `getIntlLocale()` with 3 mappings + id-ID fallback
- `frontend/src/lib/localeMap.test.ts` — new: 4 tests covering all mappings + unknown fallback
- `frontend/src/components/evaluation/forms/SelectField.tsx` — added useTranslation, replaced "Pilih..." with t('common.select')
- `frontend/src/components/evaluation/forms/SelectField.test.tsx` — added vi.mock('react-i18next'), updated placeholder assertion
- `frontend/src/components/DowntimeWarningDialog.tsx` — added useTranslation + Trans, extracted 3 strings to i18n keys
- `frontend/src/components/DowntimeWarningDialog.test.tsx` — new: 5 tests covering open/closed/dismiss/description
- `frontend/src/locales/id.json` — added 5 keys: common.select, common.delete, downtime.title/description/dismiss
- `frontend/src/locales/en.json` — added 5 keys with English translations
- `frontend/src/locales/th.json` — added 5 keys with Thai translations
