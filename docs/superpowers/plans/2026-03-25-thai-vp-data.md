# Thai VP Data Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Thailand VP data from a separate Google Sheet alongside the existing Indonesia VP data, with column drift detection and multi-marketplace frontend filtering.

**Architecture:** Add `marketplace` column to existing brand tables (same pattern as migration 026). Per-marketplace config drives sync, with a pre-sync header validation step. Frontend uses multi-select filter chips on BrandsPage.

**Tech Stack:** Python/FastAPI, PostgreSQL, Google Sheets API, React/TypeScript, Terraform (HCL)

**Spec:** `docs/superpowers/specs/2026-03-25-thai-vp-data-design.md`

---

### Task 1: Database Migration — Add marketplace to brand tables

**Files:**
- Create: `backend/app/db/migrations/versions/034_add_marketplace_to_brand_tables.py`

- [ ] **Step 1: Write the migration file**

Follow the exact pattern from migration 026. The migration must:
1. Add `marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'` to `brand_vp_data`
2. Add `CHECK (marketplace IN ('ID', 'TH'))` constraint
3. Drop old UNIQUE constraint on `brand_name` and create new UNIQUE on `(brand_name, marketplace)`
4. Add index on `marketplace`
5. Repeat steps 1-4 for `brand_meeting_data`
6. Write downgrade that reverses all changes

```python
"""Add marketplace column to brand_vp_data and brand_meeting_data

Extends multi-marketplace support to brand data tables. Follows the
same pattern as migration 026 (scoring_rules, evaluations).

Revision ID: 034
Revises: 033
Create Date: 2026-03-25
"""

import sqlalchemy as sa
from alembic import op

revision = "034"
down_revision = "033"
branch_labels = None
depends_on = None

_TABLES = ["brand_vp_data", "brand_meeting_data"]


def upgrade() -> None:
    for table in _TABLES:
        # 1. Add marketplace column (backfills existing rows with 'ID')
        op.add_column(
            table,
            sa.Column("marketplace", sa.String(2), server_default="ID", nullable=False),
        )

        # 2. Add CHECK constraint
        op.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT chk_{table}_marketplace "
            f"CHECK (marketplace IN ('ID', 'TH'))"
        )

        # 3. Drop old UNIQUE on brand_name, create new on (brand_name, marketplace)
        op.execute(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {table}_brand_name_key"
        )
        op.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT uq_{table}_brand_name_marketplace "
            f"UNIQUE (brand_name, marketplace)"
        )

        # 4. Add index on marketplace for filtering
        op.execute(
            f"CREATE INDEX idx_{table}_marketplace ON {table} (marketplace)"
        )


def downgrade() -> None:
    for table in reversed(_TABLES):
        # Drop marketplace index
        op.execute(f"DROP INDEX IF EXISTS idx_{table}_marketplace")

        # Restore original UNIQUE on brand_name
        op.execute(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS uq_{table}_brand_name_marketplace"
        )
        # Delete TH rows first to avoid unique violation
        op.execute(f"DELETE FROM {table} WHERE marketplace = 'TH'")
        op.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT {table}_brand_name_key UNIQUE (brand_name)"
        )

        # Drop CHECK and column
        op.execute(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS chk_{table}_marketplace"
        )
        op.drop_column(table, "marketplace")
```

- [ ] **Step 2: Run the migration locally**

Run: `cd backend && uv run alembic upgrade head`
Expected: Migration applies cleanly, no errors.

- [ ] **Step 3: Verify schema changes**

Run: `cd backend && uv run python -c "import asyncio; from app.db.connection import db; asyncio.run(db.initialize()); print('OK')"`
Or connect to local DB and verify:
- `brand_vp_data` has `marketplace` column with default 'ID'
- UNIQUE constraint is on `(brand_name, marketplace)`
- CHECK constraint allows only 'ID' and 'TH'

- [ ] **Step 4: Commit**

```bash
git add backend/app/db/migrations/versions/034_add_marketplace_to_brand_tables.py
git commit -m "Add migration 034: marketplace column on brand tables"
```

---

### Task 2: Update brand queries for marketplace support

**Files:**
- Modify: `backend/app/db/queries/brands.py` (all functions)
- Test: `backend/tests/unit/queries/test_brand_queries_marketplace.py` (create)

- [ ] **Step 1: Write failing tests for marketplace-aware upsert**

Create `backend/tests/unit/queries/test_brand_queries_marketplace.py`:

```python
"""Unit tests for marketplace-aware brand queries."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_batch_upsert_includes_marketplace():
    """batch_upsert_brand_data should include marketplace in INSERT and ON CONFLICT."""
    from app.db.queries.brands import batch_upsert_brand_data

    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock(return_value="INSERT 0 2")

    await batch_upsert_brand_data(
        mock_conn,
        table="brand_vp_data",
        brand_names=["Brand A", "Brand B"],
        raw_data_list=[{"col": "val1"}, {"col": "val2"}],
        marketplace="TH",
    )

    sql = mock_conn.execute.call_args[0][0]
    assert "marketplace" in sql
    assert "ON CONFLICT (brand_name, marketplace)" in sql


@pytest.mark.asyncio
async def test_batch_upsert_defaults_to_id_marketplace():
    """batch_upsert_brand_data should default marketplace to 'ID'."""
    from app.db.queries.brands import batch_upsert_brand_data

    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock(return_value="INSERT 0 1")

    await batch_upsert_brand_data(
        mock_conn,
        table="brand_vp_data",
        brand_names=["Brand A"],
        raw_data_list=[{"col": "val"}],
    )

    # Should pass 'ID' as the marketplace array
    args = mock_conn.execute.call_args[0]
    assert ["ID"] in args  # marketplace array


@pytest.mark.asyncio
async def test_get_brands_with_meeting_filters_by_marketplace():
    """get_brands_with_meeting should accept and filter by marketplace list."""
    from app.db.queries.brands import get_brands_with_meeting
    from unittest.mock import patch

    with patch("app.db.queries.brands.fetch_all", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = []

        await get_brands_with_meeting(
            AsyncMock(), limit=20, offset=0, search=None, marketplaces=["TH"]
        )

        sql = mock_fetch.call_args[0][1]
        assert "marketplace" in sql


@pytest.mark.asyncio
async def test_get_brands_count_filters_by_marketplace():
    """get_brands_count_with_search should filter by marketplace list."""
    from app.db.queries.brands import get_brands_count_with_search

    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value=5)

    result = await get_brands_count_with_search(
        mock_conn, search=None, marketplaces=["ID", "TH"]
    )

    sql = mock_conn.fetchval.call_args[0][0]
    assert "marketplace" in sql
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && uv run pytest tests/unit/queries/test_brand_queries_marketplace.py -v`
Expected: FAIL — functions don't accept `marketplace` parameter yet.

