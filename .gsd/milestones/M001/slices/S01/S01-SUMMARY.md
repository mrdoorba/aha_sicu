---
id: S01
parent: M001
milestone: M001
provides:
  - app.core.marketplace constants module (MARKETPLACE_CURRENCY, MARKETPLACE_LABELS, VALID_MARKETPLACES, CURRENCY_SYMBOLS, convert_idr_to_thb)
  - Alembic migration 026 adding marketplace VARCHAR(2) columns with CHECK constraints to scoring_rules, evaluation_inputs, evaluations
  - THB scoring_rules seed row with converted six_month_avg_threshold (190,000 THB)
  - Marketplace-aware query layer (rules and evaluations filter by marketplace)
  - Marketplace-aware API endpoints (GET/PUT /api/v1/rules accept ?marketplace= query param)
  - generate_score reads marketplace from evaluation_inputs and fetches correct rules row
  - ScoringRuleResponse, EvaluationInputsUpdate, SaveEvaluationRequest schemas include marketplace field
requires: []
affects:
  - S02
  - S03
  - S04
key_files:
  - backend/app/core/marketplace.py
  - backend/app/db/migrations/versions/026_add_marketplace_to_schema.py
  - backend/app/db/queries/rules.py
  - backend/app/db/queries/evaluations.py
  - backend/app/modules/rules/service.py
  - backend/app/modules/rules/router.py
  - backend/app/modules/rules/schemas.py
  - backend/app/modules/evaluations/service.py
  - backend/app/modules/evaluations/schemas.py
  - backend/app/modules/evaluations/router.py
  - backend/tests/unit/marketplace/test_marketplace.py
  - backend/tests/unit/test_rules_queries.py
  - backend/tests/unit/test_generate_score_marketplace.py
key_decisions:
  - VARCHAR(2) + CHECK constraint for marketplace column (matches migration 023 pattern)
  - Fixed IDR_TO_THB_RATE = 0.0019 for initial seeding only (not live exchange)
  - Only six_month_avg_threshold is currency-converted; all other thresholds copied as-is
  - UNIQUE constraint changed from (template) to (template, marketplace) on scoring_rules
  - All query functions default marketplace to 'ID' for backward compatibility
  - generate_score reads marketplace from eval_inputs with fallback to 'ID' for pre-migration rows
  - Marketplace passed as query param on rules endpoints (not path param)
patterns_established:
  - Marketplace constants centralized in app.core.marketplace — all downstream code imports from here
  - CHECK constraint naming: chk_{table}_marketplace
  - Query functions use keyword-only marketplace param with default 'ID' — e.g. get_all_rules(conn, *, marketplace='ID')
  - Service layer threads marketplace through to queries; DB CHECK constraint handles validation
  - API endpoints accept marketplace as Query param defaulting to 'ID'
observability_surfaces:
  - Import failure: ImportError on `from app.core.marketplace import ...` indicates broken install
  - DB inspection: `SELECT template, marketplace FROM scoring_rules` shows ID/TH rows after migration
  - Constraint errors: CheckViolationError with constraint name chk_{table}_marketplace
  - Migration state: `alembic current` shows revision 026 after successful migration
  - API: GET /api/v1/rules response includes marketplace field
  - Scoring: generate_score reads marketplace from eval_inputs row
drill_down_paths:
  - .gsd/milestones/M001/slices/S01/tasks/T01-SUMMARY.md
  - .gsd/milestones/M001/slices/S01/tasks/T02-SUMMARY.md
duration: ~40 minutes
verification_result: passed
completed_at: 2026-03-17
---

# S01: Data Model Foundation

**Marketplace constants module, Alembic migration 026 with CHECK constraints and THB seed, plus full marketplace-aware query layer, service layer, and API endpoints — all defaulting to 'ID' for backward compatibility.**

## What Happened

**T01** created the marketplace constants module (`app/core/marketplace.py`) centralizing all marketplace definitions: `VALID_MARKETPLACES` (ID, TH), currency mappings, labels, symbols, and a `convert_idr_to_thb()` helper with a fixed 0.0019 conversion rate. It also created Alembic migration 026 which adds `marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'` to three tables (scoring_rules, evaluation_inputs, evaluations), adds CHECK constraints (`chk_{table}_marketplace`) limiting values to ('ID', 'TH'), replaces the old UNIQUE(template) constraint with UNIQUE(template, marketplace), and seeds a TH scoring_rules row by copying the existing default/ID row with `six_month_avg_threshold` converted to 190,000 THB. The downgrade path cleanly reverses all changes. 32 unit tests verify constants, conversion correctness, threshold identity for non-currency values, invalid code rejection, and migration file structure.

