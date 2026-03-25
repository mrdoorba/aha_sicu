"""File parsing and column validation using Polars."""

from io import BytesIO
from typing import Any

import polars as pl

from app.core.exceptions import UploadException

# Shopee CSV exports include 7 metadata rows (report title, username,
# shop name, shop ID, creation date, period, blank line) before the
# actual column headers on row 8.
SHOPEE_CSV_SKIP_ROWS = 7

# ---------------------------------------------------------------------------
# English → Indonesian normalisation for Shopee CSV exports
# ---------------------------------------------------------------------------
# Shopee exports may use English column headers depending on seller language
# settings.  We normalise to Indonesian so the calculator layer stays unchanged.

_COLUMN_RENAME: dict[str, str] = {
    # CPC / Keyword report columns
    "Ad Name": "Nama Iklan",
    "Ads Type": "Jenis Iklan",
    "Product ID": "Kode Produk",
    "Placement": "Penempatan Iklan",
    "Bidding Method": "Mode Bidding",
    "Expense": "Biaya",
    "Keyword/Location": "Kata Pencarian/Penempatan",
    "GMV": "Omzet Penjualan",
    "ROAS": "Efektifitas Iklan",
    "Match Type": "Tipe Pencarian",
    # Mass Update columns
    "Product Name": "Nama Produk",
    "Variation ID": "Kode Variasi",
    "Variation Name": "Nama Variasi",
    "Price": "Harga",
}

_VALUE_MAPS: dict[str, dict[str, str]] = {
    "Status": {
        "Ongoing": "Berjalan",
        "Paused": "Dijeda",
        "Ended": "Berakhir",
    },
    "Jenis Iklan": {
        "Product Ad": "Iklan Produk",
        "Shop Ad": "Iklan Toko",
        "Product Search Ad": "Iklan Pencarian Produk",
    },
    "Penempatan Iklan": {
        "All": "Semua Penempatan",
        "Search": "Halaman Pencarian",
        "Recommendation": "Halaman Rekomendasi",
    },
    "Mode Bidding": {
        "Auto Bidding": "Bidding Otomatis",
        "Manual Bidding": "Bidding Manual",
        "GMV Max Custom ROAS": "GMV Max ROAS",
    },
}


def _normalise_english_columns(df: pl.DataFrame) -> tuple[pl.DataFrame, bool]:
    """Rename English Shopee columns to Indonesian and translate cell values.

    Also renames ``Stock*`` columns to ``Stok*`` so the calculator's
    ``startswith("Stok")`` lookup works for multi-warehouse files.

    Returns:
        Tuple of (normalised DataFrame, was_english) where was_english is True
        if English column renames were applied.
    """
    actual = set(df.columns)
    rename_map = {en: id_ for en, id_ in _COLUMN_RENAME.items() if en in actual}

    # Rename "Stock", "Stock 2", "Stock 3", … → "Stok", "Stok 2", "Stok 3", …
    for col in actual:
        if col == "Stock":
            rename_map[col] = "Stok"
        elif col.startswith("Stock "):
            rename_map[col] = "Stok " + col[len("Stock "):]

    if not rename_map:
        return df, False  # already Indonesian or unrelated

    df = df.rename(rename_map)

    for col, vmap in _VALUE_MAPS.items():
        if col in df.columns and df[col].dtype == pl.Utf8:
            df = df.with_columns(pl.col(col).replace(vmap).alias(col))

    return df, True


# ---------------------------------------------------------------------------
# Thai → Indonesian normalisation for Shopee Thailand order exports
# ---------------------------------------------------------------------------

_ORDER_EXPORT_COLUMN_RENAME_TH: dict[str, str] = {
    "หมายเลขคำสั่งซื้อ": "No. Pesanan",
    "ชื่อสินค้า": "Nama Produk",
    "ราคาตั้งต้น": "Harga Awal",
    "ราคาขาย": "Harga Setelah Diskon",
    "จำนวน": "Jumlah",
    "โค้ดส่วนลดชำระโดยผู้ขาย": "Voucher Ditanggung Penjual",
    "ส่วนลด bundle deal ชำระโดยผู้ขาย": "Paket Diskon (Diskon dari Penjual)",
    "เลขอ้างอิง SKU (SKU Reference No.)": "Nomor Referensi SKU",
    "ชื่อตัวเลือก": "Nama Variasi",
    "โค้ด Coins Cashback ชำระโดยผู้ขาย": "Cashback Koin",
    "ส่วนลดจาก Shopee": "Diskon Dari Shopee",
}


def _normalise_thai_columns(df: pl.DataFrame) -> tuple[pl.DataFrame, bool]:
    """Rename Thai Shopee order-export columns to Indonesian.

    Also computes the synthetic ``Jumlah Produk di Pesan`` column which
    does not exist in Thai exports.  It equals the count of rows sharing
    the same ``No. Pesanan`` (order number).

    Returns:
        Tuple of (normalised DataFrame, was_thai) where was_thai is True
        if Thai column renames were applied.
    """
    actual = set(df.columns)
    rename_map = {th: id_ for th, id_ in _ORDER_EXPORT_COLUMN_RENAME_TH.items() if th in actual}
    if not rename_map:
        return df, False

    df = df.rename(rename_map)

    # Compute synthetic "Jumlah Produk di Pesan" — count of rows per order
    if "No. Pesanan" in df.columns and "Jumlah Produk di Pesan" not in df.columns:
        df = df.with_columns(
            pl.col("No. Pesanan")
            .count()
            .over("No. Pesanan")
            .alias("Jumlah Produk di Pesan")
        )

    return df, True


