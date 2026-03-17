"""Unit tests for file parser module."""

import polars as pl
import pytest

from app.core.exceptions import UploadException
from app.modules.upload.parser import (
    REQUIRED_COLUMNS,
    SHOPEE_CSV_SKIP_ROWS,
    _normalise_thai_columns,
    dataframe_to_json,
    parse_csv,
    parse_excel,
    validate_columns,
)
from tests.unit.conftest import make_excel_bytes as _make_excel_bytes


# ---------------------------------------------------------------------------
# Helpers — Shopee CSV format
# ---------------------------------------------------------------------------

def _shopee_csv(header_line: str, data_lines: list[str] | None = None) -> bytes:
    """Build a Shopee-style CSV with 7 metadata rows before the real headers."""
    metadata = [
        "Semua Laporan Iklan CPC - Shopee Indonesia",
        "Username,testuser",
        "Nama Toko,Test Store",
        "ID Toko,123456",
        "Waktu Laporan Dibuat,01/01/2026 00:00",
        "Periode,01/01/2026 - 31/01/2026",
        "",  # blank line
    ]
    assert len(metadata) == SHOPEE_CSV_SKIP_ROWS
    lines = metadata + [header_line] + (data_lines or [])
    return "\n".join(lines).encode()


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------

def test_parse_csv_valid():
    csv_bytes = _shopee_csv("col_a,col_b", ["1,hello", "2,world"])
    df, lang = parse_csv(csv_bytes)
    assert df.shape == (2, 2)
    assert df.columns == ["col_a", "col_b"]
    assert lang == "id"


def test_parse_csv_empty():
    csv_bytes = _shopee_csv("col_a,col_b")
    df, lang = parse_csv(csv_bytes)
    assert len(df) == 0
    assert df.columns == ["col_a", "col_b"]
    assert lang == "id"


def test_parse_csv_invalid():
    # Empty bytes should raise parse error
    with pytest.raises(UploadException) as exc:
        parse_csv(b"")
    assert exc.value.code == "UPLOAD_PARSE_FAILED"


# ---------------------------------------------------------------------------
# Excel parsing
# ---------------------------------------------------------------------------


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
    df = pl.DataFrame({"Nama Iklan": ["x"], "Biaya": [1]})
    with pytest.raises(UploadException) as exc:
        validate_columns(df, "cpc_ad_report")
    assert exc.value.code == "UPLOAD_MISSING_COLUMNS"
    assert "Jenis Iklan" in exc.value.detail


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
    assert result["source_language"] == "id"


def test_dataframe_to_json_english():
    df = pl.DataFrame({"name": ["a"], "value": [1]})
    result = dataframe_to_json(df, source_language="en")
    assert result["source_language"] == "en"


# ---------------------------------------------------------------------------
# English CSV normalisation
# ---------------------------------------------------------------------------

def test_parse_csv_english_columns_renamed():
    """English Shopee CSV headers are normalised to Indonesian."""
    csv_bytes = _shopee_csv(
        "Ad Name,Ads Type,Product ID,Placement,Expense,Status",
        ["Test Ad,Product Ad,123,All,5000,Ongoing"],
    )
    df, lang = parse_csv(csv_bytes)
    assert "Nama Iklan" in df.columns
    assert "Jenis Iklan" in df.columns
    assert "Kode Produk" in df.columns
    assert "Penempatan Iklan" in df.columns
    assert "Biaya" in df.columns
    assert lang == "en"


