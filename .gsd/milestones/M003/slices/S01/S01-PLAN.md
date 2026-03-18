# S01: International formatting & marketplace-aware ads thresholds

**Goal:** Scoring output shows `>50,000` with comma separator; follower values formatted with commas; ads calculator uses THB-appropriate cost floor (190) for Thai marketplace. DB migration updates stored templates. Juta convention preserved for IDR.
**Demo:** Run the full backend test suite — all tests pass including the migration drift test, new formatting tests, new ads threshold tests, and existing juta verification.

## Must-Haves

- `DEFAULT_RULES` followers `message_fail` uses `>50,000` (comma), not `>50.000` (dot) (R023)
- Inline fallback in `messages.py` uses `>50,000` (R023)
- `val_str` in `messages.py` uses comma thousands separator — no `.replace(",", ".")` (R024)
- DB migration 028 patches stored `>50.000` templates to `>50,000` (R023)
- `TestMigrationTemplatesDrift` replay chain includes migration 028 (R023)
- Ads `min_cost` in `ads_keyword.py` is 100,000 for ID and 190 for TH (R025)
- `_compute_g66` juta convention for ID marketplace is preserved — verified by test (R026)

## Verification

```bash
cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M003

# Full scoring tests (includes drift test + new formatting tests)
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -x -v

# Full ads keyword tests (includes new min_cost tests)
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_ads_keyword.py -x -v

# Full backend suite — zero regressions
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/ -x -q
```

- `test_db_templates_match_default_rules` passes with 028 in replay chain
- Follower fail messages contain `>50,000` (comma), not `>50.000` (dot)
- Follower val_str for 40,000 followers renders as `40,000` not `40.000`
- Ads `calculate_sheet2(..., marketplace="TH")` uses min_cost=190
- Ads `calculate_sheet2(..., marketplace="ID")` uses min_cost=100,000
- `_compute_g66` still uses juta for ID marketplace (no code change, just verify)

## Observability / Diagnostics

- **Follower formatting:** Run `_generate_visitors_messages` with a mock row (value=40000, row=29, verdict="❌") and inspect `row.message` — must contain `40,000` (comma) and `>50,000` (comma), never dot-separated
- **Ads min_cost:** In `calculate_sheet2`, add a breakpoint or log at `min_cost =` line — value is 190 for TH, 100000 for all others; visible in the BOTTOM ads filter output
- **Migration drift:** `TestMigrationTemplatesDrift` replays all migrations on a copy of seed data and diffs against `DEFAULT_RULES` — any mismatch surfaces as a failing assertion with the exact key path and expected vs actual values
- **Failure visibility:** If a stored DB template still has `>50.000` after migration 028, the drift test emits `AssertionError: rules["visitors"]["followers"]["message_fail"]` with both values, identifying the exact stale path
- **Redaction:** No PII or secrets involved in these changes — all values are display-format thresholds and currency constants

## Verification

### Diagnostic / failure-path check

```bash
cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M003

# Verify migration 028 _apply_patches handles already-patched data gracefully (idempotency)
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "
from app.db.migrations.versions import _028_fix_follower_threshold_comma_separator as m028
import copy
from app.calculators.scoring.rules import DEFAULT_RULES
rules = copy.deepcopy(DEFAULT_RULES)
# First pass — should patch
assert m028._apply_patches(rules, forward=True) == False, 'DEFAULT_RULES already has commas, so patch should be no-op'
print('Idempotency check passed: _apply_patches returns False on already-patched data')
"
```

## Tasks

- [x] **T01: Fix follower formatting, create migration 028, and add marketplace-aware ads min_cost** `est:30m`
  - Why: All four production code changes (R023, R024, R025, R026 verification) — three files edited plus one migration created. These are small, independent, surgical edits with no cross-dependencies.
  - Files: `backend/app/calculators/scoring/rules.py`, `backend/app/calculators/scoring/messages.py`, `backend/app/calculators/ads_keyword.py`, `backend/app/db/migrations/versions/028_fix_follower_threshold_comma_separator.py`
  - Do: (1) In `rules.py`, change `>50.000` to `>50,000` in DEFAULT_RULES followers message_fail. (2) In `messages.py`, remove `.replace(",", ".")` from val_str formatting and change inline fallback `>50.000` to `>50,000`. (3) In `ads_keyword.py`, branch `min_cost` by marketplace: 100000 for non-TH, 190 for TH. (4) Create migration 028 following the `_apply_patches` pattern from migration 027, patching `["visitors", "followers", "message_fail"]` from `>50.000` to `>50,000`.
  - Verify: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "from app.calculators.scoring import rules, messages; from app.calculators import ads_keyword; from app.db.migrations.versions import _028_fix_follower_threshold_comma_separator as m028; print('All imports OK')"` — Note: existing tests will partially fail (drift test expects old values) which is expected before T02.
  - Done when: All four files are edited/created, Python imports succeed, and `>50.000` no longer appears in `rules.py`, `messages.py`, or the new migration's forward patches.

- [x] **T02: Update drift test replay chain and add unit tests for all four requirements** `est:45m`
  - Why: Closes the slice by proving all four requirements (R023–R026) through tests. Updates the drift test to include migration 028, adds formatting assertions, adds ads threshold assertions, and verifies juta preservation.
  - Files: `backend/tests/unit/calculators/test_scoring.py`, `backend/tests/unit/calculators/test_ads_keyword.py`
  - Do: (1) In `test_scoring.py` `_build_effective_db_templates()`, import m028 and call `m028._apply_patches(db, forward=True)` after m027 in the replay chain. (2) Add test for follower val_str comma formatting (40,000 not 40.000). (3) Add test for follower fail message containing `>50,000`. (4) In `test_ads_keyword.py`, add tests verifying `min_cost=190` for TH marketplace and `min_cost=100000` for ID marketplace in BOTTOM ads calculation. (5) Add/verify test that `_compute_g66` uses juta for ID marketplace and raw numbers for TH.
  - Verify: Full backend test suite passes — `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/ -x -q`
  - Done when: All backend tests pass (0 failures), including the drift test with m028, new formatting tests, new ads threshold tests, and juta verification test. Requirements R023–R026 are all validated.

## Files Likely Touched

- `backend/app/calculators/scoring/rules.py`
- `backend/app/calculators/scoring/messages.py`
- `backend/app/calculators/ads_keyword.py`
- `backend/app/db/migrations/versions/028_fix_follower_threshold_comma_separator.py`
- `backend/tests/unit/calculators/test_scoring.py`
- `backend/tests/unit/calculators/test_ads_keyword.py`
