---
estimated_steps: 5
estimated_files: 2
---

# T02: Wire marketplace from evaluation_inputs through calculator_service

**Slice:** S03 — CSV THB Parsing
**Milestone:** M001

## Description

Wire the runtime path so that `run_discount_calculator` and `run_top_sku_calculator` in `calculator_service.py` read the brand's marketplace from `evaluation_inputs` and pass it to the pure calculator functions (which T01 updated to accept `marketplace`).

**CRITICAL CORRECTION from research doc:** The S03-RESEARCH.md says to add `v.marketplace` to `get_brand_by_id` in `brands.py`. This is WRONG — `brand_vp_data` does NOT have a `marketplace` column. Migration 026 added marketplace to `evaluation_inputs`, `evaluations`, and `scoring_rules` only. The marketplace must be read from `evaluation_inputs` via `eval_queries.get_evaluation_inputs(conn, brand_id)`. This pattern is already established in `run_ads_keyword_calculator` (line ~63), which loads eval_inputs for the same brand.

**Relevant skill:** `test` (for test generation patterns)

## Steps

1. **Update `run_discount_calculator` in `calculator_service.py`** (around line 277):
   - After the brand validation block, add a call to load eval_inputs:
     ```python
     eval_inputs = await eval_queries.get_evaluation_inputs(conn, brand_id)
     marketplace = eval_inputs["marketplace"] if eval_inputs else "ID"
     ```
   - Update the `calculate_discount` call (line ~317) to pass marketplace:
     ```python
     result = calculate_discount(order_data, marketplace=marketplace)
     ```
   - Verify that `eval_queries` is already imported in the file (check the imports section). If not, add it. Look for existing usage — `run_ads_keyword_calculator` already uses it.

2. **Update `run_top_sku_calculator` in `calculator_service.py`** (around line 342):
   - Same pattern: load eval_inputs, extract marketplace with "ID" fallback
   - Update the `calculate_top_sku` call (line ~396) to pass marketplace:
     ```python
     result = calculate_top_sku(order_data, mass_update_data, marketplace=marketplace)
     ```

3. **Create `backend/tests/unit/calculators/test_calculator_service_marketplace.py`** with tests:
   - Mock `brand_queries.get_brand_by_id` to return a valid brand
   - Mock `upload_queries.get_upload_by_type` to return valid upload data
   - Mock `eval_queries.get_evaluation_inputs` to return `{"marketplace": "TH", ...}`
   - Mock `calc_queries.upsert_result` to capture the call
   - Mock `calculate_discount` / `calculate_top_sku` to capture arguments
   - **Test 1:** `run_discount_calculator` passes `marketplace="TH"` to `calculate_discount` when eval_inputs has marketplace="TH"
   - **Test 2:** `run_discount_calculator` passes `marketplace="ID"` (default) when eval_inputs is None
   - **Test 3:** `run_top_sku_calculator` passes `marketplace="TH"` to `calculate_top_sku` when eval_inputs has marketplace="TH"
   - **Test 4:** `run_top_sku_calculator` passes `marketplace="ID"` (default) when eval_inputs is None

   **Important mocking notes:** These are async functions. Use `unittest.mock.AsyncMock` for the DB query mocks. The functions use `async with db.connection() as conn:` — mock `db.connection` to return an async context manager. Look at existing test patterns in `backend/tests/unit/` for how the project mocks DB connections.

4. **Run the wiring tests:**
   ```bash
   cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M001
   PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_calculator_service_marketplace.py -x -v
   ```

5. **Run full calculator test suite** to confirm no regressions:
   ```bash
   PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/ -x -v --ignore=backend/tests/unit/calculators/test_ads_keyword.py
   ```

## Must-Haves

- [ ] `run_discount_calculator` reads marketplace from `evaluation_inputs`
- [ ] `run_discount_calculator` passes `marketplace` to `calculate_discount`
- [ ] `run_top_sku_calculator` reads marketplace from `evaluation_inputs`
- [ ] `run_top_sku_calculator` passes `marketplace` to `calculate_top_sku`
- [ ] When eval_inputs is None, marketplace defaults to "ID"
- [ ] No changes to `brands.py` (brand_vp_data has no marketplace column)

## Verification

- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_calculator_service_marketplace.py -x -v` — all 4 wiring tests pass
- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/ -x -v --ignore=backend/tests/unit/calculators/test_ads_keyword.py` — full suite passes

## Inputs

- T01 must be complete: `calculate_discount` and `calculate_top_sku` accept `marketplace` keyword param
- `backend/app/modules/evaluations/calculator_service.py` — `run_discount_calculator` (line 277) and `run_top_sku_calculator` (line 342) both load brand via `get_brand_by_id`. Neither currently loads eval_inputs or passes marketplace.
- `backend/app/db/queries/evaluations.py` — `get_evaluation_inputs(conn, brand_id)` returns `EvaluationInputsRow` which includes `marketplace: str` field (added by S01)
- `run_ads_keyword_calculator` (line ~30-70 in same file) already loads eval_inputs — follow this pattern
- Tests run from worktree: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M001` with `PYTHONPATH=backend` and venv python at `/Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python`

## Expected Output

- `backend/app/modules/evaluations/calculator_service.py` — both `run_discount_calculator` and `run_top_sku_calculator` read marketplace from eval_inputs and pass to calculator functions
- `backend/tests/unit/calculators/test_calculator_service_marketplace.py` — 4+ tests proving marketplace flows through both calculator paths
