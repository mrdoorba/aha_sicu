# S03: CSV THB Parsing — Research

**Date:** 2026-03-17
**Depth:** Targeted — known technology, clear scope, well-understood data flow

## Summary

S03 fixes the `_clean_price` function in `discount.py` and `top_sku.py` that unconditionally strips `.` as a thousands separator (Indonesian convention). Thai prices use `,` as thousands separator and `.` as decimal separator — the current code destroys THB values, producing 0.0 for any comma-containing price string.

The scope is narrow and well-defined: two calculator files have identical `_clean_price` functions that need a `marketplace` parameter. The calculator service layer (`calculator_service.py`) already loads the brand object (which carries `marketplace` after S01's migration 026), but doesn't pass it to the pure calculator functions. The fix threads `marketplace` from brand → calculator service → pure calculator → `_clean_price`.

The `_safe_num` functions in the same files also fail on comma-formatted values (returning 0.0), but `_safe_num` is used only for non-price fields like `Jumlah` (quantity) which Polars reads as Int64, so they pass through the `isinstance(value, (int, float))` branch. No `_safe_num` change is needed unless THB CSVs have formatted quantity fields — verify with a real sample.

## Recommendation

**Rename `_clean_price` to `_parse_price` with a `marketplace` parameter.** This makes the locale-dependent behavior explicit:
- `marketplace="ID"`: strip `.` (existing behavior)
- `marketplace="TH"`: strip `,`, keep `.` as decimal

Extract `_parse_price` into a shared module (`app/calculators/price_parser.py`) to eliminate the current duplication between `discount.py` and `top_sku.py`. Both files have identical `_clean_price` and `_safe_num` implementations — DRY this.

Thread `marketplace` through the calculator service: `run_discount_calculator` and `run_top_sku_calculator` already load `brand` via `get_brand_by_id` — read `brand["marketplace"]` (available after S01 migration) and pass it to the pure calculator functions. The pure functions pass it to `_parse_price`.

Do NOT change `ads_keyword.py` — its numeric columns (Biaya, Omzet Penjualan, Efektifitas Iklan) arrive as Int64/Float64 from Polars, not as formatted strings. Its `_format_idr` output formatting is an S02/S04 concern.

## Implementation Landscape

### Key Files

- `backend/app/calculators/discount.py` — Contains `_clean_price` (line 49) used on 6 price fields: Harga Awal, Harga Setelah Diskon, Voucher Ditanggung Penjual, Paket Diskon. Signature of `calculate_discount` must accept `marketplace` param.
- `backend/app/calculators/top_sku.py` — Contains identical `_clean_price` (line 48) used on 5 price fields: Harga Setelah Diskon, Voucher Ditanggung Penjual, Cashback Koin, Diskon Dari Shopee. Signature of `calculate_top_sku` must accept `marketplace` param.
- `backend/app/modules/evaluations/calculator_service.py` — Orchestrates calculator execution. `run_discount_calculator` (line 278) and `run_top_sku_calculator` (line 350+) both load `brand` via `get_brand_by_id` but don't read `marketplace`. Must extract `brand.get("marketplace", "ID")` and pass to calculator functions.
- `backend/app/db/queries/brands.py` — `get_brand_by_id` (line 141) SELECT does NOT include `marketplace` column. Must add `v.marketplace` to the SELECT list for S03 to work. (S01 added the column to the table but did not update this query.)
- `backend/tests/unit/calculators/test_discount.py` — 844 lines, tests `_clean_price` with IDR format strings. Must add THB format tests and verify backward compatibility.
- `backend/tests/unit/calculators/test_top_sku.py` — 698 lines, tests `_clean_price` with IDR format strings. Must add THB format tests.
- `backend/app/core/marketplace.py` — Already exists (S01). Import `VALID_MARKETPLACES` for parameter validation if desired.

### Data Flow

```
CSV upload → Polars read_csv → to_dicts() → JSONB in DB
                                                ↓
                            calculator_service loads parsed_data
                                                ↓
                            calls calculate_discount(order_data)
                                                ↓
                            _clean_price("125.000") → strips "." → 125000 ✓ (IDR)
                            _clean_price("1,250.50") → strips "." → float("1,25050") → 0.0 ✗ (THB)
```

**Key insight:** Polars preserves formatted price strings as `String` dtype because the `.` thousands separator prevents numeric inference. These strings arrive at `_clean_price` as-is. The function must know which format convention to apply.

### Build Order

1. **First: Shared `_parse_price` helper** — Extract from `discount.py`/`top_sku.py` into `app/calculators/price_parser.py`. Add `marketplace` parameter. Write tests for both ID and TH formats. This is the riskiest part — get it right first.

2. **Second: Update calculator signatures** — Add `marketplace` param (default `"ID"`) to `calculate_discount` and `calculate_top_sku`. Replace `_clean_price` calls with `_parse_price(value, marketplace)`. All existing tests must still pass (backward compat via default).

3. **Third: Wire calculator_service** — Read `brand["marketplace"]` in `run_discount_calculator` and `run_top_sku_calculator`. Pass to calculator functions. Also add `v.marketplace` to `get_brand_by_id` SELECT in `brands.py`.

### Verification Approach

```bash
# Unit tests — price parser
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_discount.py -x -v

# Unit tests — top_sku
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_top_sku.py -x -v

# Regression — full calculator test suite
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/ -x

# Key assertions:
# _parse_price("125.000", "ID") == 125000.0
# _parse_price("1.250.000", "ID") == 1250000.0
# _parse_price("1,250.50", "TH") == 1250.5
# _parse_price("12,500", "TH") == 12500.0
# _parse_price("1,250,000", "TH") == 1250000.0
# _parse_price("125.000", "TH") == 125.0  (dot is decimal in TH)
# Existing tests pass unchanged (marketplace defaults to "ID")
```

## Constraints

- `_clean_price` exists as two **identical copies** in `discount.py` and `top_sku.py`. Both must be updated atomically — updating one without the other creates inconsistent parsing.
- `get_brand_by_id` in `brands.py` does NOT include `marketplace` in its SELECT. This must be added for the calculator service to read it. This is a small but necessary query change outside the calculator files.
- Pure calculator functions (`calculate_discount`, `calculate_top_sku`) must remain pure — no DB I/O, no imports from service layer. Marketplace arrives as a string parameter.
- Default `marketplace="ID"` on all new parameters ensures backward compatibility. All existing callers (tests, services) work without modification.

## Common Pitfalls

- **Forgetting one of the two `_clean_price` copies** — `discount.py` and `top_sku.py` have independent copies. Both must be updated. If extracting to a shared module, ensure both files import from the shared location and delete their local copies.
- **THB decimal precision** — IDR prices are always whole numbers (`125.000` = 125,000). THB prices may have decimals (`1,250.50`). After stripping commas, `float("1250.50")` works correctly. But `round()` in output tables (`_build_output_tables` does `round(product.total_omzet)`) will discard THB satang — acceptable per the system's integer-rounding convention.
- **`_safe_num` silent failure on THB** — `_safe_num("1,250")` returns `0.0` because `float("1,250")` raises ValueError. Currently `_safe_num` is only used on quantity fields (`Jumlah`, `Jumlah Produk di Pesan`) which Polars reads as Int64, so this isn't hit. But if any THB CSV has formatted quantities, they'll silently become 0. Monitor this.
- **`brands.py` SELECT missing marketplace** — If `v.marketplace` is not added to `get_brand_by_id`, the brand dict won't have the field. `brand.get("marketplace", "ID")` in calculator_service will always default to "ID", silently using IDR parsing for THB brands. Add the column explicitly.

## Open Risks

- **Real Shopee Thailand CSV format unverified** — The assumption that THB prices use `,` thousands / `.` decimal is based on Thai locale conventions, not a verified Shopee TH export. If Shopee TH exports prices as plain integers (no formatting), the parser change is still correct (no-op on integer passthrough) but unnecessary. If Shopee TH uses a third format, the parser needs adjustment. Flagged in M001-RESEARCH as CRITICAL before production use.

## Sources

- Direct codebase inspection: `discount.py`, `top_sku.py`, `ads_keyword.py`, `calculator_service.py`, `parser.py`, `brands.py`
- Verified behavior: Polars `read_csv` preserves dotted prices as String dtype; `_clean_price("1,250.50")` returns 0.0 (confirmed via Python REPL)
- S01 Summary: `get_brand_by_id` was not updated to include `marketplace` in SELECT
