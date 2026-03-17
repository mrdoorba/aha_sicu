---
id: T02
parent: S01
milestone: M001
provides:
  - Marketplace-aware query layer (rules and evaluations filter by marketplace)
  - Marketplace-aware API endpoints (GET/PUT /api/v1/rules accept ?marketplace= query param)
  - generate_score reads marketplace from evaluation_inputs and fetches correct rules row
  - ScoringRuleResponse and evaluation schemas include marketplace field
key_files:
  - backend/app/db/queries/rules.py
  - backend/app/db/queries/evaluations.py
  - backend/app/modules/rules/service.py
  - backend/app/modules/rules/router.py
  - backend/app/modules/rules/schemas.py
  - backend/app/modules/evaluations/service.py
  - backend/app/modules/evaluations/schemas.py
  - backend/app/modules/evaluations/router.py
  - backend/tests/unit/test_rules_queries.py
  - backend/tests/unit/test_evaluation_queries.py
  - backend/tests/unit/test_generate_score_marketplace.py
  - backend/tests/integration/api/test_rules.py
  - backend/tests/integration/api/test_rules_update.py
key_decisions:
  - All query functions default marketplace to 'ID' for backward compatibility — no existing callers need changes
  - generate_score reads marketplace from eval_inputs row with fallback to 'ID' if key missing (handles pre-migration rows)
  - Marketplace passed as query param on rules endpoints (not path param) to keep existing URL structure
patterns_established:
  - Query functions use keyword-only marketplace param with default 'ID' — e.g. get_all_rules(conn, *, marketplace='ID')
  - Service layer threads marketplace through to queries without validation (DB CHECK constraint handles invalid values)
  - API endpoints accept marketplace as Query param defaulting to 'ID'
observability_surfaces:
  - API: GET /api/v1/rules response includes marketplace field — consumers can verify which rules set is returned
  - Scoring: generate_score logs marketplace from eval_inputs — visible in standard request logs
  - DB: SELECT marketplace FROM evaluation_inputs WHERE brand_id=X shows brand's configured marketplace
  - DB: SELECT marketplace FROM scoring_rules shows available rule sets (should return ID and TH)
  - Failure: Missing TH rules row surfaces as None from get_rules_by_template_and_marketplace — scoring proceeds with rules=None
duration: ~15 minutes
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T02: Marketplace-Aware Query Layer, Services, and API Endpoints

**Updated all query functions, service layer, and API endpoints to accept and filter by marketplace. Wired generate_score to read marketplace from evaluation_inputs and fetch the correct rules row.**

## What Happened

1. **Updated `backend/app/db/queries/rules.py`** — Added `RuleRow` TypedDict with `marketplace` field. All three query functions (`get_all_rules`, `get_rules_by_template_and_marketplace`, `update_rules`) now include `marketplace` in SELECT, WHERE, and RETURNING clauses. All accept `marketplace` parameter defaulting to `'ID'`.

2. **Updated `backend/app/db/queries/evaluations.py`** — Added `marketplace` to `EvaluationInputsRow` TypedDict. `get_evaluation_inputs` SELECT now includes marketplace. `upsert_evaluation_inputs` accepts marketplace as 5th positional parameter (`$5`), includes it in INSERT/ON CONFLICT UPDATE/RETURNING. `insert_evaluation` accepts marketplace as `$12` parameter.

3. **Updated `backend/app/modules/rules/schemas.py`** — Added `marketplace: str = "ID"` field to `ScoringRuleResponse`.

4. **Updated `backend/app/modules/rules/service.py`** — Threaded `marketplace` parameter through `get_all_rules` and `update_rules` service functions to corresponding query functions.

5. **Updated `backend/app/modules/rules/router.py`** — Added `marketplace: str = Query("ID")` parameter to both `GET /api/v1/rules` and `PUT /api/v1/rules/{template}` endpoints.

6. **Updated `backend/app/modules/evaluations/service.py`** — `generate_score` now reads `marketplace` from `eval_inputs` dict (with fallback to `'ID'`) and passes it to `get_rules_by_template_and_marketplace`. `save_evaluation` and `save_evaluation_inputs` accept and thread `marketplace`.

7. **Updated `backend/app/modules/evaluations/schemas.py`** — Added `marketplace: str = "ID"` to `EvaluationInputsUpdate` and `SaveEvaluationRequest`.

8. **Updated `backend/app/modules/evaluations/router.py`** — Passes `body.marketplace` through `update_evaluation` and `save_evaluation_endpoint` to service layer.

