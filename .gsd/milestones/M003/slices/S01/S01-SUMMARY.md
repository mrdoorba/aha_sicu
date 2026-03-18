---
id: S01
parent: M003
milestone: M003
provides:
  - Comma-formatted follower threshold (>50,000) in DEFAULT_RULES, inline fallbacks, and DB migration 028
  - Comma thousands separator for follower val_str display (40,000 not 40.000)
  - Marketplace-aware ads min_cost (190 THB for TH, 100,000 IDR for others)
  - DB migration 028 with importable _apply_patches for drift test replay chain
  - 8 new unit tests covering R023–R026
requires: []
affects: []
key_files:
  - backend/app/calculators/scoring/rules.py
  - backend/app/calculators/scoring/messages.py
  - backend/app/calculators/ads_keyword.py
  - backend/app/db/migrations/versions/028_fix_follower_threshold_comma_separator.py
  - backend/tests/unit/calculators/test_scoring.py
  - backend/tests/unit/calculators/test_ads_keyword.py
key_decisions:
  - D028: International comma separator convention for scoring messages (50,000 instead of 50.000)
  - D029: Ads min_cost uses IDR_TO_THB_RATE for marketplace scaling (IDR 100,000 → THB 190)
patterns_established:
  - Migration 028 follows the _apply_patches pattern from 027 — single PATCHES list with (json_path, old, new) tuples, importable for drift test replay
  - Bottom ads marketplace tests must satisfy all four BOTTOM query conditions (biaya > min_cost AND biaya > am9 AND roas < am10 AND roas < 5) — use integer ROAS values to avoid round() producing 0 for am10
observability_surfaces:
  - Migration 028 _apply_patches returns bool indicating whether any change was made (testable by drift test)
  - Drift test emits exact key path and DB vs Code values on failure at visitors.followers.message_fail
  - Targeted test commands: `pytest -k "comma or juta or drift" test_scoring.py -v` for R023/R024/R026; `pytest -k "min_cost or marketplace" test_ads_keyword.py -v` for R025
drill_down_paths:
  - .gsd/milestones/M003/slices/S01/tasks/T01-SUMMARY.md
  - .gsd/milestones/M003/slices/S01/tasks/T02-SUMMARY.md
duration: 35m
verification_result: passed
completed_at: 2026-03-18
---

# S01: International formatting & marketplace-aware ads thresholds

**Replaced Indonesian dot-separator formatting (>50.000) with international comma convention (>50,000) across all three sources of truth (DEFAULT_RULES, inline fallbacks, DB templates via migration 028), removed dot-replacing val_str formatting, and made ads BOTTOM min_cost marketplace-aware (190 THB / 100,000 IDR). All proven by 8 new tests; full suite 1097/1097 green.**

## What Happened

Two tasks delivered four independent production changes and their tests:

**T01 — Production code changes (4 files, 15m):** Changed `DEFAULT_RULES["visitors"]["followers"]["message_fail"]` from `>50.000` to `>50,000` in `rules.py`. In `messages.py`, changed the inline fallback fail message from `>50.000` to `>50,000`. In `ads_keyword.py`, changed `min_cost = 100000` to `min_cost = 100000 if marketplace != "TH" else 190` — the function already received `marketplace` as a parameter so only the threshold assignment changed. Created migration 028 following the `_apply_patches` pattern from migration 027 with a single patch entry: `["visitors", "followers", "message_fail"]` old=`>50.000` new=`>50,000`.

