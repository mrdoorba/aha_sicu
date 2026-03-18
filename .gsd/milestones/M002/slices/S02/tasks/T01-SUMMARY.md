---
id: T01
parent: S02
milestone: M002
provides:
  - Backend evaluation detail API returns marketplace field with triple-layer fallback
  - Frontend RowScore/CategoryScore types declare optional _i18n fields
  - ScoreBreakdownTable translates category names via CATEGORY_MAP + t() with raw fallback
key_files:
  - backend/app/db/queries/evaluations.py
  - backend/app/modules/evaluations/schemas.py
  - backend/app/modules/evaluations/service.py
  - backend/tests/integration/api/test_evaluation_detail.py
  - frontend/src/hooks/useScoring.ts
  - frontend/src/pages/EvaluationDetailPage.tsx
  - frontend/src/pages/EvaluationDetailPage.test.tsx
key_decisions:
  - Triple-layer marketplace fallback: SQL COALESCE → service row.get() → Pydantic default
  - CATEGORY_MAP lookup with raw-string fallback for unmapped categories (no errors for unknown categories)
patterns_established:
  - CATEGORY_MAP.find() + t() pattern for translating backend Indonesian category names in table components
observability_surfaces:
  - GET /api/v1/evaluations/{id} response includes "marketplace" field (always non-empty string, default "ID")
  - ScoreBreakdownTable renders translated category text for mapped categories, raw backend string for unmapped
duration: 15m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T01: Wire backend marketplace field and frontend type + category translation

**Add marketplace field to evaluation detail API with triple-layer fallback; add _i18n optional fields to RowScore/CategoryScore types; translate ScoreBreakdownTable categories via CATEGORY_MAP**

## What Happened

Implemented all 8 steps from the task plan without deviation:

1. **Backend TypedDict**: Added `marketplace: str` to `EvaluationDetailRow` in `evaluations.py`.
2. **Backend SQL**: Added `COALESCE(e.marketplace, 'ID') AS marketplace` to the `get_evaluation_by_id` SELECT query.
3. **Backend Pydantic**: Added `marketplace: str = "ID"` to `EvaluationDetailResponse` schema.
4. **Backend Service**: Added `marketplace=row.get("marketplace", "ID")` to the `EvaluationDetailResponse(...)` constructor call.
5. **Backend Test**: Added `"marketplace": "ID"` to `EVAL_DETAIL_ROW` fixture; added `test_get_evaluation_detail_has_marketplace` test.
6. **Frontend Types**: Added optional `metric_i18n`, `value_i18n`, `message_i18n`, `benchmark_i18n` fields to `RowScore`; added `category_i18n` to `CategoryScore`.
7. **Frontend ScoreBreakdownTable**: Imported `CATEGORY_MAP`; replaced raw `String(cat.category)` render with `CATEGORY_MAP.find()` + `t()` lookup with raw fallback.
8. **Frontend Tests**: Added 2 tests — one for Indonesian backend category name translation via CATEGORY_MAP (verifies `Operasional`, `Bisnis`, `Alat Promo`), one for unknown/English categories rendering as-is.

## Verification

- Backend evaluation detail tests: 11/11 passed (including new marketplace test)
- Frontend EvaluationDetailPage tests: 22/22 passed (including 2 new category translation tests)
- Full frontend regression: 64 test files, 553 tests passed, 0 failures

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `PYTHONPATH=backend python -m pytest backend/tests/integration/api/test_evaluation_detail.py -x -v` | 0 | ✅ pass | 3.0s |
| 2 | `cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx` | 0 | ✅ pass | 3.2s |
| 3 | `cd frontend && npx vitest run` | 0 | ✅ pass | 24.3s |

## Diagnostics

- **API inspection**: `GET /api/v1/evaluations/{id}` → response JSON includes `"marketplace": "ID"` (or actual marketplace value from DB).
- **Category translation**: Inspect `ScoreBreakdownTable` cells — mapped Indonesian category names (e.g. `Kesehatan Operasional Toko`) render as locale-translated text (`Operasional` in id, `Operations` in en); unmapped categories render raw.
- **Failure state**: Missing DB column → SQL COALESCE returns `'ID'`; missing dict key → `row.get()` returns `'ID'`; missing Pydantic field → default `"ID"`. Three layers ensure marketplace is never absent.

## Deviations

None — all 8 steps executed as planned.

## Known Issues

None.

## Files Created/Modified

- `backend/app/db/queries/evaluations.py` — Added `marketplace: str` to `EvaluationDetailRow` TypedDict; added `COALESCE(e.marketplace, 'ID')` to detail query SQL
- `backend/app/modules/evaluations/schemas.py` — Added `marketplace: str = "ID"` to `EvaluationDetailResponse`
- `backend/app/modules/evaluations/service.py` — Added `marketplace=row.get("marketplace", "ID")` to response constructor
- `backend/tests/integration/api/test_evaluation_detail.py` — Added marketplace to fixture; added `test_get_evaluation_detail_has_marketplace`
- `frontend/src/hooks/useScoring.ts` — Added optional `_i18n` fields to `RowScore` and `CategoryScore`
- `frontend/src/pages/EvaluationDetailPage.tsx` — Imported `CATEGORY_MAP`; wired `ScoreBreakdownTable` to translate categories
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — Added 2 tests for category translation and raw fallback
- `.gsd/milestones/M002/slices/S02/S02-PLAN.md` — Added Observability section; marked T01 done
- `.gsd/milestones/M002/slices/S02/tasks/T01-PLAN.md` — Added Observability Impact section
