# S01: Data Model Foundation

**Goal:** Create the marketplace constants module and the Alembic migration that adds the marketplace column to scoring_rules, evaluation_inputs, and evaluations tables, seeds THB rules, and updates constraints.
**Demo:** Create the marketplace constants module and the Alembic migration that adds the marketplace column to scoring_rules, evaluation_inputs, and evaluations tables, seeds THB rules, and updates constraints.

## Must-Haves


## Tasks

- [x] **T01: 01-data-model-foundation 01**
  - Create the marketplace constants module and the Alembic migration that adds the marketplace column to scoring_rules, evaluation_inputs, and evaluations tables, seeds THB rules, and updates constraints.

Purpose: Establishes the data foundation for multi-marketplace support. Without this migration, no downstream query or service changes can reference the marketplace dimension.
Output: `app/core/marketplace.py` constants, migration `026_add_marketplace_to_schema.py`, unit tests for constants and conversion correctness.
- [ ] **T02: 01-data-model-foundation 02**
  - Update all query functions, service layer, and API endpoints to accept and filter by marketplace. Wire generate_score to read marketplace from evaluation_inputs and fetch the correct rules row.

Purpose: Without these changes, the migration data (marketplace column, THB rules) is unused. This plan makes the application code marketplace-aware while maintaining backward compatibility (all endpoints default to 'ID').
Output: Updated queries, services, router, schemas, and tests proving marketplace filtering works end-to-end.

## Verification

- [ ] `pytest backend/tests/unit/marketplace/` passes — constants importable, THB conversion correct, non-currency thresholds identical
- [ ] Migration file `026_add_marketplace_to_schema.py` exists with upgrade/downgrade and proper revision chain
- [ ] `python -c "from app.core.marketplace import MARKETPLACE_CURRENCY, MARKETPLACE_LABELS"` succeeds from `backend/`
- [ ] Migration upgrade SQL adds CHECK constraints on marketplace columns
- [ ] Migration seeds two scoring_rules rows: `(default, ID)` and `(default, TH)`
- [ ] Downgrade path drops marketplace columns and restores original UNIQUE constraint on template
- [ ] Query layer functions accept marketplace parameter (verified in T02)
- [ ] All existing evaluation_inputs and evaluations rows default to marketplace='ID' (verified via migration DEFAULT)
- [ ] **Failure path:** test verifies that invalid marketplace codes (e.g., 'XX') are rejected by constants

## Observability / Diagnostics

- **Runtime signals:** Migration logs (Alembic output) show `026_add_marketplace` applied successfully. Marketplace constants are importable — failure surfaces as `ImportError` at service startup.
- **Inspection surfaces:** `SELECT DISTINCT marketplace FROM scoring_rules` shows `{'ID', 'TH'}` after migration. `SELECT template, marketplace, rules->'business'->'six_month_avg_threshold'->'threshold' FROM scoring_rules` verifies THB threshold.
- **Failure visibility:** CHECK constraint violations surface as `asyncpg.CheckViolationError` with constraint name `chk_scoring_rules_marketplace` / `chk_evaluation_inputs_marketplace` / `chk_evaluations_marketplace`. These are catchable and distinguishable from other DB errors.
- **Redaction:** No sensitive data in marketplace constants — no redaction needed.

## Files Likely Touched

- `backend/app/core/marketplace.py`
- `backend/app/db/migrations/versions/026_add_marketplace_to_schema.py`
- `backend/tests/unit/marketplace/__init__.py`
- `backend/tests/unit/marketplace/test_marketplace.py`
- `backend/app/db/queries/rules.py`
- `backend/app/db/queries/evaluations.py`
- `backend/app/modules/rules/service.py`
- `backend/app/modules/rules/router.py`
- `backend/app/modules/rules/schemas.py`
- `backend/app/modules/evaluations/service.py`
- `backend/tests/unit/test_evaluation_queries.py`
- `backend/tests/integration/api/test_rules.py`
