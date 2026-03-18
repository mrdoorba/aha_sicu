# S01: International formatting & marketplace-aware ads thresholds — UAT

**Milestone:** M003
**Written:** 2026-03-18

## UAT Type

- UAT mode: artifact-driven
- Why this mode is sufficient: All changes are pure calculator logic and DB migration templates — no UI, no API endpoints, no live runtime. Unit tests exercise every code path. Migration drift test proves DB↔code sync.

## Preconditions

- Working directory: `/Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M003`
- Backend venv available at `/Users/mac/HT/Project/aha_sicu/backend/.venv/`
- All commands use `PYTHONPATH=backend` prefix

## Smoke Test

```bash
cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M003
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/ -x -q
```
Expected: 1097 passed, 0 failures.

## Test Cases

### 1. Follower threshold uses comma convention (R023)

1. Run: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -k "test_follower_fail_message_contains_comma_threshold" -v`
2. **Expected:** Test passes. Follower fail message contains `>50,000` and does NOT contain `>50.000`.

### 2. DEFAULT_RULES followers message_fail has comma (R023)

1. Run: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "from app.calculators.scoring.rules import DEFAULT_RULES; msg = DEFAULT_RULES['visitors']['followers']['message_fail']; assert '>50,000' in msg and '>50.000' not in msg; print('PASS:', msg[:80])"`
2. **Expected:** Prints PASS with the message_fail string showing `>50,000`.

### 3. Follower val_str uses comma separator (R024)

1. Run: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -k "test_follower_val_str_uses_comma_when_value_is_40000" -v`
2. **Expected:** Test passes. A follower value of 40,000 renders as `40,000` in the message, never as `40.000`.

### 4. Ads min_cost is 190 for TH marketplace (R025)

1. Run: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_ads_keyword.py -k "test_min_cost_190_when_marketplace_is_th" -v`
2. **Expected:** Test passes. An ad with biaya=500 qualifies for BOTTOM ads in TH marketplace (500 > 190).

### 5. Ads min_cost is 100,000 for ID marketplace (R025)

1. Run: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_ads_keyword.py -k "test_min_cost_100000_when_marketplace_is_id" -v`
2. **Expected:** Test passes. An ad with biaya=500 does NOT qualify for BOTTOM ads in ID marketplace (500 < 100,000).

### 6. Juta convention preserved for ID marketplace (R026)

1. Run: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -k "test_compute_g66_uses_juta_when_marketplace_is_id" -v`
2. **Expected:** Test passes. ID marketplace G66 output contains "juta".

### 7. TH marketplace uses raw numbers, no juta (R026)

1. Run: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -k "test_compute_g66_uses_raw_numbers_when_marketplace_is_th" -v`
2. **Expected:** Test passes. TH marketplace G66 output contains comma-formatted numbers and does NOT contain "juta".

### 8. Migration drift test passes with m028 in replay chain (R023)

1. Run: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -k "test_db_templates_match_default_rules" -v`
2. **Expected:** Test passes. The drift test replays migrations 012→019→020→021→027→028 and the result matches DEFAULT_RULES exactly.

### 9. Migration 028 idempotency

1. Run:
   ```bash
   PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "
   import importlib, copy
   from app.calculators.scoring.rules import DEFAULT_RULES
   m028 = importlib.import_module('app.db.migrations.versions.028_fix_follower_threshold_comma_separator')
   rules = copy.deepcopy(DEFAULT_RULES)
   assert m028._apply_patches(rules, forward=True) == False
   print('PASS: _apply_patches returns False on already-patched data')
   "
   ```
2. **Expected:** Prints PASS. Applying the forward patch to data that already has `>50,000` is a no-op.

## Edge Cases

### TH ad exactly at min_cost boundary (biaya=190)

1. Run: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_ads_keyword.py -k "test_th_excludes_ad_below_190" -v`
2. **Expected:** Test passes. An ad with biaya=100 (below 190) is excluded from TH BOTTOM results.

### Migration 028 reverse patch

1. Run:
   ```bash
   PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "
   import importlib, copy
   from app.calculators.scoring.rules import DEFAULT_RULES
   m028 = importlib.import_module('app.db.migrations.versions.028_fix_follower_threshold_comma_separator')
   rules = copy.deepcopy(DEFAULT_RULES)
   rules['visitors']['followers']['message_fail'] = rules['visitors']['followers']['message_fail'].replace('>50,000', '>50.000')
   m028._apply_patches(rules, forward=True)
   assert '>50,000' in rules['visitors']['followers']['message_fail']
   m028._apply_patches(rules, forward=False)
   assert '>50.000' in rules['visitors']['followers']['message_fail']
   print('PASS: round-trip forward+reverse works')
   "
   ```
2. **Expected:** Prints PASS. Forward converts dot→comma, reverse restores comma→dot.

## Failure Signals

- Any test in `test_scoring.py` or `test_ads_keyword.py` fails — regression in formatting or threshold logic
- Drift test (`test_db_templates_match_default_rules`) fails — DB templates and DEFAULT_RULES are out of sync; check migration 028 replay chain
- String `>50.000` appears in `rules.py` or `messages.py` — formatting revert
- String `.replace(",", ".")` appears in `messages.py` — val_str formatting revert

## Requirements Proved By This UAT

- R023 — Follower threshold display uses international comma convention. Tests 1, 2, 8 prove this.
- R024 — Follower val_str uses comma separator. Test 3 proves this.
- R025 — Ads BOTTOM min_cost is marketplace-aware. Tests 4, 5 prove this.
- R026 — Juta convention preserved for ID, raw for TH. Tests 6, 7 prove this.

## Not Proven By This UAT

- Live database migration execution (028 against a real PostgreSQL instance with existing scoring_rules rows) — only the `_apply_patches` logic is tested, not the full Alembic upgrade path
- Visual rendering of formatted numbers in the frontend UI — backend-only changes

## Notes for Tester

- All tests run from the worktree directory with `PYTHONPATH=backend` and the main repo venv
- The migration 028 file starts with a digit (`028_...`) so it cannot be imported with `from ... import` — use `importlib.import_module()` as shown in the test cases
- If the drift test fails, the error message shows the exact key path and both DB and Code values — this is the most diagnostic signal for template sync issues
