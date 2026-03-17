---
id: T02
parent: S03
milestone: M001
provides:
  - Marketplace parameter wired from evaluation_inputs through calculator_service to calculate_discount and calculate_top_sku
key_files:
  - backend/app/modules/evaluations/calculator_service.py
  - backend/tests/unit/calculators/test_calculator_service_marketplace.py
key_decisions:
  - Read marketplace from eval_queries.get_evaluation_inputs (NOT from brand_vp_data which has no marketplace column)
  - Default to "ID" when eval_inputs is None for backward compatibility
patterns_established:
  - Calculator service functions load eval_inputs and extract marketplace before calling pure calculators — same pattern as run_ads_keyword_calculator loading total_products
observability_surfaces:
  - Marketplace defaults silently to "ID" when eval_inputs is None — no error. Watch for zero-value or inflated calculator outputs as sign of wrong marketplace.
duration: ~10min
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T02: Wire marketplace from evaluation_inputs through calculator_service

**Wired `run_discount_calculator` and `run_top_sku_calculator` to read marketplace from `evaluation_inputs` and pass it to the pure calculator functions.**

## What Happened

Added marketplace loading to both `run_discount_calculator` and `run_top_sku_calculator` in `calculator_service.py`. Each function now calls `eval_queries.get_evaluation_inputs(conn, brand_id)` after brand validation, extracts `marketplace` with `"ID"` fallback, and passes it as a keyword argument to the respective pure calculator function. The pattern mirrors how `run_ads_keyword_calculator` already loads `eval_inputs` for `total_products`.

No changes to `brands.py` — marketplace lives in `evaluation_inputs`, not `brand_vp_data`.

## Verification

- `PYTHONPATH=backend pytest backend/tests/unit/calculators/test_calculator_service_marketplace.py -x -v` — **4/4 passed** (TH wiring + ID default for both discount and top_sku)
- `PYTHONPATH=backend pytest backend/tests/unit/calculators/ -x -v --ignore=test_ads_keyword.py` — **457/457 passed**, 0 failures, no regressions

### Slice-level verification status (S03):
- ✅ `test_price_parser.py` — all pass
- ✅ `test_discount.py` — all pass (backward compat)
- ✅ `test_top_sku.py` — all pass (backward compat)
- ✅ `test_calculator_service_marketplace.py` — all pass (wiring)
- ✅ Full calculator suite (excluding test_ads_keyword.py) — all pass

## Diagnostics

- If a Thai brand's calculator output shows inflated prices (e.g. 125050 instead of 1250.50), check that `evaluation_inputs.marketplace` is set to `"TH"` for that brand.
- `_parse_price` returns 0.0 for unparseable values — watch for unexpected zero-value line items in calculator output.
- REPL check: `await eval_queries.get_evaluation_inputs(conn, brand_id)` → verify marketplace field.

## Deviations

- Worktree was behind `develop` and needed merging before T01's changes (price_parser.py, marketplace param on calculators) were visible. Merged + stash-popped to bring worktree current.

## Known Issues

None.

## Files Created/Modified

- `backend/app/modules/evaluations/calculator_service.py` — Added eval_inputs loading and marketplace extraction to `run_discount_calculator` (lines 311-315) and `run_top_sku_calculator` (lines 396-400); pass `marketplace=marketplace` to calculator calls
- `backend/tests/unit/calculators/test_calculator_service_marketplace.py` — 4 tests verifying marketplace flows through both calculator paths (TH passed + ID default)
