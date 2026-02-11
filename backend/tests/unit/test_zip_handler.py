"""Unit tests for ZIP archive handler."""

import zipfile
from io import BytesIO

import polars as pl
import pytest

from app.core.exceptions import UploadException
from app.modules.upload.zip_handler import (
    _extract_part_number,
    _is_valid_excel,
    process_zip,
)


# ---------------------------------------------------------------------------
# Helper: build a ZIP from DataFrames
# ---------------------------------------------------------------------------

from tests.unit.conftest import make_excel_bytes as _make_excel_bytes


def _make_zip(entries: dict[str, pl.DataFrame], header_row: int = 0) -> bytes:
    """Create a ZIP archive with multiple Excel entries.

    Args:
        entries: mapping of filename → DataFrame.
        header_row: if > 0, write headers at that row.
    """
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, df in entries.items():
            zf.writestr(name, _make_excel_bytes(df, header_row=header_row))
    return buf.getvalue()


# ---------------------------------------------------------------------------
# _extract_part_number
# ---------------------------------------------------------------------------

def test_extract_part_number_standard():
    assert _extract_part_number("data_part_1_of_3.xlsx") == 1
    assert _extract_part_number("data_part_2_of_3.xlsx") == 2
    assert _extract_part_number("data_part_3_of_3.xlsx") == 3


def test_extract_part_number_no_match():
    assert _extract_part_number("export.xlsx") == 0


def test_extract_part_number_variation():
    assert _extract_part_number("report part2of5.xlsx") == 2


# ---------------------------------------------------------------------------
# _is_valid_excel
# ---------------------------------------------------------------------------

def test_is_valid_excel():
    assert _is_valid_excel("data.xlsx") is True
    assert _is_valid_excel("data.xls") is True
    assert _is_valid_excel("__MACOSX/._data.xlsx") is False
    assert _is_valid_excel("~$data.xlsx") is False
    assert _is_valid_excel(".hidden.xlsx") is False
    assert _is_valid_excel("readme.txt") is False


# ---------------------------------------------------------------------------
# process_zip — happy path
# ---------------------------------------------------------------------------

def test_process_zip_single_file():
    df = pl.DataFrame({"Col_A": [1, 2], "Col_B": ["x", "y"]})
    zip_bytes = _make_zip({"data.xlsx": df})
    result = process_zip(zip_bytes, "order_export")
    assert result.shape == (2, 2)


def test_process_zip_multi_part():
    df1 = pl.DataFrame({"Col_A": [1], "Col_B": ["x"]})
    df2 = pl.DataFrame({"Col_A": [2], "Col_B": ["y"]})
    df3 = pl.DataFrame({"Col_A": [3], "Col_B": ["z"]})
    zip_bytes = _make_zip({
        "data_part_3_of_3.xlsx": df3,
        "data_part_1_of_3.xlsx": df1,
        "data_part_2_of_3.xlsx": df2,
    })
    result = process_zip(zip_bytes, "order_export")
    # Should be sorted by part number and concatenated
    assert len(result) == 3
    assert result["Col_A"].to_list() == [1, 2, 3]


def test_process_zip_filters_macosx():
    df = pl.DataFrame({"A": [1]})
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("data.xlsx", _make_excel_bytes(df))
        # Add __MACOSX entry
        zf.writestr("__MACOSX/._data.xlsx", b"junk")
    zip_bytes = buf.getvalue()
    result = process_zip(zip_bytes, "order_export")
    assert len(result) == 1


def test_process_zip_mass_update_header_row():
    """Mass update ZIPs should parse with header_row=2."""
    df = pl.DataFrame({"Kode Variasi": ["V1"], "Nama Produk": ["P1"], "Nama Variasi": ["NV"], "SKU": ["S1"], "Stok": [10]})
    zip_bytes = _make_zip({"data.xlsx": df}, header_row=2)
    result = process_zip(zip_bytes, "mass_update")
    assert "Kode Variasi" in result.columns
    assert "Nama Produk" in result.columns
    assert len(result) == 1


# ---------------------------------------------------------------------------
# process_zip — error cases
# ---------------------------------------------------------------------------

def test_process_zip_corrupted():
    with pytest.raises(UploadException) as exc:
        process_zip(b"not-a-zip", "order_export")
    assert exc.value.code == "UPLOAD_PARSE_FAILED"


def test_process_zip_no_excel():
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("readme.txt", "hello")
    with pytest.raises(UploadException) as exc:
        process_zip(buf.getvalue(), "order_export")
    assert exc.value.code == "UPLOAD_ZIP_NO_EXCEL"


def test_process_zip_structure_mismatch():
    df1 = pl.DataFrame({"Col_A": [1], "Col_B": ["x"]})
    df2 = pl.DataFrame({"Col_X": [2], "Col_Y": ["y"]})
    zip_bytes = _make_zip({
        "data_part_1_of_2.xlsx": df1,
        "data_part_2_of_2.xlsx": df2,
    })
    with pytest.raises(UploadException) as exc:
        process_zip(zip_bytes, "order_export")
    assert exc.value.code == "UPLOAD_ZIP_STRUCTURE_MISMATCH"
