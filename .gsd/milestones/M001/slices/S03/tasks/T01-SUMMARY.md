---
id: T01
parent: S03
milestone: M001
provides:
  - Shared _parse_price(value, marketplace) function in app/calculators/price_parser.py
  - marketplace keyword param on calculate_discount and calculate_top_sku (default "ID")
  - Backward-compatible removal of duplicate _clean_price from both calculators
key_files:
  - backend/app/calculators/price_parser.py
  - backend/app/calculators/discount.py
  - backend/app/calculators/top_sku.py
  - backend/tests/unit/calculators/test_price_parser.py
key_decisions:
  - marketplace parameter is keyword-only (after *) to avoid positional arg confusion with existing callers
patterns_established:
  - Price parsing is centralized in price_parser.py — all future calculators import _parse_price from there
  - Marketplace flows as a keyword param through calculator public functions to internal helpers
observability_surfaces:
  - _parse_price returns 0.0 silently on parse failure — watch for unexpected zero aggregations in output
duration: 15m
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T01: Extract shared _parse_price module and update calculator signatures

**Extracted duplicate `_clean_price` into shared `_parse_price(value, marketplace)` with IDR/THB support; updated both calculators with backward-compatible `marketplace` kwarg.**

## What Happened

Created `backend/app/calculators/price_parser.py` with a single `_parse_price(value, marketplace="ID")` function that handles both IDR format (strip `.` as thousands separator) and THB format (strip `,` as thousands separator, keep `.` as decimal). Removed the identical `_clean_price` functions from both `discount.py` and `top_sku.py`, replacing all call sites with `_parse_price(..., marketplace=marketplace)`. Added `*, marketplace: str = "ID"` keyword-only parameter to `calculate_discount` and `calculate_top_sku` public functions, which flows down to internal helpers. All existing callers continue working without changes due to the `"ID"` default.

## Verification

- `test_price_parser.py`: **21 passed** — covers IDR format (5), THB format (6), edge cases (10)
- `test_discount.py`: **69 passed** — all pre-existing assertions pass unchanged (backward compat confirmed)
- `test_top_sku.py`: **56 passed** — all pre-existing assertions pass unchanged (backward compat confirmed)
- `grep -rn '_clean_price' backend/app/`: **no results** — fully removed from production code
- Total: **146 tests passed**, 0 failed

### Slice-level verification status (T01 is intermediate — T02 remains):
- ✅ `test_price_parser.py` — 21 passed
- ✅ `test_discount.py` — 69 passed (backward compat)
- ✅ `test_top_sku.py` — 56 passed (backward compat)
- ⬜ `test_calculator_service_marketplace.py` — not yet created (T02)
- ⬜ Full calculator suite — pending T02

## Diagnostics

- `_parse_price` is a pure function — testable in REPL: `from app.calculators.price_parser import _parse_price; _parse_price("1,250.50", "TH")` → `1250.5`
- If THB prices show inflated values (e.g. 125050 instead of 1250.50), check that marketplace="TH" is being passed correctly through the calculator chain
- Parse failures return 0.0 silently — look for zero-value line items in calculator output as diagnostic signal

## Deviations

None.

## Known Issues

None.

## Files Created/Modified

- `backend/app/calculators/price_parser.py` — new shared module with `_parse_price(value, marketplace="ID")`
- `backend/app/calculators/discount.py` — removed `_clean_price`, imports `_parse_price`, added `marketplace` kwarg to `calculate_discount` and `_calculate_line_items`
- `backend/app/calculators/top_sku.py` — removed `_clean_price`, imports `_parse_price`, added `marketplace` kwarg to `calculate_top_sku` and `_extract_per_line`
- `backend/tests/unit/calculators/test_price_parser.py` — new: 21 tests for IDR, THB, and edge cases
- `backend/tests/unit/calculators/test_discount.py` — updated imports from `_clean_price` to `_parse_price` from `price_parser`
- `backend/tests/unit/calculators/test_top_sku.py` — updated imports from `_clean_price` to `_parse_price` from `price_parser`
