---
estimated_steps: 4
estimated_files: 2
---

# T02: Add comprehensive THB marketplace scoring tests

**Slice:** S02 — Scoring Engine Marketplace Awareness
**Milestone:** M001

## Description

Write comprehensive unit tests proving the marketplace threading works correctly for THB. Tests must cover currency formatting, business messages, competition messages, competition benchmarks, conclusion text scaling, and backward compatibility with ID marketplace. This is the slice's verification gate — S02 is not done until these tests pass.

**Relevant skill:** `test` (for test generation patterns and running)

## Steps

1. **Create `backend/tests/unit/calculators/test_scoring_marketplace.py`:**

   Import the functions under test:
   ```python
   from app.calculators.scoring import calculate_score, DEFAULT_RULES
   from app.calculators.scoring.helpers import _fmt_currency, _fmt_idr
   from app.calculators.scoring.computations import _compute_g66, _compute_g66_i18n
   from app.calculators.scoring.messages import _generate_business_messages, _generate_competition_messages
   from app.calculators.scoring.categories import _score_competition
   ```

   Write these test classes/functions:

   **a. `TestFmtCurrency`** — test the new helper:
   - `test_fmt_currency_id_marketplace`: `_fmt_currency(100_000_000, "ID")` → `"100,000,000"`
   - `test_fmt_currency_th_marketplace`: `_fmt_currency(190_000, "TH")` → `"190,000"`
   - `test_fmt_currency_defaults_to_id`: `_fmt_currency(100_000_000)` → `"100,000,000"` (same as explicit ID)
   - `test_fmt_currency_matches_fmt_idr`: `_fmt_currency(val, "ID") == _fmt_idr(val)` for several values

   **b. `TestTHBBusinessMessages`** — test business message output with THB:
   - Create a `CategoryScore` with a row 13 (monthly sales) with `verdict="✔️"`
   - Create `manual_data` with THB-scale sales (e.g., `salesMonth0: 200_000`)
   - Call `_generate_business_messages(cat, manual_data, rules=DEFAULT_RULES, marketplace='TH')`
   - Assert the row 13 message contains `"THB"` and does NOT contain `"IDR"`
   - Same test with `verdict="❌"` — assert `"THB"` present, `"IDR"` absent
   - Backward compat: same test with `marketplace='ID'` — assert `"IDR"` present

   **c. `TestTHBCompetitionMessages`** — test competition message output with THB:
   - Create competition `CategoryScore` with rows 61-63, verdict "❌"
   - Create `manual_data` with THB-scale prices (e.g., `sellingPrice: 500, marketPrice: 400`)
   - Call `_generate_competition_messages(cat, manual_data, rules=DEFAULT_RULES, marketplace='TH')`
   - Assert messages contain `"THB"`, NOT `"IDR"`
   - Same with `marketplace='ID'` — assert `"IDR"` present

   **d. `TestTHBCompetitionBenchmark`** — test benchmark string in `_score_competition`:
   - Call `_score_competition(manual_data, calculator_results, marketplace='TH')` with non-zero market prices
   - Assert `rows[0].benchmark` starts with `"THB "` not `"IDR "`
   - Same with `marketplace='ID'` — assert starts with `"IDR "`

   **e. `TestTHBConclusionText`** — test `_compute_g66` scaling:
   - Create `manual_data` with THB-scale sales (e.g., 150K-250K range)
   - Call `_compute_g66(categories, manual_data, g68_text, marketplace='TH')`
   - Assert output does NOT contain `"juta"` — THB values should show raw formatted numbers
   - Assert output contains the actual THB values formatted with commas (e.g., `"150,000"`)
   - Same with `marketplace='ID'` with IDR-scale sales (100M-200M) — assert output contains `"juta"`
   - Also test `_compute_g66_i18n` — verify the `vars` dict contains raw numbers for THB, scaled numbers for IDR

   **f. `TestFullScoringTHB`** — end-to-end `calculate_score` with THB:
   - Use the existing `full_manual_data` fixture pattern from `test_scoring.py` but with THB-scale values (divide all IDR amounts by ~500)
   - Call `calculate_score(..., marketplace='TH')`
   - Assert result is a valid `ScoringResult`
   - Find the business category → row 13 message → assert contains `"THB"`
   - Find the competition category → rows → assert benchmarks contain `"THB"`
   - Assert `closing_message` is non-empty (basic sanity)

   **g. `TestBackwardCompatibility`** — prove ID marketplace unchanged:
   - Call `calculate_score` WITHOUT `marketplace` param (relies on default)
   - Assert output is identical to calling with `marketplace='ID'`
   - This proves existing callers are unaffected

2. **Update `backend/tests/unit/test_generate_score_marketplace.py`:**
   - Add a test verifying that `calculate_score` is called with the `marketplace` kwarg when `generate_score` is invoked
   - The existing tests in this file mock `calculate_score` — add an assertion that the mock was called with `marketplace='TH'` when eval_inputs has `marketplace='TH'`

3. **Verify the drift test still passes:**
   - Run `backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py::TestMigrationTemplatesDrift -x -v`
   - If it fails, the `_build_effective_db_templates` method needs to import and apply migration 027 patches (T01 should have handled this, but verify)

4. **Run the full test suite:**
   - `backend/.venv/bin/python -m pytest backend/tests/ -x --timeout=60`
   - All tests must pass (except the 3 pre-existing failures in `test_ads_keyword.py` which are unrelated)

## Must-Haves

- [ ] ≥3 tests for `_fmt_currency` (ID, TH, default, equivalence with `_fmt_idr`)
- [ ] ≥2 tests for THB business messages (pass and fail verdict show THB, not IDR)
- [ ] ≥2 tests for THB competition messages (pass and fail show THB, not IDR)
- [ ] ≥1 test for THB competition benchmark string
- [ ] ≥2 tests for THB conclusion text (no `juta`, correct formatting; ID still has `juta`)
- [ ] ≥1 end-to-end `calculate_score(marketplace='TH')` test
- [ ] ≥1 backward compatibility test (default marketplace produces same output as explicit 'ID')
- [ ] `generate_score` marketplace wiring test updated
- [ ] `TestMigrationTemplatesDrift` still passes
- [ ] Full test suite passes

## Verification

- `backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring_marketplace.py -x -v` — all new tests pass
- `backend/.venv/bin/python -m pytest backend/tests/unit/test_generate_score_marketplace.py -x -v` — marketplace wiring tests pass
- `backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -x` — all existing tests pass (no regression)
- `backend/.venv/bin/python -m pytest backend/tests/ -x --timeout=60` — full suite green (minus 3 pre-existing failures in test_ads_keyword.py)

## Inputs

- `backend/app/calculators/scoring/` — all production code from T01 (with marketplace params)
- `backend/tests/unit/calculators/test_scoring.py` — existing test patterns, fixtures, and imports to follow
- `backend/tests/unit/test_generate_score_marketplace.py` — existing marketplace wiring tests from S01
- `backend/app/core/marketplace.py` — `MARKETPLACE_CURRENCY` constants

## Expected Output

- `backend/tests/unit/calculators/test_scoring_marketplace.py` — ≥12 new tests covering THB formatting, messages, benchmarks, conclusion, and backward compat
- `backend/tests/unit/test_generate_score_marketplace.py` — updated with `calculate_score` marketplace wiring assertion
