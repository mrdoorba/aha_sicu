"""Service for syncing evaluated brand data to a Google Sheet.

Writes one row per brand with: Periode, Brand Name, Kategori, Score Internal.
Data comes from the latest evaluation (by created_at) for each brand.
"""

import logging
from typing import Any

from asyncpg import Connection

from app.config import settings
from app.db.connection import db
from app.modules.sync.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)

HEADER_ROW = ["Periode", "Brand Name", "Kategori", "Score Internal"]
EVAL_RANGE = "SICU!A:D"
_CATEGORY_COLUMNS: dict[str, tuple[str, ...]] = {
    "ID": ("Kategori", "Category", "category"),
    "TH": ("Product Category", "Product\nCategory", "Kategori", "Category", "category"),
}


def _is_configured() -> bool:
    """Check if the eval sheet feature is configured."""
    return bool(settings.gsheets_eval_spreadsheet_id)


async def _get_latest_evaluation_per_brand(
    conn: Connection,
) -> list[dict[str, Any]]:
    """Return latest evaluation data per brand for the eval sheet.

    Each row contains: period, brand_name, kategori, final_score.
    'Latest' means most recent created_at per brand.
    """
    rows = await conn.fetch(
        """
        SELECT DISTINCT ON (e.brand_id)
               COALESCE(e.period, '') AS period,
               b.brand_name,
               COALESCE(e.marketplace, 'ID') AS marketplace,
               b.raw_data,
               e.final_score
        FROM evaluations e
        JOIN brand_vp_data b ON e.brand_id = b.id
        ORDER BY e.brand_id, e.created_at DESC
        """
    )
    return [_normalize_eval_sheet_row(dict(row)) for row in rows]


async def _get_latest_evaluation_for_brand(
    conn: Connection,
    brand_name: str,
) -> dict[str, Any] | None:
    """Return the latest evaluation data for a single brand."""
    row = await conn.fetchrow(
        """
        SELECT COALESCE(e.period, '') AS period,
               b.brand_name,
               COALESCE(e.marketplace, 'ID') AS marketplace,
               b.raw_data,
               e.final_score
        FROM evaluations e
        JOIN brand_vp_data b ON e.brand_id = b.id
        WHERE b.brand_name = $1
        ORDER BY e.created_at DESC
        LIMIT 1
        """,
        brand_name,
    )
    return _normalize_eval_sheet_row(dict(row)) if row else None


def _normalize_eval_sheet_row(data: dict[str, Any]) -> dict[str, Any]:
    """Fill marketplace-aware sheet fields from a raw evaluation row."""
    normalized = data.copy()
    raw_data = normalized.get("raw_data") or {}
    marketplace = normalized.get("marketplace") or "ID"
    category_keys = _CATEGORY_COLUMNS.get(marketplace, _CATEGORY_COLUMNS["ID"])

    kategori = normalized.get("kategori")
    if not kategori and isinstance(raw_data, dict):
        for key in category_keys:
            if raw_data.get(key):
                kategori = raw_data[key]
                break

    normalized["kategori"] = kategori or ""
    return normalized


def _brand_row(data: dict[str, Any]) -> list[str]:
    """Build a sheet row from brand evaluation data."""
    return [
        data["period"],
        data["brand_name"],
        data.get("kategori") or "",
        str(data["final_score"]),
    ]


async def sync_brand_to_sheet(brand_name: str) -> None:
    """Write or overwrite a brand's row in the eval sheet with latest data.

    Fire-and-forget safe — logs errors instead of raising.
    """
    if not _is_configured():
        return

    try:
        # Fetch latest evaluation data from DB
        async with db.connection() as conn:
            data = await _get_latest_evaluation_for_brand(conn, brand_name)

        if not data:
            logger.debug(f"No evaluations for '{brand_name}', skipping sheet sync")
            return

        client = GoogleSheetsClient()
        spreadsheet_id = settings.gsheets_eval_spreadsheet_id
        tab = settings.gsheets_eval_tab

        headers = await client.fetch_headers(spreadsheet_id, tab)
        if headers and headers != HEADER_ROW:
            logger.warning(
                "Eval sheet header drift detected; running full sync before brand update",
                extra={"brand_name": brand_name, "headers": headers},
            )
            await full_sync_eval_sheet()
            return

        # Read existing brand names from column B
        existing = await client.read_column(spreadsheet_id, f"{tab}!B:B")

        # Find existing row index (0-based, including header)
        row_idx = None
        for i, name in enumerate(existing):
            if name == brand_name:
                row_idx = i
                break

        row = _brand_row(data)

        if row_idx is not None:
            # Overwrite existing row (1-based for Sheets API)
            await client.write_rows(
                spreadsheet_id,
                f"{tab}!A{row_idx + 1}",
                [row],
            )
            logger.info(f"Updated brand '{brand_name}' in eval sheet")
        else:
            # Write header if sheet is empty
            if not existing:
                await client.write_rows(spreadsheet_id, f"{tab}!A1", [HEADER_ROW])

            # Append new row
            await client.append_rows(spreadsheet_id, EVAL_RANGE, [row])
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

        # Read existing brand names from column B
        existing = await client.read_column(spreadsheet_id, f"{settings.gsheets_eval_tab}!B:B")

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
    """Clear the eval sheet and repopulate with latest evaluation per brand.

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

    # Get latest evaluation data per brand
    async with db.connection() as conn:
        brand_data = await _get_latest_evaluation_per_brand(conn)

    # Build rows: header + data
    rows = [HEADER_ROW] + [_brand_row(d) for d in brand_data]

    # Write all at once
    if rows:
        await client.write_rows(
            spreadsheet_id,
            f"{settings.gsheets_eval_tab}!A1",
            rows,
        )

    logger.info(f"Full eval sheet sync completed: {len(brand_data)} brands")
    return {"success": True, "brands_synced": len(brand_data)}