- [ ] **Step 3: Update `batch_upsert_brand_data` in `brands.py`**

Add `marketplace: str = "ID"` parameter. Change SQL to include marketplace in INSERT and ON CONFLICT:

```python
async def batch_upsert_brand_data(
    conn: Connection,
    table: TableName,
    brand_names: list[str],
    raw_data_list: list[dict[str, Any]],
    marketplace: str = "ID",
) -> int:
    """Batch upsert brand data using unnest arrays."""
    table = _validate_table(table)

    if not brand_names:
        return 0

    raw_data_json = [json.dumps(d) for d in raw_data_list]
    marketplace_list = [marketplace] * len(brand_names)

    status = await conn.execute(
        f"""
        INSERT INTO {table} (brand_name, marketplace, raw_data, updated_at)
        SELECT unnest($1::text[]), unnest($2::text[]), unnest($3::jsonb[]), NOW()
        ON CONFLICT (brand_name, marketplace) DO UPDATE SET
            raw_data = EXCLUDED.raw_data,
            updated_at = NOW()
        """,
        brand_names,
        marketplace_list,
        raw_data_json,
    )
    return int(status.split()[-1])
```

- [ ] **Step 4: Update `upsert_brand_data`**

Add `marketplace: str = "ID"` parameter with same ON CONFLICT change:

```python
async def upsert_brand_data(
    conn: Connection,
    table: TableName,
    brand_name: str,
    raw_data: dict[str, Any],
    marketplace: str = "ID",
) -> BrandRow:
    table = _validate_table(table)

    return await fetch_one(
        conn,
        f"""
        INSERT INTO {table} (brand_name, marketplace, raw_data, updated_at)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT (brand_name, marketplace) DO UPDATE SET
            raw_data = EXCLUDED.raw_data,
            updated_at = NOW()
        RETURNING id, brand_name, raw_data, created_at, updated_at
        """,
        brand_name,
        marketplace,
        raw_data,
    )
```

- [ ] **Step 5: Update `get_brands_with_meeting`**

Add `marketplaces: list[str] | None = None` parameter. Add marketplace to JOIN and WHERE:

```python
async def get_brands_with_meeting(
    conn: Connection,
    limit: int = 20,
    offset: int = 0,
    search: str | None = None,
    marketplaces: list[str] | None = None,
) -> list[BrandWithMeetingRow]:
    """Get VP brands with LEFT JOIN to meeting data, with optional search and marketplace filter."""
    search_escaped = escape_like(search) if search else None
    return await fetch_all(
        conn,
        """
        SELECT
            v.id, v.brand_name, v.raw_data, v.updated_at, v.marketplace,
            m.raw_data AS meeting_raw_data
        FROM brand_vp_data v
        LEFT JOIN brand_meeting_data m
            ON v.brand_name = m.brand_name AND v.marketplace = m.marketplace
        WHERE ($1::text IS NULL OR v.brand_name ILIKE '%' || $1 || '%' ESCAPE '\\')
          AND ($2::text[] IS NULL OR v.marketplace = ANY($2))
        ORDER BY v.brand_name ASC
        LIMIT $3 OFFSET $4
        """,
        search_escaped,
        marketplaces,
        limit,
        offset,
    )
```

- [ ] **Step 6: Update `get_brand_by_id`**

Add marketplace to JOIN condition and select marketplace:

```python
async def get_brand_by_id(conn: Connection, brand_id: int) -> BrandWithMeetingRow | None:
    return await fetch_one(
        conn,
        """
        SELECT
            v.id, v.brand_name, v.raw_data, v.updated_at, v.marketplace,
            m.raw_data AS meeting_raw_data
        FROM brand_vp_data v
        LEFT JOIN brand_meeting_data m
            ON v.brand_name = m.brand_name AND v.marketplace = m.marketplace
        WHERE v.id = $1
        """,
        brand_id,
    )
```

- [ ] **Step 7: Update `get_brands_count_with_search`**

Add `marketplaces` parameter:

```python
async def get_brands_count_with_search(
    conn: Connection,
    search: str | None = None,
    marketplaces: list[str] | None = None,
) -> int:
    search_escaped = escape_like(search) if search else None
    result = await conn.fetchval(
        """
        SELECT COUNT(*)
        FROM brand_vp_data
        WHERE ($1::text IS NULL OR brand_name ILIKE '%' || $1 || '%' ESCAPE '\\')
          AND ($2::text[] IS NULL OR marketplace = ANY($2))
        """,
        search_escaped,
        marketplaces,
    )
    return result or 0
```

- [ ] **Step 8: Update `BrandWithMeetingRow` TypedDict**

Add `marketplace: str` field:

```python
class BrandWithMeetingRow(TypedDict):
    id: int
    brand_name: str
    raw_data: dict[str, Any]
    updated_at: datetime
    marketplace: str
    meeting_raw_data: dict[str, Any] | None
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `cd backend && uv run pytest tests/unit/queries/test_brand_queries_marketplace.py -v`
Expected: All PASS.

- [ ] **Step 10: Run existing brand tests to check no regressions**

Run: `cd backend && uv run pytest tests/integration/api/test_brands.py tests/integration/api/test_brands_detail.py -v`
Expected: All PASS (defaults keep backward compatibility).

- [ ] **Step 11: Commit**

```bash
git add backend/app/db/queries/brands.py backend/tests/unit/queries/test_brand_queries_marketplace.py
git commit -m "Add marketplace support to all brand queries"
```

---

### Task 3: Backend config — Add Thai sheet settings

**Files:**
- Modify: `backend/app/config.py:76-79`
- Modify: `backend/.env.example` (if it exists)

- [ ] **Step 1: Add Thai VP settings to `config.py`**

After line 79 (`gsheets_vp_brand_column`), add:

```python
    # VP Sheet - Thailand (brand_vp_data, marketplace='TH')
    gsheets_vp_spreadsheet_id_th: str | None = None
    gsheets_vp_range_th: str = "VP!A:W"
    gsheets_vp_brand_column_th: str = "Brand"
