"""Service for syncing evaluated brand data to a Google Sheet.

Writes one row per brand with: Waktu Submit, Periode Data, Brand Name,
Kategori, AHA Compatibility Score, Country. Data comes from the latest
evaluation (by created_at) for each brand, ordered newest submission first.
"""

import logging
import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from asyncpg import Connection

from app.config import settings
from app.core.utils import ensure_dict
from app.db.connection import db
from app.modules.sync.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)

HEADER_ROW = [
    "Waktu Submit",
    "Periode Data",
    "Brand Name",
    "Kategori",
    "AHA Compatibility Score",
    "Country",
    "Min. Anggaran Marketing",
]
_EVAL_COLUMNS = "A:G"
_WIB = ZoneInfo("Asia/Jakarta")


def _tab_ref() -> str:
    """Quoted A1 reference for the eval tab (names may contain spaces)."""
    return f"'{settings.gsheets_eval_tab}'"


def _eval_range() -> str:
    """Full A1 range for the eval tab, e.g. ``'SICU - bronze'!A:G``."""
    return f"{_tab_ref()}!{_EVAL_COLUMNS}"
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
    """Return latest evaluation data per brand, newest submission first.

    Each row contains: period, brand_name, kategori, final_score.
    'Latest' means most recent created_at per brand. The result order is the
    sheet's row order — most recently submitted at the top.
    """
    rows = await conn.fetch(
        """
        WITH latest_per_brand AS (
            SELECT DISTINCT ON (e.brand_id)
                   COALESCE(e.period, '') AS period,
                   b.brand_name,
                   COALESCE(e.marketplace, 'ID') AS marketplace,
                   b.raw_data,
                   e.final_score,
                   e.calculator_results,
                   e.created_at AS submitted_at
            FROM evaluations e
            JOIN brand_vp_data b ON e.brand_id = b.id
            ORDER BY e.brand_id, e.created_at DESC
        )
        SELECT * FROM latest_per_brand
        ORDER BY submitted_at DESC, brand_name
        """
    )
    return [_normalize_eval_sheet_row(dict(row)) for row in rows]


def _normalize_eval_sheet_row(data: dict[str, Any]) -> dict[str, Any]:
    """Fill marketplace-aware sheet fields from a raw evaluation row."""
    normalized = data.copy()
    raw_data = ensure_dict(normalized.get("raw_data"))
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


def _format_submit_date(submitted_at: Any) -> str:
    """Format an evaluation timestamp as a WIB date, e.g. '23 Jun 2026'."""
    if not isinstance(submitted_at, datetime):
        return ""
    return submitted_at.astimezone(_WIB).strftime("%-d %b %Y")


def _marketing_pct(calculator_results: Any) -> str:
    """Extract the marketing-budget percentage (e.g. '12%') from stored results."""
    summary = ensure_dict(ensure_dict(calculator_results).get("scoring_summary"))
    pct = ensure_dict(ensure_dict(summary.get("marketing_budget_i18n")).get("vars")).get("pct")
    if pct:
        return str(pct)
    # Fallback: parse the trailing percentage out of the recommendation text.
    match = re.search(r"(\d+(?:\.\d+)?%)", summary.get("marketing_budget") or "")
    return match.group(1) if match else ""


def _brand_row(data: dict[str, Any]) -> list[str]:
    """Build a sheet row from brand evaluation data."""
    return [
        _format_submit_date(data.get("submitted_at")),
        data["period"],
        data["brand_name"],
        data.get("kategori") or "",
        str(data["final_score"]),
        data.get("marketplace") or "ID",
        _marketing_pct(data.get("calculator_results")),
    ]


async def sync_brand_to_sheet(brand_name: str) -> None:
    """Reflect a brand's latest evaluation in the eval sheet.

    Rows are ordered by submission time, newest first — a property of the whole
    sheet, not of one row — so a single brand's change is applied by rewriting
    every row in order. That also self-heals header drift and stale rows.

    Fire-and-forget safe — logs errors instead of raising.
    """
    if not _is_configured():
        return

    try:
        result = await full_sync_eval_sheet()
        logger.info(
            f"Eval sheet rebuilt after change to brand '{brand_name}'",
            extra={"brands_synced": result.get("brands_synced", 0)},
        )
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

        # Read existing brand names from column C
        existing = await client.read_column(spreadsheet_id, f"{_tab_ref()}!C:C")

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
    await client.clear_sheet(spreadsheet_id, _eval_range())

    # Get latest evaluation data per brand
    async with db.connection() as conn:
        brand_data = await _get_latest_evaluation_per_brand(conn)

    # Build rows: header + data
    rows = [HEADER_ROW] + [_brand_row(d) for d in brand_data]

    # Write all at once
    if rows:
        await client.write_rows(
            spreadsheet_id,
            f"{_tab_ref()}!A1",
            rows,
        )

    logger.info(f"Full eval sheet sync completed: {len(brand_data)} brands")
    return {"success": True, "brands_synced": len(brand_data)}
