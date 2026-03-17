# S02: Scoring Engine Marketplace Awareness — UAT

**Milestone:** M001
**Written:** 2026-03-17

## UAT Type

- UAT mode: artifact-driven
- Why this mode is sufficient: The scoring engine is a pure calculation layer — all inputs and outputs are deterministic data structures. Unit tests fully exercise the contract. No server, database, or UI is needed.

## Preconditions

- Python venv available at `backend/.venv/bin/python`
- Working directory is the project root (`/Users/mac/HT/Project/aha_sicu`)
- All production code files from T01 are present (not stuck in worktree)

## Smoke Test

```bash
PYTHONPATH=backend backend/.venv/bin/python -c "
from app.calculators.scoring._calculator import calculate_score
# Minimal THB call — should not raise and should produce a ScoringResult
result = calculate_score(marketplace='TH')
assert hasattr(result, 'total_score'), 'No total_score attribute'
print('Smoke test passed: calculate_score(marketplace=TH) returns ScoringResult')
"
```

## Test Cases

### 1. THB business messages contain "THB" not "IDR"

1. Run `pytest backend/tests/unit/calculators/test_scoring_marketplace.py::TestTHBBusinessMessages -v`
2. All 3 tests pass
3. **Expected:** Pass messages with THB-scale data contain `"THB"`, fail messages contain `"THB"`, ID marketplace messages contain `"IDR"`

### 2. THB competition messages contain "THB" not "IDR"

1. Run `pytest backend/tests/unit/calculators/test_scoring_marketplace.py::TestTHBCompetitionMessages -v`
2. All 3 tests pass
3. **Expected:** Competition pass/fail messages for TH marketplace contain `"THB"`, ID marketplace contains `"IDR"`

### 3. THB competition benchmark string uses correct currency

1. Run `pytest backend/tests/unit/calculators/test_scoring_marketplace.py::TestTHBCompetitionBenchmark -v`
2. Both tests pass
3. **Expected:** THB benchmark starts with `"THB "`, IDR benchmark starts with `"IDR "`

### 4. THB conclusion text avoids "juta" scaling

1. Run `pytest backend/tests/unit/calculators/test_scoring_marketplace.py::TestTHBConclusionText -v`
2. All 4 tests pass
3. **Expected:** TH marketplace conclusion does NOT contain `"juta"`, uses raw comma-formatted numbers. ID marketplace conclusion DOES contain `"juta"` with /1M scaling. i18n vars match their respective formats.

### 5. End-to-end calculate_score with marketplace='TH'

1. Run `pytest backend/tests/unit/calculators/test_scoring_marketplace.py::TestFullScoringTHB -v`
2. All 4 tests pass
3. **Expected:** Full `calculate_score(marketplace='TH')` produces valid ScoringResult, business messages have `"THB"`, competition benchmarks have `"THB"`, conclusion has no `"juta"`

### 6. Backward compatibility — default marketplace

1. Run `pytest backend/tests/unit/calculators/test_scoring_marketplace.py::TestBackwardCompatibility -v`
2. Both tests pass
3. **Expected:** `calculate_score()` (no marketplace arg) produces identical output to `calculate_score(marketplace='ID')`. Unknown marketplace `'XX'` falls back to IDR.

### 7. generate_score → calculate_score wiring

1. Run `pytest backend/tests/unit/test_generate_score_marketplace.py -v`
2. All 4 tests pass
3. **Expected:** `generate_score` reads marketplace from eval_inputs and passes it as kwarg to `calculate_score`. Default is `'ID'` when marketplace is absent.

### 8. Existing scoring tests — no regression

1. Run `pytest backend/tests/unit/calculators/test_scoring.py -x -q`
2. **Expected:** 178 passed, 0 failed

### 9. Migration template drift — DB↔code sync

1. Run `pytest backend/tests/unit/calculators/test_scoring.py::TestMigrationTemplatesDrift -v`
2. **Expected:** 1 passed — DB templates (after replaying migrations 012→019→020→021→027) match DEFAULT_RULES

### 10. Full suite — no collateral damage

1. Run `pytest backend/tests/ -q`
2. **Expected:** ≥1046 passed, only 3 pre-existing failures in `test_ads_keyword.py`

## Edge Cases

### Unknown marketplace code falls back to IDR

1. Call `calculate_score(marketplace='XX')` (or any non-ID/TH code)
2. **Expected:** Output uses `"IDR"` currency code everywhere — `MARKETPLACE_CURRENCY.get('XX', 'IDR')` returns fallback

### Currency formatting helper with zero and negative

1. Run `pytest backend/tests/unit/calculators/test_scoring_marketplace.py::TestFmtCurrency -v`
2. **Expected:** `_fmt_currency(0, 'TH')` → `"0"`, `_fmt_currency(-500_000, 'TH')` → `"-500,000"`

### Missing {currency} kwarg in template (SafeDict resilience)

1. Manually call `_format_message_template` with a template containing `{currency}` but without passing `currency` kwarg
2. **Expected:** Renders literal `{currency}` in output (non-crashing), does NOT raise KeyError

## Failure Signals

- Any test in `test_scoring_marketplace.py` fails → THB message rendering is broken
- `TestMigrationTemplatesDrift` fails → DB templates have diverged from DEFAULT_RULES (likely a migration issue)
- Existing `test_scoring.py` tests fail → backward compatibility regression; the `marketplace='ID'` default path is broken
- `test_generate_score_marketplace.py` fails → service layer is not passing marketplace to the calculator

## Requirements Proved By This UAT

- SCORE-01 — `generate_score()` selects rules and passes marketplace to `calculate_score()` (Test Case 7)
- SCORE-02 — Message templates display correct currency per marketplace (Test Cases 1-5)

## Not Proven By This UAT

- SCORE-03 — Marketplace-specific threshold *values* (different pass/fail cutoffs for THB vs IDR) — this depends on the rules data, not the scoring engine logic. The engine threads marketplace correctly, but this UAT doesn't verify that THB rule rows have distinct threshold values.
- End-to-end with real DB — all tests use mock/fixture data, not a running database
- Frontend rendering — currency codes appear correctly in scoring messages, but how the frontend displays them is S04's scope
- CSV input parsing for THB — S03's scope

## Notes for Tester

- The 3 pre-existing failures in `test_ads_keyword.py` are unrelated to marketplace changes. They test ad keyword scoring, not the scoring calculator modified here.
- All tests run in <1 second — no database, no network, no fixtures to set up.
- If you want to manually inspect THB output, run:
  ```bash
  PYTHONPATH=backend backend/.venv/bin/python -c "
  from app.calculators.scoring._calculator import calculate_score
  r = calculate_score(marketplace='TH')
  for cat in r.category_scores:
      for row in cat.rows:
          if 'THB' in row.message or 'IDR' in row.message:
              print(f'{cat.category}: {row.message[:100]}')
  print('Conclusion:', r.email_body[:200] if r.email_body else 'N/A')
  "
  ```
