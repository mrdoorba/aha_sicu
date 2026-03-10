# Database Query Helpers Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:executing-plans to implement this plan task-by-task.

**Goal:** Add lightweight database query helpers (fetch_one/fetch_all, paginate, TypedDicts, FilterBuilder) to reduce boilerplate and improve type safety without breaking existing code.

**Architecture:** All helpers go into `backend/app/db/queries/utils.py`. TypedDicts are defined in each query module. Migration is incremental — one module at a time, validated by existing tests after each step.

**Tech Stack:** Python 3.14, asyncpg, TypedDict, pytest

---

### Task 1: Add fetch_one and fetch_all helpers

**Files:**
- Modify: `backend/app/db/queries/utils.py`
- Create: `backend/tests/unit/test_query_utils.py`

**Step 1: Write the failing tests**

```python
# backend/tests/unit/test_query_utils.py
"""Tests for database query utilities."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.db.queries.utils import escape_like, fetch_one, fetch_all, paginate


class TestFetchOne:
    @pytest.mark.asyncio
    async def test_returns_dict_when_row_exists(self):
        conn = AsyncMock()
        row = MagicMock()
        row.__iter__ = MagicMock(return_value=iter([("id", 1), ("name", "test")]))
        row.keys.return_value = ["id", "name"]
        conn.fetchrow.return_value = row
        result = await fetch_one(conn, "SELECT * FROM t WHERE id = $1", 1)
        assert result == dict(row)
        conn.fetchrow.assert_called_once_with("SELECT * FROM t WHERE id = $1", 1)

    @pytest.mark.asyncio
    async def test_returns_none_when_no_row(self):
        conn = AsyncMock()
        conn.fetchrow.return_value = None
        result = await fetch_one(conn, "SELECT * FROM t WHERE id = $1", 1)
        assert result is None

    @pytest.mark.asyncio
    async def test_passes_multiple_args(self):
        conn = AsyncMock()
        conn.fetchrow.return_value = None
        await fetch_one(conn, "SELECT * FROM t WHERE a = $1 AND b = $2", "x", 2)
        conn.fetchrow.assert_called_once_with(
            "SELECT * FROM t WHERE a = $1 AND b = $2", "x", 2
        )


class TestFetchAll:
    @pytest.mark.asyncio
    async def test_returns_list_of_dicts(self):
        conn = AsyncMock()
        row1 = MagicMock()
        row2 = MagicMock()
        conn.fetch.return_value = [row1, row2]
        result = await fetch_all(conn, "SELECT * FROM t")
        assert result == [dict(row1), dict(row2)]

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_rows(self):
        conn = AsyncMock()
        conn.fetch.return_value = []
        result = await fetch_all(conn, "SELECT * FROM t")
        assert result == []
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && uv run pytest tests/unit/test_query_utils.py -v`
Expected: FAIL with `ImportError: cannot import name 'fetch_one'`

**Step 3: Write the implementation**

Add to `backend/app/db/queries/utils.py`:

```python
from typing import Any

from asyncpg import Connection


async def fetch_one(conn: Connection, query: str, *args: Any) -> dict | None:
    """Execute query and return single row as dict, or None."""
    row = await conn.fetchrow(query, *args)
    return dict(row) if row else None


async def fetch_all(conn: Connection, query: str, *args: Any) -> list[dict]:
    """Execute query and return all rows as list of dicts."""
    rows = await conn.fetch(query, *args)
    return [dict(row) for row in rows]
```

**Step 4: Run tests to verify they pass**

Run: `cd backend && uv run pytest tests/unit/test_query_utils.py -v`
Expected: PASS

**Step 5: Run full test suite to verify no regressions**

Run: `cd backend && uv run pytest -x -q`
Expected: All tests pass

**Step 6: Commit**

```
Add fetch_one and fetch_all query helpers
```

---

### Task 2: Add paginate helper

**Files:**
- Modify: `backend/app/db/queries/utils.py`
- Modify: `backend/tests/unit/test_query_utils.py`

**Step 1: Write the failing tests**

Append to `backend/tests/unit/test_query_utils.py`:

```python
class TestPaginate:
    def test_first_page(self):
        limit, offset = paginate(page=1, limit=20)
        assert limit == 20
        assert offset == 0

    def test_second_page(self):
        limit, offset = paginate(page=2, limit=20)
        assert limit == 20
        assert offset == 20

    def test_custom_limit(self):
        limit, offset = paginate(page=3, limit=10)
        assert limit == 10
        assert offset == 20
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && uv run pytest tests/unit/test_query_utils.py::TestPaginate -v`
Expected: FAIL with `ImportError: cannot import name 'paginate'`

