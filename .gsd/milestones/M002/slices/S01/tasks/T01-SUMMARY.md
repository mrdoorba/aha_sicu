---
id: T01
parent: S01
milestone: M002
provides:
  - marketplace field in evaluation detail API response (R018)
key_files:
  - backend/app/db/queries/evaluations.py
  - backend/app/modules/evaluations/schemas.py
  - backend/app/modules/evaluations/service.py
key_decisions:
  - Dual-layer fallback: SQL COALESCE('ID') + Pydantic default='ID' ensures pre-marketplace evaluations never break
patterns_established:
  - none
observability_surfaces:
  - GET /api/evaluations/{id} response now includes marketplace field — inspect via curl or browser network tab
duration: 10m
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T01: Add marketplace to evaluation detail API response

**Wired `marketplace` from DB column through SQL query → TypedDict → Pydantic schema → API response with fallback default `"ID"`.**

## What Happened

Four changes across three files, all straightforward:

1. Added `marketplace: str` to `EvaluationDetailRow` TypedDict.
2. Added `COALESCE(e.marketplace, 'ID') AS marketplace` to the `get_evaluation_by_id` SQL SELECT — COALESCE handles NULL rows from pre-marketplace evaluations.
3. Added `marketplace: str = "ID"` to `EvaluationDetailResponse` Pydantic schema.
4. Added `marketplace=row.get("marketplace", "ID")` to the explicit constructor call in `get_evaluation_detail` service function.

The dual-layer fallback (SQL COALESCE + Pydantic default) means pre-marketplace evaluations can't produce a missing or null marketplace field.

## Verification

- `EvaluationDetailRow.__annotations__` contains `marketplace`: **True** ✅
- `EvaluationDetailResponse.model_fields['marketplace'].default`: **ID** ✅
- Backend evaluation tests: **97 passed**, 0 failed ✅
- Slice-level `evaluation_detail` tests: **10 passed**, 0 failed ✅

## Diagnostics

- `GET /api/evaluations/{id}` JSON response now includes `marketplace` field. If absent, SQL SELECT or schema wiring is broken.
- Pre-marketplace evaluations return `"ID"` — no error paths introduced.

## Deviations

None.

## Known Issues

None.

## Files Created/Modified

- `backend/app/db/queries/evaluations.py` — Added `marketplace: str` to `EvaluationDetailRow`, added `COALESCE(e.marketplace, 'ID')` to SELECT
- `backend/app/modules/evaluations/schemas.py` — Added `marketplace: str = "ID"` to `EvaluationDetailResponse`
- `backend/app/modules/evaluations/service.py` — Added `marketplace=row.get("marketplace", "ID")` to response constructor
