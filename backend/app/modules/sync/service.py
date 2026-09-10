"""Sync service for orchestrating Google Sheets brand synchronization."""

import logging
import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from app.calculators.package_fit import has_scored_vp
from app.config import settings
from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.db.queries import sync_status as sync_queries
from app.modules.sync.column_drift import (
    ColumnDriftError,
    EXPECTED_HEADERS_MEETING_ID,
    EXPECTED_HEADERS_MEETING_TH,
    EXPECTED_HEADERS_VP_ID,
    EXPECTED_HEADERS_VP_TH,
    validate_headers,
)
from app.modules.sync.schemas import (
    SheetSyncResult,
    SyncError,
    SyncResult,
    SyncStatusResponse,
)
from app.modules.sync.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)


def _summarize_changed_columns(drift: ColumnDriftError) -> str:
    """Build a compact human-readable summary of header changes."""
    parts: list[str] = []
    for change in drift.changed_columns:
        expected = change.get("expected")
        actual = change.get("actual")
        if expected and actual:
            parts.append(f"{expected} → {actual}")
        elif expected:
            parts.append(f"missing {expected}")
        elif actual:
            parts.append(f"unexpected {actual}")
    return "; ".join(parts) or "Header mismatch detected"


def _build_drift_sync_detail(drift: ColumnDriftError) -> dict[str, Any]:
    """Convert a drift error into the persisted sync_details shape."""
    return {
        "status": drift.status,
        "marketplace": drift.marketplace,
        "sheet": drift.sheet,
        "error": _summarize_changed_columns(drift),
        "expected_headers": drift.expected,
        "actual_headers": drift.actual,
        "missing": drift.missing,
        "unexpected": drift.unexpected,
        "changed_columns": drift.changed_columns,
    }


def _format_drift_error_message(detail: dict[str, Any]) -> str:
    """Build the high-level sync error message for a drift detail entry."""
    changed_columns = detail.get("changed_columns", [])
    changed_summary = "; ".join(
        (
            f"{change.get('expected')} → {change.get('actual')}"
            if change.get("expected") and change.get("actual")
            else f"missing {change.get('expected')}"
            if change.get("expected")
            else f"unexpected {change.get('actual')}"
        )
        for change in changed_columns
    )
    if not changed_summary:
        changed_summary = str(detail.get("error") or "Header mismatch detected")
    return (
        f"Column drift ({detail.get('sheet')} {detail.get('marketplace')}): "
        f"{changed_summary}"
    )


def _get_meeting_configs() -> list[dict[str, Any]]:
    """Build Meeting configs from settings. ID always, TH if configured."""
    configs = [
        {
            "marketplace": "ID",
            "spreadsheet_id": settings.gsheets_meeting_spreadsheet_id,
            "range": settings.gsheets_meeting_range,
            "brand_column": settings.gsheets_meeting_brand_column,
            "expected_headers": EXPECTED_HEADERS_MEETING_ID,
            "sheet_name": settings.gsheets_meeting_range.split("!")[0],
        },
    ]
    if settings.gsheets_meeting_spreadsheet_id_th:
        configs.append({
            "marketplace": "TH",
            "spreadsheet_id": settings.gsheets_meeting_spreadsheet_id_th,
            "range": settings.gsheets_meeting_range_th,
            "brand_column": settings.gsheets_meeting_brand_column_th,
            "expected_headers": EXPECTED_HEADERS_MEETING_TH,
            "sheet_name": settings.gsheets_meeting_range_th.split("!")[0],
        })
    return configs