**Step 3: Write the implementation**

Add to `backend/app/db/queries/utils.py`:

```python
def paginate(page: int, limit: int) -> tuple[int, int]:
    """Return (limit, offset) for SQL pagination."""
    return limit, (page - 1) * limit
```

**Step 4: Run tests to verify they pass**

Run: `cd backend && uv run pytest tests/unit/test_query_utils.py -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `cd backend && uv run pytest -x -q`
Expected: All tests pass

**Step 6: Commit**

```
Add paginate helper to query utilities
```

---

### Task 3: Add FilterBuilder

**Files:**
- Modify: `backend/app/db/queries/utils.py`
- Modify: `backend/tests/unit/test_query_utils.py`

**Step 1: Write the failing tests**

Append to `backend/tests/unit/test_query_utils.py`:

```python
from app.db.queries.utils import FilterBuilder


class TestFilterBuilder:
    def test_empty_builder_returns_empty_where(self):
        fb = FilterBuilder()
        assert fb.where_clause == ""
        assert fb.params == []
        assert fb.next_idx == 1

    def test_single_condition(self):
        fb = FilterBuilder()
        fb.add("name = {p}", "Alice")
        assert fb.where_clause == "WHERE name = $1"
        assert fb.params == ["Alice"]
        assert fb.next_idx == 2

    def test_multiple_conditions(self):
        fb = FilterBuilder()
        fb.add("name = {p}", "Alice")
        fb.add("age > {p}", 25)
        assert fb.where_clause == "WHERE name = $1 AND age > $2"
        assert fb.params == ["Alice", 25]
        assert fb.next_idx == 3

    def test_custom_start_idx(self):
        fb = FilterBuilder(start_idx=3)
        fb.add("name = {p}", "Alice")
        assert fb.where_clause == "WHERE name = $3"
        assert fb.params == ["Alice"]
        assert fb.next_idx == 4

    def test_chaining(self):
        fb = FilterBuilder()
        result = fb.add("a = {p}", 1).add("b = {p}", 2)
        assert result is fb
        assert fb.where_clause == "WHERE a = $1 AND b = $2"

    def test_ilike_pattern(self):
        fb = FilterBuilder()
        fb.add("name ILIKE '%' || {p} || '%' ESCAPE '\\'", "test")
        assert fb.where_clause == "WHERE name ILIKE '%' || $1 || '%' ESCAPE '\\'"
        assert fb.params == ["test"]
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && uv run pytest tests/unit/test_query_utils.py::TestFilterBuilder -v`
Expected: FAIL with `ImportError: cannot import name 'FilterBuilder'`

**Step 3: Write the implementation**

Add to `backend/app/db/queries/utils.py`:

```python
class FilterBuilder:
    """Build dynamic WHERE clauses with automatic $N parameter numbering."""

    def __init__(self, start_idx: int = 1) -> None:
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
        """Return the WHERE clause string, or empty string if no conditions."""
        return "WHERE " + " AND ".join(self._conditions) if self._conditions else ""

    @property
    def params(self) -> list[Any]:
        """Return the list of parameter values."""
        return self._params

    @property
    def next_idx(self) -> int:
        """Return the next available parameter index."""
        return self._idx
```

**Step 4: Run tests to verify they pass**

Run: `cd backend && uv run pytest tests/unit/test_query_utils.py -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `cd backend && uv run pytest -x -q`
Expected: All tests pass

**Step 6: Commit**

```
Add FilterBuilder for dynamic WHERE clause construction
```

---

### Task 4: Add TypedDicts to users and accounts query modules

**Files:**
- Modify: `backend/app/db/queries/users.py`
- Modify: `backend/app/modules/accounts/queries.py`

**Step 1: Add TypedDicts and update return annotations in `users.py`**

```python
# Add at top of backend/app/db/queries/users.py, after imports
from datetime import datetime
from typing import TypedDict


class UserRow(TypedDict):
    id: int
    firebase_uid: str
    email: str
    role: str
    language: str | None
    created_at: datetime
    last_login: datetime | None
```

Update function signatures:
- `get_user_by_firebase_uid` → `-> UserRow | None`
- `create_user` → `-> UserRow`
- `update_language` → `-> UserRow | None`

**Step 2: Add TypedDict to `accounts/queries.py`**

