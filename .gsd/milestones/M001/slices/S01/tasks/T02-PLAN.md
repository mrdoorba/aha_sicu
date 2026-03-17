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

## Files

- `backend/app/db/queries/rules.py`
- `backend/app/db/queries/evaluations.py`
- `backend/app/modules/rules/service.py`
- `backend/app/modules/rules/router.py`
- `backend/app/modules/rules/schemas.py`
- `backend/app/modules/evaluations/service.py`
- `backend/tests/unit/test_evaluation_queries.py`
- `backend/tests/integration/api/test_rules.py`
