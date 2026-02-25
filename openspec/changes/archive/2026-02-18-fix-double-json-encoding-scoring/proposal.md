## Why

The scoring calculator produces incorrect results (e.g., 45 instead of 77) because `manual_data` is double-JSON-encoded when saved to PostgreSQL. The asyncpg JSONB codec already calls `json.dumps`, but user code calls `json.dumps` first — resulting in data stored as a JSON string literal instead of a JSON object. The GET endpoint masks this via a Pydantic `parse_jsonb` validator, but the scoring endpoint reads the raw value and gets a string instead of a dict, causing all manual input sections to resolve as empty.

## What Changes

- Remove redundant `json.dumps()` call in `upsert_evaluation_inputs` so asyncpg's JSONB codec handles encoding correctly
- Add defensive JSON parsing in `generate_score` to handle existing double-encoded data already in the database
- Apply the same defensive parsing wherever `manual_data` is read directly from DB rows (outside Pydantic model validation)

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

_(none — this is a bug fix in internal data handling, no spec-level behavior change)_

## Impact

- **Backend**: `backend/app/db/queries/evaluations.py` (upsert function), `backend/app/modules/evaluations/service.py` (generate_score, save_evaluation)
- **Data**: Existing double-encoded rows in `evaluation_inputs.manual_data` will continue to work via defensive parsing; new saves will store correct JSONB objects
- **No API changes**: Request/response shapes are unchanged
- **No frontend changes**: The frontend already handles both formats via `parse_jsonb`
