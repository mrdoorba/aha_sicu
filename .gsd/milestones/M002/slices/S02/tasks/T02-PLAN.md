---
estimated_steps: 7
estimated_files: 2
---

# T02: Add ScoringConclusionSection with renderTranslatable() wiring

**Slice:** S02 — EvaluationDetailPage renderTranslatable() wiring
**Milestone:** M002

## Description

The core S02 deliverable. EvaluationDetailPage currently has no UI for `calculator_results.scoring_summary` data — conclusion, marketing budget, and closing message are stored but never displayed. This task adds a `ScoringConclusionSection` component that renders all three fields through `renderTranslatable()`, following the proven `KesimpulanSection` pattern from the dashboard. Pre-i18n evaluations (missing `scoring_summary` or `_i18n` fields) fall back to raw text or render nothing.

**Reference implementation:** `frontend/src/components/dashboard/KesimpulanSection.tsx` — read this file before implementing. It demonstrates the exact pattern for `isScoringSummary()` type guard, `conclusion_i18n` array rendering, `renderTranslatable()` for marketing_budget and closing_message, and `parseBulletPoints()` fallback.

## Steps

1. **Add imports**: In `frontend/src/pages/EvaluationDetailPage.tsx`, add:
   - `import { renderTranslatable, type TranslatableText } from '../utils/renderTranslatable';`
   - `isRecord` is already imported from `'../lib/typeGuards'`

2. **Add ScoringSummary interface and type guard**: Add inline in EvaluationDetailPage.tsx (near the top, after imports):
   ```typescript
   interface ScoringSummary {
     conclusion?: string;
     conclusion_i18n?: TranslatableText[];
     marketing_estimation?: string;
     marketing_budget?: string;
     marketing_budget_i18n?: TranslatableText;
     closing_message?: string;
     closing_message_i18n?: TranslatableText;
   }

   function isScoringSummary(value: unknown): value is ScoringSummary {
     if (!isRecord(value)) return false;
     const hasContent =
       typeof value.conclusion === 'string' ||
       Array.isArray(value.conclusion_i18n) ||
       typeof value.marketing_budget === 'string' ||
       typeof value.closing_message === 'string';
     return hasContent;
   }

   function parseBulletPoints(text: string): string[] {
     return text
       .split('\n')
       .map((line) => line.replace(/^[-•]\s*/, '').trim())
       .filter(Boolean);
   }
   ```

3. **Create ScoringConclusionSection component**: Add a new component function in EvaluationDetailPage.tsx:
   ```typescript
   function ScoringConclusionSection({
     calculatorResults,
     t,
   }: {
     calculatorResults: Record<string, unknown>;
     t: (key: string, vars?: Record<string, string>) => string;
   }) {
     const summary = isScoringSummary(calculatorResults.scoring_summary)
       ? calculatorResults.scoring_summary
       : undefined;

     if (!summary) return null;

     return (
       <div className="space-y-4">
         <h3 className="text-base font-semibold">{t('presentation.section.kesimpulan')}</h3>

         {/* Conclusion bullet list */}
         {summary.conclusion_i18n ? (
           <ul className="list-disc pl-5 space-y-1">
             {summary.conclusion_i18n.map((item, i) => (
               <li key={i} className="text-sm">{t(item.key, item.vars)}</li>
             ))}
           </ul>
         ) : summary.conclusion ? (
           <ul className="list-disc pl-5 space-y-1">
             {parseBulletPoints(summary.conclusion).map((point, i) => (
               <li key={i} className="text-sm">{point}</li>
             ))}
           </ul>
         ) : null}

         {/* Marketing budget */}
         {(summary.marketing_budget || summary.marketing_budget_i18n) && (
           <div className="rounded-lg border bg-muted/30 p-4">
             <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
               {t('presentation.kesimpulan.marketingBudget')}
             </p>
             <p className="text-sm font-bold text-primary">
               {renderTranslatable(summary.marketing_budget || '', summary.marketing_budget_i18n, t)}
             </p>
           </div>
         )}

         {/* Closing message */}
         {(summary.closing_message || summary.closing_message_i18n) && (
           <div className="rounded-lg border-l-4 border-primary/30 bg-primary/5 p-4">
             <p className="text-sm whitespace-pre-line">
               {renderTranslatable(summary.closing_message || '', summary.closing_message_i18n, t)}
             </p>
           </div>
         )}
       </div>
     );
   }
   ```

4. **Place ScoringConclusionSection in the page**: In the `EvaluationDetailPage` component's JSX, add `ScoringConclusionSection` as a new section inside the Calculator Results card, after the discount section `<div>` but before the closing `</CardContent>`. Pass `calculatorResults={evaluation.calculator_results}` and `t={t}`. Alternatively, place it as a separate `<Card>` between Calculator Results and Manual Inputs — use whichever reads better in the flow.

