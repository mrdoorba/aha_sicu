---
id: S03
parent: M002
milestone: M002
provides:
  - EmailLanguageSelector reusable dropdown component with shared LANGUAGES constant
  - buildI18nEmailBody utility mirroring backend _assemble_email_body section ordering with i18n support
  - buildI18nEmailSubject utility for translated email subjects
  - Language selector integrated into all 3 email dialogs (SendMailDialog, SendEmailDialog, EmailOutput)
  - R017 locale fix — all 6 hardcoded IDR keys × 3 locale files replaced with {{currency}} interpolation
  - Backend preview endpoint accepts optional language query param
  - emailBody.section.* locale keys in all 3 locale files for email section headers
requires:
  - slice: S02
    provides: renderTranslatable() wiring complete in EvaluationDetailPage; frontend types with _i18n fields; marketplace field in evaluation detail response
affects:
  - S04
key_files:
  - frontend/src/lib/languages.ts
  - frontend/src/components/shared/EmailLanguageSelector.tsx
  - frontend/src/components/shared/EmailLanguageSelector.test.tsx
  - frontend/src/utils/buildI18nEmailBody.ts
  - frontend/src/utils/buildI18nEmailBody.test.ts
  - frontend/src/components/dashboard/SendEmailDialog.tsx
  - frontend/src/components/dashboard/SendEmailDialog.test.tsx
  - frontend/src/components/evaluation/scoring/EmailOutput.tsx
  - frontend/src/components/evaluation/scoring/EmailOutput.test.tsx
  - frontend/src/components/evaluations/SendMailDialog.tsx
  - frontend/src/components/evaluations/SendMailDialog.test.tsx
  - frontend/src/components/evaluations/sendMailUtils.ts
  - frontend/src/components/evaluation/scoring/ScoringSection.tsx
  - frontend/src/pages/EvaluationDetailPage.tsx
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
  - backend/app/modules/email/router.py
key_decisions:
  - Native <select> for EmailLanguageSelector — simpler than Radix/shadcn, easier to test, appropriate for small utility dropdown
  - Dedicated emailBody.section.* locale keys instead of reusing rules.category.* — email headers differ from category names
  - EmailLanguageSelector conditionally rendered in EmailOutput (only when scoringResult present); always rendered in SendMailDialog/SendEmailDialog
  - hasI18nData guard checks for message_i18n presence before enabling language-aware rendering — graceful fallback for old evaluations
  - SECTION_DEFS declarative array mirrors backend _assemble_email_body exactly for section ordering and row filters
patterns_established:
  - Shared LANGUAGES array in lib/languages.ts as single source of truth for supported languages (consumed by LanguageToggle and EmailLanguageSelector)
  - buildI18nEmailBody pure function with SECTION_DEFS declarative config — same section order, row filters, and emoji prefixes as backend _assemble_email_body
  - Optional TFunction parameter on sendMailUtils buildSubject/buildBody — defaults to global i18n.t, overridden by fixedT for language-specific rendering
  - emailBodyOverride param on buildBody — replaces raw emailOutput with i18n-assembled body while keeping salutation/intro wrapper
  - hasI18nData guard pattern — checks scoreBreakdown rows for message_i18n presence before enabling language-aware rendering
