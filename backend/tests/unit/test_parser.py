"""Unit tests for file parser module."""

import polars as pl
import pytest

from app.core.exceptions import UploadException
from app.modules.upload.parser import (
    REQUIRED_COLUMNS,
    dataframe_to_json,
    parse_csv,
    parse_excel,
    validate_columns,
)


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------

def test_parse_csv_valid():
    csv_bytes = b"col_a,col_b\n1,hello\n2,world"
    df = parse_csv(csv_bytes)
    assert df.shape == (2, 2)
    assert df.columns == ["col_a", "col_b"]


def test_parse_csv_empty():
    csv_bytes = b"col_a,col_b\n"
    df = parse_csv(csv_bytes)
    assert len(df) == 0
    assert df.columns == ["col_a", "col_b"]


def test_parse_csv_invalid():
    # Empty bytes should raise parse error
    with pytest.raises(UploadException) as exc:
        parse_csv(b"")
    assert exc.value.code == "UPLOAD_PARSE_FAILED"


# ---------------------------------------------------------------------------
# Excel parsing
# ---------------------------------------------------------------------------

def _make_excel_bytes(df: pl.DataFrame, *, header_row: int = 0) -> bytes:
    """Helper: write a DataFrame to in-memory Excel bytes.

    For header_row > 0 we prepend blank rows so the real headers land
    at the expected row index using xlsxwriter directly.
    """
    from io import BytesIO

    import xlsxwriter

    buf = BytesIO()
    if header_row > 0:
        workbook = xlsxwriter.Workbook(buf)
        worksheet = workbook.add_worksheet()
        # Write headers at the header_row index
        for col_idx, col_name in enumerate(df.columns):
            worksheet.write(header_row, col_idx, col_name)
        # Write data starting from header_row + 1
        for row_idx, row_data in enumerate(df.to_dicts()):
            for col_idx, col_name in enumerate(df.columns):
                worksheet.write(header_row + 1 + row_idx, col_idx, row_data[col_name])
        workbook.close()
        return buf.getvalue()

    df.write_excel(buf)
    return buf.getvalue()


def test_parse_excel_valid():
    df = pl.DataFrame({"Name": ["A", "B"], "Value": [1, 2]})
    excel_bytes = _make_excel_bytes(df)
    result = parse_excel(excel_bytes)
    assert result.shape == (2, 2)
    assert "Name" in result.columns


def test_parse_excel_invalid():
    with pytest.raises(UploadException) as exc:
        parse_excel(b"not-an-excel-file")
    assert exc.value.code == "UPLOAD_PARSE_FAILED"


def test_parse_excel_header_row_2():
    """Mass Update files have headers at row 3 (0-indexed row 2)."""
    df = pl.DataFrame({"Kode Variasi": ["V1"], "Nama Produk": ["P1"], "Nama Variasi": ["V1"], "SKU": ["S1"], "Stok": [10]})
    excel_bytes = _make_excel_bytes(df, header_row=2)
    result = parse_excel(excel_bytes, header_row=2)
    assert "Kode Variasi" in result.columns
    assert "Nama Produk" in result.columns
    assert len(result) == 1


# ---------------------------------------------------------------------------
# Column validation
# ---------------------------------------------------------------------------

def test_validate_columns_cpc_ad_report_success():
    cols = REQUIRED_COLUMNS["cpc_ad_report"] + ["Extra"]
    df = pl.DataFrame({col: ["x"] for col in cols})
    validate_columns(df, "cpc_ad_report")  # should not raise


def test_validate_columns_cpc_ad_report_missing():
    df = pl.DataFrame({"Nama Produk": ["x"], "Biaya": [1]})
    with pytest.raises(UploadException) as exc:
        validate_columns(df, "cpc_ad_report")
    assert exc.value.code == "UPLOAD_MISSING_COLUMNS"
    assert "Nama Iklan" in exc.value.detail


def test_validate_columns_keyword_report_success():
    cols = REQUIRED_COLUMNS["keyword_report"]
    df = pl.DataFrame({col: ["x"] for col in cols})
    validate_columns(df, "keyword_report")


def test_validate_columns_order_export_success():
    cols = REQUIRED_COLUMNS["order_export"]
    df = pl.DataFrame({col: ["x"] for col in cols})
    validate_columns(df, "order_export")


def test_validate_columns_mass_update_success():
    cols = REQUIRED_COLUMNS["mass_update"]
    df = pl.DataFrame({col: ["x"] for col in cols})
    validate_columns(df, "mass_update")


def test_validate_columns_unknown_file_type():
    df = pl.DataFrame({"a": [1]})
    with pytest.raises(UploadException) as exc:
        validate_columns(df, "nonexistent_type")
    assert exc.value.code == "UPLOAD_INVALID_FORMAT"


# ---------------------------------------------------------------------------
# DataFrame → JSON
# ---------------------------------------------------------------------------

def test_dataframe_to_json():
    df = pl.DataFrame({"name": ["a", "b"], "value": [1, 2]})
    result = dataframe_to_json(df)
    assert result["columns"] == ["name", "value"]
    assert result["row_count"] == 2
    assert len(result["data"]) == 2
    assert result["data"][0] == {"name": "a", "value": 1}