```python
# Add at top of backend/app/modules/accounts/queries.py, after imports
from datetime import datetime
from typing import TypedDict


class AccountUserRow(TypedDict):
    id: int
    email: str
    role: str
    created_at: datetime
    last_login: datetime | None
```

Update function signatures:
- `get_all_users` → `-> list[AccountUserRow]`
- `create_user` → `-> AccountUserRow`
- `update_user_role` → `-> AccountUserRow | None`
- `get_user_by_id`: keep `-> dict | None` (returns firebase_uid too, different shape — or add `AccountUserDetailRow`)

**Step 3: Run full test suite**

Run: `cd backend && uv run pytest -x -q`
Expected: All tests pass (TypedDicts are annotation-only, no runtime change)

**Step 4: Commit**

```
Add TypedDicts for user and account query return types
```

---

### Task 5: Add TypedDicts to brands query module

**Files:**
- Modify: `backend/app/db/queries/brands.py`

**Step 1: Add TypedDicts**

```python
from datetime import datetime
from typing import Any, Literal, TypedDict


class BrandRow(TypedDict):
    id: int
    brand_name: str
    raw_data: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class BrandWithMeetingRow(TypedDict):
    id: int
    brand_name: str
    raw_data: dict[str, Any]
    updated_at: datetime
    meeting_raw_data: dict[str, Any] | None
```

Update function signatures:
- `upsert_brand_data` → `-> BrandRow`
- `get_brand_data` → `-> list[BrandRow]`
- `get_brand_by_name` → `-> BrandRow | None`
- `get_brands_with_meeting` → `-> list[BrandWithMeetingRow]`
- `get_brand_by_id` → `-> BrandWithMeetingRow | None`

**Step 2: Run full test suite**

Run: `cd backend && uv run pytest -x -q`
Expected: All tests pass

**Step 3: Commit**

```
Add TypedDicts for brand query return types
```

---

### Task 6: Add TypedDicts to evaluations query module

**Files:**
- Modify: `backend/app/db/queries/evaluations.py`

**Step 1: Add TypedDicts**

```python
from datetime import date, datetime
from typing import Any, Literal, TypedDict


class EvaluationInputsRow(TypedDict):
    id: int
    brand_id: int
    last_edited_by: int
    category_type: str | None
    manual_data: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class EvaluationListRow(TypedDict):
    id: int
    brand_name: str
    final_score: float
    verdict: str
    template: str
    evaluator_email: str
    created_at: datetime
    period: str


class GroupedEvaluationRow(TypedDict):
    brand_id: int
    brand_name: str
    evaluation_count: int
    top_score: float
    top_verdict: str
    latest_date: datetime


class BrandEvaluationRow(TypedDict):
    id: int
    final_score: float
    verdict: str
    template: str
    evaluator_email: str
    created_at: datetime
    period: str


class EvaluationDetailRow(TypedDict):
    id: int
    brand_id: int
    brand_name: str
    raw_data: dict[str, Any]
    final_score: float
    verdict: str
    template: str
    score_breakdown: list[dict[str, Any]]
    calculator_results: dict[str, Any]
    manual_inputs: dict[str, Any]
    email_output: str | None
    rule_version: int
    created_at: datetime
    period: str
    evaluator_email: str


class InsertedEvaluationRow(TypedDict):
    id: int
    brand_id: int
    final_score: float
    verdict: str
    template: str
    created_at: datetime
    period: str
```

Update function signatures accordingly.

**Step 2: Run full test suite**

Run: `cd backend && uv run pytest -x -q`
Expected: All tests pass

**Step 3: Commit**

```
Add TypedDicts for evaluation query return types
```

---

### Task 7: Add TypedDicts to remaining query modules

**Files:**
- Modify: `backend/app/db/queries/uploads.py`
- Modify: `backend/app/db/queries/calculator_results.py`
- Modify: `backend/app/db/queries/rules.py`
- Modify: `backend/app/db/queries/sync_status.py`

**Step 1: Add TypedDicts to each file**

`uploads.py`:
```python
class UploadRow(TypedDict):
    id: int
    brand_id: int
    file_type: str
    calculator_target: str
    filename: str
    file_size: int
    row_count: int
    uploaded_at: datetime

class UploadWithDataRow(UploadRow):
    parsed_data: dict[str, Any]
```

`calculator_results.py`:
```python
class CalculatorResultRow(TypedDict):
    id: int
    brand_id: int
    calculator_type: str
    details: dict[str, Any]
    output_text: str
    calculated_at: datetime
```