5. **Handle graceful fallback**: The component already returns `null` when `scoring_summary` is missing. Existing tests use `MOCK_EVALUATION.calculator_results` which does NOT contain `scoring_summary`, so existing tests will pass unchanged — the section simply won't render.

6. **Add test: i18n rendering with scoring_summary**: In `EvaluationDetailPage.test.tsx`, add a test that provides `MOCK_EVALUATION` with `scoring_summary` containing:
   ```typescript
   scoring_summary: {
     conclusion: 'Toko Anda memiliki performa yang baik',
     conclusion_i18n: [
       { key: 'scoring.conclusion.good', vars: { score: '78.5' } },
       { key: 'scoring.conclusion.improvement', vars: { area: 'ads' } },
     ],
     marketing_budget: 'Rp 5,000,000',
     marketing_budget_i18n: { key: 'scoring.marketingBudget', vars: { amount: '5,000,000', currency: 'IDR' } },
     closing_message: 'Terima kasih atas kerjasamanya',
     closing_message_i18n: { key: 'scoring.closingMessage.standard', vars: { brand: 'Nike' } },
   }
   ```
   Assert that the conclusion items render (check for the translated text from i18n keys — since tests use the default Indonesian locale, assert the key interpolation output), marketing budget section renders, and closing message section renders. Use `screen.getByText()` or `screen.queryByText()` to verify.

   **Important:** The `t()` function in tests returns the key with vars interpolated (or just the key if the locale file doesn't have it). Check what the test i18n setup does — likely returns the key itself. Assert accordingly.

7. **Add test: raw fallback without i18n fields**: Add a test with `scoring_summary` containing only raw strings (no `_i18n` fields):
   ```typescript
   scoring_summary: {
     conclusion: '- Toko bagus\n- Perlu perbaikan iklan',
     marketing_budget: 'Rp 5,000,000',
     closing_message: 'Terima kasih',
   }
   ```
   Assert the raw conclusion text is parsed into bullet points and displayed, marketing budget shows raw text, and closing message shows raw text.

## Must-Haves

- [ ] `ScoringConclusionSection` component renders conclusion, marketing_budget, closing_message from `scoring_summary`
- [ ] Conclusion renders as bullet list via `conclusion_i18n` array when present
- [ ] Conclusion falls back to `parseBulletPoints(conclusion)` when `_i18n` is absent
- [ ] Marketing budget uses `renderTranslatable()` with fallback
- [ ] Closing message uses `renderTranslatable()` with fallback
- [ ] Missing `scoring_summary` renders nothing (no errors)
- [ ] All existing tests pass unchanged (zero regressions)
- [ ] New tests cover i18n rendering and raw fallback paths

## Verification

- `cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx` — all tests pass (existing + new)
- `cd frontend && npx vitest run` — full frontend regression, zero failures
- Diagnostic: render page with MOCK_EVALUATION lacking `scoring_summary` → no conclusion section appears, no errors

## Inputs

- `frontend/src/pages/EvaluationDetailPage.tsx` — T01 should have already wired CATEGORY_MAP and imports for `categoryMap.ts`. The page uses `evaluation.calculator_results` which is `Record<string, unknown>`.
- `frontend/src/utils/renderTranslatable.ts` — `renderTranslatable(fallbackText, i18n, t)` function signature. Also exports `TranslatableText` type.
- `frontend/src/components/dashboard/KesimpulanSection.tsx` — **Reference implementation.** Read this file for the exact patterns: `isScoringSummary()`, `parseBulletPoints()`, `conclusion_i18n` array rendering, `renderTranslatable()` usage. Follow its approach closely.
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — existing `MOCK_EVALUATION`, `renderPage()`, test structure. Existing `calculator_results` does NOT include `scoring_summary`.
- S01 summary: `_i18n` fields on types are declared but `scoring_summary` consumption is this task's job.

## Expected Output

- `frontend/src/pages/EvaluationDetailPage.tsx` — New `ScoringConclusionSection` component + `isScoringSummary()` type guard + `parseBulletPoints()` helper. Component placed in the page layout rendering scoring summary data.
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — 2-3 new tests covering i18n rendering, raw fallback, and missing scoring_summary graceful handling.

## Observability Impact

- **Inspection surface:** `ScoringConclusionSection` renders inside the Calculator Results card. When `scoring_summary` is present in `evaluation.calculator_results`, the "Kesimpulan" heading, bullet-list conclusion, marketing budget box, and closing message box appear in the DOM. When absent, nothing renders — verifiable via `queryByText('Kesimpulan')` returning null.
- **i18n signal:** Conclusion items render via `t(item.key, item.vars)` — switching locale changes their text. Marketing budget and closing message render via `renderTranslatable()` — i18n-equipped evaluations show translated text, legacy evaluations show raw Indonesian strings.
- **Failure visibility:** If `scoring_summary` is not a valid object (missing, null, wrong shape), `isScoringSummary()` returns false and the component returns null silently — no errors in console. If `conclusion_i18n` array items have keys not in locale files, `t()` returns the raw key string as fallback.
