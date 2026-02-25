## Why

The Top SKU calculator's mass update lookup uses last-match-wins when multiple entries share the same product label (Nama Produk + Nama Variasi), but the reference spreadsheet (Google Sheets VLOOKUP) uses first-match-wins. This causes wrong Kode Variasi, wrong stock lookups, and an incorrect average stock value for affected products.

## What Changes

- Fix `_build_mass_update_lookup()` in `top_sku.py` to use first-match-wins semantics when building the `name_to_kode` mapping, matching VLOOKUP behavior
- Update unit tests to cover the duplicate-label scenario

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

_(none — this is a bug fix in existing calculator logic, no spec-level requirement changes)_

## Impact

- **Backend**: `backend/app/calculators/top_sku.py` — one-line change in `_build_mass_update_lookup()`
- **Tests**: `backend/tests/unit/calculators/test_top_sku.py` — add test case for duplicate labels
- **Data impact**: Corrects Kode Variasi, stock, and average stock for products with duplicate labels in mass update data
