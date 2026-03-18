# S01 — International formatting & marketplace-aware ads thresholds — Research

**Date:** 2026-03-18
**Calibration:** Light research — well-understood work using established patterns. All four changes are small, surgical edits to known files with clear existing patterns.

## Summary

This slice covers four requirements (R023–R026), all targeting hardcoded IDR artifacts left over from the Indonesia-only era. The work is straightforward: three files need edits (`rules.py`, `messages.py`, `ads_keyword.py`), one DB migration needs to be created (following the established `_apply_patches` pattern from migration 027), and the `TestMigrationTemplatesDrift` replay chain needs to include the new migration.

R026 (juta convention preserved) requires **no code change** — `_compute_g66` in `computations.py` already branches on marketplace, using juta for ID and raw formatted numbers for TH. The research confirmed this at lines 157–171. Verification is the only task.

All 255 existing calculator tests pass (178 scoring + 77 ads_keyword).

## Recommendation

Execute as four independent tasks: (1) fix `rules.py` + `messages.py` formatting, (2) create DB migration, (3) make ads `min_cost` marketplace-aware, (4) add/update tests. Tasks 1–3 can be done in any order since they touch different files. Task 4 depends on all three.

## Implementation Landscape

### Key Files

- **`backend/app/calculators/scoring/rules.py`** — `DEFAULT_RULES["visitors"]["followers"]["message_fail"]` contains `>50.000`. Change to `>50,000`. (line ~approx in followers section)
- **`backend/app/calculators/scoring/messages.py`** — Two changes needed:
  - **Line with `val_str = f"{int(row.value):,}".replace(",", ".")`** (row 29 handler in `_generate_visitors_messages`) — Remove the `.replace(",", ".")` call. Python's `:,` format already produces comma-separated output.
  - **Inline fallback** `"❌ Total Pengikut = {val_str} [Kurang Baik, nilai disarankan: >50.000]"` (row 29 fail default) — Change `>50.000` to `>50,000`.
- **`backend/app/calculators/ads_keyword.py`** — `min_cost = 100000` on line ~497 in `calculate_sheet2`. Needs marketplace branching: `min_cost = 100000 if marketplace != "TH" else 190`. Both the primary and fallback bottom queries use `min_cost`.
- **`backend/app/core/marketplace.py`** — Already has `IDR_TO_THB_RATE = 0.0019` and `convert_idr_to_thb()`. The ads calculator can either use the constant directly or hardcode 190 (since `round(100000 * 0.0019)` = 190). Hardcoding 190 is simpler and matches D029.
- **`backend/app/db/migrations/versions/`** — New migration `028_fix_follower_threshold_comma_separator.py` following the exact `_apply_patches` pattern from migration 027. Single PATCH entry: `["visitors", "followers", "message_fail"]` changing `>50.000` to `>50,000`.
- **`backend/app/db/migrations/versions/012_add_message_templates.py`** — Contains the seed `>50.000` (line 72). This file is NOT modified — the new migration 028 patches it forward.
- **`backend/app/db/migrations/versions/020_add_brackets_to_all_scoring_messages.py`** — Contains `>50.000` in its PATCHES (line 114). This file is NOT modified — 028 patches on top.
- **`backend/tests/unit/calculators/test_scoring.py`** — `TestMigrationTemplatesDrift._build_effective_db_templates()` (line 2410) must import `m028` and call `m028._apply_patches(db, forward=True)` after `m027`.
- **`backend/app/calculators/scoring/computations.py`** — `_compute_g66` (line 144) already has correct marketplace branching for juta vs raw numbers. **No change needed** — only verify via test.

### Build Order

1. **First: `rules.py` + `messages.py` changes** (R023, R024) — These are the simplest changes and are prerequisites for the drift test to pass after migration 028 is added. Changing `DEFAULT_RULES` *before* creating the migration means the drift test will initially fail (DB says `>50.000`, code says `>50,000`), which is the correct red state.
2. **Second: DB migration 028** — Create `028_fix_follower_threshold_comma_separator.py` with a single `_apply_patches` entry. After this, DB and code are back in sync → drift test should pass.
3. **Third: `ads_keyword.py` min_cost** (R025) — Independent of the formatting changes. Add marketplace parameter awareness to the `min_cost` variable in `calculate_sheet2`.
4. **Fourth: Tests** — Update drift test replay chain. Add/update unit tests for follower formatting (comma not dot), follower fail message (>50,000), ads min_cost marketplace branching, and verify juta is preserved (R026).

### Verification Approach

```bash
# Run from worktree
cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M003

# Full scoring test suite (includes drift test)
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -x -v

# Full ads keyword test suite
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_ads_keyword.py -x -v

# Full backend test suite (regression check)
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/ -x -q
```

Observable behaviors:
- `test_db_templates_match_default_rules` passes with 028 in the replay chain
- Follower fail messages contain `>50,000` (comma), not `>50.000` (dot)
- Follower val_str for 40,000 followers renders as `40,000` not `40.000`
- Ads `calculate_sheet2(..., marketplace="TH")` uses min_cost=190, not 100,000
- `_compute_g66` still uses juta for ID marketplace (no change, just verify)

## Constraints

- **Three sources of truth** must stay in sync: `DEFAULT_RULES`, inline fallback defaults in `_generate_visitors_messages`, and DB templates (via migration). The NOTE at the top of `rules.py` (line 5-11) documents this.
- **Migration 028 must expose `_apply_patches(rules, forward)`** — the drift test imports it directly.
- **Migration `down_revision` must be `"027"`** — the latest migration is 027.
- **`_generate_visitors_messages` does NOT receive a `marketplace` parameter** — it doesn't need one since the formatting change (comma separator) is universal, not marketplace-specific.

## Common Pitfalls

- **Forgetting the inline fallback in messages.py** — The fail default string `"❌ Total Pengikut = {val_str} [Kurang Baik, nilai disarankan: >50.000]"` on row 29 is separate from `DEFAULT_RULES`. Both must change.
- **Forgetting to add m028 to the drift test replay chain** — `_build_effective_db_templates()` at line 2410 of `test_scoring.py` must import and apply the new migration. Without this, the drift test will fail saying DB has `>50.000` while code has `>50,000`.
- **Using the wrong ads min_cost for TH** — D029 specifies 190 THB (= `round(100_000 * 0.0019)`). Don't use 100 or any other number.
