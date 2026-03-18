---
id: T03
parent: S03
milestone: M002
provides:
  - EmailOutput wired with language selector and dynamic i18n body rebuild from ScoringResult
  - SendMailDialog (history page) wired with language selector and i18n body from score_breakdown
  - sendMailUtils accepts optional TFunction and emailBodyOverride for language-aware rendering
  - EvaluationDetailPage passes score_breakdown and calculator_results to SendMailDialog
  - All 3 email dialogs now have language selectors completing the S03 slice goal
key_files:
  - frontend/src/components/evaluation/scoring/EmailOutput.tsx
  - frontend/src/components/evaluations/SendMailDialog.tsx
  - frontend/src/components/evaluations/sendMailUtils.ts
  - frontend/src/components/evaluation/scoring/ScoringSection.tsx
  - frontend/src/pages/EvaluationDetailPage.tsx
key_decisions:
  - EmailOutput conditionally renders language selector only when scoringResult is present — avoids confusing UI for pre-i18n data where language switching has no effect
  - SendMailDialog checks hasI18nData (any row with message_i18n) before activating i18n path — graceful fallback for old evaluations
  - Used isScoringSummary type guard pattern from EvaluationDetailPage for consistent scoring_summary extraction in SendMailDialog
patterns_established:
  - Optional TFunction parameter on sendMailUtils buildSubject/buildBody — defaults to global i18n.t, overridden by fixedT for language-specific rendering
  - emailBodyOverride param on buildBody — when i18n body is available, it replaces the raw emailOutput while keeping the salutation/intro wrapper
  - hasI18nData guard pattern — checks scoreBreakdown rows for message_i18n presence before enabling language-aware rendering
observability_surfaces:
  - EmailOutput language selector visible via data-testid="email-language-select" inside scoring card when scoringResult is present
  - SendMailDialog language selector always rendered; mail-body preview updates on language change when i18n data is available
  - Missing _i18n fields cause silent fallback to Indonesian body (correct behavior, no error)
duration: 25m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T03: Wire EmailOutput and SendMailDialog with language selector + i18n body rebuild

**Wire language selector and i18n email body rebuild into EmailOutput (scoring page) and SendMailDialog (history page), completing the S03 slice with all 3 email dialogs supporting per-email language selection.**

## What Happened

Wired the remaining two email dialogs with language selector and dynamic i18n body assembly, completing all 7 steps from the task plan:

1. **EmailOutput** — Added optional `scoringResult` prop, `EmailLanguageSelector` (conditionally rendered when scoringResult present), and `useMemo`-based body recomputation via `buildI18nEmailBody`. Copy button copies the dynamically-rendered text, not the original props. Falls back to original `subject`/`body` when scoringResult is absent.

2. **ScoringSection** — Added `scoringResult={scoringResult}` prop pass-through to EmailOutput.

3. **sendMailUtils** — Extended `buildSubject` and `buildBody` signatures with optional `TFunction` and `emailBodyOverride` parameters. Uses `t ?? i18n.t` pattern for seamless fallback.

4. **SendMailDialog** — Added `scoreBreakdown` and `calculatorResults` optional props, `EmailLanguageSelector`, `hasI18nData` guard for graceful degradation, `isScoringSummary` type guard, and `useMemo`-based i18n body computation. Resets language on dialog close.

5. **EvaluationDetailPage** — Passed `scoreBreakdown={evaluation.score_breakdown}` and `calculatorResults={evaluation.calculator_results}` to SendMailDialog.

6. **EmailOutput tests** — 7 new tests covering language selector presence/absence, dynamic body rendering, copy behavior, and language change.

7. **SendMailDialog tests** — 7 new tests covering language selector, i18n body override, no-regression for old evaluations, subject updates, TFunction usage, and emailBodyOverride.

## Verification

- EmailOutput: 11/11 tests pass (4 existing + 7 new)
- SendMailDialog: 21/21 tests pass (12 existing + 9 new)
- EvaluationDetailPage: 25/25 tests pass (no regressions)
- Full regression: 602 passed, 1 skipped, 0 failures
- All slice-level verification checks pass

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `cd frontend && npx vitest run src/components/evaluation/scoring/EmailOutput.test.tsx --reporter=verbose` | 0 | ✅ pass | 1.14s |
| 2 | `cd frontend && npx vitest run src/components/evaluations/SendMailDialog.test.tsx --reporter=verbose` | 0 | ✅ pass | 1.68s |
| 3 | `cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx --reporter=verbose` | 0 | ✅ pass | 2.17s |
| 4 | `cd frontend && npx vitest run --reporter=verbose 2>&1 \| tail -5` | 0 | ✅ pass | 29.51s |
| 5 | `cd frontend && npx vitest run src/utils/buildI18nEmailBody.test.ts --reporter=verbose` | 0 | ✅ pass | 0.69s |
| 6 | `cd frontend && npx vitest run src/components/shared/EmailLanguageSelector.test.tsx --reporter=verbose` | 0 | ✅ pass | 0.89s |
| 7 | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx --reporter=verbose` | 0 | ✅ pass | 1.59s |

## Diagnostics

- **EmailOutput language selector:** Visible via `data-testid="email-language-select"` inside the scoring card when `scoringResult` is present. If missing, the parent `ScoringSection` may not be passing `scoringResult`.
- **SendMailDialog language selector:** Always rendered. Body preview at `data-testid="mail-body"` updates on language change only when `hasI18nData` is true (requires `message_i18n` on at least one row in `scoreBreakdown`).
- **Fallback behavior:** Pre-i18n evaluations (no `_i18n` fields in score_breakdown) display the original Indonesian body — language selector renders but has no effect. This is correct behavior.
- **sendMailUtils:** `buildSubject`/`buildBody` accept optional `TFunction`. When absent, falls back to global `i18n.t`. No runtime signal — verify by comparing output text.

## Deviations

None — all 7 steps executed as planned.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/components/evaluation/scoring/EmailOutput.tsx` — Added scoringResult prop, language selector, dynamic i18n body via useMemo
- `frontend/src/components/evaluation/scoring/EmailOutput.test.tsx` — 7 new tests for language selector and dynamic body
- `frontend/src/components/evaluation/scoring/ScoringSection.tsx` — Pass scoringResult to EmailOutput
- `frontend/src/components/evaluations/SendMailDialog.tsx` — Added scoreBreakdown/calculatorResults props, language selector, hasI18nData guard, i18n body override
- `frontend/src/components/evaluations/SendMailDialog.test.tsx` — 9 new tests for language selector, i18n body, and TFunction/emailBodyOverride
- `frontend/src/components/evaluations/sendMailUtils.ts` — Added optional TFunction and emailBodyOverride params to buildSubject/buildBody
- `frontend/src/pages/EvaluationDetailPage.tsx` — Pass score_breakdown and calculator_results to SendMailDialog
