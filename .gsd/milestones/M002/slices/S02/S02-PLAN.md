# S02: EvaluationDetailPage renderTranslatable() wiring

**Goal:** All scoring text on EvaluationDetailPage — category names, conclusion, marketing budget, closing message — renders through i18n with language reactivity. Old evaluations without `_i18n` fields show raw Indonesian text.
**Demo:** Switch language toggle to EN/TH → open any evaluation in history → scoring messages, conclusions, closing messages, and marketing budget text render in the selected language. Old evaluations show raw Indonesian text with no errors.

## Must-Haves

- Backend evaluation detail API returns `marketplace` field with dual-layer fallback (SQL COALESCE + Pydantic default)
- Frontend `RowScore` and `CategoryScore` types declare optional `_i18n` fields
- `ScoreBreakdownTable` translates category names via CATEGORY_MAP + t() with raw-string fallback
- New `ScoringConclusionSection` renders conclusion (bullet list), marketing_budget, and closing_message from `calculator_results.scoring_summary` using `renderTranslatable()` with fallback
- Pre-i18n evaluations (missing `scoring_summary` or `_i18n` fields) render gracefully — no errors, no blank fields

## Proof Level

- This slice proves: integration
- Real runtime required: no (test-level proof with component rendering)
- Human/UAT required: yes (visual check — switch language, view evaluation, verify text changes)

## Verification

- Backend evaluation detail tests pass including new marketplace test:
  `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/integration/api/test_evaluation_detail.py -x`
- Frontend EvaluationDetailPage tests pass including new i18n tests:
  `cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx`
- Full frontend regression — zero failures:
  `cd frontend && npx vitest run`
- Diagnostic: evaluations without `scoring_summary` in `calculator_results` render the page without errors (proven by existing tests which lack `scoring_summary` in MOCK_EVALUATION)

## Integration Closure

- Upstream surfaces consumed: `renderTranslatable()` from `utils/renderTranslatable.ts`; `CATEGORY_MAP` from `lib/categoryMap.ts`; `KesimpulanSection` pattern from `components/dashboard/KesimpulanSection.tsx`; `isScoringSummary` type guard pattern
- New wiring introduced in this slice: `ScoringConclusionSection` in EvaluationDetailPage consuming `calculator_results.scoring_summary` via `renderTranslatable()` + `isScoringSummary()` type guard
- What remains before the milestone is truly usable end-to-end: S03 (email language selector & i18n body rebuild), S04 (locale hardcode cleanup)

## Tasks

- [x] **T01: Wire backend marketplace field and frontend type + category translation** `est:45m`
  - Why: S01 code changes were never committed to this worktree branch. Backend evaluation detail must return `marketplace`; frontend types must declare `_i18n` fields; ScoreBreakdownTable must translate category names. All three are prerequisites for the core S02 renderTranslatable() work.
  - Files: `backend/app/db/queries/evaluations.py`, `backend/app/modules/evaluations/schemas.py`, `backend/app/modules/evaluations/service.py`, `backend/tests/integration/api/test_evaluation_detail.py`, `frontend/src/hooks/useScoring.ts`, `frontend/src/pages/EvaluationDetailPage.tsx`, `frontend/src/pages/EvaluationDetailPage.test.tsx`
  - Do: (1) Add `marketplace: str` to `EvaluationDetailRow` TypedDict. (2) Add `COALESCE(e.marketplace, 'ID') AS marketplace` to `get_evaluation_by_id` SQL SELECT. (3) Add `marketplace: str = "ID"` to `EvaluationDetailResponse` Pydantic schema. (4) Add `marketplace=row.get("marketplace", "ID")` to service constructor call in `get_evaluation_detail()`. (5) Add one backend test asserting marketplace appears in API response. (6) Add `_i18n` optional fields to `RowScore` and `CategoryScore` in `useScoring.ts`. (7) Import `CATEGORY_MAP` in `EvaluationDetailPage.tsx`, update `ScoreBreakdownTable` to translate categories via `CATEGORY_MAP.find()` + `t()` with raw fallback. (8) Add frontend tests for category translation and raw fallback.
  - Verify: Backend tests pass (`PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/integration/api/test_evaluation_detail.py -x`); frontend tests pass (`cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx`)
  - Done when: GET /api/evaluations/{id} returns `marketplace` field; `RowScore`/`CategoryScore` declare `_i18n` fields; ScoreBreakdownTable renders translated category names with raw fallback; all tests pass

- [x] **T02: Add ScoringConclusionSection with renderTranslatable() wiring** `est:45m`
  - Why: The core S02 deliverable — EvaluationDetailPage must render conclusion, marketing budget, and closing message through i18n. Currently no UI section exists for `scoring_summary` data on this page. Follows the KesimpulanSection pattern from the dashboard.
  - Files: `frontend/src/pages/EvaluationDetailPage.tsx`, `frontend/src/pages/EvaluationDetailPage.test.tsx`
  - Do: (1) Import `renderTranslatable` and `TranslatableText` from `utils/renderTranslatable.ts`. (2) Import `isRecord` from `lib/typeGuards.ts` (already imported). (3) Add `isScoringSummary()` type guard and `ScoringSummary` interface inline (follow KesimpulanSection pattern). (4) Add `parseBulletPoints()` helper for conclusion fallback. (5) Create `ScoringConclusionSection` component that: extracts `scoring_summary` from `calculator_results`; renders conclusion as bullet list via `conclusion_i18n` array (each item → `t(item.key, item.vars)`) with fallback to `parseBulletPoints(conclusion)`; renders marketing_budget via `renderTranslatable()`; renders closing_message via `renderTranslatable()`. (6) Place `ScoringConclusionSection` in the Calculator Results card, after the discount section — or as a separate card before email output. (7) Handle missing `scoring_summary` gracefully — render nothing (existing evaluations in test mocks don't have it, so existing tests must continue to pass). (8) Add tests: one with `scoring_summary` containing `_i18n` fields proving renderTranslatable renders translation keys; one with `scoring_summary` containing only raw strings (no `_i18n`) proving fallback to raw text; one proving missing `scoring_summary` renders no conclusion section.
  - Verify: `cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx` (all existing + new tests pass); `cd frontend && npx vitest run` (full regression — zero failures)
  - Done when: EvaluationDetailPage renders conclusion/marketing_budget/closing_message via renderTranslatable() with i18n keys; pre-i18n evaluations fall back to raw text; missing scoring_summary shows no section; all frontend tests pass with zero regressions

## Observability / Diagnostics

- **Runtime signal:** `GET /api/v1/evaluations/{id}` response now includes `marketplace` field (string, default `"ID"`). Agents can verify by inspecting any evaluation detail API response JSON.
- **Inspection surface:** Frontend `ScoreBreakdownTable` renders translated category names. Open browser DevTools → inspect category cells → text should match locale file values for mapped categories, or raw backend strings for unmapped ones.
- **Failure visibility:** If `CATEGORY_MAP` lookup fails (no match), the raw category string renders unchanged — visible in the table cell. If `marketplace` SQL COALESCE fails, Pydantic default `"ID"` kicks in — visible in API response JSON.
- **Redaction constraints:** None — no PII or secrets involved in marketplace field or category translation.

## Files Likely Touched

- `backend/app/db/queries/evaluations.py`
- `backend/app/modules/evaluations/schemas.py`
- `backend/app/modules/evaluations/service.py`
- `backend/tests/integration/api/test_evaluation_detail.py`
- `frontend/src/hooks/useScoring.ts`
- `frontend/src/pages/EvaluationDetailPage.tsx`
- `frontend/src/pages/EvaluationDetailPage.test.tsx`
