# S03: CSV THB Parsing — UAT

**Milestone:** M001
**Written:** 2026-03-17

## UAT Type

- UAT mode: artifact-driven
- Why this mode is sufficient: All changes are pure functions and service wiring — no UI, no database writes, no server required. Unit tests exhaustively cover the contract.

## Preconditions

- Python venv available at `/Users/mac/HT/Project/aha_sicu/backend/.venv/`
- Working directory: `/Users/mac/HT/Project/aha_sicu`
- All source files from S03 present (price_parser.py, updated discount.py, updated top_sku.py, updated calculator_service.py)

## Smoke Test

```bash
cd /Users/mac/HT/Project/aha_sicu
PYTHONPATH=backend backend/.venv/bin/python -c "from app.calculators.price_parser import _parse_price; assert _parse_price('1,250.50', 'TH') == 1250.5; assert _parse_price('125.000', 'ID') == 125000.0; print('PASS')"
```
**Expected:** Prints `PASS`

## Test Cases

### 1. THB price parsing correctness

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_price_parser.py::TestParsePrice_THB -x -v`
2. **Expected:** 6/6 passed — comma-thousands stripped, dot-decimal preserved, integer strings work

### 2. IDR price parsing backward compatibility

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_price_parser.py::TestParsePrice_IDR -x -v`
2. **Expected:** 5/5 passed — dots stripped as thousands separator (existing behavior unchanged)

### 3. Edge case handling (None, empty, garbage)

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_price_parser.py::TestParsePrice_EdgeCases -x -v`
2. **Expected:** 10/10 passed — None → 0.0, empty → 0.0, non-numeric → 0.0, int/float passthrough

### 4. Discount calculator backward compatibility

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_discount.py -x -v`
2. **Expected:** 69/69 passed — all pre-existing test assertions pass without modification

### 5. Top SKU calculator backward compatibility

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_top_sku.py -x -v`
2. **Expected:** 56/56 passed — all pre-existing test assertions pass without modification

### 6. Calculator service marketplace wiring (TH flows through)

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_calculator_service_marketplace.py -x -v`
2. **Expected:** 4/4 passed — TH marketplace flows from eval_inputs to calculate_discount and calculate_top_sku; None eval_inputs defaults to "ID"

### 7. Full calculator suite regression

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/unit/calculators/ -x --ignore=backend/tests/unit/calculators/test_ads_keyword.py`
2. **Expected:** 457 passed, 0 failed (test_ads_keyword.py excluded due to pre-existing unrelated failure)

### 8. No duplicate _clean_price remains

1. Run: `grep -rn '_clean_price' backend/app/`
2. **Expected:** No output — `_clean_price` has been fully removed from production code

## Edge Cases

### THB price with no thousands separator

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -c "from app.calculators.price_parser import _parse_price; print(_parse_price('250.50', 'TH'))"`
2. **Expected:** `250.5` — decimal point preserved even without comma groups

### IDR price with no dots

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -c "from app.calculators.price_parser import _parse_price; print(_parse_price('125000', 'ID'))"`
2. **Expected:** `125000.0` — plain number passes through correctly

### Unknown marketplace falls back to IDR behavior

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -c "from app.calculators.price_parser import _parse_price; print(_parse_price('125.000', 'XX'))"`
2. **Expected:** `125000.0` — any marketplace other than "TH" uses IDR parsing (strip dots)

### THB-format price parsed as IDR (mismatched marketplace)

1. Run: `PYTHONPATH=backend backend/.venv/bin/python -c "from app.calculators.price_parser import _parse_price; print(_parse_price('1,250.50', 'ID'))"`
2. **Expected:** `1250.50` (IDR strips dots, but there's a dot before "50" — result is `125050.0` after stripping the dot, which is wrong). This demonstrates why correct marketplace selection matters.

### Null eval_inputs in calculator_service

1. Test `test_defaults_to_id_when_eval_inputs_is_none` in test_calculator_service_marketplace.py covers this
2. **Expected:** When `get_evaluation_inputs` returns None, marketplace defaults to "ID" — no crash

## Failure Signals

- Any test failure in test_price_parser.py → THB/IDR parsing logic is broken
- Any test failure in test_discount.py or test_top_sku.py → backward compatibility broken
- Any test failure in test_calculator_service_marketplace.py → marketplace wiring broken
- `grep -rn '_clean_price' backend/app/` returning results → duplicate price parsing not fully removed
- Calculator output showing unexpected 0.0 values → likely parse failure on unexpected format
- Calculator output showing values 1000x too large → marketplace mismatch (THB data parsed as IDR)

## Requirements Proved By This UAT

- **CSV-01** — THB price parsing handles comma-thousands + dot-decimal correctly (test cases 1, 6, smoke test)
- **CSV-02** — Existing IDR parsing continues unchanged (test cases 2, 4, 5, 7)

## Not Proven By This UAT

- Runtime integration with actual CSV file uploads (requires running server + database)
- Frontend marketplace selector sending correct marketplace to backend (S04 scope)
- Behavior with real THB CSV data from Shopee Thailand (only synthetic test data used)

## Notes for Tester

- `test_ads_keyword.py` has a pre-existing failure (`test_en_bottom_min_cost_50k`) unrelated to S03 — ignore it and use `--ignore` flag
- The "mismatched marketplace" edge case (THB data parsed as IDR) demonstrates a real risk — there's no validation that prevents this. The frontend marketplace selector (S04) is the intended guard.
- All tests are pure/synchronous — no database, server, or async setup needed