observability_surfaces:
  - data-testid="email-language-select" on all 3 email dialog language selectors
  - Preview endpoint accepts ?language=th|en|id query param
  - grep -c "IDR" frontend/src/locales/*.json returns 0 (all currency hardcodes eliminated)
  - buildI18nEmailBody is a pure function — verify via npx vitest run src/utils/buildI18nEmailBody.test.ts
drill_down_paths:
  - .gsd/milestones/M002/slices/S03/tasks/T01-SUMMARY.md
  - .gsd/milestones/M002/slices/S03/tasks/T02-SUMMARY.md
  - .gsd/milestones/M002/slices/S03/tasks/T03-SUMMARY.md
duration: 60m
verification_result: passed
completed_at: 2026-03-18
---

# S03: Email language selector & i18n body rebuild

**All 3 email dialogs (history SendMailDialog, dashboard SendEmailDialog, evaluation page EmailOutput) now have a language selector that rebuilds the email body in the chosen language from stored i18n data, with graceful fallback for pre-i18n evaluations. 6 hardcoded IDR locale keys replaced with {{currency}} interpolation.**

## What Happened

The slice shipped in 3 tasks building bottom-up: shared infrastructure → core utility + first dialog → remaining two dialogs.

**T01 — Shared infrastructure.** Replaced all 6 hardcoded `IDR` strings with `{{currency}}` interpolation across 3 locale files (scoring.monthlySales.pass/fail, scoring.competitionProduct.pass/fail, forms.competition.competitive/notCompetitive). Extracted the `LANGUAGES` array from `LanguageToggle.tsx` into a shared `lib/languages.ts` module as the single source of truth for supported languages. Created `EmailLanguageSelector` — a native `<select>` dropdown accepting `value` + `onChange`, defaulting to the current UI language, using the shared `LANGUAGES` array. Added `emailLanguageSelector.label` locale keys in all 3 languages.

**T02 — Core email assembly + dashboard dialog.** Created `buildI18nEmailBody()` and `buildI18nEmailSubject()` in `utils/buildI18nEmailBody.ts`. The body function mirrors backend `_assemble_email_body` exactly — same 8 category sections with correct emoji prefixes and row filters (including the tricky promo section with rows 31-43), followed by conclusion, marketing estimation, marketing budget, and closing message sections. Each row message uses `renderTranslatable()` for i18n-aware rendering with raw fallback. Wired `EmailLanguageSelector` into `SendEmailDialog` — selected language flows to mutation payload and preview URL as `?language=X` query param. Updated backend preview endpoint in `router.py` to accept optional `language` query parameter. Added 10 new `emailBody.section.*` locale keys to all 3 locale files for translated email section headers.

**T03 — Remaining two dialogs.** Wired `EmailOutput` with optional `scoringResult` prop and conditional `EmailLanguageSelector` (only renders when scoring data is available for i18n rebuild). Updated `ScoringSection` to pass `scoringResult` through. Extended `sendMailUtils.ts` `buildSubject`/`buildBody` with optional `TFunction` and `emailBodyOverride` parameters for language-specific rendering. Wired `SendMailDialog` (history page) with `scoreBreakdown` and `calculatorResults` props, language selector, and `hasI18nData` guard for graceful degradation. Updated `EvaluationDetailPage` to pass `score_breakdown` and `calculator_results` to `SendMailDialog`.

## Verification

| # | Check | Result | Details |
|---|-------|--------|---------|
| 1 | EmailLanguageSelector.test.tsx | ✅ 8/8 | Renders 3 options, onChange fires, className passthrough |
| 2 | buildI18nEmailBody.test.ts | ✅ 20/20 | Section ordering, row filtering, i18n translation, fallback, conclusion/marketing/closing |
| 3 | SendMailDialog.test.tsx | ✅ 21/21 | 12 existing + 9 new (language selector, i18n body, TFunction, emailBodyOverride) |
| 4 | SendEmailDialog.test.tsx | ✅ 22/22 | 18 existing + 4 new (language selector, mutation payload, preview URL) |
| 5 | EmailOutput.test.tsx | ✅ 11/11 | 4 existing + 7 new (language selector, dynamic body, copy behavior) |
| 6 | Full regression | ✅ 602/602 | 66 test files, 602 passed, 1 skipped, 0 failures |
| 7 | IDR hardcode check | ✅ 0 hits | grep -c "IDR" returns 0 for all 3 locale files |
| 8 | Backend preview endpoint | ✅ imports OK | preview_email_endpoint accepts optional language param |

## Requirements Advanced

- R020 — LANGUAGES array now in shared lib/languages.ts; adding a language requires only locale JSON + languages.ts entry + backend config. Full verification deferred to S04 documentation.

## Requirements Validated

- R015 — All 3 email dialogs have EmailLanguageSelector. Selector defaults to UI language, onChange updates email body preview without changing global UI language. 16 language-selector-specific tests across 3 dialog test suites.
- R016 — buildI18nEmailBody (20 unit tests) assembles email body from stored i18n structured data matching backend section ordering. buildI18nEmailSubject constructs translated subject. Pre-i18n evaluations fall back to raw email_output string. Wired into all 3 dialogs.
- R017 — All 6 keys across 3 locale files replaced with {{currency}} interpolation. grep confirms 0 IDR occurrences, 6 {{currency}} per file.

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- none

## Deviations

- **Promo row filter corrected:** Plan stated "rows 34-41" but actual backend uses PROMO_START_ROW=31 with 11 tools (rows 31-41) plus summary rows 42, 43. Implementation follows actual backend logic.
- **Added emailBody.section.\* locale keys:** Plan didn't explicitly mention adding new locale keys for email section headers, but they were needed because backend hardcodes Indonesian header text and we need translatable versions.

## Known Limitations

- **SendMailDialog language selector always visible:** Even for pre-i18n evaluations where language switching has no effect. The `hasI18nData` guard silently falls back to Indonesian body, which is correct behavior but the selector's presence may be misleading. A tooltip or disabled state could improve UX in a future pass.
- **Backend preview endpoint language param is pass-through only:** The `language` param is accepted and forwarded to `render_email_html`, but no integration test verifies the full render path. Backend email template rendering was not in scope for S03.
- **DialogContent missing Description warnings:** Radix Dialog logs accessibility warnings about missing `Description` or `aria-describedby`. Pre-existing issue across multiple dialogs, not introduced by S03.

## Follow-ups

- S04 should document the exact "add a new language" checklist — lib/languages.ts is now the frontend single source of truth, which simplifies the steps
- Consider adding a disabled/tooltip state to EmailLanguageSelector for pre-i18n evaluations where language switching has no effect
- The backend preview endpoint's language param should eventually get an integration test (not blocking for S03)

## Files Created/Modified

- `frontend/src/lib/languages.ts` — **new** shared LANGUAGES array and LanguageCode type
- `frontend/src/components/shared/EmailLanguageSelector.tsx` — **new** reusable language dropdown component
- `frontend/src/components/shared/EmailLanguageSelector.test.tsx` — **new** 8 component tests
- `frontend/src/utils/buildI18nEmailBody.ts` — **new** email body/subject assembly with i18n support + ScoringConclusionData type
- `frontend/src/utils/buildI18nEmailBody.test.ts` — **new** 20 unit tests
- `frontend/src/components/dashboard/SendEmailDialog.tsx` — added EmailLanguageSelector, language state, wired to mutation + preview
- `frontend/src/components/dashboard/SendEmailDialog.test.tsx` — added 4 language selector tests
- `frontend/src/components/evaluation/scoring/EmailOutput.tsx` — added scoringResult prop, conditional language selector, dynamic i18n body
- `frontend/src/components/evaluation/scoring/EmailOutput.test.tsx` — added 7 language/dynamic body tests
- `frontend/src/components/evaluation/scoring/ScoringSection.tsx` — passes scoringResult to EmailOutput
- `frontend/src/components/evaluations/SendMailDialog.tsx` — added scoreBreakdown/calculatorResults props, language selector, hasI18nData guard
- `frontend/src/components/evaluations/SendMailDialog.test.tsx` — added 9 language selector and i18n body tests
- `frontend/src/components/evaluations/sendMailUtils.ts` — added optional TFunction and emailBodyOverride params
- `frontend/src/pages/EvaluationDetailPage.tsx` — passes score_breakdown and calculator_results to SendMailDialog
- `frontend/src/components/layout/LanguageToggle.tsx` — imports LANGUAGES from shared lib
- `frontend/src/locales/id.json` — 6 IDR→{{currency}} replacements + emailLanguageSelector.label + 10 emailBody.section.* keys
- `frontend/src/locales/en.json` — 6 IDR→{{currency}} replacements + emailLanguageSelector.label + 10 emailBody.section.* keys
- `frontend/src/locales/th.json` — 6 IDR→{{currency}} replacements + emailLanguageSelector.label + 10 emailBody.section.* keys
- `backend/app/modules/email/router.py` — added optional language query param to preview endpoint

## Forward Intelligence

### What the next slice should know
- LANGUAGES array lives in `frontend/src/lib/languages.ts` — this is the single source of truth for supported languages on the frontend. S04's "add a language" checklist should reference this file, not LanguageToggle.tsx.
- The R017 fix (IDR→{{currency}}) is complete. S04 only needs to verify no OTHER hardcoded language assumptions remain elsewhere — the 6 locale keys are done.
- `emailBody.section.*` locale keys were added in S03 for email section headers. These are separate from `rules.category.*` keys and should be included in S04's locale audit.

### What's fragile
- `SECTION_DEFS` in `buildI18nEmailBody.ts` must stay synchronized with backend `_assemble_email_body` in `computations.py:328-440`. If the backend changes section ordering or row ranges, the frontend email body will diverge. No automated cross-validation exists.
- `sendMailUtils.ts` `buildBody` has two code paths: with `emailBodyOverride` (i18n) and without (raw). The override replaces only the email body portion while keeping the salutation/intro wrapper. If the wrapper structure changes, both paths need updating.

### Authoritative diagnostics
- `npx vitest run src/utils/buildI18nEmailBody.test.ts` — 20 tests verify section ordering, row filtering, i18n translation, and fallback. If the email body looks wrong, this test suite is the first place to check.
- `grep -c "IDR" frontend/src/locales/*.json` — must return 0 for all files. Any non-zero result means R017 has regressed.
- `data-testid="email-language-select"` — present in all 3 dialogs for automation targeting.

### What assumptions changed
- Plan assumed promo section uses rows 34-41 — actual backend uses rows 31-43 (PROMO_START_ROW=31 with 11 tools + 2 summary rows). Implementation follows the real backend, not the plan.
- Plan didn't mention needing new locale keys for email section headers — `emailBody.section.*` keys were added because backend email headers differ from category display names.
