---
id: T02
parent: S01
milestone: M003
provides:
  - Migration 028 in drift test replay chain — drift test green
  - Unit tests for follower comma formatting (R023, R024)
  - Unit tests for ads min_cost marketplace branching (R025)
  - Unit tests for juta preservation in _compute_g66 (R026)
  - Fix for T01 missed val_str .replace(",", ".") removal (R024)
key_files:
  - backend/tests/unit/calculators/test_scoring.py
  - backend/tests/unit/calculators/test_ads_keyword.py
  - backend/app/calculators/scoring/messages.py
key_decisions: []
patterns_established:
  - Bottom ads marketplace tests must satisfy all four BOTTOM query conditions (biaya > min_cost AND biaya > am9 AND roas < am10 AND roas < 5) — use integer ROAS values to avoid round() producing 0 for am10
observability_surfaces:
  - Run `pytest -k "comma or juta or drift" test_scoring.py -v` to verify R023/R024/R026 in isolation
  - Run `pytest -k "min_cost or marketplace" test_ads_keyword.py -v` to verify R025 in isolation
  - Drift test emits exact key path and DB vs Code values on failure
duration: 20m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T02: Update drift test replay chain and add unit tests for all four requirements

**Added migration 028 to drift test replay chain, wrote 8 new tests covering follower comma formatting (R023/R024), ads marketplace min_cost (R025), and juta preservation (R026), and fixed T01's missed val_str `.replace(",", ".")` removal. Full backend suite: 1097 passed, 0 failures.**

## What Happened

1. **Fixed T01 missed change:** Line 164 of `messages.py` still had `val_str = f"{int(row.value):,}".replace(",", ".")`. T01's summary claimed this was removed, but the git diff shows only the inline fallback `>50.000→>50,000` was changed. Removed the `.replace(",", ".")` so Python's `:,` format now correctly produces `40,000` (comma) instead of `40.000` (dot).

2. **Updated drift test replay chain:** Added `m028 = importlib.import_module("...028_fix_follower_threshold_comma_separator")` and `m028._apply_patches(db, forward=True)` after m027 in `TestMigrationTemplatesDrift._build_effective_db_templates()`. The drift test now replays all 6 migrations (012→019→020→021→027→028).

3. **Added follower formatting tests (R023/R024):** Three tests in `TestFollowerFormattingR023R024`:
   - `test_follower_val_str_uses_comma_when_value_is_40000` — exercises `_generate_visitors_messages` with follower value=40000, asserts `40,000` in message and `40.000` not in message
   - `test_follower_fail_message_contains_comma_threshold` — asserts fail message contains `>50,000` not `>50.000`
   - `test_default_rules_followers_message_fail_uses_comma` — direct assertion on `DEFAULT_RULES`

4. **Added ads marketplace min_cost tests (R025):** Three tests in `TestSheet2BottomMarketplaceMinCost`:
   - `test_min_cost_190_when_marketplace_is_th` — biaya=500 qualifies in TH (>190) via fallback query
   - `test_min_cost_100000_when_marketplace_is_id` — same biaya=500 excluded in ID (<100,000)
   - `test_th_excludes_ad_below_190` — biaya=100 excluded in TH (<190)

5. **Added juta preservation tests (R026):** Two tests in `TestComputeG66JutaR026`:
   - `test_compute_g66_uses_juta_when_marketplace_is_id` — ID sales output contains "juta"
   - `test_compute_g66_uses_raw_numbers_when_marketplace_is_th` — TH output contains comma-formatted numbers, no "juta"

## Verification

- All 183 scoring tests pass including drift test and 6 new R023/R024/R026 tests
- All 80 ads keyword tests pass including 3 new R025 marketplace tests
- Full backend suite: 1097 passed, 0 failures
- Migration 028 idempotency diagnostic: `_apply_patches` returns False on already-patched data

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `pytest backend/tests/unit/calculators/test_scoring.py -x -v` | 0 | ✅ pass (183/183) | 0.3s |
| 2 | `pytest backend/tests/unit/calculators/test_ads_keyword.py -x -v` | 0 | ✅ pass (80/80) | 0.04s |
| 3 | `pytest backend/tests/ -x -q` | 0 | ✅ pass (1097/1097) | 1.4s |
| 4 | `python -c "... m028._apply_patches(rules, forward=True) == False ..."` (idempotency) | 0 | ✅ pass | <1s |

## Diagnostics

- **Drift test:** On regression, emits `AssertionError: rules["visitors"]["followers"]["message_fail"]` with DB and Code values side by side
- **Formatting tests:** On failure, assertion message shows the actual formatted string for immediate diagnosis
- **Targeted test run:** `pytest -k "comma or juta or drift" test_scoring.py -v` covers R023/R024/R026; `pytest -k "min_cost or marketplace" test_ads_keyword.py -v` covers R025

## Deviations

- **Fixed T01 missed production code change:** T01's summary claimed `.replace(",", ".")` was removed from `messages.py` line 164, but the git diff shows only the inline fallback string was changed. Fixed this here since the test for R024 correctly caught the discrepancy.

## Known Issues

None.

## Files Created/Modified

- `backend/tests/unit/calculators/test_scoring.py` — Added m028 to drift test replay chain; added 6 new tests (3 for R023/R024, 2 for R026, 1 for DEFAULT_RULES assertion)
- `backend/tests/unit/calculators/test_ads_keyword.py` — Added 3 new tests for R025 marketplace-aware min_cost
- `backend/app/calculators/scoring/messages.py` — Removed `.replace(",", ".")` from val_str formatting (T01 missed change)
