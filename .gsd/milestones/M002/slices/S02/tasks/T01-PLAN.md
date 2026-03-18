---
estimated_steps: 8
estimated_files: 7
---

# T01: Wire backend marketplace field and frontend type + category translation

**Slice:** S02 — EvaluationDetailPage renderTranslatable() wiring
**Milestone:** M002

## Description

S01 code changes were documented but never committed to this worktree branch (only `.gsd/` docs were committed). This task implements the S01 code: backend evaluation detail must return `marketplace`; frontend `RowScore`/`CategoryScore` types must declare `_i18n` fields; `ScoreBreakdownTable` must translate category names via CATEGORY_MAP. These are prerequisites for T02's renderTranslatable() wiring.

## Steps

1. **Backend — TypedDict**: In `backend/app/db/queries/evaluations.py`, add `marketplace: str` to `EvaluationDetailRow` TypedDict (after `period: str`).

2. **Backend — SQL**: In the same file, in the `get_evaluation_by_id()` function's SQL SELECT statement (around line 257), add `COALESCE(e.marketplace, 'ID') AS marketplace` to the column list. The current columns end with `COALESCE(u.email, 'Pengguna Dihapus') AS evaluator_email`. Add the marketplace column before the FROM clause. Exact current SQL:
   ```sql
   SELECT e.id, e.brand_id, b.brand_name, b.raw_data,
          e.final_score, e.verdict, e.template,
          e.score_breakdown, e.calculator_results, e.manual_inputs,
          e.email_output, e.rule_version, e.created_at,
          COALESCE(e.period, '') AS period,
          COALESCE(u.email, 'Pengguna Dihapus') AS evaluator_email
   ```
   Add after the `evaluator_email` line: `COALESCE(e.marketplace, 'ID') AS marketplace`

3. **Backend — Pydantic schema**: In `backend/app/modules/evaluations/schemas.py`, add `marketplace: str = "ID"` to `EvaluationDetailResponse` class (after `period: str = ""`). The Pydantic default provides the second layer of fallback.

4. **Backend — Service**: In `backend/app/modules/evaluations/service.py`, in the `get_evaluation_detail()` function's `EvaluationDetailResponse(...)` constructor call (around line 256), add `marketplace=row.get("marketplace", "ID")` argument.

5. **Backend — Test**: In `backend/tests/integration/api/test_evaluation_detail.py`, add `"marketplace": "ID"` to the `EVAL_DETAIL_ROW` fixture. Add one test method that asserts the API response JSON contains `"marketplace": "ID"`. Follow the existing test pattern — mock the DB query return, call `GET /api/v1/evaluations/42`, assert `response.json()["marketplace"] == "ID"`.

6. **Frontend — Types**: In `frontend/src/hooks/useScoring.ts`, add optional `_i18n` fields to `RowScore`: `metric_i18n?: TranslatableText`, `value_i18n?: TranslatableText`, `message_i18n?: TranslatableText`, `benchmark_i18n?: TranslatableText`. Add to `CategoryScore`: `category_i18n?: TranslatableText`. The `TranslatableText` type is already imported in this file.

7. **Frontend — ScoreBreakdownTable**: In `frontend/src/pages/EvaluationDetailPage.tsx`:
   - Import `CATEGORY_MAP` from `../lib/categoryMap`
   - In the `ScoreBreakdownTable` component, replace `<TableCell>{String(cat.category)}</TableCell>` with logic that looks up the category: `const mapped = CATEGORY_MAP.find(m => m.backend === String(cat.category))` then renders `mapped ? t(mapped.labelKey) : String(cat.category)`. The component already receives `t` as a prop.

8. **Frontend — Tests**: In `frontend/src/pages/EvaluationDetailPage.test.tsx`:
   - Add a test that uses `MOCK_EVALUATION` with Indonesian backend category names (e.g. `'Kesehatan Operasional Toko'`) in `score_breakdown` and asserts they render as translated via CATEGORY_MAP (the default test locale is Indonesian, so the translated text should be the Indonesian i18n string from locale files).
   - Add a test that uses an unknown category name (e.g. `'Custom Category XYZ'`) and asserts it renders as-is (raw fallback).
   - The default `MOCK_EVALUATION` uses English category names ('Operational', 'Business', 'Promo Tools') which won't match CATEGORY_MAP — these tests should still pass because the raw fallback renders them unchanged.