```

- [ ] **Step 2: Update `.env.example` if it exists**

Add the new env vars with placeholder values.

- [ ] **Step 3: Commit**

```bash
git add backend/app/config.py
git commit -m "Add Thai VP sheet config settings"
```

---

### Task 4: Column drift detection — `fetch_headers` and validation

**Files:**
- Modify: `backend/app/modules/sync/sheets_client.py` (add `fetch_headers` method)
- Create: `backend/app/modules/sync/column_drift.py` (drift detection logic + expected headers)
- Test: `backend/tests/unit/sync/test_column_drift.py`

- [ ] **Step 1: Write failing tests for column drift detection**

Create `backend/tests/unit/sync/test_column_drift.py`:

```python
"""Unit tests for column drift detection."""

import pytest
from app.modules.sync.column_drift import validate_headers, ColumnDriftError


def test_validate_headers_passes_when_exact_match():
    """No error when actual headers match expected exactly."""
    expected = ["Brand", "Email", "PIC"]
    actual = ["Brand", "Email", "PIC"]
    result = validate_headers(expected, actual, marketplace="TH", sheet="VP")
    assert result is None


def test_validate_headers_detects_missing_column():
    """Returns drift error when expected column is missing."""
    expected = ["Brand", "Email", "PIC"]
    actual = ["Brand", "Email"]
    result = validate_headers(expected, actual, marketplace="TH", sheet="VP")
    assert result is not None
    assert result.marketplace == "TH"
    assert "PIC" in result.missing


def test_validate_headers_detects_unexpected_column():
    """Returns drift error when actual has extra/renamed column."""
    expected = ["Brand", "Email"]
    actual = ["Brand", "Emails"]
    result = validate_headers(expected, actual, marketplace="TH", sheet="VP")
    assert result is not None
    assert "Email" in result.missing
    assert "Emails" in result.unexpected


def test_validate_headers_detects_reordered_columns():
    """Returns drift error when columns are in wrong order."""
    expected = ["Brand", "Email", "PIC"]
    actual = ["Email", "Brand", "PIC"]
    result = validate_headers(expected, actual, marketplace="TH", sheet="VP")
    assert result is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && uv run pytest tests/unit/sync/test_column_drift.py -v`
Expected: FAIL — module doesn't exist yet.

- [ ] **Step 3: Implement `column_drift.py`**

Create `backend/app/modules/sync/column_drift.py`:

```python
"""Column drift detection for Google Sheets sync."""

from dataclasses import dataclass, field


@dataclass
class ColumnDriftError:
    """Structured error when sheet headers don't match expected."""

    marketplace: str
    sheet: str
    status: str = "column_drift"
    expected: list[str] = field(default_factory=list)
    actual: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    unexpected: list[str] = field(default_factory=list)


def validate_headers(
    expected: list[str],
    actual: list[str],
    marketplace: str,
    sheet: str,
) -> ColumnDriftError | None:
    """Compare actual sheet headers against expected.

    Returns None if headers match exactly (including order).
    Returns ColumnDriftError with details if any mismatch is found.
    """
    if expected == actual:
        return None

    expected_set = set(expected)
    actual_set = set(actual)

    return ColumnDriftError(
        marketplace=marketplace,
        sheet=sheet,
        expected=expected,
        actual=actual,
        missing=sorted(expected_set - actual_set),
        unexpected=sorted(actual_set - expected_set),
    )


# =============================================================================
# Expected headers per marketplace (defined in code, not config)
# =============================================================================

# Indonesia VP sheet columns A-Y
# TODO: Fill in the complete list during implementation by reading the actual sheet
EXPECTED_HEADERS_VP_ID: list[str] = [
    # To be populated from the actual Indonesia VP sheet header row
]

# Thailand VP sheet columns A-W
# TODO: Fill in the complete list during implementation by reading the actual sheet
EXPECTED_HEADERS_VP_TH: list[str] = [
    # To be populated from the actual Thailand VP sheet header row
]

# Indonesia Meeting sheet columns A-D
EXPECTED_HEADERS_MEETING_ID: list[str] = [
    # To be populated from the actual Indonesia Meeting sheet header row
]
```

- [ ] **Step 4: Add `fetch_headers` method to `GoogleSheetsClient`**

Add to `backend/app/modules/sync/sheets_client.py` after `fetch_sheet_data`:

```python
async def fetch_headers(
    self,
    spreadsheet_id: str,
    sheet_name: str,
) -> list[str]:
    """Fetch only the header row (row 1) from a sheet.

    Args:
        spreadsheet_id: The Google Sheets spreadsheet ID.
        sheet_name: Tab name (e.g., "VP"). Fetches range "{sheet_name}!1:1".

    Returns:
        List of header strings from the first row.

    Raises:
        SyncException: If fetch fails.
    """
    if not spreadsheet_id:
        raise SyncException(
            code="SYNC_CREDENTIALS_MISSING",
            detail="Spreadsheet ID not provided",
        )

    service = self._get_service()
    range_name = f"{sheet_name}!1:1"
    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name,
    )
    result = await asyncio.to_thread(request.execute)
    rows = result.get("values", [])
    if not rows:
        return []
    return rows[0]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && uv run pytest tests/unit/sync/test_column_drift.py -v`
Expected: All PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/modules/sync/column_drift.py backend/app/modules/sync/sheets_client.py backend/tests/unit/sync/test_column_drift.py
git commit -m "Add column drift detection and fetch_headers method"
```

---

### Task 5: Update sync service for multi-marketplace VP sync

**Files:**
- Modify: `backend/app/modules/sync/service.py`
- Modify: `backend/app/modules/sync/schemas.py`
- Test: `backend/tests/unit/sync/test_sync_service_marketplace.py` (create)

- [ ] **Step 1: Write failing tests for multi-marketplace sync**

Create `backend/tests/unit/sync/test_sync_service_marketplace.py`:

