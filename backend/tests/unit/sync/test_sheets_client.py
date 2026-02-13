"""Unit tests for Google Sheets client."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_settings():
    """Mock settings with Google Sheets configuration."""
    with patch("app.modules.sync.sheets_client.settings") as mock:
        mock.gsheets_credentials_json = None
        mock.gsheets_credentials_path = "./test-credentials.json"
        mock.gsheets_vp_spreadsheet_id = "test-vp-spreadsheet-id"
        mock.gsheets_vp_range = "VP!A:Y"
        mock.gsheets_meeting_spreadsheet_id = "test-meeting-spreadsheet-id"
        mock.gsheets_meeting_range = "ZAP: 1st Meeting!A:D"
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
async def test_fetch_sheet_data_returns_empty_list_for_empty_sheet(mock_settings, mock_google_service):
    """Test that empty sheet returns empty list."""
    from app.modules.sync.sheets_client import GoogleSheetsClient

    mock_google_service.spreadsheets().values().get().execute.return_value = {"values": []}

    client = GoogleSheetsClient()
    data = await client.fetch_sheet_data("test-id", "Sheet1!A:Z")

    assert data == []


@pytest.mark.asyncio
async def test_fetch_sheet_data_parses_correctly(mock_settings, mock_google_service):
    """Test that sheet data is correctly parsed into dictionaries."""
    from app.modules.sync.sheets_client import GoogleSheetsClient

    mock_google_service.spreadsheets().values().get().execute.return_value = {
        "values": [
            ["Nama Brand", "Category", "Status"],
            ["Nike", "Fashion", "Active"],
            ["Samsung", "Non-Fashion", "Active"],
        ]
    }

    client = GoogleSheetsClient()
    data = await client.fetch_sheet_data("test-id", "VP!A:C")

    assert len(data) == 2
    assert data[0]["Nama Brand"] == "Nike"
    assert data[0]["Category"] == "Fashion"
    assert data[1]["Nama Brand"] == "Samsung"
    assert data[1]["Category"] == "Non-Fashion"


@pytest.mark.asyncio
async def test_fetch_sheet_data_pads_short_rows(mock_settings, mock_google_service):
    """Test that rows shorter than headers are padded with empty strings."""
    from app.modules.sync.sheets_client import GoogleSheetsClient

    mock_google_service.spreadsheets().values().get().execute.return_value = {
        "values": [
            ["Brand", "Col2", "Col3", "Col4"],
            ["Nike"],  # Missing 3 columns
        ]
    }

    client = GoogleSheetsClient()
    data = await client.fetch_sheet_data("test-id", "Sheet!A:D")

    assert len(data) == 1
    assert data[0]["Brand"] == "Nike"
    assert data[0]["Col2"] == ""
    assert data[0]["Col3"] == ""
    assert data[0]["Col4"] == ""


@pytest.mark.asyncio
async def test_exponential_backoff_on_rate_limit(mock_settings, mock_google_service):
    """Test that rate limit triggers exponential backoff retry."""
    from unittest.mock import AsyncMock

    from googleapiclient.errors import HttpError

    from app.modules.sync.sheets_client import GoogleSheetsClient

    rate_limit_response = MagicMock()
    rate_limit_response.status = 429
    rate_limit_error = HttpError(resp=rate_limit_response, content=b"Rate limit exceeded")

    mock_google_service.spreadsheets().values().get().execute.side_effect = [
        rate_limit_error,
        rate_limit_error,
        {"values": [["Brand"], ["Nike"]]},
    ]

    client = GoogleSheetsClient()

    with patch("app.modules.sync.sheets_client.asyncio.sleep", new_callable=AsyncMock):
        data = await client.fetch_sheet_data("test-id", "Sheet!A:A")

    assert len(data) == 1
    assert data[0]["Brand"] == "Nike"


@pytest.mark.asyncio
async def test_rate_limit_max_retries_exceeded(mock_settings, mock_google_service):
    """Test that max retries exceeded raises SyncException."""
    from unittest.mock import AsyncMock

    from googleapiclient.errors import HttpError

    from app.core.exceptions import SyncException
    from app.modules.sync.sheets_client import GoogleSheetsClient

    rate_limit_response = MagicMock()
    rate_limit_response.status = 429
    rate_limit_error = HttpError(resp=rate_limit_response, content=b"Rate limit exceeded")

    mock_google_service.spreadsheets().values().get().execute.side_effect = [
        rate_limit_error,
        rate_limit_error,
        rate_limit_error,
    ]

    client = GoogleSheetsClient()

    with patch("app.modules.sync.sheets_client.asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(SyncException) as exc_info:
            await client.fetch_sheet_data("test-id", "Sheet!A:A")

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
        await client.fetch_sheet_data("test-id", "Sheet!A:A")

    assert exc_info.value.code == "SYNC_SHEET_NOT_FOUND"
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_permission_denied_error(mock_settings, mock_google_service):
    """Test that 403 error raises appropriate SyncException."""
    from googleapiclient.errors import HttpError

    from app.core.exceptions import SyncException
    from app.modules.sync.sheets_client import GoogleSheetsClient

    forbidden_response = MagicMock()
    forbidden_response.status = 403
    forbidden_error = HttpError(resp=forbidden_response, content=b"Forbidden")

    mock_google_service.spreadsheets().values().get().execute.side_effect = forbidden_error

    client = GoogleSheetsClient()

    with pytest.raises(SyncException) as exc_info:
        await client.fetch_sheet_data("test-id", "Sheet!A:A")

    assert exc_info.value.code == "SYNC_PERMISSION_DENIED"
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_missing_credentials_path_raises_exception():
    """Test that missing credentials path raises SyncException."""
    from app.core.exceptions import SyncException
    from app.modules.sync.sheets_client import GoogleSheetsClient

    with patch("app.modules.sync.sheets_client.settings") as mock_settings:
        mock_settings.gsheets_credentials_json = None
        mock_settings.gsheets_credentials_path = None

        client = GoogleSheetsClient()

        with pytest.raises(SyncException) as exc_info:
            await client.fetch_sheet_data("test-id", "Sheet!A:A")

        assert exc_info.value.code == "SYNC_CREDENTIALS_MISSING"


@pytest.mark.asyncio
async def test_missing_spreadsheet_id_raises_exception(mock_settings, mock_google_service):
    """Test that missing spreadsheet ID raises SyncException."""
    from app.core.exceptions import SyncException
    from app.modules.sync.sheets_client import GoogleSheetsClient

    client = GoogleSheetsClient()

    with pytest.raises(SyncException) as exc_info:
        await client.fetch_sheet_data("", "Sheet!A:A")

    assert exc_info.value.code == "SYNC_CREDENTIALS_MISSING"


@pytest.mark.asyncio
async def test_fetch_vp_data_uses_correct_config(mock_settings, mock_google_service):
    """Test that fetch_vp_data uses VP configuration."""
    from app.modules.sync.sheets_client import GoogleSheetsClient

    mock_google_service.spreadsheets().values().get().execute.return_value = {
        "values": [["Nama Brand"], ["Nike"]]
    }

    client = GoogleSheetsClient()
    await client.fetch_vp_data()

    # Verify the correct spreadsheet ID and range were used
    call_args = mock_google_service.spreadsheets().values().get.call_args
    assert call_args[1]["spreadsheetId"] == "test-vp-spreadsheet-id"
    assert call_args[1]["range"] == "VP!A:Y"


@pytest.mark.asyncio
async def test_fetch_meeting_data_uses_correct_config(mock_settings, mock_google_service):
    """Test that fetch_meeting_data uses Meeting configuration."""
    from app.modules.sync.sheets_client import GoogleSheetsClient

    mock_google_service.spreadsheets().values().get().execute.return_value = {
        "values": [["Brand"], ["Nike"]]
    }

    client = GoogleSheetsClient()
    await client.fetch_meeting_data()

    # Verify the correct spreadsheet ID and range were used
    call_args = mock_google_service.spreadsheets().values().get.call_args
    assert call_args[1]["spreadsheetId"] == "test-meeting-spreadsheet-id"
    assert call_args[1]["range"] == "ZAP: 1st Meeting!A:D"
