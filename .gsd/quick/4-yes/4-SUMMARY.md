# Quick Task: English mass update header normalisation + Stock prefix rename

**Date:** 2026-03-17
**Branch:** gsd/quick/4-yes

## What Changed
- Added mass update English→Indonesian mappings to `_COLUMN_RENAME`: Product Name, Variation ID, Variation Name, Price (Product ID was already present)
- Added `Stock*` → `Stok*` prefix rename in `_normalise_english_columns` — handles single and multi-warehouse columns (`Stock`, `Stock 2`, `Stock 3`, …)
- Wired `_normalise_english_columns` into `_parse_file()` for Excel/ZIP paths (CSV already ran it in `parse_csv`)
- Thai and English normalisation now both run in `_parse_file`, mutually exclusive by detection order
- 6 new tests: column rename, validation, single stock, multi-warehouse stock, Indonesian passthrough, startswith check

## Files Modified
- `backend/app/modules/upload/parser.py` — expanded `_COLUMN_RENAME`, Stock prefix logic in `_normalise_english_columns`
- `backend/app/modules/upload/service.py` — added English normalisation to `_parse_file` for Excel/ZIP
- `backend/tests/unit/test_parser.py` — 6 new tests in `TestEnglishMassUpdateNormalisation`

## Verification
- 1088 backend tests pass (1082 existing + 6 new)
- Validated against real Thai mass update file: all columns renamed, `Stok` matched by `startswith`, column validation passes
