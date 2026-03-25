"""Unit tests for sync service."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


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
def mock_sheets_client():
    """Mock Google Sheets client."""
    with patch("app.modules.sync.service.GoogleSheetsClient") as mock:
        instance = MagicMock()
        instance.fetch_sheet_data = AsyncMock()
        instance.fetch_headers = AsyncMock(return_value=[])
        instance.fetch_meeting_data = AsyncMock()
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_queries():
    """Mock database queries."""
    with patch("app.modules.sync.service.sync_queries") as mock_sync, patch(
        "app.modules.sync.service.brand_queries"
    ) as mock_brand:
        mock_sync.create_sync_status = AsyncMock(return_value=1)
        mock_sync.update_sync_status = AsyncMock()
        mock_sync.get_latest_sync_status = AsyncMock()
        mock_brand.upsert_brand_data = AsyncMock()
        mock_brand.batch_upsert_brand_data = AsyncMock(
            side_effect=lambda conn, table, brand_names, raw_data_list, marketplace="ID": len(brand_names)
        )
        yield mock_sync, mock_brand


@pytest.fixture
def mock_settings():
    """Mock settings with ID VP configured."""
    with patch("app.modules.sync.service.settings") as mock:
        mock.gsheets_vp_spreadsheet_id = "vp-id"
        mock.gsheets_vp_range = "VP!A:Y"
        mock.gsheets_vp_brand_column = "Nama Brand"
        mock.gsheets_vp_spreadsheet_id_th = None
        mock.gsheets_vp_range_th = "VP!A:W"
        mock.gsheets_vp_brand_column_th = "Brand"
        mock.gsheets_meeting_spreadsheet_id = "meeting-id"
        mock.gsheets_meeting_range = "ZAP: 1st Meeting!A:D"
        mock.gsheets_meeting_brand_column = "Brand"
        yield mock


async def test_run_sync_both_sheets_success(mock_db, mock_sheets_client, mock_queries, mock_settings):
    """Test successful sync of both sheets."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    # Mock VP data (now via fetch_sheet_data)
    mock_sheets_client.fetch_sheet_data.return_value = [
        {"Nama Brand": "Nike", "Category": "Fashion"},
        {"Nama Brand": "Adidas", "Category": "Fashion"},
    ]

    # Mock Meeting data
    mock_sheets_client.fetch_meeting_data.return_value = [
        {"Brand": "Samsung", "Status": "Active"},
    ]

    result = await run_sync()

    assert result.sync_id == 1
    assert "vp_id" in result.vp_results
    vp_result = result.vp_results["vp_id"]
    assert vp_result.rows_synced == 2
    assert result.meeting_result is not None
    assert result.meeting_result.rows_synced == 1
    assert result.total_synced == 3
    assert result.success is True


async def test_run_sync_vp_only(mock_db, mock_sheets_client, mock_queries):
    """Test sync with only VP sheet configured."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    with patch("app.modules.sync.service.settings") as mock_settings:
        mock_settings.gsheets_vp_spreadsheet_id = "vp-id"
        mock_settings.gsheets_vp_range = "VP!A:Y"
        mock_settings.gsheets_vp_brand_column = "Nama Brand"
        mock_settings.gsheets_vp_spreadsheet_id_th = None
        mock_settings.gsheets_meeting_spreadsheet_id = None  # Not configured

        mock_sheets_client.fetch_sheet_data.return_value = [
            {"Nama Brand": "Nike"},
        ]

        result = await run_sync()

        assert "vp_id" in result.vp_results
        assert result.vp_results["vp_id"].rows_synced == 1
        assert result.meeting_result is None
        assert result.total_synced == 1


async def test_run_sync_atomic_failure_when_batch_upsert_fails(mock_db, mock_sheets_client, mock_queries, mock_settings):
    """Test sync fails atomically when batch upsert raises."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    mock_sheets_client.fetch_sheet_data.return_value = [
        {"Nama Brand": "Nike"},
        {"Nama Brand": "Adidas"},
    ]
    mock_sheets_client.fetch_meeting_data.return_value = []

    # Batch upsert fails — entire sheet rolls back
    mock_brand.batch_upsert_brand_data.side_effect = Exception("DB error")

    result = await run_sync()

    vp_result = result.vp_results["vp_id"]
    assert vp_result.rows_synced == 0
    assert len(vp_result.errors) == 1
    assert vp_result.errors[0].brand == "batch"
    assert vp_result.success is False
    assert result.success is False