**T02 — Tests and a fix (3 files, 20m):** T02 discovered that T01 missed removing `.replace(",", ".")` from the `val_str` formatter on `messages.py` line 164. Fixed that (R024's actual one-liner), then added migration 028 to the drift test replay chain in `_build_effective_db_templates()`. Wrote 8 new tests: 3 for follower comma formatting (R023/R024), 3 for ads marketplace min_cost (R025), and 2 for juta preservation (R026).

The drift test, which replays migrations 012→019→020→021→027→028 and diffs against DEFAULT_RULES, was the single expected failure after T01. T02 resolved it by adding m028 to the replay chain.

## Verification

- **Scoring tests:** 183/183 passed — includes drift test with m028 in replay chain, 3 follower formatting tests (R023/R024), 2 juta preservation tests (R026)
- **Ads keyword tests:** 80/80 passed — includes 3 marketplace min_cost tests (R025)
- **Full backend suite:** 1097/1097 passed, 0 failures
- **Migration 028 diagnostics:** Forward patch replaces `>50.000`→`>50,000`, reverse restores it, idempotency returns `False` on already-patched data

## Requirements Advanced

None — all four requirements went directly from active to validated.

## Requirements Validated

- R023 — Follower threshold display uses `>50,000` (comma). Proven by: `test_follower_fail_message_contains_comma_threshold`, `test_default_rules_followers_message_fail_uses_comma`, drift test with m028 in replay chain
- R024 — Follower val_str uses comma thousands separator (`40,000` not `40.000`). Proven by: `test_follower_val_str_uses_comma_when_value_is_40000`
- R025 — Ads BOTTOM min_cost is 100,000 for ID and 190 for TH. Proven by: `test_min_cost_190_when_marketplace_is_th`, `test_min_cost_100000_when_marketplace_is_id`, `test_th_excludes_ad_below_190`
- R026 — G66 juta convention preserved for ID, raw numbers for TH. Proven by: `test_compute_g66_uses_juta_when_marketplace_is_id`, `test_compute_g66_uses_raw_numbers_when_marketplace_is_th`

## New Requirements Surfaced

None.

## Requirements Invalidated or Re-scoped

None.

## Deviations

T01 claimed it removed `.replace(",", ".")` from `messages.py` line 164, but the actual change only updated the inline fallback string. T02 caught this discrepancy (the R024 test correctly failed) and applied the fix. This is the only deviation — all other changes matched the plan exactly.

## Known Limitations

None — this was a single-slice milestone with no deferred work. All four requirements are fully validated.

## Follow-ups

None.

## Files Created/Modified

- `backend/app/calculators/scoring/rules.py` — Changed `>50.000` to `>50,000` in DEFAULT_RULES followers message_fail
- `backend/app/calculators/scoring/messages.py` — Removed `.replace(",", ".")` from val_str; changed inline fallback to `>50,000`
- `backend/app/calculators/ads_keyword.py` — Made min_cost marketplace-aware: 190 for TH, 100,000 otherwise
- `backend/app/db/migrations/versions/028_fix_follower_threshold_comma_separator.py` — New migration with _apply_patches for followers comma formatting
- `backend/tests/unit/calculators/test_scoring.py` — Added m028 to drift test replay chain; added 6 new tests (R023/R024/R026)
- `backend/tests/unit/calculators/test_ads_keyword.py` — Added 3 new tests for R025 marketplace-aware min_cost

## Forward Intelligence

### What the next slice should know
- This was the only slice in M003. The milestone is complete after this slice — no downstream slices consume this work within M003.
- All four requirements (R023–R026) are validated. The milestone definition of done is fully satisfied.

### What's fragile
- The drift test replay chain is now 6 migrations deep (012→019→020→021→027→028). Any future migration that touches scoring_rules message templates must be appended to `_build_effective_db_templates()` in `test_scoring.py` or the drift test fails. This is by design — it catches template/code divergence — but forgetting the step causes a confusing test failure.

### Authoritative diagnostics
- `pytest -k "comma or juta or drift" backend/tests/unit/calculators/test_scoring.py -v` — covers R023/R024/R026 in isolation. Drift test failure output shows exact key path and DB vs Code values.
- `pytest -k "min_cost or marketplace" backend/tests/unit/calculators/test_ads_keyword.py -v` — covers R025 in isolation.

### What assumptions changed
- T01 task plan assumed all four production changes in `messages.py` were a single commit. In practice, the `.replace(",", ".")` removal on line 164 was missed by T01 and caught by T02's test. Always verify git diffs against task summary claims — the summary may claim a change that didn't actually land.
