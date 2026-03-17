---
estimated_steps: 4
estimated_files: 3
---

# T01: Add marketplace to evaluation detail API response

**Slice:** S01 — EvaluationDetailPage i18n rendering
**Milestone:** M002

## Description

The `evaluations` table already has a `marketplace` column (added in M001 migration 026), but the evaluation detail query doesn't SELECT it. The frontend `EvaluationDetail` type already declares `marketplace?: string` — it just needs the backend to populate it. This task adds `marketplace` to three backend layers: SQL query, TypedDict, and response schema. Satisfies R018.

## Steps

1. Open `backend/app/db/queries/evaluations.py`. Find the `EvaluationDetailRow` TypedDict (near line 52). Add `marketplace: str` field.
2. In the same file, find the `get_evaluation_by_id` function's SQL query (near line 257). Add `e.marketplace` to the SELECT column list.
3. Open `backend/app/modules/evaluations/schemas.py`. Find `EvaluationDetailResponse` (near line 186). Add `marketplace: str = "ID"` field (default "ID" for pre-marketplace evaluations).
4. Open `backend/app/modules/evaluations/service.py`. Find `get_evaluation_detail` (near line 258). Where the `EvaluationDetailResponse` is constructed from `row`, ensure `marketplace` is passed — verify `row.get("marketplace", "ID")` or equivalent. If the constructor uses `**row` spread, the field may flow automatically from the TypedDict — confirm by checking the construction pattern.

## Must-Haves

- [ ] `EvaluationDetailRow` TypedDict includes `marketplace: str`
- [ ] SQL query in `get_evaluation_by_id` selects `e.marketplace`
- [ ] `EvaluationDetailResponse` schema includes `marketplace: str = "ID"`
- [ ] Default value "ID" ensures pre-marketplace evaluations don't break

## Verification

- Run: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002 && PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "from app.db.queries.evaluations import EvaluationDetailRow; print('marketplace' in EvaluationDetailRow.__annotations__)"`
  Expected: `True`
- Run: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002 && PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "from app.modules.evaluations.schemas import EvaluationDetailResponse; print(EvaluationDetailResponse.model_fields['marketplace'].default)"`
  Expected: `ID`
- Run existing backend tests to confirm no regressions: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002 && PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/ -x -k "evaluation" --no-header -q`

## Inputs

- `backend/app/db/queries/evaluations.py` — contains `EvaluationDetailRow` TypedDict and `get_evaluation_by_id` SQL query
- `backend/app/modules/evaluations/schemas.py` — contains `EvaluationDetailResponse` Pydantic model
- `backend/app/modules/evaluations/service.py` — contains `get_evaluation_detail` that constructs the response from the query row
- The `evaluations` table already has a `marketplace` column (added in M001 migration 026) — no migration needed

## Expected Output

- `backend/app/db/queries/evaluations.py` — `EvaluationDetailRow` has `marketplace: str` field; SQL query selects `e.marketplace`
- `backend/app/modules/evaluations/schemas.py` — `EvaluationDetailResponse` has `marketplace: str = "ID"` field
- `backend/app/modules/evaluations/service.py` — marketplace flows from query row to response (may need explicit wiring or may flow via spread)
