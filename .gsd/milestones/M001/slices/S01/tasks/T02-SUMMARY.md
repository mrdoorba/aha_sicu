---
id: T02
parent: S01
milestone: M001
provides:
<<<<<<< Updated upstream
  - Marketplace-aware query layer (rules and evaluations filter by marketplace)
  - Marketplace-aware API endpoints (GET/PUT /api/v1/rules accept ?marketplace= query param)
  - generate_score reads marketplace from evaluation_inputs and fetches correct rules row
  - ScoringRuleResponse and evaluation schemas include marketplace field
=======
  - Marketplace-aware query layer (rules and evaluations)
  - Rules API endpoint with ?marketplace= query parameter
  - generate_score reads marketplace from evaluation_inputs and fetches correct rules row
  - Marketplace field in ScoringRuleResponse, EvaluationInputsUpdate, SaveEvaluationRequest schemas
>>>>>>> Stashed changes
key_files:
  - backend/app/db/queries/rules.py
  - backend/app/db/queries/evaluations.py
  - backend/app/modules/rules/service.py
  - backend/app/modules/rules/router.py
  - backend/app/modules/rules/schemas.py
  - backend/app/modules/evaluations/service.py
<<<<<<< Updated upstream
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
=======
key_decisions:
  - get_rules_by_template renamed to get_rules_by_template_and_marketplace — explicit is better than implicit
  - All marketplace parameters default to 'ID' for full backward compatibility
  - Marketplace stored in evaluation_inputs determines which rules generate_score uses — no explicit marketplace param needed at scoring time
patterns_established:
  - All query functions accept marketplace as keyword arg with default 'ID'
  - API endpoints accept marketplace as Query param (GET) or request body field (PUT/POST)
  - generate_score derives marketplace from eval_inputs row, not from caller — single source of truth
observability_surfaces:
  - GET /api/v1/rules response includes marketplace field — callers can verify which marketplace's rules they received
  - GET /api/v1/rules?marketplace=TH vs ?marketplace=ID — compare six_month_avg_threshold to verify correct marketplace selection
  - generate_score logs (future) can include marketplace from eval_inputs for debugging rule mismatches
duration: ~20 minutes
>>>>>>> Stashed changes
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

<<<<<<< Updated upstream
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
=======
# T02: Marketplace-Aware Query Layer and API Endpoints

**Updated all query functions, service layer, and API endpoints to accept and filter by marketplace, wiring generate_score to read marketplace from evaluation_inputs and fetch the correct rules row.**

## What Happened

1. **Rules query layer** (`backend/app/db/queries/rules.py`):
   - Added `marketplace` column to `RuleRow` TypedDict and all SELECT clauses
   - `get_all_rules()` now accepts `marketplace='ID'` keyword, filters with `WHERE marketplace = $1`
   - Renamed `get_rules_by_template` → `get_rules_by_template_and_marketplace` with `WHERE template = $1 AND marketplace = $2`
   - `update_rules()` now includes `marketplace` in WHERE and RETURNING clauses

2. **Evaluations query layer** (`backend/app/db/queries/evaluations.py`):
   - Added `marketplace` field to `EvaluationInputsRow` TypedDict
   - `get_evaluation_inputs` SELECT now includes `marketplace`
   - `upsert_evaluation_inputs` accepts `marketplace` param ($5), includes in INSERT/UPDATE/RETURNING
   - `insert_evaluation` accepts `marketplace` as $12 parameter

3. **Rules schemas/service/router**:
   - `ScoringRuleResponse` schema includes `marketplace: str = "ID"`
   - Service functions accept and forward `marketplace` parameter
   - Router GET/PUT endpoints accept `marketplace` as Query parameter (default 'ID')

4. **Evaluations service**:
   - `generate_score` reads `marketplace` from `eval_inputs` row (fallback 'ID'), passes to `get_rules_by_template_and_marketplace`
   - `save_evaluation_inputs` accepts and forwards `marketplace`
   - `save_evaluation` accepts and forwards `marketplace` to `insert_evaluation`

5. **Evaluations schemas/router**:
   - `EvaluationInputsUpdate` includes `marketplace: str = "ID"`
   - `SaveEvaluationRequest` includes `marketplace: str = "ID"`
   - Router passes marketplace through to service calls

