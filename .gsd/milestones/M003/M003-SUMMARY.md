---
id: M003
provides:
  - International comma-formatted follower threshold (>50,000) across all three sources of truth
  - Comma thousands separator for follower val_str display values
  - Marketplace-aware ads BOTTOM min_cost (190 THB for TH, 100,000 IDR for others)
  - DB migration 028 updating stored message templates from dot to comma separator
  - Juta display convention preserved for Indonesian marketplace (verified, no change needed)
key_decisions:
  - D028: International comma separator convention for scoring messages (50,000 instead of 50.000)
  - D029: Ads min_cost uses IDR_TO_THB_RATE for marketplace scaling (IDR 100,000 → THB 190)
patterns_established:
  - Migration 028 follows the _apply_patches pattern from 027 — single PATCHES list with (json_path, old, new) tuples, importable for drift test replay
  - Drift test replay chain now 6 migrations deep (012→019→020→021→027→028) — any future migration touching message templates must extend this chain
observability_surfaces:
  - Migration 028 _apply_patches returns bool indicating whether any change was made
  - Drift test emits exact key path and DB vs Code values on mismatch at visitors.followers.message_fail
  - Targeted diagnostics: `pytest -k "comma or juta or drift" test_scoring.py -v` for R023/R024/R026; `pytest -k "min_cost or marketplace" test_ads_keyword.py -v` for R025
requirement_outcomes:
  - id: R023
    from_status: active
    to_status: validated
    proof: DEFAULT_RULES uses >50,000; inline fallback uses >50,000; migration 028 patches DB templates; drift test passes with m028 in replay chain; tests test_follower_fail_message_contains_comma_threshold, test_default_rules_followers_message_fail_uses_comma
  - id: R024
    from_status: active
    to_status: validated
    proof: Removed .replace(",", ".") from val_str formatting; Python :, format produces 40,000; test test_follower_val_str_uses_comma_when_value_is_40000
  - id: R025
    from_status: active
    to_status: validated
    proof: min_cost = 100000 if marketplace != "TH" else 190; tests test_min_cost_190_when_marketplace_is_th, test_min_cost_100000_when_marketplace_is_id, test_th_excludes_ad_below_190
  - id: R026
    from_status: active
    to_status: validated
    proof: Existing _compute_g66 marketplace branching correct (no code change needed); tests test_compute_g66_uses_juta_when_marketplace_is_id, test_compute_g66_uses_raw_numbers_when_marketplace_is_th
duration: 35m
verification_result: passed
completed_at: 2026-03-18
---

# M003: Hardcoded IDR Cleanup

**Replaced Indonesian-specific number formatting and hardcoded IDR thresholds with international conventions and marketplace-aware values across scoring messages, follower display, and ads cost floors.**

## What Happened

M003 was a single-slice milestone that cleaned up four IDR-specific artifacts left over from the original Indonesia-only system. The work touched three calculator files and one new DB migration.

**Follower threshold formatting (R023):** The scoring message for insufficient followers displayed `>50.000` (Indonesian dot-as-thousands convention) across three sources of truth — `DEFAULT_RULES` in `rules.py`, the inline fallback in `messages.py`, and DB-stored message templates. All three were updated to `>50,000` (international comma). Migration 028 handles the DB-stored templates, following the established `_apply_patches` pattern from migration 027.

**Follower value display (R024):** The `val_str` formatter in `messages.py` applied `.replace(",", ".")` to convert Python's comma-formatted numbers into Indonesian dot notation. This single line was removed so that `40,000` displays as `40,000` instead of `40.000`.

**Ads cost floor (R025):** The BOTTOM ads classifier in `ads_keyword.py` used a hardcoded `min_cost = 100000` — correct for IDR but absurdly high for THB (~$2,800 USD). Changed to `min_cost = 100000 if marketplace != "TH" else 190`, using the established IDR_TO_THB_RATE conversion.

**Juta preservation (R026):** The `_compute_g66` function already correctly branches by marketplace — dividing by 1,000,000 and appending "juta" for ID, using raw comma-formatted numbers for TH. No code change was needed; two new tests lock in the behavior.

The test-driven approach caught one execution gap: T01 claimed to have removed the `.replace(",", ".")` but only updated the inline fallback string. T02's test for R024 correctly failed, the fix was applied, and all 1097 backend tests passed.

