# S02: EvaluationDetailPage renderTranslatable() wiring — Research

**Date:** 2026-03-17
**Depth:** Targeted

## Summary

EvaluationDetailPage currently renders all scoring text as raw Indonesian strings — it never touches `renderTranslatable()`. The page has four areas where i18n wiring is needed:

1. **ScoreBreakdownTable** — shows category names as raw `String(cat.category)`. S01 planned CATEGORY_MAP translation but the code was never committed to this worktree branch (docs-only commits). Needs the S01 category translation wired.
2. **Scoring summary section** — conclusion, marketing_budget, and closing_message exist in `calculator_results.scoring_summary` but the page has **no UI section** for them. The dashboard's `KesimpulanSection` renders these; EvaluationDetailPage needs an equivalent.
3. **Calculator output sections** — `AdsKeywordSection` and `DiscountSection` render `output_text` (pre-rendered Indonesian string). Need to render from structured `details` with `renderTranslatable()`, following the pattern in `AdsKeywordResults.tsx`.
4. **Score breakdown rows** — `score_breakdown[].rows[]` have `message_i18n`, `metric_i18n`, `value_i18n`, `benchmark_i18n` fields but `ScoreBreakdownTable` doesn't render individual rows at all (only category + score). Expanding to show per-row messages is optional — the dashboard handles that via `DetailedEvaluation` + `CategoryMetricCard`, and the history page is a simpler summary view.

**Critical finding:** S01 code changes were NOT committed to this worktree. The S01 summary describes backend marketplace wiring (`COALESCE(e.marketplace, 'ID')` in SQL, `marketplace` in TypedDict/Pydantic/service) and frontend `_i18n` type additions on `RowScore`/`CategoryScore`, but the git log shows only docs commits. S02 must include these prerequisite changes.

## Recommendation

Build in three tasks:

1. **Backend marketplace wiring** (S01 carryover) — add `marketplace` to the evaluation detail query, TypedDict, and service constructor. Small, testable, unblocks everything.
2. **Frontend type + category translation** (S01 carryover + S02 start) — add `_i18n` fields to `RowScore`/`CategoryScore` in `useScoring.ts`, wire CATEGORY_MAP translation in `ScoreBreakdownTable`.
3. **renderTranslatable() wiring for scoring summary** — add a `ScoringConclusionSection` to EvaluationDetailPage that renders conclusion, marketing_budget, and closing_message from `calculator_results.scoring_summary` using `renderTranslatable()` with fallback. This is the core S02 deliverable.

Skip i18n wiring for calculator output sections (AdsKeyword, Discount, TopSku) — those render pre-computed `output_text` and changing them to use structured `details` is a larger refactor with its own risk surface. The roadmap scope says "scoring messages, conclusions, closing messages, and marketing budget text" — the calculator output sections are distinct from scoring messages.

## Implementation Landscape

### Key Files

- `backend/app/db/queries/evaluations.py` — `EvaluationDetailRow` TypedDict missing `marketplace`; `get_evaluation_by_id` SQL query missing `COALESCE(e.marketplace, 'ID')`
- `backend/app/modules/evaluations/service.py` — `get_evaluation_detail()` at line 256 doesn't pass `marketplace` to `EvaluationDetailResponse` constructor
- `backend/app/modules/evaluations/schemas.py` — `EvaluationDetailResponse` already has `marketplace: str = "ID"` (Pydantic default provides fallback)
- `frontend/src/hooks/useScoring.ts` — `RowScore` interface missing `_i18n` fields; `CategoryScore` missing `category_i18n`; `ScoringResult` already has `conclusion_i18n`, `marketing_budget_i18n`, `closing_message_i18n`
- `frontend/src/hooks/useEvaluationDetail.ts` — `EvaluationDetail` interface has `marketplace?: string` (already present)
- `frontend/src/pages/EvaluationDetailPage.tsx` — `ScoreBreakdownTable` renders raw category names; no scoring summary section exists
- `frontend/src/lib/categoryMap.ts` — `CATEGORY_MAP` maps Indonesian backend names to i18n label keys
- `frontend/src/utils/renderTranslatable.ts` — `renderTranslatable()` function, proven pattern
- `frontend/src/components/dashboard/KesimpulanSection.tsx` — reference implementation for conclusion/marketing/closing rendering
- `frontend/src/components/dashboard/CategoryMetricCard.tsx` — reference for per-row i18n rendering
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — 22 existing tests (455 lines)
- `backend/tests/integration/api/test_evaluation_detail.py` — 312 lines, no marketplace tests

