"""Sync service for orchestrating Google Sheets brand synchronization."""

import logging
from datetime import datetime, timezone

from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.db.queries import sync_status as sync_queries
from app.modules.sync.schemas import SyncError, SyncResult, SyncStatusResponse
from app.modules.sync.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)


async def run_sync() -> SyncResult:
    """Execute full brand sync from Google Sheets.

    Orchestrates the sync process:
    1. Create sync status record
    2. Fetch brands from Google Sheets
    3. Upsert each brand to database (partial failure tolerant)
    4. Update sync status with results

    Returns:
        SyncResult with counts and any errors encountered.
    """
    sheets_client = GoogleSheetsClient()

    # Create sync record
    async with db.connection() as conn:
        sync_id = await sync_queries.create_sync_status(
            conn,
            started_at=datetime.now(timezone.utc),
        )

    logger.info(f"Starting sync with ID: {sync_id}")

    try:
        # Fetch from Google Sheets
        brand_rows = await sheets_client.fetch_brands_from_sheet()
        logger.info(f"Fetched {len(brand_rows)} brands from Google Sheets")

        synced_count = 0
        errors: list[SyncError] = []

        # Upsert each brand (continue on individual failures)
        async with db.connection() as conn:
            for brand_data in brand_rows:
                try:
                    external_id = brand_data.get("ID") or brand_data.get("id") or ""
                    name = brand_data.get("Brand Name") or brand_data.get("name") or ""

                    if not external_id or not name:
                        errors.append(
                            SyncError(
                                brand=name or external_id or "Unknown",
                                error="Missing required field: ID or Brand Name",
                            )
                        )
                        continue

                    await brand_queries.upsert_brand(
                        conn,
                        external_id=str(external_id),
                        name=str(name),
                        category=brand_data.get("Category") or brand_data.get("category"),
                        marketplace=brand_data.get("Marketplace") or brand_data.get("marketplace"),
                        raw_data=brand_data,
                    )
                    synced_count += 1
                except Exception as e:
                    brand_name = brand_data.get("Brand Name") or brand_data.get("name") or "Unknown"
                    errors.append(SyncError(brand=brand_name, error=str(e)))
                    logger.warning(f"Failed to sync brand '{brand_name}': {e}")

        # Update sync status with success
        async with db.connection() as conn:
            await sync_queries.update_sync_status(
                conn,
                sync_id=sync_id,
                completed_at=datetime.now(timezone.utc),
                success=len(errors) == 0,
                brands_synced=synced_count,
                error_message=_format_errors(errors) if errors else None,
            )

        logger.info(f"Sync completed: {synced_count} brands synced, {len(errors)} errors")

        return SyncResult(
            sync_id=sync_id,
            brands_synced=synced_count,
            errors=errors,
            success=len(errors) == 0,
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


def _format_errors(errors: list[SyncError]) -> str:
    """Format error list for storage."""
    if not errors:
        return ""
    error_msgs = [f"{e.brand}: {e.error}" for e in errors[:10]]  # Limit to first 10
    if len(errors) > 10:
        error_msgs.append(f"... and {len(errors) - 10} more errors")
    return "; ".join(error_msgs)