```python
"""Unit tests for multi-marketplace sync logic."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.modules.sync.schemas import SheetSyncResult


@pytest.mark.asyncio
async def test_sync_sheet_to_table_passes_marketplace():
    """_sync_sheet_to_table should pass marketplace to batch_upsert."""
    from app.modules.sync.service import _sync_sheet_to_table

    with patch("app.modules.sync.service.brand_queries") as mock_bq, \
         patch("app.modules.sync.service.db") as mock_db:
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_bq.batch_upsert_brand_data = AsyncMock(return_value=1)

        result = await _sync_sheet_to_table(
            rows=[{"Brand": "Test"}],
            table="brand_vp_data",
            brand_column="Brand",
            sheet_type="vp_th",
            marketplace="TH",
        )

        mock_bq.batch_upsert_brand_data.assert_called_once()
        call_kwargs = mock_bq.batch_upsert_brand_data.call_args
        assert call_kwargs.kwargs.get("marketplace") == "TH" or "TH" in call_kwargs[0]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && uv run pytest tests/unit/sync/test_sync_service_marketplace.py -v`
Expected: FAIL — `_sync_sheet_to_table` doesn't accept `marketplace` yet.

- [ ] **Step 3: Update `_sync_sheet_to_table` to accept marketplace**

Add `marketplace: str = "ID"` parameter, pass it to `batch_upsert_brand_data`:

```python
async def _sync_sheet_to_table(
    rows: list[dict[str, Any]],
    table: str,
    brand_column: str,
    sheet_type: str,
    marketplace: str = "ID",
) -> SheetSyncResult:
```

In step 4 (batch upsert call), add `marketplace=marketplace`:

```python
synced_count = await brand_queries.batch_upsert_brand_data(
    conn,
    table=table,
    brand_names=brand_names,
    raw_data_list=raw_data_list,
    marketplace=marketplace,
)
```

- [ ] **Step 4: Delete old `_sync_vp_sheet` and replace with multi-marketplace `_sync_vp_sheets`**

**Delete** the old `_sync_vp_sheet` function (lines 129-158 of `service.py`) entirely. Also delete `fetch_vp_data` from `sheets_client.py` (lines 316-321) — it becomes dead code since the new flow calls `fetch_sheet_data` directly with per-marketplace config.

Replace with a new function that syncs all configured VP marketplaces. Each marketplace is validated for column drift before syncing:

```python
from app.modules.sync.column_drift import (
    validate_headers,
    ColumnDriftError,
    EXPECTED_HEADERS_VP_ID,
    EXPECTED_HEADERS_VP_TH,
)

# Marketplace VP configurations
_VP_CONFIGS: list[dict[str, Any]] = []

def _get_vp_configs() -> list[dict[str, Any]]:
    """Build VP configs from settings. Called at sync time, not import time."""
    configs = [
        {
            "marketplace": "ID",
            "spreadsheet_id": settings.gsheets_vp_spreadsheet_id,
            "range": settings.gsheets_vp_range,
            "brand_column": settings.gsheets_vp_brand_column,
            "expected_headers": EXPECTED_HEADERS_VP_ID,
            "sheet_name": settings.gsheets_vp_range.split("!")[0],
        },
    ]
    if settings.gsheets_vp_spreadsheet_id_th:
        configs.append({
            "marketplace": "TH",
            "spreadsheet_id": settings.gsheets_vp_spreadsheet_id_th,
            "range": settings.gsheets_vp_range_th,
            "brand_column": settings.gsheets_vp_brand_column_th,
            "expected_headers": EXPECTED_HEADERS_VP_TH,
            "sheet_name": settings.gsheets_vp_range_th.split("!")[0],
        })
    return configs


async def _sync_vp_sheets(
    sheets_client: GoogleSheetsClient,
) -> dict[str, SheetSyncResult | ColumnDriftError]:
    """Fetch and sync VP sheets for all configured marketplaces."""
    results: dict[str, SheetSyncResult | ColumnDriftError] = {}

    for cfg in _get_vp_configs():
        mk = cfg["marketplace"]
        key = f"vp_{mk.lower()}"

        if not cfg["spreadsheet_id"]:
            logger.info(f"VP spreadsheet for {mk} not configured, skipping")
            continue

        try:
            # Step 1: Validate headers
            if cfg["expected_headers"]:
                actual_headers = await sheets_client.fetch_headers(
                    cfg["spreadsheet_id"], cfg["sheet_name"]
                )
                drift = validate_headers(
                    cfg["expected_headers"], actual_headers,
                    marketplace=mk, sheet="VP",
                )
                if drift:
                    logger.warning(f"Column drift detected for VP {mk}: {drift}")
                    results[key] = drift
                    continue

            # Step 2: Fetch and sync data
            rows = await sheets_client.fetch_sheet_data(
                cfg["spreadsheet_id"], cfg["range"]
            )
            result = await _sync_sheet_to_table(
                rows=rows,
                table="brand_vp_data",
                brand_column=cfg["brand_column"],
                sheet_type=key,
                marketplace=mk,
            )
            results[key] = result

        except Exception as e:
            logger.error(f"VP sync failed for {mk}: {e}")
            results[key] = SheetSyncResult(
                sheet_type=key, rows_synced=0, errors=[], success=False
            )

    return results
```

- [ ] **Step 5: Update `_sync_meeting_sheet` to pass marketplace='ID'**

Add `marketplace="ID"` to the `_sync_sheet_to_table` call in `_sync_meeting_sheet`:

```python
result = await _sync_sheet_to_table(
    rows=meeting_rows,
    table="brand_meeting_data",
    brand_column=settings.gsheets_meeting_brand_column,
    sheet_type="meeting",
    marketplace="ID",
)
```

- [ ] **Step 6: Update `run_sync` to use new VP sync and build new sync_details format**

Replace the VP sync section in `run_sync` to use `_sync_vp_sheets` and build per-marketplace sync_details:

