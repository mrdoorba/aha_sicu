"""Sync service for orchestrating Google Sheets brand synchronization."""

import logging
import time
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
    skipped_count = 0
    errors: list[SyncError] = []

    # Step 1: Pre-filter rows with empty brand names
    valid_rows: list[dict[str, Any]] = []
    for row_data in rows:
        brand_name = row_data.get(brand_column, "").strip()
        if not brand_name:
            skipped_count += 1
            continue
        valid_rows.append(row_data)

    if skipped_count > 0:
        logger.info(f"Skipped {skipped_count} empty rows in {sheet_type} sheet")

    if not valid_rows:
        return SheetSyncResult(
            sheet_type=sheet_type,
            rows_synced=0,
            rows_skipped=skipped_count,
            errors=[],
            success=True,
        )

    # Step 2: Deduplicate by brand_name (last occurrence wins)
    seen: dict[str, dict[str, Any]] = {}
    for row_data in valid_rows:
        brand_name = row_data.get(brand_column, "").strip()
        seen[brand_name] = row_data

    dedup_count = len(valid_rows) - len(seen)
    if dedup_count > 0:
        logger.info(
            f"Deduplicated {dedup_count} duplicate brand names in {sheet_type} sheet"
        )

    # Step 3: Build parallel arrays
    brand_names = list(seen.keys())
    raw_data_list = list(seen.values())

    # Step 4: Execute batch upsert in transaction
    start_time = time.monotonic()
    try:
        async with db.connection() as conn:
            async with conn.transaction():
                synced_count = await brand_queries.batch_upsert_brand_data(
                    conn,
                    table=table,
                    brand_names=brand_names,
                    raw_data_list=raw_data_list,
                )

        duration_ms = (time.monotonic() - start_time) * 1000
        logger.info(
            "batch_upsert_complete",
            extra={
                "table": table,
                "sheet_type": sheet_type,
                "batch_size": len(brand_names),
                "skipped": skipped_count,
                "deduplicated": dedup_count,
                "duration_ms": round(duration_ms, 1),
            },
        )

        return SheetSyncResult(
            sheet_type=sheet_type,
            rows_synced=synced_count,
            rows_skipped=skipped_count,
            errors=[],
            success=True,
        )

    except Exception as e:
        duration_ms = (time.monotonic() - start_time) * 1000
        logger.error(
            f"Batch upsert failed for {sheet_type} sheet: {e}",
            extra={"table": table, "duration_ms": round(duration_ms, 1)},
        )
        errors.append(SyncError(brand="batch", error=str(e)))
        return SheetSyncResult(
            sheet_type=sheet_type,
            rows_synced=0,
            rows_skipped=skipped_count,
            errors=errors,
            success=False,
        )


async def _sync_vp_sheet(
    sheets_client: GoogleSheetsClient,
) -> SheetSyncResult | None:
    """Fetch and sync VP sheet data.

    Returns None if VP spreadsheet is not configured.
    Raises on unrecoverable fetch errors.
    """
    if not settings.gsheets_vp_spreadsheet_id:
        logger.info("VP spreadsheet not configured, skipping")
        return None

    try:
        logger.info("Fetching VP data...")
        vp_rows = await sheets_client.fetch_vp_data()
        logger.info(f"Fetched {len(vp_rows)} rows from VP sheet")

        result = await _sync_sheet_to_table(
            rows=vp_rows,
            table="brand_vp_data",
            brand_column=settings.gsheets_vp_brand_column,
            sheet_type="vp",
        )
        logger.info(
            f"VP sync: {result.rows_synced} synced, {len(result.errors)} errors"
        )
        return result
    except Exception as e:
        logger.error(f"VP sync failed: {e}")
        raise


async def _sync_meeting_sheet(
    sheets_client: GoogleSheetsClient,
) -> SheetSyncResult | None:
    """Fetch and sync Meeting sheet data.

    Returns None if Meeting spreadsheet is not configured.
    Raises on unrecoverable fetch errors.
    """
    if not settings.gsheets_meeting_spreadsheet_id:
        logger.info("Meeting spreadsheet not configured, skipping")
        return None

    try:
        logger.info("Fetching Meeting data...")
        meeting_rows = await sheets_client.fetch_meeting_data()
        logger.info(f"Fetched {len(meeting_rows)} rows from Meeting sheet")

        result = await _sync_sheet_to_table(
            rows=meeting_rows,
            table="brand_meeting_data",
            brand_column=settings.gsheets_meeting_brand_column,
            sheet_type="meeting",
        )
        logger.info(
            f"Meeting sync: {result.rows_synced} synced, "
            f"{len(result.errors)} errors"
        )
        return result
    except Exception as e:
        logger.error(f"Meeting sync failed: {e}")
        raise


async def run_sync(sync_id: int | None = None) -> SyncResult:
    """Execute full brand sync from both Google Sheets.

    Orchestrates the sync process:
    1. Create sync status record (or use pre-created sync_id)
    2. Fetch and sync VP data
    3. Fetch and sync Meeting data
    4. Update sync status with results

    Args:
        sync_id: Optional pre-created sync_status ID. If provided, skips
                 creating a new record. Used by POST /sync endpoint.

    Returns:
        SyncResult with results from both sheets.
    """
    sheets_client = GoogleSheetsClient()

    # Create sync record only if sync_id not provided
    if sync_id is None:
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
        try:
            vp_result = await _sync_vp_sheet(sheets_client)
        except Exception as e:
            all_errors.append(f"VP: {e}")
            vp_result = SheetSyncResult(
                sheet_type="vp", rows_synced=0, errors=[], success=False
            )

        # Sync Meeting sheet
        try:
            meeting_result = await _sync_meeting_sheet(sheets_client)
        except Exception as e:
            all_errors.append(f"Meeting: {e}")
            meeting_result = SheetSyncResult(
                sheet_type="meeting", rows_synced=0, errors=[], success=False
            )

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

        # Build per-sheet breakdown for persistence
        sync_details = {}
        if vp_result:
            sync_details["vp_sheet"] = {
                "rows_synced": vp_result.rows_synced,
                "rows_skipped": vp_result.rows_skipped,
                "errors": [e.model_dump() for e in vp_result.errors],
                "status": "success" if vp_result.success else "failed",
            }
        if meeting_result:
            sync_details["meeting_sheet"] = {
                "rows_synced": meeting_result.rows_synced,
                "rows_skipped": meeting_result.rows_skipped,
                "errors": [e.model_dump() for e in meeting_result.errors],
                "status": "success" if meeting_result.success else "failed",
            }

        # Update sync status
        completed_at = datetime.now(timezone.utc)
        async with db.connection() as conn:
            await sync_queries.update_sync_status(
                conn,
                sync_id=sync_id,
                completed_at=completed_at,
                success=overall_success,
                brands_synced=total_synced,
                error_message=error_message,
                sync_details=sync_details if sync_details else None,
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
        failed_at = datetime.now(timezone.utc)
        async with db.connection() as conn:
            await sync_queries.update_sync_status(
                conn,
                sync_id=sync_id,
                completed_at=failed_at,
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
        sync_details=status.get("sync_details"),
        timed_out=status.get("timed_out", False),
    )
