# T02: 01-data-model-foundation 02

**Slice:** S01 — **Milestone:** M001

## Description

Update all query functions, service layer, and API endpoints to accept and filter by marketplace. Wire generate_score to read marketplace from evaluation_inputs and fetch the correct rules row.

Purpose: Without these changes, the migration data (marketplace column, THB rules) is unused. This plan makes the application code marketplace-aware while maintaining backward compatibility (all endpoints default to 'ID').
Output: Updated queries, services, router, schemas, and tests proving marketplace filtering works end-to-end.

## Must-Haves

- [ ] "get_all_rules(conn, marketplace='ID') returns only IDR rules"
- [ ] "get_all_rules(conn, marketplace='TH') returns only THB rules"
- [ ] "get_rules_by_template_and_marketplace(conn, 'default', 'TH') returns the THB row"
- [ ] "update_rules filters by both template AND marketplace"
- [ ] "upsert_evaluation_inputs accepts and stores marketplace parameter"
- [ ] "upsert_evaluation_inputs RETURNING clause includes marketplace"
- [ ] "insert_evaluation accepts marketplace as $12 parameter"
- [ ] "generate_score reads marketplace from eval_inputs and passes to rules query"
- [ ] "GET /api/v1/rules without ?marketplace= defaults to IDR rules"
- [ ] "GET /api/v1/rules?marketplace=TH returns THB rules"
- [ ] "ScoringRuleResponse schema includes marketplace field"

## Steps

1. **Update `backend/app/db/queries/rules.py`** — Add `marketplace` column to SELECT/WHERE/RETURNING in `get_all_rules`, `get_rules_by_template_and_marketplace`, and `update_rules`. All functions accept `marketplace` param defaulting to `'ID'`.
2. **Update `backend/app/db/queries/evaluations.py`** — Add `marketplace` to `EvaluationInputsRow` TypedDict, `get_evaluation_inputs` SELECT, `upsert_evaluation_inputs` INSERT/RETURNING, and `insert_evaluation` as `$12` parameter.
3. **Update `backend/app/modules/rules/schemas.py`** — Add `marketplace: str = "ID"` field to `ScoringRuleResponse`.
4. **Update `backend/app/modules/rules/service.py`** — Thread `marketplace` parameter through `get_all_rules` and `update_rules` service functions.
5. **Update `backend/app/modules/rules/router.py`** — Add `marketplace` query parameter (default `'ID'`) to `GET /api/v1/rules` and `PUT /api/v1/rules/{template}`.
6. **Update `backend/app/modules/evaluations/service.py`** — Wire `generate_score` to read `marketplace` from `eval_inputs` row and pass to `get_rules_by_template_and_marketplace`. Thread `marketplace` through `save_evaluation` and `save_evaluation_inputs`.
7. **Update `backend/app/modules/evaluations/schemas.py`** — Add `marketplace: str = "ID"` to `EvaluationInputsUpdate` and `SaveEvaluationRequest`.
8. **Update `backend/app/modules/evaluations/router.py`** — Pass `body.marketplace` through `update_evaluation` and `save_evaluation_endpoint`.
9. **Write unit tests** — `test_rules_queries.py` (9 tests), `test_evaluation_queries.py` (18 tests), `test_generate_score_marketplace.py` (3 tests).
10. **Write integration tests** — `test_rules.py` (marketplace GET/PUT endpoints, 12 tests), `test_rules_update.py` (marketplace in response schema).
11. **Run full test suite** — verify 0 regressions from changes.

## Observability Impact

- **Query-level:** All rules queries now filter by `marketplace` — a misconfigured call omitting marketplace will default to `'ID'` (backward compatible). Missing THB rows surface as `None` returns from `get_rules_by_template_and_marketplace`.
- **API-level:** `GET /api/v1/rules` response now includes `marketplace` field. Consumers can verify marketplace filtering via `?marketplace=TH` query parameter. An incorrect marketplace value will return an empty array (no 400 error — it's a filter, not validation).
- **Scoring pipeline:** `generate_score` reads `marketplace` from `evaluation_inputs` row. If the row lacks a `marketplace` key (pre-migration data), it falls back to `'ID'`. The rules query then fetches the correct row. A mismatch (e.g., TH eval_inputs but no TH scoring_rules row) surfaces as a `None` rule_row — scoring proceeds with `rules=None` and `rule_version=1`.
- **Inspection:** `SELECT marketplace FROM evaluation_inputs WHERE brand_id = X` reveals which marketplace a brand is configured for. `SELECT marketplace FROM scoring_rules` shows available marketplace rule sets.

## Files

- `backend/app/db/queries/rules.py`
- `backend/app/db/queries/evaluations.py`
- `backend/app/modules/rules/service.py`
- `backend/app/modules/rules/router.py`
- `backend/app/modules/rules/schemas.py`
- `backend/app/modules/evaluations/service.py`
- `backend/app/modules/evaluations/schemas.py`
- `backend/app/modules/evaluations/router.py`
- `backend/tests/unit/test_rules_queries.py`
- `backend/tests/unit/test_evaluation_queries.py`
- `backend/tests/unit/test_generate_score_marketplace.py`
- `backend/tests/integration/api/test_rules.py`
- `backend/tests/integration/api/test_rules_update.py`