async def test_run_sync_skips_empty_brand_names(mock_db, mock_sheets_client, mock_queries, mock_settings):
    """Test sync skips rows with empty brand names."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    mock_sheets_client.fetch_sheet_data.return_value = [
        {"Nama Brand": "Nike"},
        {"Nama Brand": ""},  # Empty brand name
        {"Nama Brand": "   "},  # Whitespace only
    ]
    mock_sheets_client.fetch_meeting_data.return_value = []

    result = await run_sync()

    vp_result = result.vp_results["vp_id"]
    assert vp_result.rows_synced == 1
    assert vp_result.rows_skipped == 2  # Two empty rows silently skipped
    assert len(vp_result.errors) == 0  # Not counted as errors


async def test_run_sync_handles_sheet_fetch_error(mock_db, mock_sheets_client, mock_queries, mock_settings):
    """Test sync handles error fetching from sheet."""
    from app.core.exceptions import SyncException
    from app.modules.sync.service import run_sync

    mock_sync, _ = mock_queries

    mock_sheets_client.fetch_sheet_data.side_effect = SyncException(
        code="SYNC_PERMISSION_DENIED", detail="No access"
    )
    mock_sheets_client.fetch_meeting_data.return_value = [{"Brand": "Test"}]

    result = await run_sync()

    # VP failed but meeting succeeded
    assert "vp_id" in result.vp_results
    assert result.vp_results["vp_id"].success is False
    assert result.meeting_result is not None
    assert result.meeting_result.rows_synced == 1
    assert result.success is False  # Overall failed because VP failed


async def test_run_sync_empty_sheets(mock_db, mock_sheets_client, mock_queries, mock_settings):
    """Test sync with empty sheets."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    mock_sheets_client.fetch_sheet_data.return_value = []
    mock_sheets_client.fetch_meeting_data.return_value = []

    result = await run_sync()

    assert result.total_synced == 0
    assert result.total_errors == 0
    assert result.success is True


async def test_run_sync_with_pre_created_sync_id(mock_db, mock_sheets_client, mock_queries, mock_settings):
    """Test run_sync with pre-created sync_id skips creating a new sync_status record."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    mock_sheets_client.fetch_sheet_data.return_value = [
        {"Nama Brand": "Nike"},
    ]
    mock_sheets_client.fetch_meeting_data.return_value = []

    result = await run_sync(sync_id=42)

    assert result.sync_id == 42
    # Should NOT have created a new sync_status record
    mock_sync.create_sync_status.assert_not_called()
    # Should still update sync status at completion
    mock_sync.update_sync_status.assert_called_once()
    assert result.vp_results["vp_id"].rows_synced == 1
    assert result.success is True


async def test_run_sync_without_sync_id_creates_record(mock_db, mock_sheets_client, mock_queries, mock_settings):
    """Test run_sync without sync_id still creates a sync_status record (backward compatible)."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    mock_sheets_client.fetch_sheet_data.return_value = []
    mock_sheets_client.fetch_meeting_data.return_value = []

    result = await run_sync()

    assert result.sync_id == 1  # From mock default return_value
    # Should have created a new sync_status record
    mock_sync.create_sync_status.assert_called_once()


async def test_get_latest_sync_status_returns_status(mock_db, mock_queries):
    """Test get_latest_sync_status returns formatted response."""
    from app.modules.sync.service import get_latest_sync_status

    mock_sync, _ = mock_queries

    mock_sync.get_latest_sync_status.return_value = {
        "id": 1,
        "started_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
        "completed_at": datetime(2026, 2, 5, 10, 5, 0, tzinfo=timezone.utc),
        "success": True,
        "brands_synced": 100,
        "error_message": None,
    }

    result = await get_latest_sync_status()

    assert result is not None
    assert result.id == 1
    assert result.status == "success"
    assert result.brands_synced == 100
    assert result.last_sync is not None


async def test_get_latest_sync_status_returns_none_when_no_syncs(mock_db, mock_queries):
    """Test get_latest_sync_status returns None when no syncs exist."""
    from app.modules.sync.service import get_latest_sync_status

    mock_sync, _ = mock_queries
    mock_sync.get_latest_sync_status.return_value = None

    result = await get_latest_sync_status()

    assert result is None
