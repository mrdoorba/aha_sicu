"""Sync service for orchestrating Google Sheets brand synchronization."""

import logging
import time
from datetime import datetime, timezone
from typing import Any

from app.config import settings
from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.db.queries import sync_status as sync_queries
from app.modules.sync.column_drift import (
    ColumnDriftError,
    validate_headers,
    EXPECTED_HEADERS_VP_ID,
    EXPECTED_HEADERS_VP_TH,
)
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
    marketplace: str = "ID",
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
                    marketplace=marketplace,
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
            marketplace="ID",
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

    vp_results: dict[str, SheetSyncResult | ColumnDriftError] = {}
    meeting_result: SheetSyncResult | None = None
    all_errors: list[str] = []

    try:
        # Sync VP sheets (all configured marketplaces)
        try:
            vp_results = await _sync_vp_sheets(sheets_client)
        except Exception as e:
            all_errors.append(f"VP: {e}")

        # Sync Meeting sheet
        try:
            meeting_result = await _sync_meeting_sheet(sheets_client)
        except Exception as e:
            all_errors.append(f"Meeting: {e}")
            meeting_result = SheetSyncResult(
                sheet_type="meeting", rows_synced=0, errors=[], success=False
            )

        # Build sync_details with new keys
        sync_details: dict[str, Any] = {}
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
            sync_details["m1_id"] = {
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
        vp_failures = sum(
            1 for r in vp_results.values()
            if isinstance(r, SheetSyncResult) and not r.success
        )
        total_errors = vp_errors + meeting_errors + len(all_errors)
        overall_success = (
            total_errors == 0
            and len(drift_errors) == 0
            and vp_failures == 0
        )

        # Build error message
        error_message = None
        if all_errors or total_errors > 0 or drift_errors:
            error_parts = all_errors.copy()
            for r in vp_results.values():
                if isinstance(r, SheetSyncResult) and r.errors:
                    error_parts.append(f"{r.sheet_type}: {len(r.errors)} row errors")
            if meeting_result and meeting_result.errors:
                error_parts.append(f"Meeting: {len(meeting_result.errors)} row errors")
            for d in drift_errors:
                error_parts.append(f"Column drift ({d['marketplace']})")
            error_message = "; ".join(error_parts) if error_parts else None

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
            vp_results=vp_results,
            meeting_result=meeting_result,
            total_synced=total_synced,
            total_errors=total_errors,
            success=overall_success,
            column_drift_errors=drift_errors,
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