def test_parse_csv_english_values_translated():
    """English cell values for Status, Ads Type, Placement are translated."""
    csv_bytes = _shopee_csv(
        "Ad Name,Ads Type,Product ID,Placement,Expense,Status",
        [
            "Ad1,Product Ad,1,All,100,Ongoing",
            "Ad2,Shop Ad,2,Search,200,Ended",
            "Ad3,Product Ad,3,Recommendation,300,Paused",
        ],
    )
    df, lang = parse_csv(csv_bytes)
    rows = df.to_dicts()
    assert rows[0]["Status"] == "Berjalan"
    assert rows[0]["Jenis Iklan"] == "Iklan Produk"
    assert rows[0]["Penempatan Iklan"] == "Semua Penempatan"
    assert rows[1]["Status"] == "Berakhir"
    assert rows[1]["Jenis Iklan"] == "Iklan Toko"
    assert rows[1]["Penempatan Iklan"] == "Halaman Pencarian"
    assert rows[2]["Status"] == "Dijeda"
    assert rows[2]["Penempatan Iklan"] == "Halaman Rekomendasi"
    assert lang == "en"


def test_parse_csv_english_keyword_report_normalised():
    """English keyword report CSV is normalised with GMV/ROAS/Keyword columns."""
    csv_bytes = _shopee_csv(
        "Ad Name,Ads Type,Product ID,Placement,Keyword/Location,Expense,GMV,ROAS,Status",
        ["Ad1,Product Ad,1,All,Auto Selected,100,5000,10.5,Ongoing"],
    )
    df, lang = parse_csv(csv_bytes)
    assert "Kata Pencarian/Penempatan" in df.columns
    assert "Omzet Penjualan" in df.columns
    assert "Efektifitas Iklan" in df.columns
    row = df.to_dicts()[0]
    assert row["Kata Pencarian/Penempatan"] == "Auto Selected"
    assert lang == "en"


def test_parse_csv_indonesian_passthrough():
    """Indonesian CSVs pass through unchanged."""
    csv_bytes = _shopee_csv(
        "Nama Iklan,Jenis Iklan,Kode Produk,Penempatan Iklan,Biaya",
        ["Ad1,Iklan Produk,1,Semua Penempatan,100"],
    )
    df, lang = parse_csv(csv_bytes)
    assert "Nama Iklan" in df.columns
    row = df.to_dicts()[0]
    assert row["Jenis Iklan"] == "Iklan Produk"
    assert lang == "id"


def test_english_csv_validates_after_normalisation():
    """English CSV passes column validation after normalisation."""
    csv_bytes = _shopee_csv(
        "Ad Name,Ads Type,Product ID,Placement,Expense",
        ["Ad1,Product Ad,1,All,100"],
    )
    df, _lang = parse_csv(csv_bytes)
    validate_columns(df, "cpc_ad_report")  # should not raise


# ---------------------------------------------------------------------------
# Thai order export normalisation
# ---------------------------------------------------------------------------

def _thai_order_df(**overrides: list) -> pl.DataFrame:
    """Build a DataFrame with Thai order export headers."""
    base = {
        "หมายเลขคำสั่งซื้อ": ["ORD001", "ORD001", "ORD002"],
        "ชื่อสินค้า": ["Product A", "Product B", "Product C"],
        "ราคาตั้งต้น": [100, 200, 300],
        "ราคาขาย": [90, 180, 270],
        "จำนวน": [1, 2, 1],
        "โค้ดส่วนลดชำระโดยผู้ขาย": [0, 0, 0],
        "ส่วนลด bundle deal ชำระโดยผู้ขาย": [0, 0, 0],
        "เลขอ้างอิง SKU (SKU Reference No.)": ["SKU1", "SKU2", "SKU3"],
        "ชื่อตัวเลือก": ["Var A", "Var B", "Var C"],
        "โค้ด Coins Cashback ชำระโดยผู้ขาย": [0, 0, 0],
        "ส่วนลดจาก Shopee": [0, 0, 0],
    }
    base.update(overrides)
    return pl.DataFrame(base)