```python
# In run_sync, replace the VP sync try block:
vp_results: dict = {}
try:
    vp_results = await _sync_vp_sheets(sheets_client)
except Exception as e:
    all_errors.append(f"VP: {e}")

# Sync Meeting sheet (unchanged, passes marketplace='ID')
# ... existing meeting code ...

# Build sync_details with new keys
sync_details = {}
for key, result in vp_results.items():
    if isinstance(result, ColumnDriftError):
        sync_details[key] = {
            "status": "column_drift",
            "error": f"Missing: {result.missing}, Unexpected: {result.unexpected}",
            "missing": result.missing,
            "unexpected": result.unexpected,
        }
    elif isinstance(result, SheetSyncResult):
        sync_details[key] = {
            "rows_synced": result.rows_synced,
            "rows_skipped": result.rows_skipped,
            "errors": [e.model_dump() for e in result.errors],
            "status": "success" if result.success else "failed",
        }

if meeting_result:
    sync_details["meeting_id"] = {
        "rows_synced": meeting_result.rows_synced,
        "rows_skipped": meeting_result.rows_skipped,
        "errors": [e.model_dump() for e in meeting_result.errors],
        "status": "success" if meeting_result.success else "failed",
    }

# Aggregate totals from vp_results + meeting
vp_synced = sum(
    r.rows_synced for r in vp_results.values() if isinstance(r, SheetSyncResult)
)
vp_errors = sum(
    len(r.errors) for r in vp_results.values() if isinstance(r, SheetSyncResult)
)
meeting_synced = meeting_result.rows_synced if meeting_result else 0
meeting_errors = len(meeting_result.errors) if meeting_result else 0
drift_errors = [
    {"marketplace": r.marketplace, "missing": r.missing, "unexpected": r.unexpected}
    for r in vp_results.values() if isinstance(r, ColumnDriftError)
]

total_synced = vp_synced + meeting_synced
total_errors = vp_errors + meeting_errors + len(all_errors)
overall_success = total_errors == 0 and len(drift_errors) == 0 and total_synced > 0

return SyncResult(
    sync_id=sync_id,
    vp_results=vp_results,
    meeting_result=meeting_result,
    total_synced=total_synced,
    total_errors=total_errors,
    success=overall_success,
    column_drift_errors=drift_errors,
)
```

- [ ] **Step 7: Update `SyncResult` schema to handle multiple VP results**

In `backend/app/modules/sync/schemas.py`, update `SyncResult`:

```python
class SyncResult(BaseModel):
    """Result of a full sync operation."""

    sync_id: int
    vp_results: dict[str, Any] = {}  # key: vp_id, vp_th, etc.
    meeting_result: SheetSyncResult | None = None
    total_synced: int
    total_errors: int
    success: bool
    column_drift_errors: list[dict[str, Any]] = []  # drift errors for frontend popup
```

- [ ] **Step 8: Run tests**

Run: `cd backend && uv run pytest tests/unit/sync/test_sync_service_marketplace.py -v`
Expected: All PASS.

- [ ] **Step 9: Update existing tests that reference deleted `fetch_vp_data`**

The following test files mock `fetch_vp_data` which was deleted in Step 4:
- `backend/tests/unit/sync/test_sheets_client.py` — has `test_fetch_vp_data_uses_correct_config`
- `backend/tests/unit/sync/test_service.py` — mocks `fetch_vp_data` in multiple test functions

Update these tests:
1. Remove or replace `test_fetch_vp_data_uses_correct_config` (the convenience method no longer exists)
2. In `test_service.py`, update mocks from `sheets_client.fetch_vp_data` to `sheets_client.fetch_sheet_data` and `sheets_client.fetch_headers`, matching the new `_sync_vp_sheets` flow

- [ ] **Step 10: Run all sync tests to check no regressions**

Run: `cd backend && uv run pytest tests/ -k sync -v`
Expected: All PASS.

- [ ] **Step 11: Commit**

```bash
git add backend/app/modules/sync/service.py backend/app/modules/sync/schemas.py backend/app/modules/sync/sheets_client.py backend/tests/unit/sync/
git commit -m "Update sync service for multi-marketplace VP sync with drift detection"
```

---

### Task 6: Update brands API layer — marketplace filter and schema

**Files:**
- Modify: `backend/app/modules/brands/schemas.py`
- Modify: `backend/app/modules/brands/service.py`
- Modify: `backend/app/modules/brands/router.py`

- [ ] **Step 1: Add `marketplace` field to brand schemas**

In `backend/app/modules/brands/schemas.py`, add to both `BrandListItem` and `BrandDetailResponse`:

```python
class BrandListItem(BaseModel):
    id: int
    brand_name: str
    raw_data: dict[str, Any]
    updated_at: datetime
    marketplace: str = "ID"
    meeting_raw_data: dict[str, Any] | None = None
    # ... validators unchanged
```

Same for `BrandDetailResponse`.

- [ ] **Step 2: Add `marketplace` query parameter to router**

In `backend/app/modules/brands/router.py`:

```python
@router.get("", response_model=BrandListResponse)
async def list_brands(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, max_length=200, description="Search by brand name"),
    marketplace: str | None = Query(None, description="Comma-separated marketplace filter (e.g., 'ID,TH')"),
    current_user: dict = Depends(get_current_user),
) -> BrandListResponse:
    marketplaces = [m.strip() for m in marketplace.split(",")] if marketplace else None
    return await get_brands_paginated(page=page, limit=limit, search=search, marketplaces=marketplaces)
```

- [ ] **Step 3: Update `get_brands_paginated` service function**

In `backend/app/modules/brands/service.py`:

```python
async def get_brands_paginated(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    marketplaces: list[str] | None = None,
) -> BrandListResponse:
    limit, offset = paginate(page, limit)

    async with db.connection() as conn:
        rows = await brand_queries.get_brands_with_meeting(
            conn, limit=limit, offset=offset, search=search, marketplaces=marketplaces
        )
        total = await brand_queries.get_brands_count_with_search(
            conn, search=search, marketplaces=marketplaces
        )

    items = [BrandListItem(**row) for row in rows]
    pages = math.ceil(total / limit) if total > 0 else 0

    return BrandListResponse(
        items=items, total=total, page=page, limit=limit, pages=pages,
    )
```

- [ ] **Step 4: Run existing brand tests**

Run: `cd backend && uv run pytest tests/integration/api/test_brands.py tests/integration/api/test_brands_detail.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/brands/schemas.py backend/app/modules/brands/service.py backend/app/modules/brands/router.py
git commit -m "Add marketplace filter to brands API endpoint"
```

---

### Task 7: Update evaluation service — marketplace-aware BrandRawData

**Files:**
- Modify: `backend/app/modules/evaluations/service.py:254-261`
- Test: `backend/tests/unit/evaluations/test_brand_raw_data_mapping.py` (create)

- [ ] **Step 1: Write failing test for marketplace-aware BrandRawData extraction**

Create `backend/tests/unit/evaluations/test_brand_raw_data_mapping.py`:

