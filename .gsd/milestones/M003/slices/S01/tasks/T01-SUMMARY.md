---
id: T01
parent: S01
milestone: M003
provides:
  - Comma-formatted follower threshold (>50,000) in DEFAULT_RULES, messages.py inline fallback, and migration 028
  - Marketplace-aware ads min_cost (190 THB for TH, 100000 IDR for others)
  - DB migration 028 with importable _apply_patches for drift test replay chain
key_files:
  - backend/app/calculators/scoring/rules.py
  - backend/app/calculators/scoring/messages.py
  - backend/app/calculators/ads_keyword.py
  - backend/app/db/migrations/versions/028_fix_follower_threshold_comma_separator.py
key_decisions: []
patterns_established:
  - Migration 028 follows the _apply_patches pattern from 027 — single PATCHES list with (json_path, old, new) tuples
observability_surfaces:
  - Migration 028 _apply_patches returns bool indicating whether any change was made (testable by drift test)
  - Drift test now shows exact mismatch between DB and DEFAULT_RULES at visitors.followers.message_fail path (expected red state until T02 adds m028 to replay chain)
duration: 15m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T01: Fix follower formatting, create migration 028, and add marketplace-aware ads min_cost

**Changed follower threshold from dot separator (>50.000) to comma (>50,000) across all three sources of truth, removed dot-replacing val_str formatting, made ads min_cost marketplace-aware (190 THB / 100000 IDR), and created DB migration 028.**

## What Happened

Four independent production code changes, each touching a different file:

1. **rules.py** — `DEFAULT_RULES["visitors"]["followers"]["message_fail"]` changed from `>50.000` to `>50,000`. Single string replacement.

2. **messages.py** — Two edits in `_generate_visitors_messages` for row 29 (followers): removed `.replace(",", ".")` from the `val_str` formatter so Python's `:,` format produces `40,000` instead of `40.000`, and changed the inline fallback fail message from `>50.000` to `>50,000`.

3. **ads_keyword.py** — Changed `min_cost = 100000` to `min_cost = 100000 if marketplace != "TH" else 190`. The function already receives `marketplace` as a parameter. Both primary and fallback bottom queries reference the same `min_cost` variable.

4. **Migration 028** — New file following the exact `_apply_patches` pattern from migration 027. Single patch entry: `["visitors", "followers", "message_fail"]` old=`>50.000` new=`>50,000`. The function is importable via `importlib.import_module` for the drift test replay chain.

## Verification

- **Import check:** All four production files import without errors; `DEFAULT_RULES` contains `>50,000` and not `>50.000`
- **Migration 028 unit verification:** Forward patch replaces `>50.000`→`>50,000`, reverse patch restores it, idempotency returns `False` on already-patched data
- **Scoring tests:** 177 passed, 1 failed (drift test — expected red state; T02 will add m028 to replay chain)
- **Ads keyword tests:** 77 passed, 0 failed
- **Full backend suite:** 1088 passed, 1 failed (only the expected drift test)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `python -c "from app.calculators.scoring import rules, messages; ..."` (import + rules check) | 0 | ✅ pass | <1s |
| 2 | `python -c "import importlib; m028 = ..."` (migration 028 forward/reverse/idempotency) | 0 | ✅ pass | <1s |
| 3 | `pytest backend/tests/unit/calculators/test_scoring.py -x -v` | 1 | ⚠️ expected fail (drift test) | 3.3s |
| 4 | `pytest backend/tests/unit/calculators/test_ads_keyword.py -x -v` | 0 | ✅ pass (77/77) | 3.3s |
| 5 | `pytest backend/tests/ -q` | 1 | ⚠️ 1088 pass, 1 expected fail | 1.9s |
| 6 | `python -c "... m028._apply_patches(rules, forward=True) == False ..."` (idempotency diagnostic) | 0 | ✅ pass | <1s |

## Diagnostics

- **Drift test failure message** shows exact key path and DB vs Code values: `visitors.followers.message_fail` — this is the intended red state that T02 resolves by adding m028 to the replay chain
- **Migration 028 `_apply_patches`** returns `bool` — callers can check if the patch was actually applied or was a no-op

## Deviations

None — all four changes matched the task plan exactly.

## Known Issues

- `TestMigrationTemplatesDrift::test_db_templates_match_default_rules` fails because the replay chain in `_build_effective_db_templates()` does not yet include migration 028. This is expected and will be fixed in T02.

## Files Created/Modified

- `backend/app/calculators/scoring/rules.py` — Changed `>50.000` to `>50,000` in DEFAULT_RULES followers message_fail
- `backend/app/calculators/scoring/messages.py` — Removed `.replace(",", ".")` from val_str; changed inline fallback to `>50,000`
- `backend/app/calculators/ads_keyword.py` — Made min_cost marketplace-aware: 190 for TH, 100000 otherwise
- `backend/app/db/migrations/versions/028_fix_follower_threshold_comma_separator.py` — New migration with _apply_patches for followers comma formatting
