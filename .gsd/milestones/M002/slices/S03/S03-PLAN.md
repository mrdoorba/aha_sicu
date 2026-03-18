# S03: Email language selector & i18n body rebuild

**Goal:** All three email dialogs (history SendMailDialog, dashboard SendEmailDialog, evaluation page EmailOutput) have a language selector that defaults to the UI language. Choosing a different language rebuilds the email body/subject in that language without changing the global UI language.
**Demo:** Open any email send dialog → pick TH from language dropdown → email body preview renders in Thai while UI stays in current language.

## Must-Haves

- `EmailLanguageSelector` component — reusable language dropdown for all email dialogs
- `buildI18nEmailBody()` utility that assembles plain-text email body from `score_breakdown` i18n fields, mirroring backend `_assemble_email_body` section ordering
- `buildI18nEmailSubject()` utility for subject line
- Language selector integrated into `SendMailDialog` (history), `SendEmailDialog` (dashboard), `EmailOutput` (evaluation page)
- R017: All 6 hardcoded `IDR` locale keys across 3 files replaced with `{{currency}}` interpolation
- Pre-i18n evaluations (missing `_i18n` fields) fall back to raw Indonesian body — language selector has no effect (correct behavior)
- Backend preview endpoint accepts optional `language` query param for dashboard email preview

## Proof Level

- This slice proves: integration
- Real runtime required: no (component tests + unit tests prove all contracts)
- Human/UAT required: yes (visual check of email body rendering across languages)

## Verification