# ---------------------------------------------------------------------------
# Thai → Indonesian normalisation for Shopee Thailand mass update exports
# ---------------------------------------------------------------------------

_MASS_UPDATE_COLUMN_RENAME_TH: dict[str, str] = {
    "รหัสสินค้า": "Kode Produk",
    "ชื่อสินค้า": "Nama Produk",
    "รหัสตัวเลือกสินค้า": "Kode Variasi",
    "ชื่อตัวเลือกสินค้า": "Nama Variasi",
    "เลข SKU": "SKU",
    "ราคา": "Harga",
}


def _normalise_thai_mass_update(df: pl.DataFrame) -> tuple[pl.DataFrame, bool]:
    """Rename Thai Shopee mass-update columns to Indonesian.

    Also renames ``คลัง*`` columns to ``Stok*`` so the calculator's
    ``startswith("Stok")`` lookup works for multi-warehouse files.

    Returns:
        Tuple of (normalised DataFrame, was_thai) where was_thai is True
        if Thai column renames were applied.
    """
    actual = set(df.columns)
    rename_map = {th: id_ for th, id_ in _MASS_UPDATE_COLUMN_RENAME_TH.items() if th in actual}

    # Rename "คลัง", "คลัง 2", "คลัง 3", … → "Stok", "Stok 2", "Stok 3", …
    for col in actual:
        if col == "คลัง":
            rename_map[col] = "Stok"
        elif col.startswith("คลัง "):
            rename_map[col] = "Stok " + col[len("คลัง "):]

    if not rename_map:
        return df, False

    df = df.rename(rename_map)
    return df, True


# Required columns per file type — matched against actual Shopee exports.
REQUIRED_COLUMNS: dict[str, list[str]] = {
    "cpc_ad_report": [
        "Nama Iklan",
        "Jenis Iklan",
        "Kode Produk",
        "Penempatan Iklan",
        "Biaya",
    ],
    "keyword_report": [
        "Kata Pencarian/Penempatan",
        "Jenis Iklan",
        "Kode Produk",
        "Penempatan Iklan",
        "Biaya",
        "Omzet Penjualan",
        "Efektifitas Iklan",
    ],
    "order_export": [
        "No. Pesanan",
        "Nama Produk",
        "Harga Awal",
        "Harga Setelah Diskon",
        "Jumlah",
        "Voucher Ditanggung Penjual",
        "Paket Diskon (Diskon dari Penjual)",
        "Nomor Referensi SKU",
        "Nama Variasi",
        "Jumlah Produk di Pesan",
        "Cashback Koin",
        "Diskon Dari Shopee",
    ],
    "mass_update": [
        "Kode Produk",
        "Nama Produk",
        "Kode Variasi",
        "Nama Variasi",
        "SKU",
        "Harga",
    ],
}


def parse_csv(file_bytes: bytes) -> tuple[pl.DataFrame, str]:
    """Parse a Shopee CSV export into a Polars DataFrame.

    Shopee CSV exports contain 7 metadata rows before the actual column
    headers, so we skip them.  ``truncate_ragged_lines`` handles the
    metadata rows that have fewer fields than the data section.

    English column headers are automatically normalised to Indonesian.

    Returns:
        Tuple of (DataFrame, source_language) where source_language is
        ``"en"`` if English columns were detected, ``"id"`` otherwise.
    """
    try:
        df = pl.read_csv(
            BytesIO(file_bytes),
            skip_rows=SHOPEE_CSV_SKIP_ROWS,
            truncate_ragged_lines=True,
        )
        df, was_english = _normalise_english_columns(df)
        return df, "en" if was_english else "id"
    except UploadException:
        raise
    except Exception as e:
        raise UploadException(
            code="UPLOAD_PARSE_FAILED",
            detail=f"Failed to parse CSV file: {e}",
        ) from e


def parse_excel(file_bytes: bytes, header_row: int = 0) -> pl.DataFrame:
    """Parse Excel bytes into a Polars DataFrame.

    Args:
        file_bytes: Raw Excel file content.
        header_row: 0-indexed row to use as header. Mass Update uses 2.
    """
    try:
        return pl.read_excel(
            BytesIO(file_bytes),
            engine="calamine",
            read_options={"header_row": header_row},
        )
    except Exception as e:
        raise UploadException(
            code="UPLOAD_PARSE_FAILED",
            detail=f"Failed to parse Excel file: {e}",
        ) from e


def validate_columns(df: pl.DataFrame, file_type: str) -> None:
    """Validate that the DataFrame contains all required columns for the file type.

    Raises UploadException with UPLOAD_MISSING_COLUMNS if any are absent.
    """
    required = REQUIRED_COLUMNS.get(file_type)
    if required is None:
        raise UploadException(
            code="UPLOAD_INVALID_FORMAT",
            detail=f"Unknown file type: {file_type}",
        )

    actual_columns = set(df.columns)
    missing = [col for col in required if col not in actual_columns]
    if missing:
        raise UploadException(
            code="UPLOAD_MISSING_COLUMNS",
            detail=f"Missing required columns for {file_type}: {', '.join(missing)}",
        )


def dataframe_to_json(
    df: pl.DataFrame, *, source_language: str = "id"
) -> dict[str, Any]:
    """Convert a Polars DataFrame to a JSON-serializable dict for JSONB storage.

    Uses columnar rows format (list-of-lists) instead of list-of-dicts
    to avoid repeating column names for every row.

    Args:
        df: The DataFrame to convert.
        source_language: ``"en"``, ``"id"``, or ``"th"`` — detected language.
    """
    return {
        "columns": df.columns,
        "rows": [list(r) for r in df.rows()],
        "row_count": len(df),
        "source_language": source_language,
    }
