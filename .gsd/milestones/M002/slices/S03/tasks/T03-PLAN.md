---
estimated_steps: 7
estimated_files: 7
---

# T03: Wire EmailOutput and SendMailDialog with language selector + i18n body rebuild

**Slice:** S03 — Email language selector & i18n body rebuild
**Milestone:** M002

## Description

This task wires the language selector and i18n email body assembly into the remaining two email dialogs: `EmailOutput` (evaluation scoring page) and `SendMailDialog` (history detail page). Both need interface changes to receive the structured scoring data needed by `buildI18nEmailBody()`, and their parent components must be updated to pass the data through.

**Relevant installed skill:** `test` — for updating existing tests.

## Steps

1. **Update `EmailOutput` component interface** — In `frontend/src/components/evaluation/scoring/EmailOutput.tsx`:
   - Add optional props: `scoringResult?: ScoringResult | null` (the full scoring result from the evaluation page)
   - Import `EmailLanguageSelector` from `../../shared/EmailLanguageSelector`
   - Import `buildI18nEmailBody`, `buildI18nEmailSubject`, `ScoringConclusionData` from `../../../utils/buildI18nEmailBody`
   - Import `i18n` from `../../../i18n` (for `i18n.getFixedT`)
   - Add state: `const [emailLanguage, setEmailLanguage] = useState(i18n.language)`
   - When `scoringResult` is present, derive `scoringSummary` from the result's fields:
     ```ts
     const scoringSummary: ScoringConclusionData | null = scoringResult ? {
       conclusion: scoringResult.conclusion,
       conclusion_i18n: scoringResult.conclusion_i18n,
       marketing_budget: scoringResult.marketing_budget,
       marketing_budget_i18n: scoringResult.marketing_budget_i18n,
       closing_message: scoringResult.closing_message,
       closing_message_i18n: scoringResult.closing_message_i18n,
       marketing_estimation: scoringResult.marketing_estimation,
     } : null;
     ```
   - Use `useMemo` to compute displayed body/subject:
     - If `scoringResult` present: `const fixedT = i18n.getFixedT(emailLanguage)` → `buildI18nEmailBody(scoringResult.category_scores, scoringSummary, fixedT)` for body, `buildI18nEmailSubject(brandName, period, fixedT)` for subject (though subject isn't used by EmailOutput currently — only body and the original subject prop)
     - If `scoringResult` absent: fall back to original `subject`/`body` props
   - Render `EmailLanguageSelector` next to the copy button in the header row (only when `scoringResult` is present — without it, language switching has no effect)
   - The copy button should copy the dynamically-rendered text, not the original props

2. **Update `ScoringSection` to pass `scoringResult` to `EmailOutput`** — In `frontend/src/components/evaluation/scoring/ScoringSection.tsx`:
   - Change the `<EmailOutput subject={...} body={...} />` call to also pass `scoringResult={scoringResult}`
   - The `scoringResult` is already available in `ScoringSection`'s props/state

3. **Update `sendMailUtils.ts` to accept optional `TFunction`** — In `frontend/src/components/evaluations/sendMailUtils.ts`:
   - Change `buildSubject(brandName, period)` signature to `buildSubject(brandName: string, period: string, t?: TFunction)` — use `t ?? i18n.t` for the translation call
   - Change `buildBody(...)` signature to add optional `t?: TFunction` and optional `emailBodyOverride?: string` params. When `emailBodyOverride` is provided, use it instead of the `emailOutput` parameter for the body content. Use `t ?? i18n.t` for the salutation/intro translation calls.

4. **Update `SendMailDialog` component** — In `frontend/src/components/evaluations/SendMailDialog.tsx`:
   - Add optional props: `scoreBreakdown?: Array<Record<string, unknown>>`, `calculatorResults?: Record<string, unknown>`, `marketplace?: string`
   - Import `EmailLanguageSelector`, `buildI18nEmailBody`, `ScoringConclusionData` from appropriate paths
   - Import `i18n` from `../../i18n`
   - Import `CategoryScore` from `../../hooks/useScoring`
   - Add state: `const [emailLanguage, setEmailLanguage] = useState<string>(i18n.language)`
   - Add `useMemo` to build the i18n email body when `scoreBreakdown` is provided:
     - Cast `scoreBreakdown` to `CategoryScore[]` (the data shape is the same, it's stored as `Record<string, unknown>[]` in `EvaluationDetail` for flexibility)
     - Extract `scoringSummary` from `calculatorResults.scoring_summary` if it exists (use `isScoringSummary()` type guard pattern from EvaluationDetailPage, or a simpler check)
     - `const fixedT = i18n.getFixedT(emailLanguage)`
     - `const i18nBody = buildI18nEmailBody(castScores, scoringSummary, fixedT)`
   - Pass the `i18nBody` to `buildBody()` via the new `emailBodyOverride` param when available; fall back to the original `emailOutput` prop when `scoreBreakdown` is not provided or has no `_i18n` data
   - Similarly use `buildSubject(brandName, period, fixedT)` for the translated subject
   - Render `EmailLanguageSelector` in the dialog (between the PIC email field and the subject preview)
   - Reset `emailLanguage` to `i18n.language` in `handleOpenChange` when dialog closes

5. **Update `EvaluationDetailPage` to pass data to `SendMailDialog`** — In `frontend/src/pages/EvaluationDetailPage.tsx`:
   - Find the `<SendMailDialog>` usage (around line 722-730)
   - Add props: `scoreBreakdown={evaluation.score_breakdown}`, `calculatorResults={evaluation.calculator_results}`, `marketplace={evaluation.marketplace}`

6. **Update `EmailOutput.test.tsx`** — Add tests:
   - When `scoringResult` is provided, language selector renders
   - When `scoringResult` is absent, language selector does NOT render (graceful degradation)
   - Changing language updates the displayed body text (use a mock scoringResult with `_i18n` fields)
   - Copy button copies the dynamically-rendered text

7. **Update `SendMailDialog.test.tsx`** — Add tests:
   - Language selector renders in the dialog
   - When `scoreBreakdown` with `_i18n` fields is provided and language changed, body updates
   - When `scoreBreakdown` is not provided (old evaluations), dialog works exactly as before (no regression)
   - Subject updates when language changes and `scoreBreakdown` is available

## Must-Haves

- [ ] `EmailOutput` renders language selector when `scoringResult` is present
- [ ] `EmailOutput` falls back to original `subject`/`body` props when `scoringResult` is absent
- [ ] `ScoringSection` passes `scoringResult` to `EmailOutput`
- [ ] `SendMailDialog` renders language selector
- [ ] `SendMailDialog` rebuilds email body from `scoreBreakdown` i18n data when language changes
- [ ] `SendMailDialog` falls back to original `emailOutput` when `scoreBreakdown` is absent
- [ ] `EvaluationDetailPage` passes `score_breakdown` and `calculator_results` to `SendMailDialog`
- [ ] `sendMailUtils.ts` accepts optional `TFunction` for language-aware rendering
- [ ] All existing tests pass unchanged or are updated to accommodate new optional props
- [ ] Full test suite passes with 0 regressions

## Verification

- `cd frontend && npx vitest run src/components/evaluation/scoring/EmailOutput.test.tsx --reporter=verbose` — existing + new tests pass
- `cd frontend && npx vitest run src/components/evaluations/SendMailDialog.test.tsx --reporter=verbose` — existing + new tests pass
- `cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx --reporter=verbose` — existing tests pass (no regression from new props)
- `cd frontend && npx vitest run --reporter=verbose 2>&1 | tail -5` — full regression: 0 failures

## Inputs

- T01 output: `EmailLanguageSelector` component, `LANGUAGES` constant, locale files with `{{currency}}`
- T02 output: `buildI18nEmailBody()`, `buildI18nEmailSubject()`, `ScoringConclusionData` type in `frontend/src/utils/buildI18nEmailBody.ts`; `SendEmailDialog` already wired as reference implementation
- `frontend/src/utils/renderTranslatable.ts` — `TranslatableText` type
- `frontend/src/hooks/useScoring.ts` — `ScoringResult`, `CategoryScore` types
- `frontend/src/hooks/useEvaluationDetail.ts` — `EvaluationDetail` type with `score_breakdown: Array<Record<string, unknown>>`, `calculator_results: Record<string, unknown>`
- `frontend/src/pages/EvaluationDetailPage.tsx` — contains `isScoringSummary()` type guard and `ScoringConclusionSection` inline component as reference patterns
- `frontend/src/i18n.ts` — `i18n.getFixedT(lang)` method

## Observability Impact

- **EmailOutput language selector:** Visible via `data-testid="email-language-select"` inside the scoring card when `scoringResult` is present. Changing the value causes the `<pre>` body preview to re-render in the selected language. If missing, `scoringResult` is null or undefined — check that `ScoringSection` passes it through.
- **SendMailDialog language selector:** Always rendered in the dialog. The `data-testid="mail-body"` preview updates when language changes and `scoreBreakdown` with `_i18n` fields is provided. If body doesn't update on language change, check `hasI18nData` computation — it requires `message_i18n` on at least one row.
- **sendMailUtils TFunction:** When a `TFunction` is passed, `buildSubject`/`buildBody` use it instead of the global `i18n.t`. This is transparent — no runtime signal, only different translated output. Verify by comparing subject/body text in different languages.
- **Failure visibility:** If `buildI18nEmailBody` throws, the dialog will error-boundary. Missing `_i18n` fields cause silent fallback to the original Indonesian body — functionally correct but not translated. Inspect the `scoreBreakdown` data shape in DevTools if translation doesn't switch.

## Expected Output

- `frontend/src/components/evaluation/scoring/EmailOutput.tsx` — modified with language selector + dynamic body
- `frontend/src/components/evaluation/scoring/EmailOutput.test.tsx` — updated with new tests
- `frontend/src/components/evaluation/scoring/ScoringSection.tsx` — modified to pass scoringResult to EmailOutput
- `frontend/src/components/evaluations/SendMailDialog.tsx` — modified with language selector + dynamic body
- `frontend/src/components/evaluations/SendMailDialog.test.tsx` — updated with new tests
- `frontend/src/components/evaluations/sendMailUtils.ts` — modified with optional TFunction + emailBodyOverride params
- `frontend/src/pages/EvaluationDetailPage.tsx` — modified to pass score_breakdown and calculator_results to SendMailDialog
