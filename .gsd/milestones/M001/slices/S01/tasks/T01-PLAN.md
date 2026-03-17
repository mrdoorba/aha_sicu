# T01: 01-data-model-foundation 01

**Slice:** S01 — **Milestone:** M001

## Description

Create the marketplace constants module and the Alembic migration that adds the marketplace column to scoring_rules, evaluation_inputs, and evaluations tables, seeds THB rules, and updates constraints.

Purpose: Establishes the data foundation for multi-marketplace support. Without this migration, no downstream query or service changes can reference the marketplace dimension.
Output: `app/core/marketplace.py` constants, migration `026_add_marketplace_to_schema.py`, unit tests for constants and conversion correctness.

## Must-Haves

- [ ] "scoring_rules table has marketplace VARCHAR(2) NOT NULL column with CHECK constraint"
- [ ] "scoring_rules UNIQUE constraint is (template, marketplace) not just (template)"
- [ ] "evaluation_inputs table has marketplace VARCHAR(2) NOT NULL DEFAULT 'ID' column"
- [ ] "evaluations table has marketplace VARCHAR(2) NOT NULL DEFAULT 'ID' column"
- [ ] "Two scoring_rules rows exist: default/ID and default/TH"
- [ ] "THB six_month_avg_threshold equals 100000000 * 0.0019 = 190000.0"
- [ ] "All non-currency thresholds are identical between ID and TH rows"
- [ ] "MARKETPLACE_CURRENCY and MARKETPLACE_LABELS constants are importable from app.core.marketplace"

## Files

- `backend/app/core/marketplace.py`
- `backend/app/db/migrations/versions/026_add_marketplace_to_schema.py`
- `backend/tests/unit/marketplace/__init__.py`
- `backend/tests/unit/marketplace/test_marketplace.py`

## Steps

1. Create `backend/app/core/marketplace.py` with `MARKETPLACE_CURRENCY`, `MARKETPLACE_LABELS`, `VALID_MARKETPLACES`, and a `convert_idr_to_thb(value)` helper
2. Create `backend/tests/unit/marketplace/__init__.py` (empty)
3. Create `backend/tests/unit/marketplace/test_marketplace.py` with tests for constants importability, THB conversion math, non-currency threshold identity, and invalid marketplace rejection
4. Run tests — expect failures (Red phase)
5. Create `backend/app/db/migrations/versions/026_add_marketplace_to_schema.py` with:
   - Add `marketplace VARCHAR(2)` + CHECK constraint + NOT NULL DEFAULT 'ID' to `scoring_rules`, `evaluation_inputs`, `evaluations`
   - Update `scoring_rules` UNIQUE from `(template)` to `(template, marketplace)`
   - Seed THB row by copying existing `default/ID` row and converting `six_month_avg_threshold` (100M IDR × 0.0019 = 190,000 THB)
   - Downgrade reverses all changes
6. Run tests — expect pass (Green phase)
7. Verify migration SQL is syntactically valid by reviewing generated statements

## Observability Impact

- **New signal:** `app.core.marketplace` module becomes importable — absence means broken install/packaging.
- **DB inspection:** After migration, `SELECT template, marketplace FROM scoring_rules` shows two rows. `SELECT marketplace, rules->'business'->'six_month_avg_threshold'->'threshold' FROM scoring_rules WHERE marketplace='TH'` returns `190000.0`.
- **Constraint errors:** Invalid marketplace values produce `CheckViolationError` with constraint names `chk_scoring_rules_marketplace`, `chk_evaluation_inputs_marketplace`, `chk_evaluations_marketplace` — these are grep-able in logs.
- **Failure state:** If migration fails midway, `alembic current` shows the DB stuck before revision `026`. Partial state is detectable via `\d scoring_rules` showing presence/absence of `marketplace` column.
