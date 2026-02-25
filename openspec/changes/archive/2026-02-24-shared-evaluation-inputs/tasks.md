## 1. Database Migration

- [x] 1.1 Create Alembic migration `015_shared_evaluation_inputs.py`: consolidate duplicate `evaluation_inputs` rows per brand (keep most recent `updated_at`), rename `user_id` → `last_edited_by`, drop `UNIQUE (brand_id, user_id)` and `idx_evaluation_inputs_user_id`, add `UNIQUE (brand_id)`
- [x] 1.2 Run migration locally and verify: one row per brand, `last_edited_by` column exists, old constraint gone, new constraint present

## 2. Backend Queries

- [x] 2.1 Update `get_evaluation_inputs(conn, brand_id)`: remove `user_id` param, query `WHERE brand_id = $1` only, return `last_edited_by` instead of `user_id`
- [x] 2.2 Update `upsert_evaluation_inputs(conn, brand_id, last_edited_by, ...)`: rename `user_id` param to `last_edited_by`, change conflict target from `(brand_id, user_id)` to `(brand_id)`
- [x] 2.3 Remove `get_any_evaluation_inputs` — now redundant with the updated `get_evaluation_inputs`

## 3. Backend Service

- [x] 3.1 Update `get_evaluation_state(brand_id)`: remove `user_id` param, call `get_evaluation_inputs(conn, brand_id)` without user filter
- [x] 3.2 Update `save_evaluation_inputs(brand_id, last_edited_by, ...)`: rename `user_id` to `last_edited_by`, pass to updated upsert query
- [x] 3.3 Update `generate_score`: keep `user_id` for the `evaluations` record but load inputs via `get_evaluation_inputs(conn, brand_id)` (no user_id)

## 4. Calculator Service

- [x] 4.1 Update `_run_ads_keyword`, `_run_discount`, `_run_top_sku` in `calculator_service.py`: load evaluation inputs by `brand_id` only (remove `user_id` from `get_evaluation_inputs` calls)
- [x] 4.2 Update `check_calculator_readiness` and `run_ready_calculators` in `engine.py` if they reference `get_any_evaluation_inputs` — switch to `get_evaluation_inputs`

## 5. Router

- [x] 5.1 Update `GET /api/v1/evaluations/brands/{brand_id}`: call `get_evaluation_state(brand_id)` without `user_id`
- [x] 5.2 Update `PUT /api/v1/evaluations/brands/{brand_id}`: pass `last_edited_by=current_user["id"]` instead of `user_id`
- [x] 5.3 Update calculator POST endpoints: remove `user_id` from `get_evaluation_inputs` calls where applicable

## 6. Tests

- [x] 6.1 Update existing evaluation backend tests to match new function signatures (remove `user_id` from input queries)
- [x] 6.2 Add test: two different users saving inputs for the same brand — second save overwrites first (last-write-wins), `last_edited_by` reflects second user
- [x] 6.3 Add test: fetching evaluation inputs returns data regardless of who saved it
- [x] 6.4 Run full backend test suite (`uv run pytest -v`) and fix any breakages
- [x] 6.5 Run linter (`uv run ruff check .`) and fix any issues