class TestThaiOrderExportNormalisation:
    """Tests for _normalise_thai_columns."""

    def test_renames_all_columns_to_indonesian(self):
        df = _thai_order_df()
        result, was_thai = _normalise_thai_columns(df)

        assert was_thai is True
        assert "No. Pesanan" in result.columns
        assert "Nama Produk" in result.columns
        assert "Harga Awal" in result.columns
        assert "Harga Setelah Diskon" in result.columns
        assert "Jumlah" in result.columns
        assert "Voucher Ditanggung Penjual" in result.columns
        assert "Paket Diskon (Diskon dari Penjual)" in result.columns
        assert "Nomor Referensi SKU" in result.columns
        assert "Nama Variasi" in result.columns
        assert "Cashback Koin" in result.columns
        assert "Diskon Dari Shopee" in result.columns

    def test_computes_jumlah_produk_di_pesan(self):
        """Synthetic column = count of rows per order number."""
        df = _thai_order_df()
        result, _ = _normalise_thai_columns(df)

        assert "Jumlah Produk di Pesan" in result.columns
        rows = result.to_dicts()
        # ORD001 appears twice → 2, ORD002 appears once → 1
        assert rows[0]["Jumlah Produk di Pesan"] == 2
        assert rows[1]["Jumlah Produk di Pesan"] == 2
        assert rows[2]["Jumlah Produk di Pesan"] == 1

    def test_single_item_order_gets_count_1(self):
        df = _thai_order_df(**{
            "หมายเลขคำสั่งซื้อ": ["ORD001"],
            "ชื่อสินค้า": ["Product A"],
            "ราคาตั้งต้น": [100],
            "ราคาขาย": [90],
            "จำนวน": [1],
            "โค้ดส่วนลดชำระโดยผู้ขาย": [0],
            "ส่วนลด bundle deal ชำระโดยผู้ขาย": [0],
            "เลขอ้างอิง SKU (SKU Reference No.)": ["SKU1"],
            "ชื่อตัวเลือก": ["Var A"],
            "โค้ด Coins Cashback ชำระโดยผู้ขาย": [0],
            "ส่วนลดจาก Shopee": [0],
        })
        result, _ = _normalise_thai_columns(df)
        assert result.to_dicts()[0]["Jumlah Produk di Pesan"] == 1

    def test_validates_after_normalisation(self):
        """Thai order export passes column validation after normalisation."""
        df = _thai_order_df()
        result, _ = _normalise_thai_columns(df)
        validate_columns(result, "order_export")  # should not raise

    def test_indonesian_passthrough(self):
        """Indonesian DataFrames pass through unchanged."""
        cols = REQUIRED_COLUMNS["order_export"]
        df = pl.DataFrame({col: ["x"] for col in cols})
        result, was_thai = _normalise_thai_columns(df)
        assert was_thai is False
        assert result.columns == df.columns

    def test_does_not_overwrite_existing_jumlah_produk(self):
        """If the column already exists (Indonesian file), don't recompute it."""
        cols = REQUIRED_COLUMNS["order_export"]
        df = pl.DataFrame({col: ["x"] for col in cols})
        result, was_thai = _normalise_thai_columns(df)
        assert was_thai is False
        # Column should still have original value
        assert result.to_dicts()[0]["Jumlah Produk di Pesan"] == "x"

    def test_large_order_count(self):
        """Order with 5 items gets count 5 for all rows."""
        n = 5
        df = _thai_order_df(**{
            "หมายเลขคำสั่งซื้อ": ["ORD001"] * n,
            "ชื่อสินค้า": [f"Product {i}" for i in range(n)],
            "ราคาตั้งต้น": [100] * n,
            "ราคาขาย": [90] * n,
            "จำนวน": [1] * n,
            "โค้ดส่วนลดชำระโดยผู้ขาย": [0] * n,
            "ส่วนลด bundle deal ชำระโดยผู้ขาย": [0] * n,
            "เลขอ้างอิง SKU (SKU Reference No.)": [f"SKU{i}" for i in range(n)],
            "ชื่อตัวเลือก": [f"Var {i}" for i in range(n)],
            "โค้ด Coins Cashback ชำระโดยผู้ขาย": [0] * n,
            "ส่วนลดจาก Shopee": [0] * n,
        })
        result, _ = _normalise_thai_columns(df)
        rows = result.to_dicts()
        assert all(r["Jumlah Produk di Pesan"] == 5 for r in rows)
