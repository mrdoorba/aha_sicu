---
id: T01
parent: S03
milestone: M002
provides:
  - R017 locale fix: all 6 hardcoded IDR keys × 3 locale files replaced with {{currency}} interpolation
  - Shared LANGUAGES constant and LanguageCode type in lib/languages.ts
  - EmailLanguageSelector reusable dropdown component with tests
key_files:
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
  - frontend/src/lib/languages.ts
  - frontend/src/components/layout/LanguageToggle.tsx
  - frontend/src/components/shared/EmailLanguageSelector.tsx
  - frontend/src/components/shared/EmailLanguageSelector.test.tsx
key_decisions:
  - Used native <select> instead of Radix/shadcn Select for EmailLanguageSelector — simpler, easier to test, and appropriate for a small utility dropdown inside dialogs
patterns_established:
  - Shared LANGUAGES array in lib/languages.ts as single source of truth for supported languages
  - EmailLanguageSelector uses native <select> with data-testid for easy automation targeting
observability_surfaces:
  - data-testid="email-language-select" on the dropdown element for test/automation targeting
  - grep -c "IDR" frontend/src/locales/*.json returns 0 (all currency hardcodes eliminated)
duration: 15m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T01: Fix R017 locale hardcodes + create EmailLanguageSelector component

**Replace 6 hardcoded IDR strings with {{currency}} interpolation in 3 locale files, extract shared LANGUAGES constant, and create reusable EmailLanguageSelector dropdown component with 8 passing tests.**

## What Happened

1. **R017 locale fix:** Replaced all `IDR` occurrences across `id.json`, `en.json`, and `th.json` with `{{currency}}` interpolation variable in 6 keys: `scoring.monthlySales.pass`, `scoring.monthlySales.fail`, `scoring.competitionProduct.pass`, `scoring.competitionProduct.fail`, `forms.competition.competitive`, and `forms.competition.notCompetitive`. The backend already provides `currency` in i18n vars, so these keys will now render the correct currency code (IDR or THB) based on marketplace.

2. **Added `emailLanguageSelector.label` key** to all 3 locale files: "Bahasa Email" (ID), "Email Language" (EN), "ภาษาอีเมล" (TH).

3. **Created `frontend/src/lib/languages.ts`** exporting the `LANGUAGES` array and `LanguageCode` type. This is now the single source of truth for supported languages.

4. **Updated `LanguageToggle.tsx`** to import `LANGUAGES` from the shared module instead of defining it locally. Removed the local constant.

5. **Created `EmailLanguageSelector` component** — a native `<select>` dropdown with label, accepting `value`, `onChange`, and optional `className` props. Uses the shared `LANGUAGES` array and `useTranslation` for the label.

6. **Wrote 8 tests** covering: rendering 3 options, label display, current value selection for all 3 language codes, onChange firing, className pass-through, and rendering without errors for each valid code.

## Verification

- EmailLanguageSelector tests: 8/8 passed
- Full regression: 65 test files passed, 564 tests passed, 0 failures
- IDR grep check: 0 occurrences in all 3 locale files
- {{currency}} count: 6 per file (correct)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `cd frontend && npx vitest run src/components/shared/EmailLanguageSelector.test.tsx --reporter=verbose` | 0 | ✅ pass | 0.9s |
| 2 | `cd frontend && npx vitest run --reporter=verbose 2>&1 \| tail -5` | 0 | ✅ pass | 33s |
| 3 | `grep -c "IDR" frontend/src/locales/id.json frontend/src/locales/en.json frontend/src/locales/th.json` | 1 (grep no-match = success) | ✅ pass | 0.1s |

### Slice-level verification (partial — T01 is first task of S03)

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | EmailLanguageSelector.test.tsx | ✅ pass | 8/8 tests |
| 2 | buildI18nEmailBody.test.ts | ⏳ not yet | T02 deliverable |
| 3 | SendMailDialog.test.tsx | ⏳ not yet | T03 deliverable |
| 4 | SendEmailDialog.test.tsx | ⏳ not yet | T02 deliverable |
| 5 | EmailOutput.test.tsx | ⏳ not yet | T03 deliverable |
| 6 | Full regression | ✅ pass | 564 passed, 0 failures |

## Diagnostics

- **Currency interpolation:** If `{{currency}}` appears literally in rendered text, it means the calling code isn't passing `currency` as an i18n interpolation variable. Check the scoring/competition code paths that use these 6 keys.
- **EmailLanguageSelector:** Renders with `data-testid="email-language-select"` and `id="email-language-select"`. The label uses the `emailLanguageSelector.label` translation key.
- **LANGUAGES constant:** Imported from `frontend/src/lib/languages.ts`. If a new language is added, only this file needs updating (plus the locale JSON).

## Deviations

- Used `sed` for locale file replacements after the Edit tool's exact-match approach had difficulty with Unicode bullet characters (•) in the forms.competition keys. The `sed` approach was more reliable for bulk pattern replacement.
- Used native `<select>` instead of Radix/shadcn Select for the EmailLanguageSelector — the plan allowed this ("plain `<select>` matching existing patterns"). This choice simplifies testing significantly (no portal/accessibility workarounds needed).

## Known Issues

None.

## Files Created/Modified

- `frontend/src/locales/id.json` — 6 IDR→{{currency}} replacements + added emailLanguageSelector.label key
- `frontend/src/locales/en.json` — 6 IDR→{{currency}} replacements + added emailLanguageSelector.label key
- `frontend/src/locales/th.json` — 6 IDR→{{currency}} replacements + added emailLanguageSelector.label key
- `frontend/src/lib/languages.ts` — **new** shared LANGUAGES constant and LanguageCode type
- `frontend/src/components/layout/LanguageToggle.tsx` — removed local LANGUAGES, imports from shared lib
- `frontend/src/components/shared/EmailLanguageSelector.tsx` — **new** reusable language selector dropdown
- `frontend/src/components/shared/EmailLanguageSelector.test.tsx` — **new** 8 component tests
- `.gsd/milestones/M002/slices/S03/tasks/T01-PLAN.md` — added Observability Impact section
