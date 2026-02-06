"""Sync service for orchestrating Google Sheets brand synchronization."""

import logging
from datetime import datetime, timezone
from typing import Any

from app.config import settings
from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.db.queries import sync_status as sync_queries
from app.modules.sync.schemas import (
    SheetSyncResult,
    SyncError,
    SyncResult,
    SyncStatusResponse,
)
from app.modules.sync.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)


async def _sync_sheet_to_table(
    rows: list[dict[str, Any]],
    table: str,
    brand_column: str,
    sheet_type: str,
) -> SheetSyncResult:
    """Sync rows from a sheet to a database table.

    Args:
        rows: List of row dictionaries from Google Sheets.
        table: Target table name ("brand_vp_data" or "brand_meeting_data").
        brand_column: Column name containing the brand name.
        sheet_type: "vp" or "meeting" for logging.

    Returns:
        SheetSyncResult with counts and errors.
    """
    synced_count = 0
    skipped_count = 0
    errors: list[SyncError] = []

    async with db.connection() as conn:
        for row_data in rows:
            try:
                brand_name = row_data.get(brand_column, "").strip()

                if not brand_name:
                    skipped_count += 1
                    continue

                await brand_queries.upsert_brand_data(
                    conn,
                    table=table,
                    brand_name=brand_name,
                    raw_data=row_data,
                )
                synced_count += 1

            except Exception as e:
                brand_name = row_data.get(brand_column, "Unknown")
                errors.append(SyncError(brand=brand_name, error=str(e)))
                logger.warning(f"Failed to sync {sheet_type} brand '{brand_name}': {e}")

    if skipped_count > 0:
        logger.info(f"Skipped {skipped_count} empty rows in {sheet_type} sheet")

    return SheetSyncResult(
        sheet_type=sheet_type,
        rows_synced=synced_count,
        rows_skipped=skipped_count,
        errors=errors,
        success=len(errors) == 0,
    )


async def run_sync() -> SyncResult:
    """Execute full brand sync from both Google Sheets.

    Orchestrates the sync process:
    1. Create sync status record
    2. Fetch and sync VP data
    3. Fetch and sync Meeting data
    4. Update sync status with results

    Returns:
        SyncResult with results from both sheets.
    """
    sheets_client = GoogleSheetsClient()

    # Create sync record
    async with db.connection() as conn:
        sync_id = await sync_queries.create_sync_status(
            conn,
            started_at=datetime.now(timezone.utc),
        )

    logger.info(f"Starting sync with ID: {sync_id}")

    vp_result: SheetSyncResult | None = None
    meeting_result: SheetSyncResult | None = None
    all_errors: list[str] = []

    try:
        # Sync VP sheet
        if settings.gsheets_vp_spreadsheet_id:
            try:
                logger.info("Fetching VP data...")
                vp_rows = await sheets_client.fetch_vp_data()
                logger.info(f"Fetched {len(vp_rows)} rows from VP sheet")

                vp_result = await _sync_sheet_to_table(
                    rows=vp_rows,
                    table="brand_vp_data",
                    brand_column=settings.gsheets_vp_brand_column,
                    sheet_type="vp",
                )
                logger.info(
                    f"VP sync: {vp_result.rows_synced} synced, {len(vp_result.errors)} errors"
                )
            except Exception as e:
                logger.error(f"VP sync failed: {e}")
                all_errors.append(f"VP: {e}")
                vp_result = SheetSyncResult(
                    sheet_type="vp", rows_synced=0, errors=[], success=False
                )
        else:
            logger.info("VP spreadsheet not configured, skipping")

        # Sync Meeting sheet
        if settings.gsheets_meeting_spreadsheet_id:
            try:
                logger.info("Fetching Meeting data...")
                meeting_rows = await sheets_client.fetch_meeting_data()
                logger.info(f"Fetched {len(meeting_rows)} rows from Meeting sheet")

                meeting_result = await _sync_sheet_to_table(
                    rows=meeting_rows,
                    table="brand_meeting_data",
                    brand_column=settings.gsheets_meeting_brand_column,
                    sheet_type="meeting",
                )
                logger.info(
                    f"Meeting sync: {meeting_result.rows_synced} synced, "
                    f"{len(meeting_result.errors)} errors"
                )
            except Exception as e:
                logger.error(f"Meeting sync failed: {e}")
                all_errors.append(f"Meeting: {e}")
                meeting_result = SheetSyncResult(
                    sheet_type="meeting", rows_synced=0, errors=[], success=False
                )
        else:
            logger.info("Meeting spreadsheet not configured, skipping")

        # Calculate totals
        total_synced = (vp_result.rows_synced if vp_result else 0) + (
            meeting_result.rows_synced if meeting_result else 0
        )
        total_errors = (
            (len(vp_result.errors) if vp_result else 0)
            + (len(meeting_result.errors) if meeting_result else 0)
            + len(all_errors)
        )
        overall_success = total_errors == 0 and bool(vp_result or meeting_result)

        # Build error message
        error_message = None
        if all_errors or total_errors > 0:
            error_parts = all_errors.copy()
            if vp_result and vp_result.errors:
                error_parts.append(f"VP: {len(vp_result.errors)} row errors")
            if meeting_result and meeting_result.errors:
                error_parts.append(f"Meeting: {len(meeting_result.errors)} row errors")
            error_message = "; ".join(error_parts)

        # Update sync status
        async with db.connection() as conn:
            await sync_queries.update_sync_status(
                conn,
                sync_id=sync_id,
                completed_at=datetime.now(timezone.utc),
                success=overall_success,
                brands_synced=total_synced,
                error_message=error_message,
            )

        logger.info(f"Sync completed: {total_synced} total synced, {total_errors} errors")

        return SyncResult(
            sync_id=sync_id,
            vp_result=vp_result,
            meeting_result=meeting_result,
            total_synced=total_synced,
            total_errors=total_errors,
            success=overall_success,
        )

    except Exception as e:
        # Update sync status with failure
        async with db.connection() as conn:
            await sync_queries.update_sync_status(
                conn,
                sync_id=sync_id,
                completed_at=datetime.now(timezone.utc),
                success=False,
                brands_synced=0,
                error_message=str(e),
            )
        logger.error(f"SYNC_FAILED: {e}")
        raise


async def get_latest_sync_status() -> SyncStatusResponse | None:
    """Get the most recent sync status.

    Returns:
        SyncStatusResponse if a sync exists, None otherwise.
    """
    async with db.connection() as conn:
        status = await sync_queries.get_latest_sync_status(conn)

    if not status:
        return None

    return SyncStatusResponse(
        id=status["id"],
        started_at=status["started_at"],
        completed_at=status["completed_at"],
        success=status["success"],
        brands_synced=status["brands_synced"],
        error_message=status["error_message"],
    )
