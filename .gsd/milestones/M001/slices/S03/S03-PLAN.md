# S03: CSV THB Parsing

**Goal:** Price parsing in discount and top_sku calculators correctly handles both IDR format (`.` as thousands separator) and THB format (`,` as thousands separator, `.` as decimal).
**Demo:** Unit tests prove `_parse_price("1,250.50", "TH")` returns 1250.5, `_parse_price("125.000", "ID")` returns 125000.0, and both `calculate_discount` and `calculate_top_sku` accept a `marketplace` parameter that flows through to price parsing. The calculator_service reads marketplace from `evaluation_inputs` and passes it to the pure calculator functions.

## Must-Haves

- Shared `_parse_price(value, marketplace)` function in `app/calculators/price_parser.py` replacing duplicate `_clean_price` in discount.py and top_sku.py
- IDR parsing: strip `.` as thousands separator (existing behavior preserved)
- THB parsing: strip `,` as thousands separator, keep `.` as decimal
- `calculate_discount` and `calculate_top_sku` accept `marketplace` param (default `"ID"`)
- `calculator_service.py` reads `marketplace` from `evaluation_inputs` and passes it to calculator functions
- All existing calculator tests pass without modification (backward compat via default `"ID"`)

## Proof Level

- This slice proves: contract
- Real runtime required: no
- Human/UAT required: no

## Verification

- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_price_parser.py -x -v` — all pass
- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_discount.py -x -v` — all pass (backward compat)
- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_top_sku.py -x -v` — all pass (backward compat)
- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_calculator_service_marketplace.py -x -v` — all pass (wiring)
- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/ -x` — full calculator suite passes (3 pre-existing failures in test_ads_keyword.py excluded)

## Observability / Diagnostics

- **Runtime signals:** `_parse_price` returns 0.0 for any unparseable value — downstream calculators will show zero-value line items rather than crash. Watch for unexpected 0.0 aggregations in calculator output as a sign of parsing issues.
- **Inspection surfaces:** Run `_parse_price(sample_value, marketplace)` in a REPL to verify parsing for any currency format. Calculator test suites exercise both IDR and THB formats.
- **Failure visibility:** If marketplace param is missing or wrong, price parsing silently falls back to IDR behavior (default `"ID"`). No explicit error is raised — this is by design for backward compatibility. Incorrect marketplace will show in calculator output (e.g., THB prices parsed as IDR will be 1000x too large or return 0.0).
- **Redaction constraints:** None — price values are not PII.

## Integration Closure

- Upstream surfaces consumed: `app/core/marketplace.py` (VALID_MARKETPLACES), `app/db/queries/evaluations.py` (get_evaluation_inputs returns marketplace)
- New wiring introduced in this slice: `calculator_service.py` reads marketplace from eval_inputs and passes to pure calculator functions
- What remains before the milestone is truly usable end-to-end: S04 (frontend marketplace selector so users can choose TH before uploading CSVs)

## Tasks

- [x] **T01: Extract shared _parse_price module and update calculator signatures** `est:45m`
  - Why: The core parsing logic — two identical `_clean_price` functions in discount.py and top_sku.py unconditionally strip `.` which destroys THB prices. Must extract into a shared module with marketplace-aware parsing, update both calculator public functions to accept `marketplace`, and write comprehensive tests. This is the highest-risk task — get parsing right first.
  - Files: `backend/app/calculators/price_parser.py` (new), `backend/app/calculators/discount.py`, `backend/app/calculators/top_sku.py`, `backend/tests/unit/calculators/test_price_parser.py` (new), `backend/tests/unit/calculators/test_discount.py`, `backend/tests/unit/calculators/test_top_sku.py`
  - Do: (1) Create `price_parser.py` with `_parse_price(value, marketplace="ID")` — for ID: strip `.`, for TH: strip `,`, keep `.` as decimal. Handle None, int, float, empty string, non-numeric. (2) In discount.py: remove `_clean_price`, import `_parse_price` from price_parser, add `marketplace="ID"` param to `calculate_discount`, pass to all `_parse_price` calls. (3) Same for top_sku.py: remove `_clean_price`, import, add `marketplace="ID"` to `calculate_top_sku`, pass through. (4) Create `test_price_parser.py` with tests for both formats. (5) Update existing test imports in test_discount.py and test_top_sku.py — change `_clean_price` imports to `_parse_price` from price_parser, adjust test assertions to pass `marketplace` where needed. All existing test assertions must still pass.
  - Verify: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_price_parser.py backend/tests/unit/calculators/test_discount.py backend/tests/unit/calculators/test_top_sku.py -x -v`
  - Done when: All tests pass including new price parser tests and all pre-existing discount/top_sku tests (backward compat confirmed)

- [ ] **T02: Wire marketplace from evaluation_inputs through calculator_service** `est:30m`
  - Why: The calculator_service must read `marketplace` from `evaluation_inputs` (which already stores it after S01) and pass it to the pure calculator functions. Without this wiring, the TH marketplace param never reaches the price parser at runtime.
  - Files: `backend/app/modules/evaluations/calculator_service.py`, `backend/tests/unit/calculators/test_calculator_service_marketplace.py` (new)
  - Do: (1) In `run_discount_calculator`: after loading `brand`, also load `eval_inputs` via `eval_queries.get_evaluation_inputs(conn, brand_id)`, extract `marketplace = eval_inputs["marketplace"] if eval_inputs else "ID"`, pass `marketplace=marketplace` to `calculate_discount(order_data, marketplace=marketplace)`. (2) Same for `run_top_sku_calculator`: load eval_inputs, extract marketplace, pass `marketplace=marketplace` to `calculate_top_sku(order_data, mass_update_data, marketplace=marketplace)`. (3) Write unit tests that mock `get_evaluation_inputs` and verify marketplace flows through to `calculate_discount` / `calculate_top_sku` calls. **IMPORTANT CORRECTION:** The research doc says to add `v.marketplace` to `get_brand_by_id` in brands.py — this is WRONG. `brand_vp_data` does NOT have a marketplace column. Marketplace lives on `evaluation_inputs` (added by migration 026). Read it from there, following the same pattern as `run_ads_keyword_calculator` which already loads eval_inputs.
  - Verify: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_calculator_service_marketplace.py -x -v`
  - Done when: Unit tests prove marketplace flows from eval_inputs through calculator_service to calculator functions for both discount and top_sku paths

## Files Likely Touched

- `backend/app/calculators/price_parser.py` (new — shared parsing module)
- `backend/app/calculators/discount.py` (remove _clean_price, import _parse_price, add marketplace param)
- `backend/app/calculators/top_sku.py` (remove _clean_price, import _parse_price, add marketplace param)
- `backend/app/modules/evaluations/calculator_service.py` (wire marketplace from eval_inputs)
- `backend/tests/unit/calculators/test_price_parser.py` (new — parser tests)
- `backend/tests/unit/calculators/test_discount.py` (update imports)
- `backend/tests/unit/calculators/test_top_sku.py` (update imports)
- `backend/tests/unit/calculators/test_calculator_service_marketplace.py` (new — wiring tests)