`rules.py`:
```python
class RuleRow(TypedDict):
    id: int
    template: str
    rules: dict[str, Any]
    version: int
    updated_by: int | None
    updated_at: datetime
```

`sync_status.py`:
```python
class SyncStatusRow(TypedDict):
    id: int
    started_at: datetime
    completed_at: datetime | None
    success: bool | None
    brands_synced: int | None
    error_message: str | None
    sync_details: dict[str, Any] | None

class SyncStatusLatestRow(SyncStatusRow):
    timed_out: bool
```

**Step 2: Run full test suite**

Run: `cd backend && uv run pytest -x -q`
Expected: All tests pass

**Step 3: Commit**

```
Add TypedDicts for upload, calculator, rule, and sync query return types
```

---

### Task 8: Migrate query modules to use fetch_one/fetch_all

**Files:**
- Modify: `backend/app/db/queries/users.py`
- Modify: `backend/app/db/queries/evaluations.py`
- Modify: `backend/app/db/queries/brands.py`
- Modify: `backend/app/db/queries/uploads.py`
- Modify: `backend/app/db/queries/calculator_results.py`
- Modify: `backend/app/db/queries/rules.py`
- Modify: `backend/app/db/queries/sync_status.py`
- Modify: `backend/app/modules/accounts/queries.py`

**Step 1: Migrate each module one at a time**

For each module, replace:
```python
row = await conn.fetchrow(query, *args)
return dict(row) if row else None
```
with:
```python
return await fetch_one(conn, query, *args)
```

And replace:
```python
rows = await conn.fetch(query, *args)
return [dict(row) for row in rows]
```
with:
```python
return await fetch_all(conn, query, *args)
```

Add import at top of each file:
```python
from app.db.queries.utils import fetch_one, fetch_all
```

**Important:** Do NOT migrate functions that use `conn.fetchval` or `conn.execute` — those don't return row dicts.

**Step 2: Run full test suite after each module**

Run: `cd backend && uv run pytest -x -q`
Expected: All tests pass after each module migration

**Step 3: Commit**

```
Migrate query modules to use fetch_one/fetch_all helpers
```

---

### Task 9: Migrate services to use paginate helper

**Files:**
- Modify: `backend/app/modules/evaluations/service.py`
- Modify: `backend/app/modules/brands/service.py`

**Step 1: Replace offset calculations**

In `evaluations/service.py` (lines 56 and 110), replace:
```python
offset = (page - 1) * limit
```
with:
```python
from app.db.queries.utils import paginate
# ...
limit, offset = paginate(page, limit)
```

In `brands/service.py` (line 28), same replacement.

**Step 2: Run full test suite**

Run: `cd backend && uv run pytest -x -q`
Expected: All tests pass

**Step 3: Commit**

```
Migrate services to use paginate helper
```

---

### Task 10: Refactor _build_filter_clauses to use FilterBuilder

**Files:**
- Modify: `backend/app/db/queries/evaluations.py`

**Step 1: Refactor `_build_filter_clauses` internally**

Replace the manual implementation with FilterBuilder, keeping the same function signature:

```python
from app.db.queries.utils import escape_like, FilterBuilder

def _build_filter_clauses(
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[str, list[Any], int]:
    """Build conditional WHERE clauses for evaluation list/count queries."""
    fb = FilterBuilder()

    if search:
        fb.add("b.brand_name ILIKE '%' || {p} || '%' ESCAPE '\\'", escape_like(search))

    if date_from:
        fb.add("e.created_at >= {p}", date_from)

    if date_to:
        fb.add("e.created_at < ({p} + interval '1 day')", date_to)

    return fb.where_clause, fb.params, fb.next_idx
```

The function signature and return type are unchanged — all callers work without modification.

**Step 2: Run full test suite**

Run: `cd backend && uv run pytest -x -q`
Expected: All tests pass

**Step 3: Commit**

```
Refactor _build_filter_clauses to use FilterBuilder
```

---

### Task 11: Final verification

**Step 1: Run full backend test suite**

Run: `cd backend && uv run pytest -v`
Expected: All tests pass

**Step 2: Run linter**

Run: `cd backend && uv run ruff check .`
Expected: No errors

**Step 3: Verify type annotations work**

Run: `cd backend && uv run ruff check . --select I`
Expected: Import sorting clean

**Step 4: Commit any final cleanup if needed**
