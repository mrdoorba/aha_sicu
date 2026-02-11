"""File parsing and column validation using Polars."""

from io import BytesIO
from typing import Any

import polars as pl

from app.core.exceptions import UploadException

# Required columns per file type (case-sensitive)
REQUIRED_COLUMNS: dict[str, list[str]] = {
    "cpc_ad_report": [
        "Nama Produk",
        "Nama Iklan",
        "Tipe Iklan",
        "Penempatan",
        "Tipe Biaya",
        "Biaya",
    ],
    "keyword_report": [
        "Kata Kunci Pencarian",
        "Klik",
        "Kunjungan",
        "Pesanan",
        "Pendapatan",
        "Biaya Iklan",
        "ROAS",
    ],
    "order_export": [
        "No. Pesanan",
        "Nama Produk",
        "Harga Awal",
        "Harga Setelah Diskon",
        "Jumlah",
        "Voucher Ditanggung Penjual",
        "Paket Diskon",
        "Nomor Referensi SKU",
        "Nama Variasi",
        "Jumlah Produk di Pesan",
        "Cashback Koin",
        "Diskon dari Shopee",
    ],
    "mass_update": [
        "Kode Variasi",
        "Nama Produk",
        "Nama Variasi",
        "SKU",
        "Stok",
    ],
}


def parse_csv(file_bytes: bytes) -> pl.DataFrame:
    """Parse CSV bytes into a Polars DataFrame."""
    try:
        return pl.read_csv(BytesIO(file_bytes))
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


def dataframe_to_json(df: pl.DataFrame) -> dict[str, Any]:
    """Convert a Polars DataFrame to a JSON-serializable dict for JSONB storage."""
    return {
        "columns": df.columns,
        "data": df.to_dicts(),
        "row_count": len(df),
    }