6. **Updated existing tests** to account for renamed function and new marketplace field:
   - `test_rules_update.py` expected_fields updated
   - `test_scoring.py` mocks updated from `get_rules_by_template` → `get_rules_by_template_and_marketplace`

## Verification

- `pytest tests/unit/test_rules_queries.py` — **9/9 passed** (marketplace filtering in queries)
- `pytest tests/unit/test_evaluation_queries.py` — **18/18 passed** (marketplace in upsert/insert/get)
- `pytest tests/unit/test_generate_score_marketplace.py` — **3/3 passed** (marketplace wiring in generate_score)
- `pytest tests/integration/api/test_rules.py` — **12/12 passed** (API endpoint with ?marketplace=)
- `pytest tests/integration/api/test_rules_update.py` — **12/12 passed** (response schema with marketplace)
- `pytest tests/integration/api/test_scoring.py` — **12/12 passed** (scoring with renamed function)
- **Full suite: 1031 passed, 3 failed** (3 failures are pre-existing in test_ads_keyword.py, unrelated)

Slice verification status (9/9 items now covered):
- ✓ pytest passes (marketplace unit tests)
- ✓ Migration file exists (T01)
- ✓ Constants importable (T01)
- ✓ CHECK constraints present (T01)
- ✓ Seeds two rows (T01)
- ✓ Downgrade path correct (T01)
- ✓ Query layer functions accept marketplace parameter ← **this task**
- ✓ DEFAULT 'ID' backfills existing rows (T01 migration)
- ✓ Invalid codes rejected by constants (T01)

## Diagnostics

- **API inspection:** `GET /api/v1/rules` returns rules with `marketplace: "ID"`. `GET /api/v1/rules?marketplace=TH` returns THB rules.
- **Threshold comparison:** Compare `rules.business.six_month_avg_threshold.threshold` between ID (100M) and TH (190K) responses.
- **generate_score marketplace:** Check which rules row was loaded by inspecting the rule_version in the scoring response — if it matches the TH row's version, marketplace wiring is correct.
- **Backward compatibility:** All endpoints work without marketplace parameter — defaults to 'ID'.

## Deviations

- Added `marketplace` field to `EvaluationInputsUpdate` and `SaveEvaluationRequest` schemas (not explicitly in plan but necessary for the router to pass marketplace through to the service layer).
- Updated `test_rules_update.py` and `test_scoring.py` which were not in the original plan's file list but broke due to the renamed function and new schema field.
>>>>>>> Stashed changes

## Known Issues

- 3 pre-existing test failures in `tests/unit/calculators/test_ads_keyword.py` (unrelated to marketplace work)
<<<<<<< Updated upstream
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
=======

## Files Created/Modified

- `backend/app/db/queries/rules.py` — Added marketplace filtering to all query functions, renamed get_rules_by_template
- `backend/app/db/queries/evaluations.py` — Added marketplace to upsert_evaluation_inputs, insert_evaluation, get_evaluation_inputs
- `backend/app/modules/rules/schemas.py` — Added marketplace field to ScoringRuleResponse
- `backend/app/modules/rules/service.py` — Added marketplace parameter to get_all_rules, update_rules
- `backend/app/modules/rules/router.py` — Added marketplace Query parameter to GET/PUT endpoints
- `backend/app/modules/evaluations/service.py` — generate_score reads marketplace from eval_inputs; save functions forward marketplace
- `backend/app/modules/evaluations/schemas.py` — Added marketplace to EvaluationInputsUpdate and SaveEvaluationRequest
- `backend/app/modules/evaluations/router.py` — Pass marketplace through to service calls
- `backend/tests/unit/test_rules_queries.py` — 9 new unit tests for marketplace-filtered rules queries
- `backend/tests/unit/test_evaluation_queries.py` — 18 tests (5 new for marketplace in evaluations queries)
- `backend/tests/unit/test_generate_score_marketplace.py` — 3 new tests for marketplace wiring in generate_score
- `backend/tests/integration/api/test_rules.py` — 12 tests (4 new for marketplace API endpoints)
- `backend/tests/integration/api/test_rules_update.py` — Updated expected_fields to include marketplace
- `backend/tests/integration/api/test_scoring.py` — Updated mocks for renamed function
>>>>>>> Stashed changes