## Cross-Slice Verification

Single-slice milestone — no cross-slice integration needed. Verification was done against the five success criteria from the roadmap:

| Success Criterion | Evidence |
|---|---|
| Follower messages display `>50,000` (comma) | `rules.py:65` has `>50,000`; `messages.py:175` has `>50,000`; migration 028 patches DB templates; drift test passes |
| Follower val_str uses comma separator | `.replace(",", ".")` removed from `messages.py`; `test_follower_val_str_uses_comma_when_value_is_40000` passes |
| Ads BOTTOM cost floor: 100,000 ID / 190 TH | `ads_keyword.py:497`: `min_cost = 100000 if marketplace != "TH" else 190`; 3 tests pass |
| Juta convention preserved for ID | `test_compute_g66_uses_juta_when_marketplace_is_id` passes; no code change to `_compute_g66` |
| All existing tests pass | 1097/1097 backend tests green, 0 failures |

**Definition of Done** — all six items verified:
- ✅ R023–R026 satisfied (all four validated with test evidence)
- ✅ Migration 028 updates `>50.000` → `>50,000` in DB templates
- ✅ DEFAULT_RULES, inline fallbacks, and DB templates in sync (drift test passes)
- ✅ TestMigrationTemplatesDrift passes with m028 in replay chain
- ✅ Ads calculator uses marketplace-aware min_cost
- ✅ Full backend suite: 1097/1097 passed

## Requirement Changes

- R023: active → validated — DEFAULT_RULES, inline fallback, and DB migration all use `>50,000`; drift test and 2 unit tests prove it
- R024: active → validated — `.replace(",", ".")` removed; `test_follower_val_str_uses_comma_when_value_is_40000` proves comma output
- R025: active → validated — `min_cost` branches by marketplace (190 TH / 100,000 ID); 3 unit tests prove it
- R026: active → validated — existing `_compute_g66` branching correct; 2 unit tests lock in juta for ID, raw numbers for TH

## Forward Intelligence

### What the next milestone should know
- All IDR-specific hardcoding in the scoring and ads calculators is now cleaned up. The system uses international comma convention consistently for number formatting.
- The drift test replay chain is 6 migrations deep (012→019→020→021→027→028). Any future migration modifying scoring message templates must be appended to `_build_effective_db_templates()` in `test_scoring.py`.
- Backend test count is 1097. Frontend test count is 602 (unchanged by this milestone — no frontend changes).

### What's fragile
- The drift test replay chain in `test_scoring.py::_build_effective_db_templates()` — forgetting to add a new message-template migration causes a confusing test failure that doesn't obviously point to the missing migration step.
- The `min_cost` threshold in `ads_keyword.py` is a simple if/else on marketplace. If a third marketplace is added, this needs to become a lookup table or config-driven value.

### Authoritative diagnostics
- `pytest -k "comma or juta or drift" backend/tests/unit/calculators/test_scoring.py -v` — covers R023/R024/R026; drift test failure output shows exact key path and DB vs Code values
- `pytest -k "min_cost or marketplace" backend/tests/unit/calculators/test_ads_keyword.py -v` — covers R025 in isolation
- Full suite: `PYTHONPATH=backend python -m pytest backend/tests/ -x -q` — 1097 tests, ~1.4s

### What assumptions changed
- T01 task plan assumed all production changes in `messages.py` would be captured in a single pass. The `.replace(",", ".")` removal on line 164 was missed by T01 and only caught by T02's test. Lesson: always verify git diffs against task summary claims.

## Files Created/Modified

- `backend/app/calculators/scoring/rules.py` — Changed `>50.000` to `>50,000` in DEFAULT_RULES followers message_fail
- `backend/app/calculators/scoring/messages.py` — Removed `.replace(",", ".")` from val_str; changed inline fallback to `>50,000`
- `backend/app/calculators/ads_keyword.py` — Made min_cost marketplace-aware: 190 for TH, 100,000 otherwise
- `backend/app/db/migrations/versions/028_fix_follower_threshold_comma_separator.py` — New migration with _apply_patches for followers comma formatting
- `backend/tests/unit/calculators/test_scoring.py` — Added m028 to drift test replay chain; added 6 new tests (R023/R024/R026)
- `backend/tests/unit/calculators/test_ads_keyword.py` — Added 3 new tests for R025 marketplace-aware min_cost