```python
"""Unit tests for marketplace-aware BrandRawData extraction."""

import pytest


def test_brand_raw_data_uses_thai_columns_when_marketplace_th():
    """BrandRawData should use Thai column names for TH marketplace."""
    from app.modules.evaluations.service import _BRAND_RAW_DATA_COLUMNS

    th_cols = _BRAND_RAW_DATA_COLUMNS["TH"]
    assert th_cols["pic_name"] == "PIC"
    assert th_cols["store_link"] == "Shopee Link"
    assert th_cols["kategori"] == "Product Category"


def test_brand_raw_data_uses_indonesian_columns_when_marketplace_id():
    """BrandRawData should use Indonesian column names for ID marketplace."""
    from app.modules.evaluations.service import _BRAND_RAW_DATA_COLUMNS

    id_cols = _BRAND_RAW_DATA_COLUMNS["ID"]
    assert id_cols["pic_name"] == "Nama PIC/ Jabatan*"
    assert id_cols["store_link"] == "Link Shopee Mall / LazMall"
    assert id_cols["kategori"] == "Kategori"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && uv run pytest tests/unit/evaluations/test_brand_raw_data_mapping.py -v`
Expected: FAIL — `_BRAND_RAW_DATA_COLUMNS` doesn't exist yet.

- [ ] **Step 3: Add per-marketplace column mapping constant**

At the top of `backend/app/modules/evaluations/service.py`, add:

```python
# Per-marketplace mapping from raw_data column names to BrandRawData fields
_BRAND_RAW_DATA_COLUMNS: dict[str, dict[str, str]] = {
    "ID": {
        "email": "Email",
        "pic_name": "Nama PIC/ Jabatan*",
        "store_link": "Link Shopee Mall / LazMall",
        "kategori": "Kategori",
    },
    "TH": {
        "email": "Email",
        "pic_name": "PIC",
        "store_link": "Shopee Link",
        "kategori": "Product Category",
    },
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && uv run pytest tests/unit/evaluations/test_brand_raw_data_mapping.py -v`
Expected: All PASS.

- [ ] **Step 5: Update BrandRawData extraction to use marketplace**

Replace lines 254-261:

```python
    raw_data = ensure_dict(row.get("raw_data"))
    marketplace = row.get("marketplace", "ID")
    col_map = _BRAND_RAW_DATA_COLUMNS.get(marketplace, _BRAND_RAW_DATA_COLUMNS["ID"])
    brand_raw_data = BrandRawData(
        email=raw_data.get(col_map["email"]),
        pic_name=raw_data.get(col_map["pic_name"]),
        store_link=raw_data.get(col_map["store_link"]),
        kategori=raw_data.get(col_map["kategori"]),
    )
```

- [ ] **Step 6: Run evaluation tests**

Run: `cd backend && uv run pytest tests/ -k evaluation -v`
Expected: All PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/app/modules/evaluations/service.py backend/tests/unit/evaluations/test_brand_raw_data_mapping.py
git commit -m "Use marketplace-aware column mapping for BrandRawData extraction"
```

---

### Task 8: Frontend — Add marketplace to types and API hook

**Files:**
- Modify: `frontend/src/hooks/useBrands.ts`
- Modify: `frontend/src/hooks/useBrandDetail.ts`
- Modify: `frontend/src/hooks/useSync.ts`

- [ ] **Step 1: Add marketplace to BrandListItem type and query**

In `frontend/src/hooks/useBrands.ts`:

```typescript
export interface BrandListItem {
  id: number;
  brand_name: string;
  raw_data: Record<string, unknown>;
  updated_at: string;
  marketplace: string;
  meeting_raw_data: Record<string, unknown> | null;
}