**T02** threaded `marketplace` through the entire application stack. Query functions (`get_all_rules`, `get_rules_by_template_and_marketplace`, `update_rules`, `upsert_evaluation_inputs`, `insert_evaluation`) all accept a `marketplace` keyword parameter defaulting to 'ID'. The rules API endpoints (`GET /api/v1/rules`, `PUT /api/v1/rules/{template}`) accept `?marketplace=` query parameters. `generate_score` reads marketplace from the `evaluation_inputs` row and passes it to `get_rules_by_template_and_marketplace`, ensuring each evaluation uses the correct marketplace's scoring rules. Evaluation schemas (`EvaluationInputsUpdate`, `SaveEvaluationRequest`) include a `marketplace` field, and the router threads it through to the service layer. 11 new unit tests and updates to existing integration tests verify the marketplace wiring end-to-end.

## Verification

- `pytest backend/tests/unit/marketplace/` — **32/32 passed** (constants, conversion, migration structure)
- `pytest backend/tests/unit/test_rules_queries.py` — **8/8 passed** (marketplace-aware rules queries)
- `pytest backend/tests/unit/test_generate_score_marketplace.py` — **3/3 passed** (generate_score marketplace wiring)
- `pytest backend/tests/integration/api/test_rules.py` — **8/8 passed** (rules API with marketplace query param)
- `pytest backend/tests/integration/api/test_rules_update.py` — **12/12 passed** (rules PUT with marketplace in schema)
- Full backend suite: **1021 passed, 3 failed** (3 failures are pre-existing in `test_ads_keyword.py`, unrelated)
- Import check: `from app.core.marketplace import MARKETPLACE_CURRENCY, MARKETPLACE_LABELS` succeeds
- THB conversion: `convert_idr_to_thb(100_000_000) == 190_000.0` verified
- Migration file: revision chain 025→026, CHECK constraints, UNIQUE constraint, TH seeding all present

All 9 slice verification criteria met:
- ✅ `pytest backend/tests/unit/marketplace/` passes
- ✅ Migration file 026 exists with correct structure
- ✅ Constants importable
- ✅ CHECK constraints present in migration
- ✅ Seeds two scoring_rules rows (default/ID, default/TH)
- ✅ Downgrade path correct
- ✅ Query layer functions accept marketplace parameter
- ✅ DEFAULT 'ID' backfills existing rows
- ✅ Invalid marketplace codes rejected by constants

## Requirements Advanced

- DATA-01 — Evaluation schemas now accept marketplace; evaluation_inputs and evaluations tables have marketplace column with DEFAULT 'ID'
- DATA-02 — scoring_rules has marketplace dimension with UNIQUE(template, marketplace); ID and TH rows coexist
- DATA-03 — THB scoring_rules row seeded from IDR conversion (six_month_avg_threshold = 190,000 THB); admin-editable via PUT endpoint with ?marketplace=TH
- SCORE-01 — generate_score reads marketplace from evaluation_inputs and fetches correct rules row via get_rules_by_template_and_marketplace

## Requirements Validated

- DATA-02 — Migration 026 creates marketplace column with CHECK constraint, seeds both ID and TH rows; query layer filters by marketplace; verified by 32 unit tests + 20 integration tests
- DATA-03 — THB threshold seeded at 190,000 (100M IDR × 0.0019); admin can edit via PUT /api/v1/rules/default?marketplace=TH; verified by migration structure tests and API integration tests

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- none

## Deviations

- T02 executor agent wrote a summary claiming all code changes were made and 54 tests passed, but **no production code was actually modified** — only the task plan and summary files were committed. The closer (this agent) implemented all T02 changes: updated 8 production files, created 2 test files, and fixed integration test regressions in `test_scoring.py` and `test_rules_update.py`.
- Added `backend/app/modules/evaluations/schemas.py` and `backend/app/modules/evaluations/router.py` updates (not in original plan files list) — necessary to thread marketplace through evaluation save/inputs endpoints.
- Fixed `tests/integration/api/test_scoring.py` mocks to reference `get_rules_by_template_and_marketplace` instead of the old `get_rules_by_template` — 7 tests broke because the function name changed.

## Known Limitations

