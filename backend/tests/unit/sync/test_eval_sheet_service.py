"""Unit tests for eval_sheet_service — syncing evaluation data to Google Sheet."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.modules.sync.eval_sheet_service import (
    HEADER_ROW,
    _brand_row,
    _eval_range,
    _marketing_pct,
    _normalize_eval_sheet_row,
    full_sync_eval_sheet,
    remove_brand_from_sheet,
    sync_brand_to_sheet,
)

MODULE = "app.modules.sync.eval_sheet_service"

# 2026-06-23 05:00 UTC = 12:00 WIB → formats as "23 Jun 2026"
SUBMITTED_AT = datetime(2026, 6, 23, 5, 0, 0, tzinfo=timezone.utc)
SUBMITTED_DATE = "23 Jun 2026"


# --- _brand_row ---


def test_brand_row_formats_all_fields():
    """should format all fields into a sheet row when all data present"""
    data = {
        "submitted_at": SUBMITTED_AT,
        "period": "Jan 2026",
        "brand_name": "Nike",
        "kategori": "Sepatu",
        "final_score": 72.50,
        "marketplace": "TH",
        "calculator_results": {
            "scoring_summary": {"marketing_budget_i18n": {"vars": {"pct": "12%"}}}
        },
    }
    assert _brand_row(data) == [SUBMITTED_DATE, "Jan 2026", "Nike", "Sepatu", "72.5", "TH", "12%"]


def test_brand_row_handles_missing_kategori():
    """should use empty string when kategori is None"""
    data = {
        "submitted_at": SUBMITTED_AT,
        "period": "Feb 2026",
        "brand_name": "Adidas",
        "kategori": None,
        "final_score": 85.00,
    }
    assert _brand_row(data) == [SUBMITTED_DATE, "Feb 2026", "Adidas", "", "85.0", "ID", ""]


def test_brand_row_handles_missing_submitted_at():
    """should use empty string when submitted_at is absent"""
    data = {
        "period": "Feb 2026",
        "brand_name": "Adidas",
        "kategori": "Sepatu",
        "final_score": 85.00,
    }
    assert _brand_row(data) == ["", "Feb 2026", "Adidas", "Sepatu", "85.0", "ID", ""]


# --- _marketing_pct ---


def test_marketing_pct_reads_i18n_vars():
    """should read the exact pct from marketing_budget_i18n vars"""
    cr = {"scoring_summary": {"marketing_budget_i18n": {"vars": {"pct": "18%"}}}}
    assert _marketing_pct(cr) == "18%"


def test_marketing_pct_falls_back_to_text():
    """should parse the percentage out of the recommendation text when i18n absent"""
    cr = {"scoring_summary": {"marketing_budget": "💡Minimum anggaran marketing ... = 12%"}}
    assert _marketing_pct(cr) == "12%"


def test_marketing_pct_parses_json_string():
    """should handle double-encoded calculator_results"""
    cr = '{"scoring_summary": {"marketing_budget_i18n": {"vars": {"pct": "25%"}}}}'
    assert _marketing_pct(cr) == "25%"


def test_marketing_pct_empty_when_missing():
    """should return empty string when no marketing data present"""
    assert _marketing_pct(None) == ""
    assert _marketing_pct({}) == ""


def test_normalize_eval_sheet_row_uses_th_category_key():
    """should resolve Product Category for Thailand marketplace rows"""
    data = {
        "period": "Feb 2026",
        "brand_name": "Cintage",
        "marketplace": "TH",
        "raw_data": {"Product Category": "Cardigan"},
        "final_score": 82.0,
    }

    normalized = _normalize_eval_sheet_row(data)

    assert normalized["kategori"] == "Cardigan"


def test_normalize_eval_sheet_row_uses_th_multiline_category_key():
    """should resolve Product\\nCategory when the sheet header contains a newline"""
    data = {
        "period": "Feb 2026",
        "brand_name": "Cintage",
        "marketplace": "TH",
        "raw_data": {"Product\nCategory": "Cardigan"},
        "final_score": 82.0,
    }

    normalized = _normalize_eval_sheet_row(data)

    assert normalized["kategori"] == "Cardigan"


def test_normalize_eval_sheet_row_falls_back_to_id_category_key():
    """should still read Kategori when marketplace-specific key is absent"""
    data = {
        "period": "Feb 2026",
        "brand_name": "Nike",
        "marketplace": "ID",
        "raw_data": {"Kategori": "Sepatu"},
        "final_score": 82.0,
    }

    normalized = _normalize_eval_sheet_row(data)

    assert normalized["kategori"] == "Sepatu"


def test_normalize_eval_sheet_row_uses_legacy_generic_category_key():
    """should fall back to generic category keys for older brand payloads"""
    data = {
        "period": "Feb 2026",
        "brand_name": "Nike",
        "marketplace": "ID",
        "raw_data": {"category": "Sepatu"},
        "final_score": 82.0,
    }

    normalized = _normalize_eval_sheet_row(data)

    assert normalized["kategori"] == "Sepatu"


def test_normalize_eval_sheet_row_parses_json_string_raw_data():
    """should parse double-encoded raw_data rows before reading category keys"""
    data = {
        "period": "Feb 2026",
        "brand_name": "Digi Living",
        "marketplace": "ID",
        "raw_data": '{"Kategori":"Beauty"}',
        "final_score": 65.0,
    }

    normalized = _normalize_eval_sheet_row(data)

    assert normalized["kategori"] == "Beauty"


# --- HEADER_ROW / range ---


def test_header_row_has_correct_columns():
    """should carry the six original columns plus Min. Anggaran Marketing"""
    assert HEADER_ROW == [
        "Waktu Submit",
        "Periode Data",
        "Brand Name",
        "Kategori",
        "AHA Compatibility Score",
        "Country",
        "Min. Anggaran Marketing",
    ]


def test_eval_range_covers_seven_columns_on_configured_tab():
    """should cover columns A through G on the quoted eval tab"""
    with patch(f"{MODULE}.settings") as mock_settings:
        mock_settings.gsheets_eval_tab = "SICU - bronze"
        assert _eval_range() == "'SICU - bronze'!A:G"


# --- sync_brand_to_sheet ---


async def test_sync_brand_to_sheet_skips_when_not_configured():
    """should return early when eval sheet is not configured"""
    with patch(f"{MODULE}._is_configured", return_value=False):
        await sync_brand_to_sheet("Nike")
        # No exception, no side effects


async def test_sync_brand_to_sheet_rebuilds_whole_sheet():
    """should rebuild every row so the newest-first order holds after a submit"""
    with (
        patch(f"{MODULE}._is_configured", return_value=True),
        patch(f"{MODULE}.full_sync_eval_sheet", new=AsyncMock()) as mock_full_sync,
    ):
        mock_full_sync.return_value = {"success": True, "brands_synced": 3}

        await sync_brand_to_sheet("Nike")

        mock_full_sync.assert_awaited_once()


async def test_sync_brand_to_sheet_swallows_failures():
    """should stay fire-and-forget safe when the rebuild raises"""
    with (
        patch(f"{MODULE}._is_configured", return_value=True),
        patch(f"{MODULE}.full_sync_eval_sheet", new=AsyncMock()) as mock_full_sync,
    ):
        mock_full_sync.side_effect = RuntimeError("sheets down")

        await sync_brand_to_sheet("Nike")  # must not raise


# --- remove_brand_from_sheet ---


async def test_remove_brand_reads_column_c():
    """should read brand names from column C (where Brand Name now lives)"""
    mock_client = AsyncMock()
    mock_client.read_column = AsyncMock(return_value=["Brand Name", "Nike"])

    with (
        patch(f"{MODULE}._is_configured", return_value=True),
        patch(f"{MODULE}.GoogleSheetsClient", return_value=mock_client),
        patch(f"{MODULE}.settings") as mock_settings,
    ):
        mock_settings.gsheets_eval_spreadsheet_id = "sheet-123"
        mock_settings.gsheets_eval_tab = "SICU - bronze"

        await remove_brand_from_sheet("Nike")

        mock_client.read_column.assert_awaited_once_with("sheet-123", "'SICU - bronze'!C:C")


# --- full_sync_eval_sheet ---


async def test_full_sync_returns_error_when_not_configured():
    """should return error dict when eval sheet not configured"""
    with patch(f"{MODULE}.settings") as mock_settings:
        mock_settings.gsheets_eval_spreadsheet_id = None

        result = await full_sync_eval_sheet()

        assert result["success"] is False
        assert result["error"] == "Eval sheet not configured"


async def test_full_sync_writes_header_and_data():
    """should clear sheet and write header + one row per brand"""
    brand_data = [
        {"submitted_at": SUBMITTED_AT, "period": "Jan 2026", "brand_name": "Nike",
         "kategori": "Sepatu", "final_score": 72.5,
         "calculator_results": {"scoring_summary": {"marketing_budget_i18n": {"vars": {"pct": "12%"}}}}},
        {"submitted_at": SUBMITTED_AT, "period": "Feb 2026", "brand_name": "Adidas",
         "kategori": None, "final_score": 85.0},
    ]
    mock_conn = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=[AsyncMock(**d) for d in brand_data])

    mock_client = AsyncMock()

    with (
        patch(f"{MODULE}.settings") as mock_settings,
        patch(f"{MODULE}.db") as mock_db,
        patch(f"{MODULE}.GoogleSheetsClient", return_value=mock_client),
        patch(f"{MODULE}._get_latest_evaluation_per_brand", return_value=brand_data),
    ):
        mock_settings.gsheets_eval_spreadsheet_id = "sheet-123"
        mock_settings.gsheets_eval_tab = "SICU - bronze"
        mock_db.connection.return_value.__aenter__.return_value = mock_conn

        result = await full_sync_eval_sheet()

        assert result["success"] is True
        assert result["brands_synced"] == 2

        # Verify clear was called on the quoted A:G range
        mock_client.clear_sheet.assert_awaited_once_with("sheet-123", "'SICU - bronze'!A:G")

        # Verify write includes header + 2 data rows
        write_args = mock_client.write_rows.call_args
        rows = write_args[0][2]
        assert rows[0] == HEADER_ROW
        assert rows[1] == [SUBMITTED_DATE, "Jan 2026", "Nike", "Sepatu", "72.5", "ID", "12%"]
        assert rows[2] == [SUBMITTED_DATE, "Feb 2026", "Adidas", "", "85.0", "ID", ""]


async def test_full_sync_writes_rows_newest_submission_first():
    """should keep the query's newest-first order when writing rows"""
    newer = datetime(2026, 7, 1, 5, 0, 0, tzinfo=timezone.utc)
    older = datetime(2026, 6, 23, 5, 0, 0, tzinfo=timezone.utc)
    brand_data = [
        {"submitted_at": newer, "period": "Jul 2026", "brand_name": "Adidas",
         "kategori": "Sepatu", "final_score": 85.0},
        {"submitted_at": older, "period": "Jun 2026", "brand_name": "Nike",
         "kategori": "Sepatu", "final_score": 72.5},
    ]
    mock_client = AsyncMock()

    with (
        patch(f"{MODULE}.settings") as mock_settings,
        patch(f"{MODULE}.db") as mock_db,
        patch(f"{MODULE}.GoogleSheetsClient", return_value=mock_client),
        patch(f"{MODULE}._get_latest_evaluation_per_brand", return_value=brand_data),
    ):
        mock_settings.gsheets_eval_spreadsheet_id = "sheet-123"
        mock_settings.gsheets_eval_tab = "SICU - bronze"
        mock_db.connection.return_value.__aenter__.return_value = AsyncMock()

        await full_sync_eval_sheet()

        rows = mock_client.write_rows.call_args[0][2]
        assert [row[0] for row in rows[1:]] == ["1 Jul 2026", "23 Jun 2026"]
