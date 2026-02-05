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

    async def fetch_brands_from_sheet(self) -> list[dict[str, Any]]:
        """Fetch brand data from Google Sheet with exponential backoff retry.

        Returns:
            List of brand dictionaries parsed from sheet rows.

        Raises:
            SyncException: If fetch fails after retries or due to configuration issues.
        """
        if not settings.gsheets_spreadsheet_id:
            raise SyncException(
                code="SYNC_CREDENTIALS_MISSING",
                detail="Google Sheets spreadsheet ID not configured",
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
                        spreadsheetId=settings.gsheets_spreadsheet_id,
                        range=settings.gsheets_range,
                    )
                    .execute()
                )

                rows = result.get("values", [])
                if not rows:
                    return []

                # First row is header
                headers = rows[0]
                brands = []
                for row in rows[1:]:
                    # Pad row with empty strings if shorter than headers
                    padded_row = row + [""] * (len(headers) - len(row))
                    brand_data = dict(zip(headers, padded_row))
                    brands.append(brand_data)

                logger.info(f"Successfully fetched {len(brands)} brands from Google Sheets")
                return brands

            except HttpError as e:
                if e.resp.status == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        delay = base_delay * (2**attempt)  # Exponential backoff
                        logger.warning(
                            f"SYNC_RATE_LIMITED: Rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{max_retries})"
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
                    logger.error(f"SYNC_SHEET_NOT_FOUND: Spreadsheet not found or inaccessible")
                    raise SyncException(
                        code="SYNC_SHEET_NOT_FOUND",
                        detail="Spreadsheet not found or not accessible",
                        status_code=404,
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
            detail="Failed to fetch brands after all retries",
        )