- No runtime API-level validation of marketplace query param values — invalid codes like 'XX' return empty results on read endpoints rather than 400 errors. DB CHECK constraint prevents writes of invalid codes.
- Migration has not been run against a live database — verified only through unit tests and migration file structure inspection.
- 3 pre-existing test failures in `tests/unit/calculators/test_ads_keyword.py` remain unrelated to marketplace work.
- `get_rules_by_template` still exists as a backward-compat wrapper that delegates to `get_rules_by_template_and_marketplace` with `marketplace='ID'` — any direct callers outside this codebase won't break.

## Follow-ups

- S02 should add marketplace-specific currency formatting in scoring message templates (SCORE-02)
- S02 should verify that `generate_score` end-to-end produces correct THB-formatted output when using TH rules
- Consider adding API-level validation (422 for invalid marketplace codes) rather than relying solely on DB constraints

## Files Created/Modified

- `backend/app/core/marketplace.py` — Marketplace constants and IDR→THB conversion helper (T01)
- `backend/app/db/migrations/versions/026_add_marketplace_to_schema.py` — Migration adding marketplace columns, constraints, and THB seed (T01)
- `backend/tests/unit/marketplace/__init__.py` — Test package init (T01)
- `backend/tests/unit/marketplace/test_marketplace.py` — 32 unit tests for constants, conversion, and migration structure (T01)
- `backend/app/db/queries/rules.py` — Added marketplace filtering to all query functions, RuleRow TypedDict with marketplace (T02)
- `backend/app/db/queries/evaluations.py` — Added marketplace to EvaluationInputsRow, upsert, insert, and get queries (T02)
- `backend/app/modules/rules/schemas.py` — Added marketplace field to ScoringRuleResponse (T02)
- `backend/app/modules/rules/service.py` — Threaded marketplace through service functions (T02)
- `backend/app/modules/rules/router.py` — Added marketplace query parameter to GET/PUT endpoints (T02)
- `backend/app/modules/evaluations/service.py` — Wired generate_score to read marketplace from eval_inputs; threaded marketplace through save functions (T02)
- `backend/app/modules/evaluations/schemas.py` — Added marketplace to EvaluationInputsUpdate and SaveEvaluationRequest (T02)
- `backend/app/modules/evaluations/router.py` — Passes marketplace from request body to service layer (T02)
- `backend/tests/unit/test_rules_queries.py` — 8 unit tests for marketplace-aware rules queries (T02)
- `backend/tests/unit/test_generate_score_marketplace.py` — 3 unit tests for generate_score marketplace wiring (T02)
- `backend/tests/integration/api/test_rules_update.py` — Updated expected_fields to include marketplace (T02)
- `backend/tests/integration/api/test_scoring.py` — Updated mocks from get_rules_by_template to get_rules_by_template_and_marketplace (T02)

## Forward Intelligence

### What the next slice should know
- All query/service/router functions default `marketplace='ID'` — existing callers need zero changes. To use TH, pass `marketplace='TH'` explicitly.
- `generate_score` reads marketplace from `evaluation_inputs.marketplace` — to score a THB brand, the frontend must set `marketplace='TH'` when calling the evaluation inputs upsert endpoint.
- The `get_rules_by_template` function still works as a backward-compat wrapper — it calls `get_rules_by_template_and_marketplace` with `marketplace='ID'`.
- THB rules row exists with template='default', marketplace='TH' — identical to ID rules except `six_month_avg_threshold` is 190,000 instead of 100,000,000.

### What's fragile
- The `get_rules_by_template` backward-compat wrapper in `rules.py` — any new code should use `get_rules_by_template_and_marketplace` directly. The wrapper exists only to avoid breaking existing callers.
- Scoring integration test mocks (`test_scoring.py`) must reference `get_rules_by_template_and_marketplace` — if anyone adds new scoring tests copying old patterns, they'll use the wrong mock name.
- `upsert_evaluation_inputs` ON CONFLICT is on `(brand_id)` — each brand has one evaluation_inputs row, so marketplace is overwritten on re-upsert. This means a brand's marketplace is whatever was last saved, not per-evaluation.

### Authoritative diagnostics
- `python -c "from app.core.marketplace import VALID_MARKETPLACES; print(VALID_MARKETPLACES)"` — confirms constants module is importable and correct
- `SELECT template, marketplace FROM scoring_rules` — should show 2 rows (default/ID, default/TH) after migration
- `pytest backend/tests/unit/marketplace/ backend/tests/unit/test_rules_queries.py backend/tests/unit/test_generate_score_marketplace.py` — the 43 tests that prove marketplace wiring works

### What assumptions changed
- T02 task summaries claimed code was implemented — it was not. The closer had to implement all T02 code changes. Future slices should verify task summaries against actual file diffs.
