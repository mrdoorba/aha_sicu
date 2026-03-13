"""Service for syncing evaluated brand status to a Google Sheet."""

import logging

from asyncpg import Connection

from app.config import settings
from app.db.connection import db
from app.modules.sync.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)

HEADER_ROW = ["Brand Name", "Evaluated"]
EVAL_RANGE = "SICU!A:B"


def _is_configured() -> bool:
    """Check if the eval sheet feature is configured."""
    return bool(settings.gsheets_eval_spreadsheet_id)


async def _get_all_evaluated_brand_names(conn: Connection) -> list[str]:
    """Return distinct brand names that have at least one evaluation."""
    rows = await conn.fetch(
        """
        SELECT DISTINCT b.brand_name
        FROM evaluations e
        JOIN brand_vp_data b ON e.brand_id = b.id
        ORDER BY b.brand_name
        """
    )
    return [row["brand_name"] for row in rows]


async def sync_brand_to_sheet(brand_name: str) -> None:
    """Add a brand row to the eval sheet if not already present.

    Fire-and-forget safe — logs errors instead of raising.
    """
    if not _is_configured():
        return

    try:
        client = GoogleSheetsClient()
        spreadsheet_id = settings.gsheets_eval_spreadsheet_id

        # Read existing brand names from column A
        existing = await client.read_column(spreadsheet_id, f"{settings.gsheets_eval_tab}!A:A")

        # Check if brand already in sheet (skip header row)
        brand_names = existing[1:] if len(existing) > 1 else []
        if brand_name in brand_names:
            logger.debug(f"Brand '{brand_name}' already in eval sheet, skipping")
            return

        # If sheet is empty, write header first
        if not existing:
            await client.write_rows(spreadsheet_id, f"{settings.gsheets_eval_tab}!A1", [HEADER_ROW])

        # Append brand row
        await client.append_rows(
            spreadsheet_id,
            EVAL_RANGE,
            [[brand_name, "Yes"]],
        )
        logger.info(f"Added brand '{brand_name}' to eval sheet")

    except Exception:
        logger.exception(f"Failed to sync brand '{brand_name}' to eval sheet")


async def remove_brand_from_sheet(brand_name: str) -> None:
    """Remove a brand row from the eval sheet.

    Fire-and-forget safe — logs errors instead of raising.
    """
    if not _is_configured():
        return

    try:
        client = GoogleSheetsClient()
        spreadsheet_id = settings.gsheets_eval_spreadsheet_id

        # Read existing brand names from column A
        existing = await client.read_column(spreadsheet_id, f"{settings.gsheets_eval_tab}!A:A")

        # Find the row index (0-based) of the brand
        row_indices = [
            i for i, name in enumerate(existing)
            if name == brand_name
        ]

        if not row_indices:
            logger.debug(f"Brand '{brand_name}' not found in eval sheet, nothing to remove")
            return

        await client.delete_rows(
            spreadsheet_id,
            settings.gsheets_eval_tab,
            row_indices,
        )
        logger.info(f"Removed brand '{brand_name}' from eval sheet")

    except Exception:
        logger.exception(f"Failed to remove brand '{brand_name}' from eval sheet")


async def full_sync_eval_sheet() -> dict:
    """Clear the eval sheet and repopulate with all evaluated brands.

    Returns:
        Dict with success status and brands_synced count.

    Raises:
        Exception: On failure (not fire-and-forget — called from manual endpoint).
    """
    spreadsheet_id = settings.gsheets_eval_spreadsheet_id
    if not spreadsheet_id:
        return {"success": False, "brands_synced": 0, "error": "Eval sheet not configured"}

    client = GoogleSheetsClient()

    # Clear existing data
    await client.clear_sheet(spreadsheet_id, EVAL_RANGE)

    # Get all evaluated brands from DB
    async with db.connection() as conn:
        brand_names = await _get_all_evaluated_brand_names(conn)

    # Build rows: header + data
    rows = [HEADER_ROW] + [[name, "Yes"] for name in brand_names]

    # Write all at once
    if rows:
        await client.write_rows(
            spreadsheet_id,
            f"{settings.gsheets_eval_tab}!A1",
            rows,
        )

    logger.info(f"Full eval sheet sync completed: {len(brand_names)} brands")
    return {"success": True, "brands_synced": len(brand_names)}
