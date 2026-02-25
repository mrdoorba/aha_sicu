## Why

The Python implementation of G72/G73 (marketing budget recommendation) does not match the original spreadsheet formula. In the spreadsheet, G72 is a **boolean comparison** (`capped_value > ceiling(G68)`), and G73 **branches** on that boolean — using the capped value when TRUE, or the raw G68 ceiling value when FALSE. The Python code treats G72 as a float (always the capped value), losing the FALSE branch entirely. This means non-fashion stores are **hard-capped at 20%** even when the competitor analysis (G68) suggests a higher marketing budget is appropriate.

## What Changes

- **Fix `_compute_g72`** to implement the correct branching logic: compute both the capped value (left side) and the G68 ceiling value (right side), compare them, and return the appropriate percentage based on which is greater
- **Fix G68 value parsing** in G72: the spreadsheet LEFT side uses `VALUE(LEFT(G68, FIND("~", G68)-1))` (raw percentage before "~"), while the RIGHT side uses `CEILING(REGEXEXTRACT(G68, number)/100, 0.01)`. The Python code currently conflates these two different extractions
- **Update existing tests** to cover the FALSE branch where the result exceeds 20% for non-fashion stores

## Capabilities

### New Capabilities

_None_

### Modified Capabilities

- `evaluation-scoring`: The marketing budget percentage calculation (G72/G73) gains correct branching logic, allowing non-fashion results between 20-25% when G68 competitor data justifies it

## Impact

- **Code**: `backend/app/calculators/scoring.py` — `_compute_g72` function (lines 1397-1435)
- **Tests**: `backend/tests/unit/calculators/test_scoring.py` — G72/G73 test cases
- **API behavior**: Evaluations for non-fashion stores with high competitor marketing percentages will now correctly produce recommendations above 20% (up to 25%), matching the spreadsheet behavior