async def _sync_sheet_to_table(
    rows: list[dict[str, Any]],
    table: str,
    brand_column: str,
    sheet_type: str,
    marketplace: str = "ID",
    prefer_row: Callable[[dict[str, Any]], bool] | None = None,
) -> SheetSyncResult:
    """Sync rows from a sheet to a database table.

    Args:
        rows: List of row dictionaries from Google Sheets.
        table: Target table name ("brand_vp_data" or "brand_meeting_data").
        brand_column: Column name containing the brand name.
        sheet_type: "vp" or "meeting" for logging.
        prefer_row: Decides which of two rows sharing a brand name survives.
            A row this returns True for is never displaced by one it returns
            False for; otherwise the later row wins. None means the later row
            always wins.

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

    # Step 2: Deduplicate by brand_name (last occurrence wins, unless
    # prefer_row ranks the row already held above it)
    seen: dict[str, dict[str, Any]] = {}
    for row_data in valid_rows:
        brand_name = row_data.get(brand_column, "").strip()
        held = seen.get(brand_name)
        if (
            prefer_row is not None
            and held is not None
            and prefer_row(held)
            and not prefer_row(row_data)
        ):
            continue
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
                prefer_row=has_scored_vp,
            )
            results[key] = result

        except Exception as e:
            logger.error(f"VP sync failed for {mk}: {e}")
            results[key] = SheetSyncResult(
                sheet_type=key, rows_synced=0, errors=[], success=False
            )

    return results


async def _sync_meeting_sheets(
    sheets_client: GoogleSheetsClient,
) -> dict[str, SheetSyncResult | ColumnDriftError]:
    """Fetch and sync Meeting sheets for all configured marketplaces."""
    results: dict[str, SheetSyncResult | ColumnDriftError] = {}

    for cfg in _get_meeting_configs():
        mk = cfg["marketplace"]
        key = f"m1_{mk.lower()}"

        if not cfg["spreadsheet_id"]:
            logger.info(f"Meeting spreadsheet for {mk} not configured, skipping")
            continue

        try:
            actual_headers = await sheets_client.fetch_headers(
                cfg["spreadsheet_id"], cfg["sheet_name"]
            )
            drift = validate_headers(
                cfg["expected_headers"], actual_headers,
                marketplace=mk, sheet="Meeting",
            )
            if drift:
                logger.warning(f"Column drift detected for Meeting {mk}: {drift}")
                results[key] = drift
                continue

            rows = await sheets_client.fetch_sheet_data(
                cfg["spreadsheet_id"], cfg["range"]
            )
            result = await _sync_sheet_to_table(
                rows=rows,
                table="brand_meeting_data",
                brand_column=cfg["brand_column"],
                sheet_type=key,
                marketplace=mk,
            )
            results[key] = result

        except Exception as e:
            logger.error(f"Meeting sync failed for {mk}: {e}")
            results[key] = SheetSyncResult(
                sheet_type=key, rows_synced=0, errors=[], success=False
            )

    return results


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
    meeting_results: dict[str, SheetSyncResult | ColumnDriftError] = {}
    all_errors: list[str] = []

    try:
        # Sync VP sheets (all configured marketplaces)
        try:
            vp_results = await _sync_vp_sheets(sheets_client)
        except Exception as e:
            all_errors.append(f"VP: {e}")

        # Sync Meeting sheets (all configured marketplaces)
        try:
            meeting_results = await _sync_meeting_sheets(sheets_client)
        except Exception as e:
            all_errors.append(f"Meeting: {e}")

        # VP and Meeting results share the same shape; aggregate over both.
        all_results = {**vp_results, **meeting_results}

        # Build sync_details with per-sheet keys (vp_id, vp_th, m1_id, m1_th)
        sync_details: dict[str, Any] = {}
        for key, result in all_results.items():
            if isinstance(result, ColumnDriftError):
                sync_details[key] = _build_drift_sync_detail(result)
            elif isinstance(result, SheetSyncResult):
                sync_details[key] = {
                    "rows_synced": result.rows_synced,
                    "rows_skipped": result.rows_skipped,
                    "errors": [e.model_dump() for e in result.errors],
                    "status": "success" if result.success else "failed",
                }

        # Aggregate totals across all sheets
        total_synced = sum(
            r.rows_synced for r in all_results.values() if isinstance(r, SheetSyncResult)
        )
        sheet_errors = sum(
            len(r.errors) for r in all_results.values() if isinstance(r, SheetSyncResult)
        )
        drift_errors = [
            _build_drift_sync_detail(r)
            for r in all_results.values()
            if isinstance(r, ColumnDriftError)
        ]
        failures = sum(
            1 for r in all_results.values()
            if isinstance(r, SheetSyncResult) and not r.success
        )
        total_errors = sheet_errors + len(all_errors)
        overall_success = (
            total_errors == 0
            and len(drift_errors) == 0
            and failures == 0
        )

        # Build error message
        error_message = None
        if all_errors or total_errors > 0 or drift_errors:
            error_parts = all_errors.copy()
            for r in all_results.values():
                if isinstance(r, SheetSyncResult) and r.errors:
                    error_parts.append(f"{r.sheet_type}: {len(r.errors)} row errors")
            for d in drift_errors:
                error_parts.append(_format_drift_error_message(d))
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

        m1_id_result = meeting_results.get("m1_id")
        return SyncResult(
            sync_id=sync_id,
            vp_results=all_results,
            meeting_result=(
                m1_id_result if isinstance(m1_id_result, SheetSyncResult) else None
            ),
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
