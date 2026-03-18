---
id: M002
provides:
  - EvaluationDetailPage renders all scoring text (categories, conclusions, marketing budget, closing message) through i18n with language reactivity
  - All 3 email dialogs (SendMailDialog, SendEmailDialog, EmailOutput) have independent email language selector
  - buildI18nEmailBody utility assembles email body from stored i18n data in any supported language
  - Backend evaluation detail API returns marketplace field with triple-layer fallback
  - Frontend RowScore/CategoryScore types explicitly declare _i18n fields
  - All locale files use {{currency}} interpolation — zero hardcoded IDR
  - LanguageCode type centralized in lib/languages.ts as single source of truth
  - docs/adding-a-language.md documents all 7 touch points for adding a new language
key_decisions:
  - D019: renderTranslatable() with stored _i18n keys, falling back to raw Indonesian text when keys are absent
  - D020: Email language independent of UI language via i18n.getFixedT(selectedLang)
  - D021: Email body rebuilt from i18n keys at render time; pre-rendered email_output is fallback only
  - D022: Locale files use {{currency}} variable for all currency references
  - D023: Triple-layer marketplace fallback (SQL COALESCE → service row.get → Pydantic default)
  - D024: ScoringConclusionSection inline in EvaluationDetailPage.tsx matching local component pattern
  - D025: CATEGORY_MAP.find() + t() with raw-string fallback for translating Indonesian backend category names
  - D026: Dedicated emailBody.section.* locale keys for email section headers (distinct from rules.category.*)
  - D027: EmailLanguageSelector conditional rendering based on scoringResult/hasI18nData presence
patterns_established:
  - renderTranslatable() + isScoringSummary() type guard for consuming scoring_summary on detail pages
  - CATEGORY_MAP.find() + t() with raw-string fallback for translating Indonesian backend category names
  - buildI18nEmailBody with SECTION_DEFS declarative config mirroring backend _assemble_email_body
  - Shared LANGUAGES array in lib/languages.ts as single source of truth for supported languages
  - hasI18nData guard for graceful degradation when pre-i18n evaluations lack _i18n fields
  - EmailLanguageSelector reusable dropdown for per-email language selection across all dialog types
