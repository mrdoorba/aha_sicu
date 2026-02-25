## 1. Fix JSONB Double-Encoding in Query Layer

- [x] 1.1 Remove `json.dumps()` from `upsert_evaluation_inputs` in `backend/app/db/queries/evaluations.py` — pass `manual_data` dict directly to asyncpg
- [x] 1.2 Remove `json.dumps()` from `insert_evaluation` in `backend/app/db/queries/evaluations.py` — pass `score_breakdown`, `calculator_results`, and `manual_inputs` dicts directly to asyncpg

## 2. Add Defensive Parsing in Service Layer

- [x] 2.1 Add `_ensure_dict` helper in `backend/app/modules/evaluations/service.py` that calls `json.loads()` if the value is a string, returns as-is if already a dict
- [x] 2.2 Apply `_ensure_dict` to `manual_data` in `generate_score` (service.py line 174)
- [x] 2.3 ~~Apply `_ensure_dict` to `manual_data` in `save_evaluation`~~ N/A — `save_evaluation` receives data from frontend params, doesn't read from DB. `calculator_service.py` already has its own defensive check.

## 3. Update Tests

- [x] 3.1 Add a test that verifies `generate_score` correctly handles double-encoded (string) manual_data
- [x] 3.2 Add a test that verifies `generate_score` correctly handles properly-encoded (dict) manual_data
- [x] 3.3 Update any existing test fixtures that use `json.dumps()` for JSONB parameters to pass dicts directly
