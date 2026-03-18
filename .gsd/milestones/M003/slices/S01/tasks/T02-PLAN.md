---
estimated_steps: 6
estimated_files: 2
---

# T02: Update drift test replay chain and add unit tests for all four requirements

**Slice:** S01 — International formatting & marketplace-aware ads thresholds
**Milestone:** M003

## Description

Close the slice by proving all four requirements (R023–R026) through tests. The production code was changed in T01 — this task updates the migration drift test to include migration 028 and adds new unit tests for follower formatting, ads min_cost marketplace branching, and juta preservation. After this task, the full backend test suite passes with zero failures.

**Skill hint:** Load the `test` skill. Existing test patterns in `test_scoring.py` and `test_ads_keyword.py` must be followed exactly. Use `PYTHONPATH=backend` with the main repo venv at `/Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python` to run tests.

## Steps

1. **Read existing test patterns** — Before writing any tests, read the relevant sections of both test files to understand conventions:
   - `backend/tests/unit/calculators/test_scoring.py` — Find `_build_effective_db_templates` (around line 2410) to see the migration replay chain and understand the import pattern for migrations. Also study existing test methods for assertion style.
   - `backend/tests/unit/calculators/test_ads_keyword.py` — Study existing tests to understand how `calculate_sheet2` is called, how marketplace is passed, and how assertions are structured.

2. **Update drift test replay chain in `test_scoring.py`** — In `TestMigrationTemplatesDrift._build_effective_db_templates()`:
   - Add import for migration 028: `from app.db.migrations.versions import _028_fix_follower_threshold_comma_separator as m028` (use the underscore-prefixed import name matching the file naming convention — check how m027 is imported and follow the same pattern)
   - After the `m027._apply_patches(db, forward=True)` call, add `m028._apply_patches(db, forward=True)`
   - This makes the test replay DB state through all migrations and compare against current `DEFAULT_RULES`

3. **Add follower val_str comma formatting test in `test_scoring.py`** — Add a test that exercises `_generate_visitors_messages` (or the higher-level scoring path) with a follower value like 40000 and asserts the output message contains `40,000` (comma) and does NOT contain `40.000` (dot). Follow existing test naming: `test_<expected>_when_<condition>`.

4. **Add follower fail message threshold test in `test_scoring.py`** — Add a test that verifies the follower fail message contains `>50,000` (comma) and not `>50.000` (dot). This can be tested via `DEFAULT_RULES` directly or through the scoring output for a follower count below 50000.

5. **Add ads min_cost marketplace tests in `test_ads_keyword.py`** — Add two tests:
   - `test_min_cost_190_when_marketplace_is_th` — Call `calculate_sheet2` (or the relevant function) with `marketplace="TH"` and verify the BOTTOM ads cost reflects a 190 THB floor, not 100,000.
   - `test_min_cost_100000_when_marketplace_is_id` — Call with `marketplace="ID"` (or default) and verify the BOTTOM ads cost reflects a 100,000 IDR floor.
   
   Study existing test fixtures and mocking patterns carefully. The ads tests may need specific mock data structures for the keyword input.

6. **Add juta preservation verification test in `test_scoring.py`** — Add a test that calls `_compute_g66` (or exercises it through the scoring path) with `marketplace="ID"` and a sales value large enough to trigger the juta display, and asserts the output contains "juta". Add a parallel test with `marketplace="TH"` asserting the output does NOT contain "juta" and uses raw comma-formatted numbers. This verifies R026 without any code change.

7. **Run full backend test suite and verify zero failures:**
   ```bash
   cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M003
   PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/ -x -q
   ```
   All tests must pass. If any fail, diagnose and fix the test code (not the production code — that was verified in T01).

## Must-Haves

- [ ] Migration 028 is in the drift test replay chain (`_build_effective_db_templates`)
- [ ] `test_db_templates_match_default_rules` passes (drift test green)
- [ ] Test exists proving follower val_str uses comma separator (40,000 not 40.000)
- [ ] Test exists proving follower fail message contains `>50,000`
- [ ] Test exists proving ads min_cost=190 for TH marketplace
- [ ] Test exists proving ads min_cost=100000 for ID marketplace
- [ ] Test exists proving `_compute_g66` uses juta for ID, raw numbers for TH
- [ ] Full backend test suite passes with zero failures

## Verification

- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -x -v` — all scoring tests pass including drift test
- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_ads_keyword.py -x -v` — all ads tests pass including new marketplace tests
- `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/ -x -q` — full suite, zero failures

## Observability Impact

- **Drift test failure signal:** When migration 028 is missing from the replay chain, `test_db_templates_match_default_rules` fails with an `AssertionError` showing the exact JSON path (`visitors.followers.message_fail`) and expected vs actual values — this is the primary failure surface for R023 regression.
- **Formatting test signal:** `test_follower_val_str_uses_comma_when_value_is_40000` and `test_follower_fail_message_contains_comma_threshold` fail with assertion messages showing the actual formatted string, making it immediately clear whether dot or comma was used.
- **Ads threshold signal:** `test_min_cost_190_when_marketplace_is_th` and `test_min_cost_100000_when_marketplace_is_id` fail by showing the actual BOTTOM ads cost value, revealing whether the marketplace branching is active.
- **Juta signal:** `test_compute_g66_uses_juta_when_marketplace_is_id` and `test_compute_g66_uses_raw_numbers_when_marketplace_is_th` fail with the actual g66 string, making the presence/absence of "juta" immediately visible.
- **Future agent inspection:** Run `PYTHONPATH=backend pytest backend/tests/unit/calculators/test_scoring.py -k "comma or juta or drift" -v` to check all R023/R024/R026 tests in isolation. Run `PYTHONPATH=backend pytest backend/tests/unit/calculators/test_ads_keyword.py -k "min_cost" -v` for R025.

## Inputs

- T01 output: `rules.py` with `>50,000`, `messages.py` with comma formatting, `ads_keyword.py` with marketplace branching, migration 028 with `_apply_patches`
- `backend/tests/unit/calculators/test_scoring.py` — Existing test file to extend (~2400+ lines). Contains `TestMigrationTemplatesDrift` class with `_build_effective_db_templates` method.
- `backend/tests/unit/calculators/test_ads_keyword.py` — Existing test file to extend. Contains tests for `calculate_sheet2` with various inputs.
- `backend/app/calculators/scoring/computations.py` — Contains `_compute_g66` with marketplace branching (lines 144–171). Read to understand the juta logic for writing the verification test.

## Expected Output

- `backend/tests/unit/calculators/test_scoring.py` — Updated drift test replay chain + new tests for follower formatting (R023, R024) and juta preservation (R026)
- `backend/tests/unit/calculators/test_ads_keyword.py` — New tests for marketplace-aware min_cost (R025)
- Full backend test suite: all pass, zero failures
