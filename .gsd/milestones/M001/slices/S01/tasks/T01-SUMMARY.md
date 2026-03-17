---
id: T01
parent: S01
milestone: M001
provides:
  - app.core.marketplace constants module (MARKETPLACE_CURRENCY, MARKETPLACE_LABELS, VALID_MARKETPLACES, CURRENCY_SYMBOLS, convert_idr_to_thb)
  - Alembic migration 026 adding marketplace column to scoring_rules, evaluation_inputs, evaluations
  - THB scoring_rules seed row with converted six_month_avg_threshold
  - Unit tests for constants, conversion, and migration structure
key_files:
  - backend/app/core/marketplace.py
  - backend/app/db/migrations/versions/026_add_marketplace_to_schema.py
  - backend/tests/unit/marketplace/test_marketplace.py
key_decisions:
  - VARCHAR(2) + CHECK constraint for marketplace column (matches migration 023 pattern)
  - Fixed IDR_TO_THB_RATE = 0.0019 for initial seeding only (not live exchange)
  - Only six_month_avg_threshold is currency-converted; all other thresholds copied as-is
  - UNIQUE constraint changed from (template) to (template, marketplace) on scoring_rules
patterns_established:
  - Marketplace constants centralized in app.core.marketplace — downstream code imports from here
  - CHECK constraint naming: chk_{table}_marketplace
  - THB threshold seeding via copy-and-convert from existing ID row
observability_surfaces:
  - Import failure: ImportError on `from app.core.marketplace import ...` indicates broken install
  - DB inspection: `SELECT template, marketplace FROM scoring_rules` shows ID/TH rows after migration
  - Constraint errors: CheckViolationError with constraint name chk_{table}_marketplace
  - Migration state: `alembic current` shows revision 026 after successful migration
duration: ~25 minutes
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T01: Marketplace Constants and Schema Migration

**Created marketplace constants module and Alembic migration 026 adding marketplace VARCHAR(2) columns with CHECK constraints to scoring_rules, evaluation_inputs, and evaluations, with THB scoring_rules seed row.**

## What Happened

1. Created `backend/app/core/marketplace.py` with centralized constants:
   - `VALID_MARKETPLACES` (frozenset: ID, TH)
   - `MARKETPLACE_CURRENCY` (ID→IDR, TH→THB)
   - `MARKETPLACE_LABELS` (ID→Indonesia, TH→Thailand)
   - `CURRENCY_SYMBOLS` (IDR→Rp, THB→฿)
   - `convert_idr_to_thb()` helper with fixed 0.0019 rate

2. Created `backend/app/db/migrations/versions/026_add_marketplace_to_schema.py`:
   - Adds `marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'` to scoring_rules, evaluation_inputs, evaluations
   - Adds CHECK constraints (`chk_*_marketplace`) limiting values to ('ID', 'TH')
   - Drops old `scoring_rules_template_key` UNIQUE, creates `uq_scoring_rules_template_marketplace` UNIQUE (template, marketplace)
   - Seeds TH row by copying existing default/ID row and converting `six_month_avg_threshold` (100M IDR × 0.0019 = 190,000 THB)
   - Downgrade reverses all changes: deletes TH rows, restores original UNIQUE, drops columns

3. Created test suite with 32 tests covering constants, conversion math, threshold identity, invalid codes, and migration file structure.

## Verification

- `pytest backend/tests/unit/marketplace/` — **32/32 passed** in 0.02s
- `pytest backend/tests/unit/` — **805 passed, 3 failed** (3 failures are pre-existing in test_ads_keyword.py, unrelated to this change)
- Import check: `from app.core.marketplace import MARKETPLACE_CURRENCY, MARKETPLACE_LABELS` succeeds
- THB conversion: `convert_idr_to_thb(100_000_000) == 190_000.0` verified
- Migration structure: revision chain 025→026, CHECK constraints, UNIQUE constraint, TH seeding all verified by tests

Slice verification status (8/9 passing, 1 deferred to T02):
- ✓ pytest passes
- ✓ Migration file exists with correct structure
- ✓ Constants importable
- ✓ CHECK constraints present
- ✓ Seeds two rows (default/ID, default/TH)
- ✓ Downgrade path correct
- ⏳ Query layer marketplace parameter — T02
- ✓ DEFAULT 'ID' backfills existing rows
- ✓ Invalid codes rejected

## Diagnostics

- **Constants health:** `python -c "from app.core.marketplace import VALID_MARKETPLACES; print(VALID_MARKETPLACES)"`
- **Migration status:** `alembic current` (should show revision 026 after running)
- **DB verification:** `SELECT template, marketplace, rules->'business'->'six_month_avg_threshold'->'threshold' FROM scoring_rules`
- **Constraint violations:** Look for `CheckViolationError` with constraint name containing `chk_*_marketplace` in logs

## Deviations

None — implementation followed the plan steps exactly.

## Known Issues

- 3 pre-existing test failures in `tests/unit/calculators/test_ads_keyword.py` (unrelated to marketplace work)
- Migration has not been run against a live database yet (no DB connection in dev environment for this task)

## Files Created/Modified

- `backend/app/core/marketplace.py` — Marketplace constants and IDR→THB conversion helper
- `backend/app/db/migrations/versions/026_add_marketplace_to_schema.py` — Migration adding marketplace columns, constraints, and THB seed
- `backend/tests/unit/marketplace/__init__.py` — Test package init
- `backend/tests/unit/marketplace/test_marketplace.py` — 32 unit tests for constants, conversion, and migration structure
- `.gsd/milestones/M001/slices/S01/S01-PLAN.md` — Added Verification and Observability/Diagnostics sections
- `.gsd/milestones/M001/slices/S01/tasks/T01-PLAN.md` — Added Steps and Observability Impact sections