observability_surfaces:
  - GET /api/v1/evaluations/{id} response includes marketplace field — absent field indicates SQL or schema wiring broken
  - data-testid="email-language-select" present on all 3 email dialog language selectors
  - grep -c "IDR" frontend/src/locales/*.json → all return 0 confirms R017 holds
  - grep -c "{{currency}}" frontend/src/locales/*.json → all return 6 confirms interpolation in place
  - "Kesimpulan" heading in Calculator Results card — presence confirms scoring_summary rendered
  - npx vitest run src/utils/buildI18nEmailBody.test.ts — 20 tests verify email body assembly correctness
requirement_outcomes:
  - id: R014
    from_status: active
    to_status: validated
    proof: EvaluationDetailPage renders category names via CATEGORY_MAP + t(), conclusion/marketing_budget/closing_message via renderTranslatable() + ScoringConclusionSection. 25 EvaluationDetailPage tests pass (including 5 i18n-specific). Pre-i18n evaluations fall back to raw Indonesian text.
  - id: R015
    from_status: validated
    to_status: validated
    proof: Already validated in S03. All 3 dialogs have EmailLanguageSelector with data-testid="email-language-select". 16 language-selector-specific tests across 3 dialog test suites.
  - id: R016
    from_status: validated
    to_status: validated
    proof: Already validated in S03. buildI18nEmailBody (20 unit tests) mirrors backend _assemble_email_body. Wired into all 3 dialogs.
  - id: R017
    from_status: validated
    to_status: validated
    proof: Already validated in S03, re-verified in S04. grep -c "IDR" returns 0 for all 3 locale files. grep -c "{{currency}}" returns 6 for each.
  - id: R018
    from_status: validated
    to_status: validated
    proof: Already validated in S01. Backend test test_get_evaluation_detail_has_marketplace passes. Triple-layer fallback confirmed.
  - id: R019
    from_status: active
    to_status: validated
    proof: Existing tests use MOCK_EVALUATION without scoring_summary or _i18n fields — all 602 pass with no errors. ScoringConclusionSection returns null when scoring_summary absent. ScoreBreakdownTable falls back to raw category string for unmapped names.
  - id: R020
    from_status: validated
    to_status: validated
    proof: Already validated in S04. docs/adding-a-language.md (267 lines) covers 7 touch points. LanguageCode derives from LANGUAGES array. Zero inline type unions.
  - id: R021
    from_status: active
    to_status: validated
    proof: useScoring.ts declares 8 optional _i18n fields on RowScore and CategoryScore (metric_i18n, value_i18n, message_i18n, benchmark_i18n, category_i18n, conclusion_i18n, marketing_budget_i18n, closing_message_i18n). TypeScript compilation succeeds. 602 frontend tests pass.
  - id: R022
    from_status: active
    to_status: validated
    proof: M002 made zero database schema changes. Only change was adding COALESCE(e.marketplace, 'ID') to the evaluation detail SELECT query — reads an existing column. No migrations, no data modifications.
duration: 130m
verification_result: passed
completed_at: 2026-03-18
---

# M002: Evaluation Results i18n

**Evaluation results on the history detail page and in email output now render in the selected language (ID/EN/TH), with independent email language selection across all 3 dialogs, graceful fallback for pre-i18n evaluations, and a documented path for adding future languages.**

## What Happened

M002 delivered full i18n coverage for evaluation results in 4 slices over ~130 minutes.

**S01 laid the foundation** — the backend evaluation detail API gained a `marketplace` field with triple-layer fallback (SQL COALESCE → service default → Pydantic default), ensuring pre-marketplace evaluations always return `"ID"`. Frontend TypeScript types (`RowScore`, `CategoryScore`) received explicit `_i18n` field declarations. `ScoreBreakdownTable` was wired to translate Indonesian backend category names via `CATEGORY_MAP.find() + t()` with raw-string fallback for unknown categories.

**S02 completed the detail page** — a `ScoringConclusionSection` component (inline in `EvaluationDetailPage.tsx`) renders conclusion as a bullet list, marketing budget, and closing message, all through `renderTranslatable()` with `isScoringSummary()` type guard. When `scoring_summary` is absent (all pre-i18n evaluations), the component returns null silently. This completed the EvaluationDetailPage i18n wiring — switching the language toggle causes all scoring text to re-render in the selected language.

**S03 tackled email output** — three components shipped: `EmailLanguageSelector` (reusable native `<select>` dropdown), `buildI18nEmailBody` (pure function mirroring backend `_assemble_email_body` with SECTION_DEFS declarative config), and `buildI18nEmailSubject`. All 3 email dialogs (`SendMailDialog`, `SendEmailDialog`, `EmailOutput`) gained language selectors. The email body rebuilds from stored i18n data when the user picks a different language, while the UI language stays unchanged. S03 also fixed R017 — all 6 hardcoded `IDR` strings across 3 locale files were replaced with `{{currency}}` interpolation. The backend preview endpoint was extended to accept an optional `?language=` query parameter.

**S04 cleaned up and future-proofed** — `docs/adding-a-language.md` (267 lines) documents all 7 touch points for adding a new language. Three inline `'id' | 'en' | 'th'` type unions were replaced with `LanguageCode` imported from `lib/languages.ts`, making the `LANGUAGES` array the single source of truth.

Cross-slice integration was clean: S01's type declarations and CATEGORY_MAP pattern flowed into S02's renderTranslatable() wiring; S02's proven i18n rendering informed S03's email body assembly; S03's LANGUAGES extraction enabled S04's type centralization. No slice required rework of a previous slice's output.

## Cross-Slice Verification

| Success Criterion | Evidence | Result |
|-------------------|----------|--------|
| Switching language toggle to EN/TH on history detail page shows scoring text in that language | S02: `ScoringConclusionSection` renders conclusion/marketing_budget/closing_message via `renderTranslatable()`; `ScoreBreakdownTable` translates categories via `CATEGORY_MAP + t()`. 25 `EvaluationDetailPage` tests pass including 5 i18n-specific tests proving translation pipeline. | ✅ |
| Email send dialogs across all pages have a language selector defaulting to UI language | S03: `EmailLanguageSelector` integrated into `SendMailDialog`, `SendEmailDialog`, `EmailOutput`. `data-testid="email-language-select"` present in all 3 production components and verified by 16 language-selector-specific tests. | ✅ |
| Email body renders in the chosen email language without changing UI language | S03: `buildI18nEmailBody` (20 unit tests) assembles body from i18n keys using `i18n.getFixedT(selectedLang)`. Wired into all 3 dialogs with verified body updates on language change. Global `i18n.language` is not modified. | ✅ |
| Pre-i18n evaluations display Indonesian text correctly — no errors or blank fields | S01+S02: Existing 22 tests use `MOCK_EVALUATION` without `scoring_summary` or `_i18n` fields — all pass. `ScoringConclusionSection` returns null for missing `scoring_summary`. `ScoreBreakdownTable` falls back to raw category string. S03: `hasI18nData` guard falls back to original Indonesian body for pre-i18n evaluations. | ✅ |
| Adding a 4th language requires only a locale JSON file and config additions | S04: `docs/adding-a-language.md` (267 lines) covers 7 touch points — 3 frontend (locale JSON, i18n.ts import, LANGUAGES array), 3 backend (auth Literal, email regex, STRINGS/CATEGORY_MAP), 1 auto-derived (LanguageCode type). No schema changes, migrations, or new components required. Zero inline type unions remain. | ✅ |

**Definition of Done — all items confirmed:**
- ✅ EvaluationDetailPage renders all scoring text through i18n with language reactivity (S02)
- ✅ All 3 email dialogs have language selector with correct defaults (S03)
- ✅ Email body reconstructs from i18n keys in the selected language (S03)
- ✅ Locale files contain no hardcoded currency codes — `grep -c "IDR"` returns 0 for all 3 files (S03, re-verified S04)
- ✅ Frontend types explicitly declare i18n fields — 8 `_i18n` fields on `RowScore`/`CategoryScore` in `useScoring.ts` (S01)
- ✅ All existing tests pass with zero regressions — 602 frontend passed, 11 backend evaluation detail passed (S04 final run)
- ✅ Documented checklist confirms adding a new language is locale-file-only — `docs/adding-a-language.md` (S04)

## Requirement Changes

- **R014:** active → validated — EvaluationDetailPage renders category names via CATEGORY_MAP + t(), scoring messages via row _i18n fields, conclusion/marketing_budget/closing_message via renderTranslatable() + ScoringConclusionSection. 25 EvaluationDetailPage tests pass including 5 i18n-specific.
- **R015:** validated (no change) — All 3 dialogs have EmailLanguageSelector. 16 language-selector-specific tests.
- **R016:** validated (no change) — buildI18nEmailBody (20 tests) mirrors backend. Wired into all 3 dialogs.
- **R017:** validated (no change) — grep confirms 0 IDR, 6 {{currency}} per file.
- **R018:** validated (no change) — Backend test proves marketplace field returned; triple-layer fallback.
- **R019:** active → validated — 602 tests pass with mocks lacking _i18n/scoring_summary. ScoringConclusionSection returns null for absent data. ScoreBreakdownTable raw-string fallback proven.
- **R020:** validated (no change) — docs/adding-a-language.md covers 7 touch points. LanguageCode centralized.
- **R021:** active → validated — useScoring.ts declares 8 _i18n fields. TypeScript compilation succeeds. 602 tests pass.
- **R022:** active → validated — Zero DB schema changes in M002. Only addition: COALESCE on existing marketplace column in SELECT query.

## Forward Intelligence

### What the next milestone should know
- The i18n pipeline is fully operational for evaluation results: backend generates TranslatableText structs, frontend consumes them via renderTranslatable(). Any new scoring text or evaluation output should follow this pattern.
- `LANGUAGES` array in `frontend/src/lib/languages.ts` is the single source of truth for supported languages. `LanguageCode` type derives from it automatically. Adding a language follows the documented 7-step checklist in `docs/adding-a-language.md`.
- `buildI18nEmailBody` mirrors backend `_assemble_email_body` — these two must stay synchronized manually. No automated cross-validation exists.
- Email language selection is decoupled from UI language via `i18n.getFixedT(selectedLang)` pattern. The dashboard's `SendEmailDialog` passes language to the backend SMTP renderer; the history's `SendMailDialog` assembles the body client-side via `buildI18nEmailBody`.

### What's fragile
- `SECTION_DEFS` in `buildI18nEmailBody.ts` must match backend `_assemble_email_body` in `computations.py:328-440` — section ordering, row ranges, emoji prefixes. If backend changes, frontend email body silently diverges. No automated sync exists.
- `CATEGORY_MAP` is duplicated: frontend `categoryMap.ts` and backend `template.py`. New categories require updating both. Fallback is graceful (raw Indonesian string) but invisible.
- `docs/adding-a-language.md` references approximate line numbers that will drift as code evolves.
- `parseBulletPoints()` splits on newlines and strips `•/-` prefixes — unusual bullet formats from backend would break the split.
- 2 tests in `RulesPage.test.tsx` are intermittently flaky (password confirmation timeout) — pre-existing, unrelated to i18n.

### Authoritative diagnostics
- `npx vitest run` from `frontend/` — 602 tests, 66 files. Fastest full-regression signal.
- `npx vitest run src/utils/buildI18nEmailBody.test.ts` — 20 tests for email body assembly correctness.
- `npx vitest run src/pages/EvaluationDetailPage.test.tsx` — 25 tests for detail page i18n rendering.
- `PYTHONPATH=backend python -m pytest backend/tests/integration/api/test_evaluation_detail.py` — 11 tests for API response shape including marketplace.
- `grep -c "IDR" frontend/src/locales/*.json` — must return 0 for all files (R017).
- `grep -rn "'id' | 'en' | 'th'" frontend/src/ --include='*.ts' --include='*.tsx' | grep -v '.test.'` — must be empty (no inline type unions).

### What assumptions changed
- Plan assumed promo section uses rows 34-41 — actual backend uses PROMO_START_ROW=31 with rows 31-43. S03 implementation follows the real backend.
- Plan didn't anticipate needing `emailBody.section.*` locale keys — backend email headers differ from category display names, requiring separate keys.
- ScoreBreakdownTable already received `t` as a prop, making category translation simpler than planned (no new `useTranslation()` import needed).
- `fields.ts` still has static `unit: 'IDR'` on ~16 field definitions — this is an intentional M001 decision (D014) to keep fields.ts as static config with render-layer override, not a locale hardcode.

## Files Created/Modified

- `backend/app/db/queries/evaluations.py` — Added marketplace to EvaluationDetailRow TypedDict and COALESCE to detail query SQL
- `backend/app/modules/evaluations/schemas.py` — Added marketplace field with default "ID" to EvaluationDetailResponse
- `backend/app/modules/evaluations/service.py` — Added marketplace to response constructor with row.get fallback
- `backend/app/modules/email/router.py` — Added optional language query param to preview endpoint
- `backend/tests/integration/api/test_evaluation_detail.py` — Added marketplace fixture and test_get_evaluation_detail_has_marketplace
- `frontend/src/lib/languages.ts` — New shared LANGUAGES array and LanguageCode type
- `frontend/src/components/shared/EmailLanguageSelector.tsx` — New reusable email language dropdown
- `frontend/src/components/shared/EmailLanguageSelector.test.tsx` — 8 component tests
- `frontend/src/utils/buildI18nEmailBody.ts` — New email body/subject assembly with i18n support
- `frontend/src/utils/buildI18nEmailBody.test.ts` — 20 unit tests
- `frontend/src/hooks/useScoring.ts` — Added _i18n optional fields to RowScore and CategoryScore
- `frontend/src/pages/EvaluationDetailPage.tsx` — Imported CATEGORY_MAP and renderTranslatable; wired ScoreBreakdownTable category translation; added ScoringConclusionSection
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — Added 5 i18n tests (category translation, i18n rendering, raw fallback, missing scoring_summary)
- `frontend/src/components/dashboard/SendEmailDialog.tsx` — Added EmailLanguageSelector, language state, wired to mutation + preview
- `frontend/src/components/dashboard/SendEmailDialog.test.tsx` — Added 4 language selector tests
- `frontend/src/components/evaluation/scoring/EmailOutput.tsx` — Added scoringResult prop, conditional language selector, dynamic i18n body
- `frontend/src/components/evaluation/scoring/EmailOutput.test.tsx` — Added 7 language/dynamic body tests
- `frontend/src/components/evaluation/scoring/ScoringSection.tsx` — Passes scoringResult to EmailOutput
- `frontend/src/components/evaluations/SendMailDialog.tsx` — Added scoreBreakdown/calculatorResults props, language selector, hasI18nData guard
- `frontend/src/components/evaluations/SendMailDialog.test.tsx` — Added 9 language selector and i18n body tests
- `frontend/src/components/evaluations/sendMailUtils.ts` — Added optional TFunction and emailBodyOverride params
- `frontend/src/components/layout/LanguageToggle.tsx` — Imports LANGUAGES from shared lib; uses LanguageCode type
- `frontend/src/services/apiClient.ts` — Replaced inline type unions with LanguageCode import
- `frontend/src/locales/id.json` — 6 IDR→{{currency}} replacements + emailLanguageSelector.label + 10 emailBody.section.* keys
- `frontend/src/locales/en.json` — 6 IDR→{{currency}} replacements + emailLanguageSelector.label + 10 emailBody.section.* keys
- `frontend/src/locales/th.json` — 6 IDR→{{currency}} replacements + emailLanguageSelector.label + 10 emailBody.section.* keys
- `docs/adding-a-language.md` — Complete 7-touch-point checklist for adding a new language (267 lines)
