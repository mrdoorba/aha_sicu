"""Unit tests for sync service."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_db():
    """Mock database connection."""
    with patch("app.modules.sync.service.db") as mock:
        mock_conn = AsyncMock()
        mock.connection.return_value.__aenter__.return_value = mock_conn
        mock.connection.return_value.__aexit__.return_value = None
        yield mock, mock_conn


@pytest.fixture
def mock_sheets_client():
    """Mock Google Sheets client."""
    with patch("app.modules.sync.service.GoogleSheetsClient") as mock:
        instance = MagicMock()
        instance.fetch_brands_from_sheet = AsyncMock()
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
        mock_brand.upsert_brand = AsyncMock()
        yield mock_sync, mock_brand


@pytest.mark.asyncio
async def test_run_sync_success(mock_db, mock_sheets_client, mock_queries):
    """Test successful sync operation."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    # Mock sheet data
    mock_sheets_client.fetch_brands_from_sheet.return_value = [
        {"ID": "1", "Brand Name": "Nike", "Category": "Fashion", "Marketplace": "Shopee"},
        {"ID": "2", "Brand Name": "Samsung", "Category": "Non-Fashion", "Marketplace": "Tokopedia"},
    ]

    result = await run_sync()

    assert result.sync_id == 1
    assert result.brands_synced == 2
    assert result.success is True
    assert len(result.errors) == 0

    # Verify sync status was created and updated
    mock_sync.create_sync_status.assert_called_once()
    mock_sync.update_sync_status.assert_called_once()

    # Verify brands were upserted
    assert mock_brand.upsert_brand.call_count == 2


@pytest.mark.asyncio
async def test_run_sync_partial_failure(mock_db, mock_sheets_client, mock_queries):
    """Test sync with partial failures (some brands fail to upsert)."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    # Mock sheet data
    mock_sheets_client.fetch_brands_from_sheet.return_value = [
        {"ID": "1", "Brand Name": "Nike", "Category": "Fashion"},
        {"ID": "2", "Brand Name": "Samsung", "Category": "Non-Fashion"},
    ]

    # First brand succeeds, second fails
    mock_brand.upsert_brand.side_effect = [None, Exception("Database error")]

    result = await run_sync()

    assert result.sync_id == 1
    assert result.brands_synced == 1
    assert result.success is False
    assert len(result.errors) == 1
    assert result.errors[0].brand == "Samsung"
    assert "Database error" in result.errors[0].error


@pytest.mark.asyncio
async def test_run_sync_skips_missing_required_fields(mock_db, mock_sheets_client, mock_queries):
    """Test sync skips brands missing required fields."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    # Mock sheet data with missing fields
    mock_sheets_client.fetch_brands_from_sheet.return_value = [
        {"ID": "1", "Brand Name": "Nike"},  # Valid
        {"ID": "", "Brand Name": "Samsung"},  # Missing ID
        {"ID": "3", "Brand Name": ""},  # Missing name
        {"Category": "Fashion"},  # Missing both
    ]

    result = await run_sync()

    assert result.brands_synced == 1  # Only Nike synced
    assert len(result.errors) == 3  # Three brands failed


@pytest.mark.asyncio
async def test_run_sync_handles_sheets_error(mock_db, mock_sheets_client, mock_queries):
    """Test sync handles Google Sheets fetch error."""
    from app.core.exceptions import SyncException
    from app.modules.sync.service import run_sync

    mock_sync, _ = mock_queries

    # Mock sheets client error
    mock_sheets_client.fetch_brands_from_sheet.side_effect = SyncException(
        code="SYNC_FAILED", detail="Connection error"
    )

    with pytest.raises(SyncException) as exc_info:
        await run_sync()

    assert exc_info.value.code == "SYNC_FAILED"

    # Verify sync status was updated with failure
    mock_sync.update_sync_status.assert_called_once()
    call_kwargs = mock_sync.update_sync_status.call_args
    assert call_kwargs[1]["success"] is False


@pytest.mark.asyncio
async def test_run_sync_empty_sheet(mock_db, mock_sheets_client, mock_queries):
    """Test sync with empty sheet."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    # Mock empty sheet
    mock_sheets_client.fetch_brands_from_sheet.return_value = []

    result = await run_sync()

    assert result.sync_id == 1
    assert result.brands_synced == 0
    assert result.success is True
    assert len(result.errors) == 0

    # Brand upsert should not be called
    mock_brand.upsert_brand.assert_not_called()


@pytest.mark.asyncio
async def test_get_latest_sync_status_returns_status(mock_db, mock_queries):
    """Test get_latest_sync_status returns formatted response."""
    from app.modules.sync.service import get_latest_sync_status

    mock_sync, _ = mock_queries
    _, mock_conn = mock_db

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
    assert result.success is True
    assert result.brands_synced == 100


@pytest.mark.asyncio
async def test_get_latest_sync_status_returns_none_when_no_syncs(mock_db, mock_queries):
    """Test get_latest_sync_status returns None when no syncs exist."""
    from app.modules.sync.service import get_latest_sync_status

    mock_sync, _ = mock_queries

    mock_sync.get_latest_sync_status.return_value = None

    result = await get_latest_sync_status()

    assert result is None


@pytest.mark.asyncio
async def test_run_sync_handles_alternative_column_names(mock_db, mock_sheets_client, mock_queries):
    """Test sync handles alternative column names (lowercase)."""
    from app.modules.sync.service import run_sync

    mock_sync, mock_brand = mock_queries

    # Mock sheet data with alternative column names
    mock_sheets_client.fetch_brands_from_sheet.return_value = [
        {"id": "1", "name": "Nike", "category": "Fashion", "marketplace": "Shopee"},
    ]

    result = await run_sync()

    assert result.brands_synced == 1
    assert result.success is True
