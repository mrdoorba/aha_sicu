"""Unit tests for Google Sheets client."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_settings():
    """Mock settings with Google Sheets configuration."""
    with patch("app.modules.sync.sheets_client.settings") as mock:
        mock.gsheets_credentials_path = "./test-credentials.json"
        mock.gsheets_spreadsheet_id = "test-spreadsheet-id"
        mock.gsheets_range = "Sheet1!A:Z"
        yield mock


@pytest.fixture
def mock_google_service():
    """Mock Google Sheets service."""
    with patch("app.modules.sync.sheets_client.service_account") as mock_sa, patch(
        "app.modules.sync.sheets_client.build"
    ) as mock_build:
        mock_creds = MagicMock()
        mock_sa.Credentials.from_service_account_file.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        yield mock_service


@pytest.mark.asyncio
async def test_fetch_brands_returns_empty_list_for_empty_sheet(mock_settings, mock_google_service):
    """Test that empty sheet returns empty list."""
    from app.modules.sync.sheets_client import GoogleSheetsClient

    mock_google_service.spreadsheets().values().get().execute.return_value = {"values": []}

    client = GoogleSheetsClient()
    brands = await client.fetch_brands_from_sheet()

    assert brands == []


@pytest.mark.asyncio
async def test_fetch_brands_parses_sheet_data_correctly(mock_settings, mock_google_service):
    """Test that sheet data is correctly parsed into brand dictionaries."""
    from app.modules.sync.sheets_client import GoogleSheetsClient

    mock_google_service.spreadsheets().values().get().execute.return_value = {
        "values": [
            ["ID", "Brand Name", "Category", "Marketplace"],
            ["1", "Nike", "Fashion", "Shopee"],
            ["2", "Samsung", "Non-Fashion", "Tokopedia"],
        ]
    }

    client = GoogleSheetsClient()
    brands = await client.fetch_brands_from_sheet()

    assert len(brands) == 2
    assert brands[0]["ID"] == "1"
    assert brands[0]["Brand Name"] == "Nike"
    assert brands[0]["Category"] == "Fashion"
    assert brands[0]["Marketplace"] == "Shopee"
    assert brands[1]["ID"] == "2"
    assert brands[1]["Brand Name"] == "Samsung"
    assert brands[1]["Category"] == "Non-Fashion"


@pytest.mark.asyncio
async def test_fetch_brands_handles_rows_shorter_than_headers(mock_settings, mock_google_service):
    """Test that rows shorter than headers are padded with empty strings."""
    from app.modules.sync.sheets_client import GoogleSheetsClient

    mock_google_service.spreadsheets().values().get().execute.return_value = {
        "values": [
            ["ID", "Brand Name", "Category", "Marketplace"],
            ["1", "Nike"],  # Missing category and marketplace
        ]
    }

    client = GoogleSheetsClient()
    brands = await client.fetch_brands_from_sheet()

    assert len(brands) == 1
    assert brands[0]["ID"] == "1"
    assert brands[0]["Brand Name"] == "Nike"
    assert brands[0]["Category"] == ""
    assert brands[0]["Marketplace"] == ""


@pytest.mark.asyncio
async def test_exponential_backoff_on_rate_limit(mock_settings, mock_google_service):
    """Test that rate limit triggers exponential backoff retry."""
    from unittest.mock import AsyncMock

    from googleapiclient.errors import HttpError

    from app.modules.sync.sheets_client import GoogleSheetsClient

    # Create rate limit error
    rate_limit_response = MagicMock()
    rate_limit_response.status = 429
    rate_limit_error = HttpError(resp=rate_limit_response, content=b"Rate limit exceeded")

    # Fail twice with rate limit, succeed on third
    mock_google_service.spreadsheets().values().get().execute.side_effect = [
        rate_limit_error,
        rate_limit_error,
        {"values": [["ID", "Name"], ["1", "Brand"]]},
    ]

    client = GoogleSheetsClient()

    # Patch asyncio.sleep to speed up test
    with patch("app.modules.sync.sheets_client.asyncio.sleep", new_callable=AsyncMock):
        brands = await client.fetch_brands_from_sheet()

    assert len(brands) == 1
    assert brands[0]["Name"] == "Brand"


@pytest.mark.asyncio
async def test_rate_limit_max_retries_exceeded(mock_settings, mock_google_service):
    """Test that max retries exceeded raises SyncException."""
    from unittest.mock import AsyncMock

    from googleapiclient.errors import HttpError

    from app.core.exceptions import SyncException
    from app.modules.sync.sheets_client import GoogleSheetsClient

    # Create rate limit error
    rate_limit_response = MagicMock()
    rate_limit_response.status = 429
    rate_limit_error = HttpError(resp=rate_limit_response, content=b"Rate limit exceeded")

    # Fail all 3 attempts with rate limit
    mock_google_service.spreadsheets().values().get().execute.side_effect = [
        rate_limit_error,
        rate_limit_error,
        rate_limit_error,
    ]

    client = GoogleSheetsClient()

    with patch("app.modules.sync.sheets_client.asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(SyncException) as exc_info:
            await client.fetch_brands_from_sheet()

    assert exc_info.value.code == "SYNC_RATE_LIMITED"
    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_spreadsheet_not_found_error(mock_settings, mock_google_service):
    """Test that 404 error raises appropriate SyncException."""
    from googleapiclient.errors import HttpError

    from app.core.exceptions import SyncException
    from app.modules.sync.sheets_client import GoogleSheetsClient

    not_found_response = MagicMock()
    not_found_response.status = 404
    not_found_error = HttpError(resp=not_found_response, content=b"Not found")

    mock_google_service.spreadsheets().values().get().execute.side_effect = not_found_error

    client = GoogleSheetsClient()

    with pytest.raises(SyncException) as exc_info:
        await client.fetch_brands_from_sheet()

    assert exc_info.value.code == "SYNC_SHEET_NOT_FOUND"
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_missing_credentials_path_raises_exception():
    """Test that missing credentials path raises SyncException."""
    from app.core.exceptions import SyncException
    from app.modules.sync.sheets_client import GoogleSheetsClient

    with patch("app.modules.sync.sheets_client.settings") as mock_settings:
        mock_settings.gsheets_credentials_path = None
        mock_settings.gsheets_spreadsheet_id = "test-id"

        client = GoogleSheetsClient()

        with pytest.raises(SyncException) as exc_info:
            await client.fetch_brands_from_sheet()

        assert exc_info.value.code == "SYNC_CREDENTIALS_MISSING"


@pytest.mark.asyncio
async def test_missing_spreadsheet_id_raises_exception(mock_google_service):
    """Test that missing spreadsheet ID raises SyncException."""
    from app.core.exceptions import SyncException
    from app.modules.sync.sheets_client import GoogleSheetsClient

    with patch("app.modules.sync.sheets_client.settings") as mock_settings:
        mock_settings.gsheets_credentials_path = "./creds.json"
        mock_settings.gsheets_spreadsheet_id = None

        client = GoogleSheetsClient()

        with pytest.raises(SyncException) as exc_info:
            await client.fetch_brands_from_sheet()

        assert exc_info.value.code == "SYNC_CREDENTIALS_MISSING"