export function useBrands(page = 1, limit = 20, search = '', marketplaces?: string[]) {
  const marketplaceParam = marketplaces?.length ? marketplaces.join(',') : undefined;
  return useQuery({
    queryKey: ['brands', page, limit, search, marketplaceParam],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/brands', {
        params: {
          query: {
            page,
            limit,
            ...(search ? { search } : {}),
            ...(marketplaceParam ? { marketplace: marketplaceParam } : {}),
          },
        },
      });
      if (error) throw new Error('Failed to fetch brands');
      return data as BrandListResponse;
    },
  });
}
```

- [ ] **Step 2: Add marketplace to BrandDetail type**

In `frontend/src/hooks/useBrandDetail.ts`, add `marketplace` to the `BrandDetail` interface:

```typescript
export interface BrandDetail {
  id: number;
  brand_name: string;
  raw_data: Record<string, unknown>;
  updated_at: string;
  marketplace: string;
  meeting_raw_data: Record<string, unknown> | null;
}
```

This is critical — `EvaluationHeader` receives `marketplace` from `BrandDetail`. Without this field, marketplace-aware VP display fields (Task 11) would always fall back to ID.

- [ ] **Step 3: Update `SyncStatusData` type for new sync_details keys**

In `frontend/src/hooks/useSync.ts`, update the `sync_details` type to handle both old and new keys:

```typescript
export interface SyncStatusData {
  id: number;
  last_sync: string;
  status: 'success' | 'failed' | 'in_progress';
  started_at: string;
  completed_at: string | null;
  brands_synced: number;
  error_message: string | null;
  sync_details: Record<string, {
    rows_synced?: number;
    rows_skipped?: number;
    status: string;
    error?: string;
    missing?: string[];
    unexpected?: string[];
  }> | null;
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/hooks/useBrands.ts frontend/src/hooks/useBrandDetail.ts frontend/src/hooks/useSync.ts
git commit -m "Add marketplace to frontend brand types and API hooks"
```

---

### Task 9: Frontend — Marketplace filter chips on BrandsPage

**Files:**
- Modify: `frontend/src/pages/BrandsPage.tsx`
- Modify: `frontend/src/components/brands/BrandTable.tsx`

- [ ] **Step 1: Add marketplace filter state and chips to BrandsPage**

In `frontend/src/pages/BrandsPage.tsx`, add filter state and toggle buttons between SyncStatus and Search:

```tsx
const [activeMarketplaces, setActiveMarketplaces] = useState<string[]>(['ID', 'TH']);

const toggleMarketplace = (mp: string) => {
  setActiveMarketplaces((prev) => {
    if (prev.includes(mp)) {
      // Don't allow deselecting all
      if (prev.length === 1) return prev;
      return prev.filter((m) => m !== mp);
    }
    return [...prev, mp];
  });
  setPage(1);
};
```

Pass `activeMarketplaces` to `useBrands`:

```tsx
const { data, isLoading, isError } = useBrands(page, limit, debouncedSearch, activeMarketplaces);
```

Add filter chips JSX between SyncStatus and Search. Use i18n keys for button labels (add `brands.filterID` and `brands.filterTH` to locale files):

```tsx
{/* Marketplace Filters */}
<div className="mb-4 flex gap-2">
  <Button
    variant={activeMarketplaces.includes('ID') ? 'default' : 'outline'}
    size="sm"
    onClick={() => toggleMarketplace('ID')}
  >
    {t('brands.filterID', { defaultValue: '🇮🇩 Indonesia' })}
  </Button>
  <Button
    variant={activeMarketplaces.includes('TH') ? 'default' : 'outline'}
    size="sm"
    onClick={() => toggleMarketplace('TH')}
  >
    {t('brands.filterTH', { defaultValue: '🇹🇭 Thailand' })}
  </Button>
</div>
```

- [ ] **Step 2: Make BrandTable marketplace-aware**

In `frontend/src/components/brands/BrandTable.tsx`:

Add per-marketplace priority keys:

```typescript
const PRIORITY_KEYS_BY_MARKETPLACE: Record<string, string[]> = {
  ID: ['Nama PIC/ Jabatan*', 'Kategori', 'No WA*'],
  TH: ['PIC', 'Product Category', 'Contact Number'],
};

const PRIORITY_LABELS_BY_MARKETPLACE: Record<string, Record<string, string>> = {
  ID: { 'Nama PIC/ Jabatan*': 'Nama PIC', 'No WA*': 'No WA' },
  TH: {},
};
```

Update `summarizeRawData` to accept marketplace:

```typescript
function summarizeRawData(rawData: Record<string, unknown>, marketplace: string): string {
  const keys = PRIORITY_KEYS_BY_MARKETPLACE[marketplace] ?? PRIORITY_KEYS_BY_MARKETPLACE['ID'];
  const labels = PRIORITY_LABELS_BY_MARKETPLACE[marketplace] ?? {};
  const parts: string[] = [];
  for (const key of keys) {
    if (key in rawData && rawData[key] !== '' && rawData[key] != null) {
      const label = labels[key] ?? key;
      parts.push(`${label}: ${String(rawData[key])}`);
    }
    if (parts.length >= 3) break;
  }
  return parts.join(' | ');
}
```

Add marketplace badge to each row and pass marketplace to summarize:

```tsx
<TableCell className="font-medium">
  <span className="mr-2">{brand.marketplace === 'TH' ? '🇹🇭' : '🇮🇩'}</span>
  {brand.brand_name}
</TableCell>
<TableCell className="text-sm text-muted-foreground">
  {summarizeRawData(brand.raw_data, brand.marketplace) || t('brandTable.fallback.noData')}
</TableCell>
```

- [ ] **Step 3: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds with no TypeScript errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/BrandsPage.tsx frontend/src/components/brands/BrandTable.tsx
git commit -m "Add marketplace filter chips and marketplace-aware brand table"
```

---

### Task 10: Frontend — SyncStatus per-marketplace breakdown and drift dialog

**Files:**
- Modify: `frontend/src/components/sync/SyncStatus.tsx`

- [ ] **Step 1: Update SyncStatus to show per-marketplace breakdown**

Replace the sync_details rendering section (lines 94-112) to handle both old and new key formats, and show a dialog on column drift:

```tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { useState } from 'react';

// Inside SyncStatus component, add drift dialog state:
const [driftError, setDriftError] = useState<{
  marketplace: string;
  missing: string[];
  unexpected: string[];
} | null>(null);

// After triggerSync.mutate onSuccess, check for column drift:
onSuccess: (data: any) => {
  // Check for column drift in response
  if (data?.column_drift_errors?.length > 0) {
    setDriftError(data.column_drift_errors[0]);
  } else {
    toast.success(t('sync.startSuccess'));
  }
},
```

Update the sync details display to handle new keys:

```tsx
{syncStatus?.sync_details && syncStatus.status !== 'in_progress' && (
  <div className="flex gap-4 text-xs text-muted-foreground">
    {Object.entries(syncStatus.sync_details).map(([key, detail]) => (
      <span key={key}>
        {key.toUpperCase()}: {detail.rows_synced ?? 0}{' '}
        {detail.status === 'success' ? '\u2713' :
         detail.status === 'column_drift' ? '\u26A0' : '\u2717'}
      </span>
    ))}
  </div>
)}
```

Add the drift dialog at the end of the component:

```tsx
<Dialog open={!!driftError} onOpenChange={() => setDriftError(null)}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>{t('sync.columnDrift.title', { defaultValue: 'Column Mismatch Detected' })}</DialogTitle>
    </DialogHeader>
    <div className="space-y-2 text-sm">
      <p>{t('sync.columnDrift.marketplace', { defaultValue: 'Marketplace' })}: <strong>{driftError?.marketplace}</strong></p>
      {driftError?.missing.length ? (
        <p>{t('sync.columnDrift.missing', { defaultValue: 'Missing columns' })}: {driftError.missing.join(', ')}</p>
      ) : null}
      {driftError?.unexpected.length ? (
        <p>{t('sync.columnDrift.unexpected', { defaultValue: 'Unexpected columns' })}: {driftError.unexpected.join(', ')}</p>
      ) : null}
    </div>
    <DialogFooter>
      <Button onClick={() => setDriftError(null)}>OK</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

- [ ] **Step 2: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds with no TypeScript errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/sync/SyncStatus.tsx
git commit -m "Add per-marketplace sync status and column drift dialog"
```

---

### Task 11: Frontend — Update EvaluationHeader and orchestrator for marketplace-aware VP fields

**Files:**
- Modify: `frontend/src/components/evaluation/EvaluationHeader.tsx:15-21, 36-42`
- Modify: `frontend/src/hooks/useEvaluationOrchestrator.ts` (sync marketplace from brand)

- [ ] **Step 1: Initialize marketplace from brand data in `useEvaluationOrchestrator`**

In `frontend/src/hooks/useEvaluationOrchestrator.ts`, the marketplace state is initialized as `useState<string>('ID')` and never synced from the brand's actual marketplace. Add a `useEffect` to sync it:

```typescript
// After the brand detail query resolves, sync marketplace from the brand
useEffect(() => {
  if (brand?.marketplace) {
    setMarketplace(brand.marketplace);
  }
}, [brand?.marketplace]);
```

Without this, a Thai brand opened from the brands list would always show Indonesian VP field labels, defeating the purpose of marketplace-aware display fields below.

- [ ] **Step 2: Make VP_DISPLAY_FIELDS marketplace-aware**

Replace the hardcoded `VP_DISPLAY_FIELDS` and `getFieldLabel`:

```typescript
const VP_DISPLAY_FIELDS_BY_MARKETPLACE: Record<string, readonly string[]> = {
  ID: ['Nama PIC/ Jabatan*', 'No WA*', 'Email', 'Kategori', 'Link Shopee Mall / LazMall'],
  TH: ['PIC', 'Contact Number', 'Email', 'Product Category', 'Shopee Link'],
};

// Inside EvaluationHeader component:
const vpDisplayFields = VP_DISPLAY_FIELDS_BY_MARKETPLACE[marketplace ?? 'ID']
  ?? VP_DISPLAY_FIELDS_BY_MARKETPLACE['ID'];

const getFieldLabel = (key: string): string => {
  const labelMap: Record<string, string> = {
    'Nama PIC/ Jabatan*': t('evaluationHeader.fieldLabel.namaPic'),
    'No WA*': t('evaluationHeader.fieldLabel.noWa'),
    'Link Shopee Mall / LazMall': t('evaluationHeader.fieldLabel.linkToko'),
  };
  return labelMap[key] ?? key;
};
```

Update the vpFields filter to use the marketplace-aware list:

```typescript
const vpFields = vpDisplayFields
  .filter((key) => {
    const val = brand.raw_data[key];
    return val !== undefined && val !== null && val !== '';
  })
  .map((key) => [key, String(brand.raw_data[key])] as [string, string]);
```

- [ ] **Step 3: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/evaluation/EvaluationHeader.tsx frontend/src/hooks/useEvaluationOrchestrator.ts
git commit -m "Make EvaluationHeader VP display fields marketplace-aware"
```

---

### Task 12: Terraform — Add Thai VP env vars

**Files:**
- Modify: `infrastructure/terraform/variables.tf`
- Modify: `infrastructure/terraform/modules/environment/variables.tf`
- Modify: `infrastructure/terraform/modules/environment/main.tf`
- Modify: `infrastructure/terraform/main.tf`
- Modify: `infrastructure/terraform/environments/dev.tfvars`
- Modify: `infrastructure/terraform/environments/prod.tfvars`

**Note:** The spec lists 3 env vars (`GSHEETS_VP_SPREADSHEET_ID_TH`, `GSHEETS_VP_RANGE_TH`, `GSHEETS_VP_BRAND_COLUMN_TH`). We only add `GSHEETS_VP_SPREADSHEET_ID_TH` to Terraform because `GSHEETS_VP_RANGE_TH` and `GSHEETS_VP_BRAND_COLUMN_TH` have sensible defaults in `config.py` and are unlikely to differ between dev/prod. This matches the existing pattern where `GSHEETS_VP_RANGE` and `GSHEETS_VP_BRAND_COLUMN` for Indonesia are also not in Terraform.

- [ ] **Step 1: Add root variables**

In `infrastructure/terraform/variables.tf`, after `gsheets_eval_spreadsheet_id` (line 71):

```hcl
variable "gsheets_vp_spreadsheet_id_th" {
  description = "Google Sheets spreadsheet ID for VP brand data (Thailand)"
  type        = string
  default     = ""
}
```

- [ ] **Step 2: Add module variables**

In `infrastructure/terraform/modules/environment/variables.tf`, after `gsheets_eval_spreadsheet_id` (line 94):

```hcl
variable "gsheets_vp_spreadsheet_id_th" {
  description = "Google Sheets spreadsheet ID for VP brand data (Thailand)"
  type        = string
  default     = ""
}
```

- [ ] **Step 3: Add Cloud Run env block**

In `infrastructure/terraform/modules/environment/main.tf`, after the `GSHEETS_EVAL_SPREADSHEET_ID` env block (after line 329):

```hcl
      env {
        name  = "GSHEETS_VP_SPREADSHEET_ID_TH"
        value = var.gsheets_vp_spreadsheet_id_th
      }
```

- [ ] **Step 4: Pass variable to dev and prod modules**

In `infrastructure/terraform/main.tf`:

After line 126 (dev module gsheets section):
```hcl
  gsheets_vp_spreadsheet_id_th   = var.gsheets_vp_spreadsheet_id_th
```

After line 161 (prod module gsheets section):
```hcl
  gsheets_vp_spreadsheet_id_th   = var.gsheets_vp_spreadsheet_id_th
```

- [ ] **Step 5: Set values in tfvars**

In `infrastructure/terraform/environments/dev.tfvars`, after line 21:
```hcl
gsheets_vp_spreadsheet_id_th   = ""  # TODO: Set Thai VP spreadsheet ID
```

In `infrastructure/terraform/environments/prod.tfvars`, add same.

- [ ] **Step 6: Validate Terraform**

Run: `cd infrastructure/terraform && terraform validate`
Expected: Configuration is valid.

- [ ] **Step 7: Commit**

```bash
git add infrastructure/terraform/
git commit -m "Add Thai VP spreadsheet ID to Terraform config"
```

---

### Task 13: Populate expected headers and end-to-end verification

**Files:**
- Modify: `backend/app/modules/sync/column_drift.py` (fill in header lists)

- [ ] **Step 1: Fetch actual headers from both sheets**

Manually read the current header rows from both Google Sheets (Indonesia VP and Thailand VP) and populate the `EXPECTED_HEADERS_VP_ID`, `EXPECTED_HEADERS_VP_TH`, and `EXPECTED_HEADERS_MEETING_ID` lists in `column_drift.py`.

This requires access to the actual spreadsheets. Use the Google Sheets API or check the sheet manually.

- [ ] **Step 2: Run the full test suite**

Run: `cd backend && uv run pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 3: Run the frontend build**

Run: `cd frontend && npm run build`
Expected: Build succeeds.

- [ ] **Step 4: Manual smoke test**

1. Start the backend locally: `cd backend && uv run uvicorn app.main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Navigate to Brands page — verify marketplace filter chips appear
4. Click Sync — verify per-marketplace results show
5. Check that Indonesia brands display correctly
6. If Thai sheet is configured, verify Thai brands appear

- [ ] **Step 5: Final commit**

```bash
git add backend/app/modules/sync/column_drift.py
git commit -m "Populate expected sheet headers for drift detection"
```
