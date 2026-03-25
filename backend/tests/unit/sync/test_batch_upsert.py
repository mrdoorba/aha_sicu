"""Unit tests for batch upsert and atomic sync pipeline."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_conn():
    """Mock asyncpg connection."""
    conn = AsyncMock()
    conn.execute = AsyncMock(return_value="INSERT 0 5")
    return conn


@pytest.fixture
def mock_db():
    """Mock database connection with transaction support."""
    with patch("app.modules.sync.service.db") as mock:
        mock_conn = AsyncMock()
        mock_txn = MagicMock()
        mock_txn.__aenter__ = AsyncMock(return_value=None)
        mock_txn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.transaction = MagicMock(return_value=mock_txn)
        mock.connection.return_value.__aenter__.return_value = mock_conn
        mock.connection.return_value.__aexit__.return_value = None
        yield mock, mock_conn


@pytest.fixture
def mock_brand_queries():
    """Mock brand_queries module."""
    with patch("app.modules.sync.service.brand_queries") as mock:
        mock.batch_upsert_brand_data = AsyncMock(
            side_effect=lambda conn, table, brand_names, raw_data_list, marketplace="ID": len(brand_names)
        )
        yield mock


# --- batch_upsert_brand_data tests ---


async def test_batch_upsert_returns_count_when_all_rows_valid(mock_conn):
    """Verify unnest query is called with correct arrays and returns parsed int."""
    from app.db.queries.brands import batch_upsert_brand_data

    mock_conn.execute.return_value = "INSERT 0 3"

    result = await batch_upsert_brand_data(
        mock_conn,
        table="brand_vp_data",
        brand_names=["Nike", "Adidas", "Puma"],
        raw_data_list=[{"a": 1}, {"b": 2}, {"c": 3}],
    )

    assert result == 3
    mock_conn.execute.assert_called_once()
    call_args = mock_conn.execute.call_args
    assert "unnest($1::text[])" in call_args[0][0]
    assert "unnest($2::text[])" in call_args[0][0]  # marketplace array
    assert "unnest($3::jsonb[])" in call_args[0][0]
    assert "ON CONFLICT (brand_name, marketplace) DO UPDATE" in call_args[0][0]
    assert call_args[0][1] == ["Nike", "Adidas", "Puma"]


async def test_batch_upsert_rejects_when_invalid_table_name(mock_conn):
    """Verify ValueError for table not in allowlist."""
    from app.db.queries.brands import batch_upsert_brand_data

    with pytest.raises(ValueError, match="Invalid table name"):
        await batch_upsert_brand_data(
            mock_conn,
            table="malicious_table",
            brand_names=["Nike"],
            raw_data_list=[{"a": 1}],
        )

    mock_conn.execute.assert_not_called()


async def test_batch_upsert_returns_zero_when_empty_input(mock_conn):
    """Verify empty input returns 0 without hitting the database."""
    from app.db.queries.brands import batch_upsert_brand_data

    result = await batch_upsert_brand_data(
        mock_conn,
        table="brand_vp_data",
        brand_names=[],
        raw_data_list=[],
    )

    assert result == 0
    mock_conn.execute.assert_not_called()


async def test_batch_upsert_returns_parsed_int_when_status_string_valid(mock_conn):
    """Verify 'INSERT 0 50' is parsed to integer 50."""
    from app.db.queries.brands import batch_upsert_brand_data

    mock_conn.execute.return_value = "INSERT 0 50"

    result = await batch_upsert_brand_data(
        mock_conn,
        table="brand_meeting_data",
        brand_names=["A"] * 50,
        raw_data_list=[{"x": 1}] * 50,
    )

    assert result == 50
    assert isinstance(result, int)


# --- _sync_sheet_to_table tests ---


async def test_sync_sheet_skips_when_empty_brand_names(mock_db, mock_brand_queries):
    """Verify rows with empty brand names are excluded before batch upsert."""
    from app.modules.sync.service import _sync_sheet_to_table

    rows = [
        {"brand": "Nike", "data": "a"},
        {"brand": "", "data": "b"},
        {"brand": "   ", "data": "c"},
        {"brand": "Adidas", "data": "d"},
    ]

    result = await _sync_sheet_to_table(
        rows=rows, table="brand_vp_data", brand_column="brand", sheet_type="vp"
    )

    assert result.rows_skipped == 2
    assert result.rows_synced == 2
    assert result.success is True
    # Only valid rows passed to batch_upsert
    call_args = mock_brand_queries.batch_upsert_brand_data.call_args
    assert call_args.kwargs["brand_names"] == ["Nike", "Adidas"]


async def test_sync_sheet_rolls_back_when_batch_upsert_fails(mock_db, mock_brand_queries):
    """Verify SheetSyncResult has success=False when batch upsert raises."""
    from app.modules.sync.service import _sync_sheet_to_table

    mock_brand_queries.batch_upsert_brand_data.side_effect = Exception("DB connection lost")

    rows = [
        {"brand": "Nike", "data": "a"},
        {"brand": "Adidas", "data": "b"},
    ]

    result = await _sync_sheet_to_table(
        rows=rows, table="brand_vp_data", brand_column="brand", sheet_type="vp"
    )

    assert result.success is False
    assert result.rows_synced == 0
    assert len(result.errors) == 1
    assert result.errors[0].brand == "batch"
    assert "DB connection lost" in result.errors[0].error


async def test_sync_sheet_returns_success_when_all_rows_synced(mock_db, mock_brand_queries):
    """Happy path: all rows synced successfully."""
    from app.modules.sync.service import _sync_sheet_to_table

    rows = [
        {"brand": "Nike", "data": "a"},
        {"brand": "Adidas", "data": "b"},
        {"brand": "Puma", "data": "c"},
    ]

    result = await _sync_sheet_to_table(
        rows=rows, table="brand_vp_data", brand_column="brand", sheet_type="vp"
    )

    assert result.success is True
    assert result.rows_synced == 3
    assert result.rows_skipped == 0
    assert len(result.errors) == 0


async def test_sync_sheet_deduplicates_when_duplicate_brand_names(mock_db, mock_brand_queries):
    """Verify only last occurrence of each brand_name reaches batch upsert."""
    from app.modules.sync.service import _sync_sheet_to_table

    rows = [
        {"brand": "Nike", "data": "old"},
        {"brand": "Adidas", "data": "only"},
        {"brand": "Nike", "data": "new"},  # Duplicate — should overwrite
    ]

    result = await _sync_sheet_to_table(
        rows=rows, table="brand_vp_data", brand_column="brand", sheet_type="vp"
    )

    assert result.success is True
    assert result.rows_synced == 2  # Only 2 unique brands

    call_args = mock_brand_queries.batch_upsert_brand_data.call_args
    brand_names = call_args.kwargs["brand_names"]
    raw_data_list = call_args.kwargs["raw_data_list"]

    assert len(brand_names) == 2
    assert "Nike" in brand_names
    assert "Adidas" in brand_names

    # Nike's data should be the LAST occurrence
    nike_idx = brand_names.index("Nike")
    assert raw_data_list[nike_idx]["data"] == "new"
