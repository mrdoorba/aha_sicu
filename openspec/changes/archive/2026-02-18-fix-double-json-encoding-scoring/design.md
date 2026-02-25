## Context

The asyncpg connection pool registers a JSONB codec (`connection.py:12-14`) with `encoder=json.dumps, decoder=json.loads`. This means asyncpg automatically encodes Python dicts to JSON on write and decodes JSON to Python dicts on read.

However, `upsert_evaluation_inputs` (`evaluations.py:55`) manually calls `json.dumps(manual_data)` before passing to asyncpg — producing a string that asyncpg's encoder then encodes again. The result is a JSONB text value (`"\"{ ... }\""`) rather than a JSONB object (`{ ... }`).

The GET endpoint masks this via a Pydantic `parse_jsonb` field validator that calls `json.loads` on string values. The scoring path reads `row["manual_data"]` directly — getting a string that `_get_nested()` treats as non-dict, returning `None` for every section.

## Goals / Non-Goals

**Goals:**
- Fix scoring to correctly read manual_data as a dict
- Fix the save path so new data is stored as proper JSONB objects
- Handle existing double-encoded data in the database without a migration
- Ensure all backend code paths that read `manual_data` directly are protected

**Non-Goals:**
- Database migration to fix existing rows (defensive parsing handles them)
- Frontend changes (already works via `parse_jsonb`)
- Changes to the scoring calculator logic itself

## Decisions

### 1. Remove `json.dumps` from upsert query

**Decision**: Pass `manual_data` dict directly to asyncpg, letting the registered JSONB codec handle encoding.

**Rationale**: The codec exists precisely for this purpose. Double-encoding is the root cause. Same pattern should be applied to all JSONB parameters in query functions.

**Alternative**: Keep `json.dumps` and remove the asyncpg codec — rejected because the codec is the correct asyncpg pattern and is used project-wide.

### 2. Add defensive `_ensure_dict` helper in service layer

**Decision**: Add a small helper that calls `json.loads()` if the value is a string, used at the service layer wherever `manual_data` is extracted from a DB row outside of Pydantic validation.

**Rationale**: Existing rows in the database are already double-encoded. A data migration is unnecessary overhead — defensive parsing at read time handles both old (string) and new (dict) formats transparently.

**Alternative**: Run a SQL migration (`UPDATE evaluation_inputs SET manual_data = manual_data::text::jsonb`) — rejected as unnecessary risk for a problem that defensive parsing solves.

### 3. Audit all JSONB parameter passing in query files

**Decision**: Check all query files for the same `json.dumps` pattern and fix them consistently.

**Rationale**: The same double-encoding bug may exist in other queries (e.g., `insert_evaluation` which stores `score_breakdown`, `calculator_results`, `manual_inputs`). Fix all instances to prevent future issues.

## Risks / Trade-offs

- **[Existing data]** Old rows remain double-encoded → Mitigated by defensive `_ensure_dict` parsing at read time. Both formats work transparently.
- **[Other queries]** Removing `json.dumps` from queries that store to non-JSONB columns would break → Mitigated by only changing parameters that map to JSONB columns.
- **[Test coverage]** Existing tests may pass strings (matching the bug) → Tests need updating to pass dicts instead.