### Data Shape in Stored Evaluations

`calculator_results.scoring_summary` contains:
```json
{
  "conclusion": "string (Indonesian)",
  "conclusion_i18n": [{ "key": "scoring.conclusion.X", "vars": {...} }, ...],
  "marketing_estimation": "string",
  "marketing_budget": "string (Indonesian)",
  "marketing_budget_i18n": { "key": "scoring.marketingBudget", "vars": {...} },
  "closing_message": "string (Indonesian)",
  "closing_message_i18n": { "key": "scoring.closingMessage.X", "vars": {...} }
}
```

`score_breakdown[].rows[]` contains:
```json
{
  "metric": "string", "value": "...", "benchmark": "string", "message": "string", "score": 0,
  "metric_i18n": { "key": "...", "vars": {...} },
  "message_i18n": { "key": "...", "vars": {...} },
  "benchmark_i18n": { "key": "...", "vars": {...} },
  "value_i18n": { "key": "...", "vars": {...} }
}
```

### Build Order

1. **T01: Backend marketplace in evaluation detail** — Add `marketplace: str` to `EvaluationDetailRow`, add `COALESCE(e.marketplace, 'ID') AS marketplace` to SQL SELECT, add `marketplace=row.get("marketplace", "ID")` to service constructor. Add one backend test. This unblocks all frontend work.

2. **T02: Frontend types + ScoreBreakdownTable category translation** — Add `_i18n` optional fields to `RowScore` and `CategoryScore` in `useScoring.ts`. Import `CATEGORY_MAP` in `EvaluationDetailPage.tsx`, wire `CATEGORY_MAP.find()` + `t()` for category name display in `ScoreBreakdownTable` with raw fallback. Add tests.

3. **T03: Scoring summary section with renderTranslatable()** — Create a `ScoringConclusionSection` inline component (or section) in `EvaluationDetailPage.tsx` that extracts `scoring_summary` from `calculator_results`, renders conclusion via `conclusion_i18n` array (fallback: parse bullet points from `conclusion`), marketing_budget via `renderTranslatable()`, closing_message via `renderTranslatable()`. Pattern: follow `KesimpulanSection.tsx` exactly. Add tests for i18n rendering and raw fallback.

### Verification Approach

- **Backend:** Run existing evaluation detail tests + new marketplace test:
  ```bash
  PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/integration/api/test_evaluation_detail.py -x
  ```

- **Frontend:** Run EvaluationDetailPage tests:
  ```bash
  cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx
  ```

- **Full regression:** Run all frontend tests to verify no breakage:
  ```bash
  cd frontend && npx vitest run
  ```

## Constraints

- S01 code was never committed to this worktree (only docs). T01 and T02 must implement the S01 code changes as prerequisites.
- `EvaluationDetail` interface in `useEvaluationDetail.ts` types `score_breakdown` as `Array<Record<string, unknown>>` — no strong typing on rows. Must use runtime checks (`isRecord`, `Array.isArray`) when accessing `rows` and `_i18n` fields.
- `calculator_results` is `Record<string, unknown>` — the `scoring_summary` access needs a type guard or careful casting (follow `KesimpulanSection`'s `isScoringSummary()` pattern).

## Common Pitfalls

- **ScoreBreakdownTable already receives `t` as a prop** — don't add a new `useTranslation()` call; use the existing `t` prop.
- **Mock data in tests must include `scoring_summary` in `calculator_results`** — the existing `MOCK_EVALUATION.calculator_results` doesn't have it. Must add it for new tests.
- **`conclusion_i18n` is an array of TranslatableText** — unlike `marketing_budget_i18n` (single object), conclusion is rendered as a bullet list where each item is a separate translatable. See `KesimpulanSection.tsx` lines 58-77.
- **Pre-i18n fallback** — old evaluations won't have `scoring_summary` in `calculator_results` at all (it was added to the save flow later). The new section must handle missing `scoring_summary` gracefully — show nothing or show raw `email_output`.
