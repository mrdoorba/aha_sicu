# Quick Task: English mass update + ads keyword currency + runtime fixes

**Date:** 2026-03-17
**Branch:** gsd/quick/4-yes

## What Changed
- Added mass update English→Indonesian column mappings (Product Name, Variation ID, Variation Name, Price) to `_COLUMN_RENAME`
- Added `Stock*` → `Stok*` prefix rename for multi-warehouse English files
- Wired `_normalise_english_columns` into Excel/ZIP parsing path in `_parse_file()`
- Dropped blank trailing rows from mass update Excel files (443 → 440)
- Fixed `get_rules_by_template_and_marketplace` called with positional arg instead of keyword-only — caused `TypeError` at runtime ("Hitung Skor" failed)
- Made ads keyword calculator currency-aware — `_format_idr` now accepts currency param, threaded `marketplace` through `calculate_ads_keyword` → `calculate_sheet1`/`calculate_sheet2` → `_format_top_ad`/`_format_bottom_ad`
- Added Kisubo Thailand to `seed_local.py` so it survives Docker rebuilds

## Files Modified
- `backend/app/modules/upload/parser.py` — expanded `_COLUMN_RENAME`, Stock prefix logic
- `backend/app/modules/upload/service.py` — English normalisation for Excel/ZIP, blank row filter
- `backend/app/calculators/ads_keyword.py` — marketplace-aware currency formatting
- `backend/app/modules/evaluations/calculator_service.py` — keyword arg fix, marketplace pass-through
- `backend/app/modules/evaluations/service.py` — keyword arg fix for rules query
- `backend/tests/unit/test_parser.py` — 6 new tests in `TestEnglishMassUpdateNormalisation`
- `backend/tests/unit/test_generate_score_marketplace.py` — assertion style fix
- `backend/scripts/seed_local.py` — Kisubo Thailand test brand

## Verification
- 1088 backend tests pass
- Validated against real Thai mass update file (440 rows, all columns renamed)
- Docker rebuild + runtime test confirmed THB currency in ads keyword output
