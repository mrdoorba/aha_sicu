# Database Query Helpers — Design Document

**Date:** 2026-03-10
**Status:** Approved

## Problem

The database query layer has three recurring pain points:

1. **Repetitive `dict(row)` conversion** — every query function ends with `dict(row) if row else None` or `[dict(row) for row in rows]`, with no type information on the returned dicts.
2. **Duplicated pagination math** — `offset = (page - 1) * limit` is repeated across three service modules.
3. **Error-prone dynamic filter building** — `_build_filter_clauses` manually tracks `$N` parameter indices, which is fragile when adding/reordering filters.

## Approach

**Additive, incremental helpers** — no new dependencies, no existing behavior changes. Each improvement is a new function/class in `backend/app/db/queries/utils.py` that existing code can adopt one function at a time.

## Design

### 1. `fetch_one()` / `fetch_all()`

Wrap asyncpg calls with automatic `dict(row)` conversion.

```python
async def fetch_one(conn: Connection, query: str, *args: Any) -> dict | None:
    row = await conn.fetchrow(query, *args)
    return dict(row) if row else None

async def fetch_all(conn: Connection, query: str, *args: Any) -> list[dict]:
    rows = await conn.fetch(query, *args)
    return [dict(row) for row in rows]
```

### 2. `paginate()`

Single source of truth for offset calculation.

```python
def paginate(page: int, limit: int) -> tuple[int, int]:
    """Return (limit, offset) for SQL pagination."""
    return limit, (page - 1) * limit
```

### 3. TypedDicts for Query Return Shapes

Each query module defines TypedDicts for its return shapes, providing IDE autocomplete and static type checking with zero runtime overhead.

Modules and their TypedDicts:
- **users.py** — `UserRow`
- **brands.py** — `BrandRow`, `BrandWithMeetingRow`
- **evaluations.py** — `EvaluationInputsRow`, `EvaluationListRow`, `GroupedEvaluationRow`, `BrandEvaluationRow`, `EvaluationDetailRow`, `InsertedEvaluationRow`
- **uploads.py** — `UploadRow`, `UploadWithDataRow`
- **calculator_results.py** — `CalculatorResultRow`, `CalculatorResultWithDetailsRow`
- **rules.py** — `RuleRow`
- **sync_status.py** — `SyncStatusRow`, `SyncStatusLatestRow`
- **accounts/queries.py** — `AccountUserRow`

### 4. `FilterBuilder`

Encapsulates dynamic WHERE clause construction with automatic `$N` numbering.

```python
class FilterBuilder:
    def __init__(self, start_idx: int = 1):
        self._conditions: list[str] = []
        self._params: list[Any] = []
        self._idx = start_idx

    def add(self, condition_template: str, value: Any) -> "FilterBuilder":
        """Add a condition. Use {p} as placeholder for the $N parameter."""
        self._conditions.append(condition_template.replace("{p}", f"${self._idx}"))
        self._params.append(value)
        self._idx += 1
        return self

    @property
    def where_clause(self) -> str:
        return "WHERE " + " AND ".join(self._conditions) if self._conditions else ""

    @property
    def params(self) -> list[Any]:
        return self._params

    @property
    def next_idx(self) -> int:
        return self._idx
```

## Backward Compatibility

All changes are additive:
- New functions/classes added to `utils.py` — no existing signatures modified
- TypedDicts are annotation-only — no runtime behavior change
- `FilterBuilder` coexists with `_build_filter_clauses` — existing function stays untouched
- Migration is per-function, validated by existing tests at each step

## Migration Strategy

1. Add all helpers and TypedDicts first (no existing code touched)
2. Migrate query modules one at a time to use `fetch_one`/`fetch_all` and TypedDict return annotations
3. Migrate service modules to use `paginate()`
4. Optionally refactor `_build_filter_clauses` to use `FilterBuilder` internally
5. Run full test suite after each module migration

## Testing

- Unit tests for `fetch_one`, `fetch_all`, `paginate`, `FilterBuilder`
- Existing tests serve as regression tests for each migrated module