- `cd frontend && npx vitest run src/utils/buildI18nEmailBody.test.ts --reporter=verbose` — unit tests for email body assembly with i18n, fallback, and section ordering
- `cd frontend && npx vitest run src/components/shared/EmailLanguageSelector.test.tsx --reporter=verbose` — component renders 3 languages, onChange fires
- `cd frontend && npx vitest run src/components/evaluations/SendMailDialog.test.tsx --reporter=verbose` — existing + new tests for language selector and dynamic body
- `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx --reporter=verbose` — existing + new tests for language selector
- `cd frontend && npx vitest run src/components/evaluation/scoring/EmailOutput.test.tsx --reporter=verbose` — existing + new tests for language selector and dynamic body
- `cd frontend && npx vitest run --reporter=verbose 2>&1 | tail -5` — full regression: all 556+ tests pass, 0 failures
- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/integration/api/test_email.py -x -v` — backend preview endpoint test (if exists)

## Observability / Diagnostics

- Runtime signals: email language selector value is passed as `language` field in SendEmailDialog mutation payload; preview endpoint logs language param
- Inspection surfaces: in each dialog, the language dropdown is visible and the body preview updates reactively; backend preview endpoint accepts `?language=th` query param
- Failure visibility: wrong language in email body is immediately visible in the dialog preview; missing `_i18n` fields cause fallback to Indonesian (visible but not broken)
- Redaction constraints: none

## Integration Closure

- Upstream surfaces consumed: `renderTranslatable()` from `utils/renderTranslatable.ts`; `CATEGORY_MAP` from `lib/categoryMap.ts`; `ScoringResult` and `CategoryScore`/`RowScore` types from `hooks/useScoring.ts`; `EvaluationDetail` from `hooks/useEvaluationDetail.ts`; `i18n.getFixedT()` from i18next; backend `_assemble_email_body` section ordering from `computations.py`
- New wiring introduced in this slice: `EmailLanguageSelector` composed into 3 dialog components; `buildI18nEmailBody` consumed by `SendMailDialog` and `EmailOutput`; `ScoringSection` passes full `scoringResult` to `EmailOutput`; `EvaluationDetailPage` passes `score_breakdown` and `calculator_results` to `SendMailDialog`; backend preview endpoint gains `language` query param
- What remains before the milestone is truly usable end-to-end: S04 (locale hardcode cleanup for non-R017 items, future-proofing documentation) — but all email dialogs are fully functional after S03

## Tasks

- [x] **T01: Fix R017 locale hardcodes + create EmailLanguageSelector component** `est:45m`
  - Why: R017 (hardcoded IDR) is a prerequisite for correct currency display in rebuilt email bodies. The `EmailLanguageSelector` and shared `LANGUAGES` constant are needed by all three dialog wiring tasks.
  - Files: `frontend/src/locales/id.json`, `frontend/src/locales/en.json`, `frontend/src/locales/th.json`, `frontend/src/lib/languages.ts`, `frontend/src/components/layout/LanguageToggle.tsx`, `frontend/src/components/shared/EmailLanguageSelector.tsx`, `frontend/src/components/shared/EmailLanguageSelector.test.tsx`
  - Do: (1) Replace `IDR` with `{{currency}}` in 6 keys across 3 locale files (scoring.monthlySales.pass/fail, scoring.competitionProduct.pass/fail, forms.competition.competitive/notCompetitive). (2) Create `frontend/src/lib/languages.ts` exporting the `LANGUAGES` array. (3) Update `LanguageToggle.tsx` to import from the new shared location. (4) Create `EmailLanguageSelector` component — a simple `<select>` dropdown accepting `value` + `onChange`, defaulting to `i18n.language`, using the shared `LANGUAGES` array. (5) Write tests for `EmailLanguageSelector`.
  - Verify: `cd frontend && npx vitest run src/components/shared/EmailLanguageSelector.test.tsx --reporter=verbose` passes; full regression passes
  - Done when: 6 locale keys use `{{currency}}`; `LANGUAGES` exported from `lib/languages.ts`; `EmailLanguageSelector` renders and fires onChange; all existing tests pass

- [x] **T02: Create buildI18nEmailBody utility + wire SendEmailDialog language selector** `est:1h`
  - Why: The core email body assembly function must mirror backend `_assemble_email_body` section ordering and use `i18n.getFixedT(lang)` to render each row's `message_i18n`. Wiring into SendEmailDialog (the simplest dialog) proves the pattern works end-to-end.
  - Files: `frontend/src/utils/buildI18nEmailBody.ts`, `frontend/src/utils/buildI18nEmailBody.test.ts`, `frontend/src/components/dashboard/SendEmailDialog.tsx`, `frontend/src/components/dashboard/SendEmailDialog.test.tsx`, `backend/app/modules/email/router.py`
  - Do: (1) Create `buildI18nEmailBody.ts` with `buildI18nEmailBody(categoryScores, scoringSummary, t)` and `buildI18nEmailSubject(brandName, period, t)`. The body function mirrors `_assemble_email_body` from `backend/app/calculators/scoring/computations.py:328-440` — same section order, same row filters, same emoji headers. Uses `renderTranslatable(row.message, row.message_i18n, t)` for each row message, `CATEGORY_MAP` for section headers. (2) Write comprehensive unit tests. (3) Add `EmailLanguageSelector` to `SendEmailDialog` — wire selected language to mutation payload's `language` field and to the preview endpoint URL as `?language=X` query param. (4) Add optional `language` query param to backend `preview_email_endpoint` in `router.py`. (5) Update `SendEmailDialog.test.tsx` with language selector tests.
  - Verify: `cd frontend && npx vitest run src/utils/buildI18nEmailBody.test.ts --reporter=verbose` passes; `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx --reporter=verbose` passes; full regression passes
  - Done when: `buildI18nEmailBody` produces correct section-ordered body from mock i18n data; `buildI18nEmailSubject` produces translated subject; `SendEmailDialog` has language selector that controls mutation language and preview URL; backend preview endpoint accepts `language` query param

- [x] **T03: Wire EmailOutput and SendMailDialog with language selector + i18n body rebuild** `est:1h`
  - Why: The remaining two dialogs need the language selector and dynamic body assembly. `EmailOutput` needs `ScoringResult` data flow from `ScoringSection`. `SendMailDialog` needs `score_breakdown` and `calculator_results` from `EvaluationDetailPage`.
  - Files: `frontend/src/components/evaluation/scoring/EmailOutput.tsx`, `frontend/src/components/evaluation/scoring/EmailOutput.test.tsx`, `frontend/src/components/evaluation/scoring/ScoringSection.tsx`, `frontend/src/components/evaluations/SendMailDialog.tsx`, `frontend/src/components/evaluations/SendMailDialog.test.tsx`, `frontend/src/components/evaluations/sendMailUtils.ts`, `frontend/src/pages/EvaluationDetailPage.tsx`
  - Do: (1) Update `EmailOutput` interface to accept optional `scoringResult: ScoringResult | null` + `marketplace?: string`. Add `EmailLanguageSelector`. When `scoringResult` is present and language selected, use `buildI18nEmailBody(scoringResult.category_scores, scoringSummary, getFixedT(lang))` and `buildI18nEmailSubject(...)` to rebuild subject/body. Fall back to original `subject`/`body` props when `scoringResult` absent. (2) Update `ScoringSection` to pass `scoringResult` to `EmailOutput`. (3) Update `SendMailDialog` interface to accept optional `scoreBreakdown` and `calculatorResults` props. Add `EmailLanguageSelector`. When selected language differs from default and i18n data available, use `buildI18nEmailBody` to rebuild the email body portion. Update `sendMailUtils.ts` `buildSubject`/`buildBody` to accept an optional `TFunction` param (falling back to global `i18n.t`). (4) Update `EvaluationDetailPage` to pass `evaluation.score_breakdown` and `evaluation.calculator_results` to `SendMailDialog`. (5) Update tests for all modified components.
  - Verify: `cd frontend && npx vitest run src/components/evaluation/scoring/EmailOutput.test.tsx src/components/evaluations/SendMailDialog.test.tsx --reporter=verbose` passes; full regression `cd frontend && npx vitest run --reporter=verbose 2>&1 | tail -5` shows 0 failures
  - Done when: All 3 email dialogs render `EmailLanguageSelector`; switching language in any dialog updates the email body preview; pre-i18n evaluations fall back gracefully; all existing + new tests pass

## Files Likely Touched

- `frontend/src/locales/id.json`
- `frontend/src/locales/en.json`
- `frontend/src/locales/th.json`
- `frontend/src/lib/languages.ts` (new)
- `frontend/src/components/layout/LanguageToggle.tsx`
- `frontend/src/components/shared/EmailLanguageSelector.tsx` (new)
- `frontend/src/components/shared/EmailLanguageSelector.test.tsx` (new)
- `frontend/src/utils/buildI18nEmailBody.ts` (new)
- `frontend/src/utils/buildI18nEmailBody.test.ts` (new)
- `frontend/src/components/dashboard/SendEmailDialog.tsx`
- `frontend/src/components/dashboard/SendEmailDialog.test.tsx`
- `frontend/src/components/evaluation/scoring/EmailOutput.tsx`
- `frontend/src/components/evaluation/scoring/EmailOutput.test.tsx`
- `frontend/src/components/evaluation/scoring/ScoringSection.tsx`
- `frontend/src/components/evaluations/SendMailDialog.tsx`
- `frontend/src/components/evaluations/SendMailDialog.test.tsx`
- `frontend/src/components/evaluations/sendMailUtils.ts`
- `frontend/src/pages/EvaluationDetailPage.tsx`
- `backend/app/modules/email/router.py`