## Must-Haves

- [ ] `EvaluationDetailRow` TypedDict includes `marketplace: str`
- [ ] `get_evaluation_by_id` SQL returns `COALESCE(e.marketplace, 'ID') AS marketplace`
- [ ] `EvaluationDetailResponse` Pydantic model includes `marketplace: str = "ID"`
- [ ] Service constructor passes `marketplace=row.get("marketplace", "ID")`
- [ ] Backend test asserts `marketplace` field in API response
- [ ] `RowScore` has optional `metric_i18n`, `value_i18n`, `message_i18n`, `benchmark_i18n` fields
- [ ] `CategoryScore` has optional `category_i18n` field
- [ ] `ScoreBreakdownTable` translates categories via CATEGORY_MAP + t() with raw fallback
- [ ] Frontend tests cover category translation and raw fallback
- [ ] All existing tests still pass (zero regressions)

## Verification

- Backend: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/integration/api/test_evaluation_detail.py -x`
- Frontend: `cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx`
- Full regression: `cd frontend && npx vitest run`
- Note: 3 pre-existing failures in `test_ads_keyword.py` are known and unrelated — ignore them.

## Observability Impact

- **New API field:** `marketplace` added to `GET /api/v1/evaluations/{id}` response. Future agents verify by checking `response.json()["marketplace"]` — should always be a non-empty string (default `"ID"`).
- **Frontend translation:** Category names in `ScoreBreakdownTable` now go through `CATEGORY_MAP` + `t()`. Inspect rendered table cells: mapped categories show locale-translated text; unmapped categories show the raw backend string (fallback path).
- **Failure state visibility:** Missing `marketplace` column in DB → SQL `COALESCE` returns `'ID'`. Missing `marketplace` in row dict → service `row.get()` returns `'ID'`. Missing Pydantic field → default `"ID"`. Three-layer fallback ensures the field is never absent from API responses.

## Inputs

- `backend/app/db/queries/evaluations.py` — `EvaluationDetailRow` TypedDict (line 52), `get_evaluation_by_id` SQL (line 257)
- `backend/app/modules/evaluations/schemas.py` — `EvaluationDetailResponse` class (line 270)
- `backend/app/modules/evaluations/service.py` — `get_evaluation_detail()` constructor call (line 256)
- `backend/tests/integration/api/test_evaluation_detail.py` — `EVAL_DETAIL_ROW` fixture, existing test patterns
- `frontend/src/hooks/useScoring.ts` — `RowScore` (line 7), `CategoryScore` (line 17), `TranslatableText` import
- `frontend/src/pages/EvaluationDetailPage.tsx` — `ScoreBreakdownTable` component (line 101)
- `frontend/src/lib/categoryMap.ts` — `CATEGORY_MAP` array with `backend`/`labelKey` pairs
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — `MOCK_EVALUATION`, `renderPage()`, existing test structure

## Expected Output

- `backend/app/db/queries/evaluations.py` — `EvaluationDetailRow` has `marketplace: str`; SQL query includes `COALESCE(e.marketplace, 'ID')`
- `backend/app/modules/evaluations/schemas.py` — `EvaluationDetailResponse` has `marketplace: str = "ID"`
- `backend/app/modules/evaluations/service.py` — constructor passes `marketplace=row.get("marketplace", "ID")`
- `backend/tests/integration/api/test_evaluation_detail.py` — new marketplace test + fixture updated
- `frontend/src/hooks/useScoring.ts` — `RowScore` and `CategoryScore` have `_i18n` optional fields
- `frontend/src/pages/EvaluationDetailPage.tsx` — `ScoreBreakdownTable` uses CATEGORY_MAP for category translation
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — 2+ new tests for category translation and raw fallback
