---
estimated_steps: 8
estimated_files: 6
---

# T01: Extract shared _parse_price module and update calculator signatures

**Slice:** S03 — CSV THB Parsing
**Milestone:** M001

## Description

The core parsing fix for THB price support. Two identical `_clean_price` functions in `discount.py` and `top_sku.py` unconditionally strip `.` as a thousands separator (Indonesian convention). Thai prices use `,` as thousands separator and `.` as decimal — the current code returns 0.0 for any THB price with commas.

Extract a shared `_parse_price(value, marketplace)` function into a new `price_parser.py` module. Update both calculator files to import from it and add `marketplace` parameter (default `"ID"`) to their public functions. Write comprehensive tests. Ensure all existing tests pass unchanged (backward compat via default).

**Relevant skill:** `test` (for test generation patterns)

## Steps

1. **Create `backend/app/calculators/price_parser.py`** with:
   ```python
   def _parse_price(value: Any, marketplace: str = "ID") -> float:
   ```
   - If `value` is None → return 0.0
   - If `value` is int or float → return float(value)
   - Convert to string, strip whitespace
   - If empty → return 0.0
   - If `marketplace == "TH"`: strip `,` (thousands separator), keep `.` (decimal)
   - Else (ID or any other): strip `.` (thousands separator) — existing behavior
   - Try `float()`, on ValueError return 0.0

2. **Create `backend/tests/unit/calculators/test_price_parser.py`** with tests covering:
   - IDR format: `_parse_price("125.000") == 125000.0`, `_parse_price("1.250.000") == 1250000.0`
   - THB format: `_parse_price("1,250.50", "TH") == 1250.5`, `_parse_price("12,500", "TH") == 12500.0`, `_parse_price("1,250,000", "TH") == 1250000.0`
   - THB decimal-only: `_parse_price("125.50", "TH") == 125.5`
   - Edge cases: None → 0.0, empty string → 0.0, int passthrough, float passthrough, non-numeric string → 0.0
   - Default marketplace is "ID" (no second arg = IDR behavior)
   - Run and confirm all pass

3. **Update `backend/app/calculators/discount.py`**:
   - Remove the `_clean_price` function (lines 49–67)
   - Add import: `from app.calculators.price_parser import _parse_price`
   - Change `calculate_discount` signature: add `*, marketplace: str = "ID"` as keyword-only parameter after `order_data`
   - Replace all `_clean_price(...)` calls with `_parse_price(..., marketplace=marketplace)` (6 call sites at lines 125, 126, 132, 133, and any others)

4. **Update `backend/app/calculators/top_sku.py`**:
   - Remove the `_clean_price` function (lines 48–66)
   - Add import: `from app.calculators.price_parser import _parse_price`
   - Change `calculate_top_sku` signature: add `*, marketplace: str = "ID"` as keyword-only parameter after `mass_update_data`
   - Replace all `_clean_price(...)` calls with `_parse_price(..., marketplace=marketplace)` (5 call sites at lines 97, 100, 101, 102, and any others)

5. **Update `backend/tests/unit/calculators/test_discount.py`**:
   - Change the import line from `from app.calculators.discount import _clean_price, ...` to `from app.calculators.price_parser import _parse_price`
   - In `TestCleanPrice` class (or rename to `TestParsePrice`): update test calls from `_clean_price(...)` to `_parse_price(...)` — all existing assertions should pass since default marketplace is "ID"
   - Optionally add THB test cases in the same class

6. **Update `backend/tests/unit/calculators/test_top_sku.py`**:
   - Same import change as discount tests
   - Same test updates from `_clean_price` to `_parse_price`

7. **Run all calculator tests** to confirm backward compatibility:
   ```bash
   cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M001
   PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_price_parser.py backend/tests/unit/calculators/test_discount.py backend/tests/unit/calculators/test_top_sku.py -x -v
   ```

8. **Verify no remaining references** to `_clean_price` in production code:
   ```bash
   grep -rn '_clean_price' backend/app/ --include='*.py'
   ```
   Should return nothing.

## Must-Haves

- [ ] `_parse_price("125.000")` returns 125000.0 (IDR default)
- [ ] `_parse_price("1.250.000")` returns 1250000.0 (IDR)
- [ ] `_parse_price("1,250.50", "TH")` returns 1250.5 (THB)
- [ ] `_parse_price("12,500", "TH")` returns 12500.0 (THB)
- [ ] `_parse_price("1,250,000", "TH")` returns 1250000.0 (THB)
- [ ] `_parse_price("125.50", "TH")` returns 125.5 (THB decimal)
- [ ] `_parse_price(None)` returns 0.0
- [ ] `_parse_price("abc")` returns 0.0
- [ ] `calculate_discount(order_data)` still works without marketplace param (default "ID")
- [ ] `calculate_top_sku(order_data, mass_update_data)` still works without marketplace param
- [ ] No `_clean_price` function remains in discount.py or top_sku.py
- [ ] All pre-existing test assertions in test_discount.py and test_top_sku.py still pass

## Verification

- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_price_parser.py -x -v` — all new parser tests pass
- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_discount.py -x -v` — all existing discount tests pass
- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_top_sku.py -x -v` — all existing top_sku tests pass
- `grep -rn '_clean_price' backend/app/ --include='*.py'` — returns nothing

## Inputs

- `backend/app/calculators/discount.py` — contains `_clean_price` (lines 49–67), `calculate_discount` (line 320). The `_clean_price` function strips `.` and calls `float()`. 6 call sites in `_calculate_line_items`.
- `backend/app/calculators/top_sku.py` — contains identical `_clean_price` (lines 48–66), `calculate_top_sku` (line 313). 5 call sites in line-item processing.
- `backend/tests/unit/calculators/test_discount.py` — imports `_clean_price` from `app.calculators.discount` (line 17). `TestCleanPrice` class (line 68) has 8 test methods.
- `backend/tests/unit/calculators/test_top_sku.py` — imports `_clean_price` from `app.calculators.top_sku`. Similar `TestCleanPrice` class.
- Tests run from worktree: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M001` with `PYTHONPATH=backend` and venv python at `/Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python`

## Expected Output

- `backend/app/calculators/price_parser.py` — new shared module with `_parse_price(value, marketplace="ID")` function
- `backend/tests/unit/calculators/test_price_parser.py` — comprehensive tests for both IDR and THB parsing
- `backend/app/calculators/discount.py` — `_clean_price` removed, imports `_parse_price`, `calculate_discount` has `marketplace` kwarg
- `backend/app/calculators/top_sku.py` — `_clean_price` removed, imports `_parse_price`, `calculate_top_sku` has `marketplace` kwarg
- `backend/tests/unit/calculators/test_discount.py` — imports updated from `_clean_price` to `_parse_price`
- `backend/tests/unit/calculators/test_top_sku.py` — imports updated from `_clean_price` to `_parse_price`
