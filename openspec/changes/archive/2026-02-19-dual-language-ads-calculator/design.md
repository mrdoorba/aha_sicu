## Context

The Ads Keyword Calculator processes two Shopee CSV exports (CPC Ad Report + Keyword/Placement Report). Shopee exports these in either Indonesian or English depending on seller language settings. The original spreadsheet maintained two separate formula sets — one for each language — with genuinely different business logic (not just translations).

Currently, `parser.py` normalises English CSVs to Indonesian column names and cell values, then a single calculator runs. This loses the language signal and always applies Indonesian business rules.

Reference: `my-documents/ads-calculators.md` contains the original Google Sheets formulas for both versions.

## Goals / Non-Goals

**Goals:**
- Detect CSV language at parse time and persist it in parsed data metadata
- Run the correct calculator variant (Indonesian or English business rules) based on detected language
- Both CPC and Keyword CSVs for the same brand MUST be the same language

**Non-Goals:**
- Changing how other calculators (Discount, Top SKU) work — ads-only
- Supporting mixed-language uploads within one brand evaluation
- Fixing bugs in the English spreadsheet (copy-paste errors in flag 4, trailing spaces) — we implement the *intended* logic
- Changing the parser's column/value normalisation — we still normalise to Indonesian, but record original language

## Decisions

### 1. Language detection: at parse time in `parser.py`

Detection heuristic: if `_COLUMN_RENAME` triggers any renames, the CSV is English. Otherwise Indonesian.

Store as `"source_language": "en"` or `"source_language": "id"` in the `parsed_data` dict alongside `columns`, `data`, `row_count`.

**Why not detect in the calculator?** The calculator is a pure function with no knowledge of file origins. The parser already knows the language because it does the renaming.

### 2. Keep normalisation, add language flag

We continue normalising English → Indonesian (column names + cell values) so the calculator always works with Indonesian field values. The language flag only switches *business logic* (which flags to generate, which thresholds to use).

**Alternative considered:** Don't normalise, keep English values and handle both in calculator. Rejected — would double the string comparisons throughout the calculator and create maintenance burden.

### 3. Calculator receives a `language: "id" | "en"` parameter

`calculate_ads_keyword()`, `calculate_sheet1()`, `calculate_sheet2()` all get a `language` parameter defaulting to `"id"` for backwards compatibility.

The calculator service extracts `source_language` from either the CPC or keyword upload's `parsed_data` and passes it through.

### 4. English spreadsheet bugs — implement intended logic

The English spreadsheet has known bugs (flag 4 checks Discovery but says Pencarian, flag 2 uses "Berjalan" instead of "Ongoing", flag 8 has trailing space). Since we normalise to Indonesian values, these bugs don't apply. We implement the *intended* 9-flag logic for English.

Corrected English flag 4: check Halaman Pencarian + Bidding Otomatis (not Discovery).

## Risks / Trade-offs

- **[Risk] Language mismatch between CPC and Keyword CSV** → Calculator service validates both uploads have the same `source_language`. If mismatched, raise `CALC_MISSING_DATA` error.
- **[Risk] Existing data in DB has no language flag** → Default to `"id"` when `source_language` is absent. All existing data was processed as Indonesian, so this is correct.
- **[Trade-off] Two code paths in one calculator** → Increases complexity, but the alternative (two separate calculator files) would duplicate ~80% of shared logic. Conditional branches within shared functions is the lesser evil.
