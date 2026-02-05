"""Google Sheets client for fetching brand data."""

import asyncio
import logging
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings
from app.core.exceptions import SyncException

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class GoogleSheetsClient:
    """Client for interacting with Google Sheets API."""

    def __init__(self) -> None:
        self._service = None

    def _get_service(self):
        """Lazy initialization of Google Sheets service."""
        if self._service is None:
            if not settings.gsheets_credentials_path:
                raise SyncException(
                    code="SYNC_CREDENTIALS_MISSING",
                    detail="Google Sheets credentials path not configured",
                )
            creds = service_account.Credentials.from_service_account_file(
                settings.gsheets_credentials_path,
                scopes=SCOPES,
            )
            self._service = build("sheets", "v4", credentials=creds)
        return self._service

    async def fetch_sheet_data(
        self,
        spreadsheet_id: str,
        range_name: str,
    ) -> list[dict[str, Any]]:
        """Fetch data from a Google Sheet with exponential backoff retry.

        Args:
            spreadsheet_id: The Google Sheets spreadsheet ID.
            range_name: The range to fetch (e.g., "VP!A:Y").

        Returns:
            List of dictionaries, one per row (header row becomes keys).

        Raises:
            SyncException: If fetch fails after retries or due to configuration issues.
        """
        if not spreadsheet_id:
            raise SyncException(
                code="SYNC_CREDENTIALS_MISSING",
                detail="Spreadsheet ID not provided",
            )

        max_retries = 3
        base_delay = 1.0  # seconds

        for attempt in range(max_retries):
            try:
                service = self._get_service()
                # Run synchronous Google API call in thread pool
                result = await asyncio.to_thread(
                    lambda: service.spreadsheets()
                    .values()
                    .get(
                        spreadsheetId=spreadsheet_id,
                        range=range_name,
                    )
                    .execute()
                )

                rows = result.get("values", [])
                if not rows:
                    return []

                # First row is header
                headers = rows[0]
                data = []
                for row in rows[1:]:
                    # Pad row with empty strings if shorter than headers
                    padded_row = row + [""] * (len(headers) - len(row))
                    row_data = dict(zip(headers, padded_row))
                    data.append(row_data)

                logger.info(
                    f"Successfully fetched {len(data)} rows from {spreadsheet_id} range {range_name}"
                )
                return data

            except HttpError as e:
                if e.resp.status == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        delay = base_delay * (2**attempt)  # Exponential backoff
                        logger.warning(
                            f"SYNC_RATE_LIMITED: Rate limit hit, retrying in {delay}s "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(delay)
                        continue
                    logger.error("SYNC_RATE_LIMITED: Max retries exceeded due to rate limiting")
                    raise SyncException(
                        code="SYNC_RATE_LIMITED",
                        detail="Max retries exceeded due to rate limiting",
                        status_code=429,
                    )
                elif e.resp.status == 404:
                    logger.error(f"SYNC_SHEET_NOT_FOUND: Spreadsheet {spreadsheet_id} not found")
                    raise SyncException(
                        code="SYNC_SHEET_NOT_FOUND",
                        detail=f"Spreadsheet not found or not accessible: {spreadsheet_id}",
                        status_code=404,
                    )
                elif e.resp.status == 403:
                    logger.error(f"SYNC_PERMISSION_DENIED: No access to spreadsheet {spreadsheet_id}")
                    raise SyncException(
                        code="SYNC_PERMISSION_DENIED",
                        detail=f"Permission denied. Share the sheet with the service account.",
                        status_code=403,
                    )
                else:
                    logger.error(f"SYNC_FAILED: Google Sheets API error: {e}")
                    raise SyncException(
                        code="SYNC_FAILED",
                        detail=f"Google Sheets API error: {e}",
                    )
            except SyncException:
                # Re-raise SyncException as-is
                raise
            except FileNotFoundError:
                logger.error("SYNC_CREDENTIALS_MISSING: Credentials file not found")
                raise SyncException(
                    code="SYNC_CREDENTIALS_MISSING",
                    detail=f"Credentials file not found at: {settings.gsheets_credentials_path}",
                )
            except Exception as e:
                logger.error(f"SYNC_FAILED: Unexpected error fetching from Google Sheets: {e}")
                raise SyncException(
                    code="SYNC_FAILED",
                    detail=f"Unexpected error: {e}",
                )

        # Should not reach here, but handle gracefully
        raise SyncException(
            code="SYNC_FAILED",
            detail="Failed to fetch data after all retries",
        )

    async def fetch_vp_data(self) -> list[dict[str, Any]]:
        """Fetch VP brand data from configured spreadsheet."""
        return await self.fetch_sheet_data(
            spreadsheet_id=settings.gsheets_vp_spreadsheet_id,
            range_name=settings.gsheets_vp_range,
        )

    async def fetch_meeting_data(self) -> list[dict[str, Any]]:
        """Fetch 1st Meeting brand data from configured spreadsheet."""
        return await self.fetch_sheet_data(
            spreadsheet_id=settings.gsheets_meeting_spreadsheet_id,
            range_name=settings.gsheets_meeting_range,
        )
