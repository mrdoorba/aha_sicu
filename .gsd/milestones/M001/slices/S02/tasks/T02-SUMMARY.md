---
id: T02
parent: S02
milestone: M001
provides:
  - 24 unit tests proving THB marketplace scoring correctness across all dimensions
  - generate_score → calculate_score marketplace wiring verification
  - Backward compatibility proof (default = explicit ID)
  - Unknown marketplace fallback test (XX → IDR)
key_files:
  - backend/tests/unit/calculators/test_scoring_marketplace.py
  - backend/tests/unit/test_generate_score_marketplace.py
key_decisions:
  - Fixed existing S01 wiring test assertions to use positional arg style matching the T01 service.py change (get_rules_by_template_and_marketplace passes marketplace as positional, not keyword)
  - Brought T01 uncommitted production code from worktree into main repo to enable test execution
patterns_established:
  - Use _make_*_cat() helpers to construct CategoryScore fixtures with specific verdicts for isolated message testing
  - Test marketplace threading at 3 levels: unit (helpers/messages), integration (categories+computations), e2e (calculate_score)
observability_surfaces:
  - Run `pytest backend/tests/unit/calculators/test_scoring_marketplace.py -v` — each test name encodes the marketplace dimension being verified
  - TestBackwardCompatibility catches regressions where default marketplace diverges from explicit 'ID'
duration: 15m
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T02: Add comprehensive THB marketplace scoring tests

**Created 24 unit tests covering currency formatting, business/competition messages, benchmarks, conclusion text, end-to-end scoring, and backward compatibility for THB marketplace. Added marketplace wiring test for generate_score → calculate_score passthrough.**

## What Happened

1. Created `backend/tests/unit/calculators/test_scoring_marketplace.py` with 7 test classes:
   - **TestFmtCurrency** (6 tests): ID format, TH format, default→ID, equivalence with `_fmt_idr`, zero, negative
   - **TestTHBBusinessMessages** (3 tests): pass/fail verdicts show THB not IDR, ID shows IDR
   - **TestTHBCompetitionMessages** (3 tests): fail/pass verdicts show THB not IDR, ID shows IDR
   - **TestTHBCompetitionBenchmark** (2 tests): THB benchmark starts with "THB ", IDR starts with "IDR "
   - **TestTHBConclusionText** (4 tests): THB has no "juta", raw comma-formatted values; IDR has "juta" scaled; i18n vars verified for both
   - **TestFullScoringTHB** (4 tests): end-to-end `calculate_score(marketplace='TH')` — valid result, business messages have THB, competition benchmarks have THB, conclusion has no juta
   - **TestBackwardCompatibility** (2 tests): default marketplace = explicit 'ID' (total score, email body, conclusion identical); unknown marketplace 'XX' falls back to IDR

2. Added `test_generate_score_passes_marketplace_to_calculate_score` to `test_generate_score_marketplace.py` — verifies the service layer passes `marketplace='TH'` kwarg to `calculate_score` when eval_inputs contains `marketplace: 'TH'`.

3. Fixed existing S01 wiring test assertions: T01's service.py passes marketplace as a positional arg to `get_rules_by_template_and_marketplace`, but the S01 tests expected it as a keyword arg. Updated both `assert_called_once_with` calls.

4. Brought T01 production code changes from the worktree (`.gsd/worktrees/M001/`) into the main repo — T01 had written the code but it was uncommitted in the worktree, not in the develop branch.

## Verification

- `pytest backend/tests/unit/calculators/test_scoring_marketplace.py -x -v` → **24 passed** ✅
- `pytest backend/tests/unit/test_generate_score_marketplace.py -x -v` → **4 passed** ✅
- `pytest backend/tests/unit/calculators/test_scoring.py::TestMigrationTemplatesDrift -x -v` → **1 passed** ✅
- `pytest backend/tests/unit/calculators/test_scoring.py -x -q` → **178 passed** ✅ (no regression)
- `pytest backend/tests/ -q` → **1046 passed, 3 failed** ✅ (3 failures are pre-existing in `test_ads_keyword.py`)

### Slice-level verification status (T02 — final task):
- ✅ `test_scoring.py -x` — all 178 existing tests pass (no regression)
- ✅ `test_scoring_marketplace.py -x` — all 24 new THB-specific tests pass
- ✅ `test_generate_score_marketplace.py -x` — all 4 marketplace wiring tests pass
- ✅ Full suite: 1046 passed, 3 pre-existing failures in `test_ads_keyword.py` (unrelated)
- ✅ THB business messages contain "THB" not "IDR"
- ✅ THB competition messages contain "THB" not "IDR"
- ✅ THB competition benchmark starts with "THB "
- ✅ THB conclusion text does NOT contain "juta"
- ✅ ID marketplace output unchanged from current behavior
- ✅ Unknown marketplace 'XX' defaults to IDR output

## Diagnostics

- Run `pytest backend/tests/unit/calculators/test_scoring_marketplace.py -v` to see per-test pass/fail
- Test names encode the dimension: `test_thb_business_pass_message_contains_thb` → if this fails, the business message template is broken for THB
- `TestBackwardCompatibility::test_default_marketplace_equals_explicit_id` — if this fails, a change broke the default marketplace behavior
- `TestBackwardCompatibility::test_unknown_marketplace_falls_back_to_idr` — verifies MARKETPLACE_CURRENCY.get() fallback

## Deviations

- **T01 code was uncommitted in worktree**: The T01 summary reported all changes as complete, but the production code modifications existed only as uncommitted changes in `.gsd/worktrees/M001/`. Copied 6 scoring module files + service.py + migration + test_scoring.py from the worktree to the main repo to enable test execution.
- **Fixed S01 wiring test assertions**: T01 changed `get_rules_by_template_and_marketplace` from keyword to positional arg passing. The existing S01 tests used `marketplace="TH"` kwarg style which no longer matched. Updated to positional `"TH"` style.

## Known Issues

- Pre-existing 3 test failures in `backend/tests/unit/calculators/test_ads_keyword.py` — unrelated to scoring changes.
- T01 production code was not properly committed; this task brought those changes into the develop branch's working tree.

## Files Created/Modified

- `backend/tests/unit/calculators/test_scoring_marketplace.py` — **created** — 24 tests covering all THB marketplace scoring dimensions
- `backend/tests/unit/test_generate_score_marketplace.py` — **modified** — added `test_generate_score_passes_marketplace_to_calculate_score`, fixed 2 assertion arg styles
- `backend/app/calculators/scoring/_calculator.py` — **copied from worktree** — T01's marketplace parameter threading
- `backend/app/calculators/scoring/categories.py` — **copied from worktree** — T01's marketplace-aware `_score_competition`
- `backend/app/calculators/scoring/computations.py` — **copied from worktree** — T01's marketplace-aware `_compute_g66`/`_compute_g66_i18n`
- `backend/app/calculators/scoring/helpers.py` — **copied from worktree** — T01's `_fmt_currency` helper
- `backend/app/calculators/scoring/messages.py` — **copied from worktree** — T01's marketplace-aware message generators
- `backend/app/calculators/scoring/rules.py` — **copied from worktree** — T01's `{currency}` placeholder templates
- `backend/app/modules/evaluations/service.py` — **copied from worktree** — T01's marketplace passthrough
- `backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py` — **copied from worktree** — T01's migration
- `backend/tests/unit/calculators/test_scoring.py` — **copied from worktree** — T01's drift test update