9. **Wrote 54 tests** across 5 test files covering all must-haves:
   - 9 unit tests for rules queries (marketplace filtering, SQL verification)
   - 18 unit tests for evaluation queries (upsert, insert, marketplace params)
   - 3 unit tests for generate_score marketplace wiring
   - 12 integration tests for rules API endpoints (marketplace query param)
   - 12 integration tests for rules PUT endpoint (schema validation)

## Verification

- `pytest tests/unit/test_rules_queries.py tests/unit/test_evaluation_queries.py tests/unit/test_generate_score_marketplace.py tests/integration/api/test_rules.py tests/integration/api/test_rules_update.py` — **54/54 passed**
- Full test suite: **1031 passed, 3 failed** (3 failures are pre-existing in `test_ads_keyword.py`, unrelated to this change)
- All 11 must-haves verified by passing tests:
  - ✅ get_all_rules defaults to marketplace='ID'
  - ✅ get_all_rules with marketplace='TH' returns THB rules
  - ✅ get_rules_by_template_and_marketplace for TH returns THB row
  - ✅ update_rules WHERE clause includes template AND marketplace
  - ✅ upsert_evaluation_inputs accepts and stores marketplace
  - ✅ upsert_evaluation_inputs RETURNING includes marketplace
  - ✅ insert_evaluation accepts marketplace as $12
  - ✅ generate_score reads marketplace from eval_inputs and passes to rules query
  - ✅ GET /api/v1/rules without ?marketplace= defaults to ID
  - ✅ GET /api/v1/rules?marketplace=TH returns THB rules
  - ✅ ScoringRuleResponse includes marketplace field

Slice verification status (9/9 passing — all criteria met):
- ✅ pytest backend/tests/unit/marketplace/ passes
- ✅ Migration file exists with correct structure
- ✅ Constants importable
- ✅ CHECK constraints present
- ✅ Seeds two rows (default/ID, default/TH)
- ✅ Downgrade path correct
- ✅ Query layer functions accept marketplace parameter
- ✅ DEFAULT 'ID' backfills existing rows
- ✅ Invalid codes rejected by constants

## Diagnostics

- **Rules API:** `curl /api/v1/rules` returns ID rules; `curl /api/v1/rules?marketplace=TH` returns TH rules
- **Scoring pipeline:** Check which rules row generate_score uses: look at `marketplace` field in `evaluation_inputs` for the brand being scored
- **DB inspection:** `SELECT template, marketplace FROM scoring_rules` should show 2 rows (default/ID, default/TH)
- **Failure mode:** If a marketplace has no scoring_rules row, `get_rules_by_template_and_marketplace` returns `None` — scoring proceeds with `rules=None` and `rule_version=1`

## Deviations

- Added `test_generate_score_marketplace.py` (not in original plan files list) to cover the generate_score→rules_query wiring
- Added `test_rules_update.py` updates to ensure response schema includes marketplace field
- Updated `backend/app/modules/evaluations/schemas.py` and `backend/app/modules/evaluations/router.py` (not in original plan files list) — necessary to thread marketplace through the evaluation save/inputs endpoints

## Known Issues

- 3 pre-existing test failures in `tests/unit/calculators/test_ads_keyword.py` (unrelated to marketplace work)
- No runtime validation of marketplace query param values at the API level — invalid codes like 'XX' will return empty results rather than 400 errors (DB CHECK constraint prevents writes of invalid codes)

## Files Created/Modified

- `backend/app/db/queries/rules.py` — Added marketplace filtering to all query functions, RuleRow TypedDict
- `backend/app/db/queries/evaluations.py` — Added marketplace to EvaluationInputsRow, upsert, insert, and get queries
- `backend/app/modules/rules/schemas.py` — Added marketplace field to ScoringRuleResponse
- `backend/app/modules/rules/service.py` — Threaded marketplace through service functions
- `backend/app/modules/rules/router.py` — Added marketplace query parameter to GET/PUT endpoints
- `backend/app/modules/evaluations/service.py` — Wired generate_score to read marketplace from eval_inputs; threaded marketplace through save functions
- `backend/app/modules/evaluations/schemas.py` — Added marketplace to EvaluationInputsUpdate and SaveEvaluationRequest
- `backend/app/modules/evaluations/router.py` — Passes marketplace from request body to service layer
- `backend/tests/unit/test_rules_queries.py` — 9 unit tests for marketplace-aware rules queries
- `backend/tests/unit/test_evaluation_queries.py` — 18 unit tests for marketplace-aware evaluation queries
- `backend/tests/unit/test_generate_score_marketplace.py` — 3 unit tests for generate_score marketplace wiring
- `backend/tests/integration/api/test_rules.py` — 12 integration tests for rules API with marketplace
- `backend/tests/integration/api/test_rules_update.py` — 12 integration tests for rules PUT with marketplace in schema
