---
id: S03
parent: M001
milestone: M001
provides:
  - Shared _parse_price(value, marketplace) function with IDR/THB support
  - marketplace keyword param on calculate_discount and calculate_top_sku (default "ID")
  - calculator_service reads marketplace from evaluation_inputs and passes to pure calculators
requires:
  - slice: S01
    provides: marketplace column on evaluation_inputs table, get_evaluation_inputs query
affects:
  - S04
key_files:
  - backend/app/calculators/price_parser.py
  - backend/app/calculators/discount.py
  - backend/app/calculators/top_sku.py
  - backend/app/modules/evaluations/calculator_service.py
  - backend/tests/unit/calculators/test_price_parser.py
  - backend/tests/unit/calculators/test_calculator_service_marketplace.py
key_decisions:
  - Centralized price parsing in price_parser.py — all calculators import _parse_price from there (D011)
  - Read marketplace from evaluation_inputs (not brand_vp_data) because marketplace lives on eval_inputs (D012)
  - marketplace is keyword-only (after *) with default "ID" for full backward compatibility (D013)
patterns_established:
  - Price parsing is centralized in price_parser.py — future marketplaces add a branch there
  - Marketplace flows as a keyword param through calculator public functions to internal helpers
  - Calculator service loads eval_inputs and extracts marketplace before calling pure calculators (same pattern as ads_keyword loading total_products)
observability_surfaces:
  - _parse_price returns 0.0 on any parse failure — watch for unexpected zero-value line items
  - REPL diagnostic: from app.calculators.price_parser import _parse_price; _parse_price("1,250.50", "TH")
drill_down_paths:
  - .gsd/milestones/M001/slices/S03/tasks/T01-SUMMARY.md
  - .gsd/milestones/M001/slices/S03/tasks/T02-SUMMARY.md
duration: ~25min
verification_result: passed
completed_at: 2026-03-17
---

# S03: CSV THB Parsing

**Marketplace-aware price parsing with shared module, replacing duplicate _clean_price with unified _parse_price that handles IDR (`.` thousands) and THB (`,` thousands, `.` decimal) formats.**

## What Happened

Extracted the duplicated `_clean_price` function from `discount.py` and `top_sku.py` into a new shared module `price_parser.py` with a single `_parse_price(value, marketplace="ID")` function. For IDR (default), it strips `.` as thousands separator. For THB, it strips `,` as thousands separator and preserves `.` as decimal. Both `calculate_discount` and `calculate_top_sku` gained a keyword-only `marketplace` parameter (default `"ID"`) that flows through to all internal `_parse_price` calls.

The calculator_service was then wired so `run_discount_calculator` and `run_top_sku_calculator` load `evaluation_inputs` via `eval_queries.get_evaluation_inputs(conn, brand_id)`, extract `marketplace` (defaulting to `"ID"` when eval_inputs is None), and pass it to the pure calculator functions. This follows the existing pattern where `run_ads_keyword_calculator` already loads eval_inputs for `total_products`.

All existing callers continue working unchanged — the `"ID"` default means no behavioral change unless marketplace is explicitly set to `"TH"`.

## Verification

- **test_price_parser.py**: 21/21 passed — IDR format (5), THB format (6), edge cases (10)
- **test_discount.py**: 69/69 passed — all pre-existing assertions unchanged (backward compat)
- **test_top_sku.py**: 56/56 passed — all pre-existing assertions unchanged (backward compat)
- **test_calculator_service_marketplace.py**: 4/4 passed — TH wiring + ID default for both discount and top_sku paths
- **Full calculator suite** (excluding test_ads_keyword.py pre-existing failure): 457/457 passed
- **REPL verification**: `_parse_price("1,250.50", "TH")` → `1250.5`, `_parse_price("125.000", "ID")` → `125000.0`
- **grep verification**: `grep -rn '_clean_price' backend/app/` returns no results — fully removed

## Requirements Advanced

None — both CSV requirements moved directly to Validated.

## Requirements Validated

- **CSV-01** — 21 unit tests prove THB parsing handles comma-thousands + dot-decimal correctly; 4 wiring tests prove marketplace flows end-to-end from eval_inputs through calculator_service to calculator functions
- **CSV-02** — 125 pre-existing discount/top_sku tests pass unchanged with default marketplace="ID"; 457 total calculator tests pass with zero regressions

## New Requirements Surfaced

None.

## Requirements Invalidated or Re-scoped

None.

## Deviations

- T02 discovered that the worktree was behind `develop` and needed merging before T01's changes were visible. Resolved via merge + stash-pop. The final copy from worktree to main repo was needed because auto-commit had only captured .gsd/ files, not production code changes — consistent with the KNOWLEDGE.md warning about worktree divergence.

## Known Limitations

- `_parse_price` silently returns 0.0 for unparseable values — no error raised. This is by design for robustness but means corrupted input data produces zeros rather than failures.
- If marketplace is wrong (e.g., IDR-formatted prices parsed as THB), values will be silently incorrect (inflated or zeroed). No runtime validation that marketplace matches the actual CSV format.

## Follow-ups

None discovered during execution.

## Files Created/Modified

- `backend/app/calculators/price_parser.py` — new shared module with `_parse_price(value, marketplace="ID")`
- `backend/app/calculators/discount.py` — removed `_clean_price`, imports `_parse_price`, added `marketplace` kwarg
- `backend/app/calculators/top_sku.py` — removed `_clean_price`, imports `_parse_price`, added `marketplace` kwarg
- `backend/app/modules/evaluations/calculator_service.py` — added eval_inputs loading and marketplace passthrough to both `run_discount_calculator` and `run_top_sku_calculator`
- `backend/tests/unit/calculators/test_price_parser.py` — new: 21 tests covering IDR, THB, and edge cases
- `backend/tests/unit/calculators/test_calculator_service_marketplace.py` — new: 4 wiring tests
- `backend/tests/unit/calculators/test_discount.py` — updated imports from `_clean_price` to `_parse_price`
- `backend/tests/unit/calculators/test_top_sku.py` — updated imports from `_clean_price` to `_parse_price`

## Forward Intelligence

### What the next slice should know
- All backend calculator wiring is complete. The discount and top_sku calculators will automatically parse prices in THB format when evaluation_inputs.marketplace is set to "TH". S04 (frontend) only needs to ensure the marketplace selector sets this value before evaluation runs.
- The `price_parser.py` module is the single source of truth for price format handling. If a new marketplace is added, only one file needs a new branch.

### What's fragile
- Silent 0.0 fallback on parse failure means incorrect marketplace selection produces wrong results without any error signal. The only diagnostic is checking calculator output for unexpected zero-value or inflated line items.
- `_parse_price` has no validation that the marketplace string is valid — any value other than "TH" falls through to IDR behavior. This is intentional but means typos silently work "wrong."

### Authoritative diagnostics
- `test_price_parser.py` is the definitive test for parsing correctness — 21 tests cover both formats and all edge cases
- `test_calculator_service_marketplace.py` is the definitive test for wiring — proves marketplace flows from eval_inputs to calculator functions
- REPL: `from app.calculators.price_parser import _parse_price; _parse_price(value, marketplace)` for ad-hoc verification

### What assumptions changed
- No assumptions changed. The plan correctly identified that marketplace lives on evaluation_inputs (not brand_vp_data), and the implementation followed the established eval_inputs loading pattern from ads_keyword_calculator.
