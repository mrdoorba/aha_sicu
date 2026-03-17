# S01: Data Model Foundation — UAT

**Milestone:** M001
**Written:** 2026-03-17

## UAT Type

- UAT mode: artifact-driven
- Why this mode is sufficient: This slice creates database schema (migration), constants module, and API wiring — all verifiable through unit/integration tests and import checks without a live database or running server.

## Preconditions

- Python virtualenv activated: `cd backend && source .venv/bin/activate`
- No live database required — tests use mocks
- Migration file exists at `backend/app/db/migrations/versions/026_add_marketplace_to_schema.py`

## Smoke Test

```bash
cd backend && source .venv/bin/activate
python -c "from app.core.marketplace import VALID_MARKETPLACES, MARKETPLACE_CURRENCY; print(VALID_MARKETPLACES, MARKETPLACE_CURRENCY)"
# Expected: frozenset({'ID', 'TH'}) {'ID': 'IDR', 'TH': 'THB'}
```

## Test Cases

### 1. Marketplace constants are importable and correct

1. Run: `python -c "from app.core.marketplace import VALID_MARKETPLACES, MARKETPLACE_CURRENCY, MARKETPLACE_LABELS, CURRENCY_SYMBOLS; print(VALID_MARKETPLACES); print(MARKETPLACE_CURRENCY); print(MARKETPLACE_LABELS); print(CURRENCY_SYMBOLS)"`
2. **Expected:**
   - `frozenset({'ID', 'TH'})`
   - `{'ID': 'IDR', 'TH': 'THB'}`
   - `{'ID': 'Indonesia', 'TH': 'Thailand'}`
   - `{'IDR': 'Rp', 'THB': '฿'}`

### 2. IDR to THB conversion produces correct values

1. Run: `python -c "from app.core.marketplace import convert_idr_to_thb; print(convert_idr_to_thb(100_000_000)); print(convert_idr_to_thb(0)); print(convert_idr_to_thb(50_000))"`
2. **Expected:**
   - `190000.0` (100M IDR × 0.0019)
   - `0.0`
   - `95.0` (50K IDR × 0.0019)

### 3. Migration file has correct structure

1. Run: `python -m pytest tests/unit/marketplace/test_marketplace.py -k "Migration" -v`
2. **Expected:** 8 tests pass, verifying:
   - Migration file exists
   - Has upgrade and downgrade functions
   - Revision is 026, down_revision is 025
   - Adds CHECK constraints
   - Seeds TH row
   - Updates UNIQUE constraint

### 4. Rules query layer accepts marketplace parameter

1. Run: `python -m pytest tests/unit/test_rules_queries.py -v`
2. **Expected:** 8 tests pass, verifying:
   - `get_all_rules` defaults to marketplace='ID'
   - `get_all_rules` with marketplace='TH' passes 'TH' to SQL
   - `get_rules_by_template_and_marketplace` filters by both template and marketplace
   - `update_rules` WHERE clause includes both template AND marketplace
   - RETURNING clause includes marketplace field

### 5. generate_score reads marketplace from evaluation_inputs

1. Run: `python -m pytest tests/unit/test_generate_score_marketplace.py -v`
2. **Expected:** 3 tests pass, verifying:
   - Reads marketplace='TH' from eval_inputs and passes to rules query
   - Defaults to marketplace='ID' when eval_inputs has no marketplace key
   - Defaults to 'ID' when eval_inputs is None (raises CalculatorException for missing data)

### 6. Rules API endpoints accept marketplace query parameter

1. Run: `python -m pytest tests/integration/api/test_rules.py tests/integration/api/test_rules_update.py -v`
2. **Expected:** 20 tests pass, verifying:
   - GET /api/v1/rules works with and without ?marketplace= param
   - PUT /api/v1/rules/{template} works with marketplace
   - Response schema includes marketplace field
   - Auth and role checks still work

### 7. Full test suite shows no regressions

1. Run: `python -m pytest tests/ --tb=short`
2. **Expected:** 1021 passed, 3 failed (pre-existing test_ads_keyword.py failures only)

## Edge Cases

### Invalid marketplace code in constants

1. Run: `python -c "from app.core.marketplace import VALID_MARKETPLACES; print('XX' in VALID_MARKETPLACES); print('id' in VALID_MARKETPLACES)"`
2. **Expected:** Both print `False` — codes are case-sensitive, only 'ID' and 'TH' are valid

### Invalid marketplace code in MARKETPLACE_CURRENCY lookup

1. Run: `python -c "from app.core.marketplace import MARKETPLACE_CURRENCY; print(MARKETPLACE_CURRENCY['XX'])"`
2. **Expected:** `KeyError: 'XX'` — invalid codes are not silently accepted

### Backward compatibility — existing callers without marketplace param

1. Run: `python -m pytest tests/integration/api/test_scoring.py -v --tb=short`
2. **Expected:** All scoring integration tests pass — `generate_score` defaults to 'ID' when marketplace is not specified

### Zero and negative conversion values

1. Run: `python -c "from app.core.marketplace import convert_idr_to_thb; print(convert_idr_to_thb(0)); print(convert_idr_to_thb(-100))"`
2. **Expected:** `0.0` and `-0.19` — function applies rate mathematically without validation

## Failure Signals

- `ImportError` on `from app.core.marketplace import ...` — constants module missing or broken
- `TypeError: 'MagicMock' object can't be awaited` in test_scoring.py — mock not updated to use `get_rules_by_template_and_marketplace`
- `KeyError: 'marketplace'` in response parsing — schema not including marketplace field
- `asyncpg.CheckViolationError` with constraint `chk_*_marketplace` — invalid marketplace code written to DB
- Any test failure in `test_rules_queries.py` or `test_generate_score_marketplace.py` — marketplace wiring broken

## Requirements Proved By This UAT

- DATA-02 — Test cases 3, 4 prove marketplace dimension exists in scoring_rules with ID/TH coexistence
- DATA-03 — Test case 2 proves THB thresholds derived from IDR conversion; test case 6 proves admin can edit via API
- SCORE-01 — Test case 5 proves generate_score selects rules based on evaluation's marketplace

## Not Proven By This UAT

- DATA-01 at runtime — evaluation stores marketplace but no live DB test confirms persistence
- SCORE-02 — Scoring message templates do not yet display currency codes (S02 scope)
- SCORE-03 — Only six_month_avg_threshold is marketplace-specific; other revenue thresholds need S02
- Migration execution on a live database — verified by file structure only, not by running `alembic upgrade`
- API-level validation of invalid marketplace codes (e.g., ?marketplace=XX returns empty results, not 400)

## Notes for Tester

- The 3 failures in `test_ads_keyword.py` are pre-existing and unrelated to marketplace work — ignore them.
- Migration 026 has not been run against a live DB. When deploying, run `alembic upgrade head` and verify with `SELECT template, marketplace FROM scoring_rules` — should show 2 rows.
- The `get_rules_by_template` function still exists as a wrapper — it's not dead code, just a backward-compat shim.
