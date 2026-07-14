"""Upload service — orchestrates signed URL generation, parsing, and storage."""

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from asyncpg import Connection
import polars as pl

from app.calculators.engine import clear_dependent_results, run_calculators_for_upload
from app.config import settings
from app.core.exceptions import AppException, UploadException
from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.db.queries import pending_uploads as pending_queries
from app.db.queries import uploads as upload_queries
from app.modules.upload.gcs_client import get_storage_client, make_object_name
from app.modules.upload.parser import (
    _normalise_english_columns,
    _normalise_thai_columns,
    _normalise_thai_mass_update,
    dataframe_to_json,
    parse_csv,
    parse_excel,
    validate_columns,
)
from app.modules.upload.schemas import (
    AutoCalculatedItem,
    BrandUploadsResponse,
    DownloadResponse,
    ProcessUploadResponse,
    SignedUrlResponse,
    UploadResponse,
)
from app.modules.upload.zip_handler import process_zip

logger = logging.getLogger(__name__)


def _parse_file(
    file_bytes: bytes, filename_lower: str, file_type: str,
) -> tuple:
    """Parse file bytes into a DataFrame based on extension.

    Returns (df, source_language). Delegates to the appropriate parser
    based on file extension.  English and Thai column headers are
    normalised to Indonesian so the calculator layer stays unchanged.
    """
    source_language = "id"

    if filename_lower.endswith(".zip"):
        df = process_zip(file_bytes, file_type)
    elif filename_lower.endswith(".csv"):
        df, source_language = parse_csv(file_bytes)
    elif filename_lower.endswith((".xlsx", ".xls")):
        header_row = 2 if file_type == "mass_update" else 0
        df = parse_excel(file_bytes, header_row=header_row)
    else:
        raise UploadException(
            code="UPLOAD_INVALID_FORMAT",
            detail=f"Unsupported file extension: {filename_lower}",
        )

    # Normalise English columns → Indonesian (CSV already does this in
    # parse_csv, but Excel/ZIP files need it here)
    if source_language == "id":  # skip if parse_csv already detected English
        df, was_english = _normalise_english_columns(df)
        if was_english:
            source_language = "en"

    # Normalise Thai columns → Indonesian (gated by file_type)
    if source_language != "en":  # Thai and English are mutually exclusive
        if file_type == "order_export":
            df, was_thai = _normalise_thai_columns(df)
        elif file_type == "mass_update":
            df, was_thai = _normalise_thai_mass_update(df)
        else:
            was_thai = False
        if was_thai:
            source_language = "th"

    # Drop blank rows in mass_update files (trailing empties from Excel)
    if file_type == "mass_update" and "Kode Produk" in df.columns:
        df = df.filter(
            pl.col("Kode Produk").is_not_null()
            & (pl.col("Kode Produk").cast(pl.Utf8) != "")
        )

    return df, source_language


_VALID_FILE_TYPES: frozenset[str] = frozenset(
    ["cpc_ad_report", "keyword_report", "order_export", "mass_update"]
)

# Maps file_type → accepted file extensions
_ACCEPTED_EXTENSIONS: dict[str, frozenset[str]] = {
    "cpc_ad_report": frozenset([".csv"]),
    "keyword_report": frozenset([".csv"]),
    "order_export": frozenset([".xlsx", ".zip"]),
    "mass_update": frozenset([".xlsx", ".zip"]),
}

# Maps file_type → calculator_target
_CALCULATOR_TARGETS: dict[str, str] = {
    "cpc_ad_report": "ads_keyword",
    "keyword_report": "ads_keyword",
    "order_export": "top_sku,discount",
    "mass_update": "top_sku",
}


@dataclass
class PendingUpload:
    upload_id: str
    brand_id: int
    file_type: str
    filename: str
    object_name: str


def _validate_file_type(file_type: str) -> None:
    """Raise if file_type is not one of the allowed values."""
    if file_type not in _VALID_FILE_TYPES:
        raise UploadException(
            code="UPLOAD_INVALID_FORMAT",
            detail=f"Invalid file_type '{file_type}'. Must be one of: {', '.join(sorted(_VALID_FILE_TYPES))}",
        )


def _validate_extension(filename: str, file_type: str) -> None:
    """Raise if the filename extension is not accepted for the given file type."""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    accepted = _ACCEPTED_EXTENSIONS[file_type]
    if ext not in accepted:
        raise UploadException(
            code="UPLOAD_INVALID_FORMAT",
            detail=f"File extension '{ext}' not accepted for {file_type}. Accepted: {', '.join(sorted(accepted))}",
        )


async def request_signed_url(
    brand_id: int,
    file_type: str,
    filename: str,
    content_type: str,
) -> SignedUrlResponse:
    """Validate inputs, generate a signed upload URL, and track the pending upload."""
    _validate_file_type(file_type)
    _validate_extension(filename, file_type)

    # Verify brand exists and cleanup expired pending uploads
    async with db.connection() as conn:
        brand = await brand_queries.get_brand_by_id(conn, brand_id)
        if not brand:
            raise AppException(
                code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
            )
        await pending_queries.cleanup_expired_uploads(conn)

    upload_id = str(uuid.uuid4())
    object_name = make_object_name(upload_id, filename)
    expiry_minutes = 15
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)

    storage = get_storage_client()
    try:
        upload_url = await asyncio.to_thread(
            storage.generate_signed_upload_url, object_name, content_type, expiry_minutes
        )
    except Exception as e:
        logger.exception("Failed to generate signed upload URL for %s", object_name)
        raise UploadException(
            code="UPLOAD_SIGNED_URL_FAILED",
            detail="Could not generate an upload URL. Please try again.",
            status_code=502,
        ) from e

    async with db.connection() as conn:
        await pending_queries.create_pending_upload(
            conn,
            upload_id=upload_id,
            brand_id=brand_id,
            file_type=file_type,
            filename=filename,
            content_type=content_type,
            object_name=object_name,
            expires_at=expires_at,
        )

    return SignedUrlResponse(
        upload_url=upload_url,
        upload_id=upload_id,
        expires_at=expires_at,
    )


async def _claim_pending_upload(
    conn: Connection, upload_id: str,
) -> PendingUpload:
    """Atomically claim a pending upload from the database.

    Uses DELETE...RETURNING to prevent race conditions across Cloud Run
    instances. The SQL WHERE expires_at > NOW() provides defense-in-depth.
    """
    row = await pending_queries.claim_pending_upload(conn, upload_id)
    if not row:
        raise UploadException(
            code="UPLOAD_SIGNED_URL_EXPIRED",
            detail="Upload ID not found or expired",
        )

    return PendingUpload(
        upload_id=row["upload_id"],
        brand_id=row["brand_id"],
        file_type=row["file_type"],
        filename=row["filename"],
        object_name=row["object_name"],
    )


async def _download_and_parse(
    pending: PendingUpload, file_type: str,
) -> tuple[list[dict], int, str]:
    """Download file from storage, parse it, and return (parsed_data, file_size, source_language)."""
    storage = get_storage_client()

    try:
        file_bytes = await asyncio.to_thread(storage.download_file, pending.object_name)
    except Exception as e:
        raise UploadException(
            code="UPLOAD_PROCESSING_FAILED",
            detail=f"Failed to download file from storage: {e}",
        ) from e

    file_size = len(file_bytes)

    max_bytes = settings.upload_max_file_mb * 1024 * 1024
    if file_size > max_bytes:
        del file_bytes
        raise UploadException(
            code="UPLOAD_TOO_LARGE",
            detail=f"File exceeds the {settings.upload_max_file_mb} MB upload limit",
        )

    try:
        df, source_language = _parse_file(
            file_bytes, pending.filename.lower(), file_type,
        )
    except UploadException:
        raise
    except Exception as e:
        raise UploadException(
            code="UPLOAD_PARSE_FAILED",
            detail=f"Failed to parse file: {e}",
        ) from e

    del file_bytes

    validate_columns(df, file_type)

    row_count = len(df)
    parsed_data = dataframe_to_json(df, source_language=source_language)
    del df

    return parsed_data, file_size, row_count


async def _store_and_auto_execute(
    brand_id: int, file_type: str, pending: PendingUpload,
    parsed_data: list[dict], file_size: int, row_count: int, user_id: int,
    storage_path: str | None = None,
) -> tuple[dict, list[dict]]:
    """Store parsed data in DB and auto-execute dependent calculators."""
    calculator_target = _CALCULATOR_TARGETS[file_type]

    async with db.connection() as conn:
        async with conn.transaction():
            row = await upload_queries.upsert_upload(
                conn,
                brand_id=brand_id,
                file_type=file_type,
                calculator_target=calculator_target,
                filename=pending.filename,
                file_size=file_size,
                row_count=row_count,
                parsed_data=parsed_data,
                uploaded_by=user_id,
                storage_path=storage_path,
            )

        # Build in-memory cache so calculators skip re-fetching large JSONB
        upload_cache = {
            file_type: {"parsed_data": parsed_data, "brand_id": brand_id, "file_type": file_type},
        }

        try:
            await clear_dependent_results(brand_id, file_type, conn)
            auto_calc_raw = await run_calculators_for_upload(
                brand_id, file_type, conn, upload_cache=upload_cache,
            )
        except Exception as e:
            logger.warning(
                "Auto-execute failed after upload for brand %d, file_type %s: %s",
                brand_id, file_type, e, exc_info=True,
            )
            auto_calc_raw = []

    return row, auto_calc_raw


async def process_upload(
    upload_id: str,
    brand_id: int,
    file_type: str,
    user_id: int,
) -> ProcessUploadResponse:
    """Download file from storage, parse, validate, store parsed data, auto-execute calculators."""
    _validate_file_type(file_type)

    # Single connection for claim + brand lookup + old storage path check
    async with db.connection() as conn:
        pending = await _claim_pending_upload(conn, upload_id)

        # Validate brand_id/file_type match after claim
        if pending.brand_id != brand_id or pending.file_type != file_type:
            raise UploadException(
                code="UPLOAD_PROCESSING_FAILED",
                detail="Upload ID does not match brand_id/file_type",
            )

        brand = await brand_queries.get_brand_by_id(conn, brand_id)
        if not brand:
            raise AppException(
                code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
            )

        # Lightweight query — only fetch storage_path, skip large parsed_data
        old_storage_path = await upload_queries.get_storage_path_by_type(
            conn, brand_id, file_type
        )

    pending.filename = f"{brand['brand_name']}_{pending.filename}"

    parsed_data, file_size, row_count = await _download_and_parse(pending, file_type)

    # Delete old file from storage if replacing
    if old_storage_path:
        storage = get_storage_client()
        try:
            await asyncio.to_thread(storage.delete_file, old_storage_path)
        except Exception as e:
            logger.warning("Failed to delete old file from storage: %s", e)

    row, auto_calc_raw = await _store_and_auto_execute(
        brand_id, file_type, pending, parsed_data, file_size, row_count, user_id,
        storage_path=pending.object_name,
    )

    upload_resp = UploadResponse(
        id=row["id"],
        brand_id=row["brand_id"],
        file_type=row["file_type"],
        filename=row["filename"],
        file_size=row["file_size"],
        row_count=row["row_count"],
        uploaded_at=row["uploaded_at"],
    )

    auto_calculated = [
        AutoCalculatedItem(
            calculator_type=item["calculator_type"],
            status=item["status"],
            result=item.get("result"),
            reason=item.get("reason"),
        )
        for item in auto_calc_raw
    ]

    return ProcessUploadResponse(upload=upload_resp, auto_calculated=auto_calculated)


async def get_brand_uploads(brand_id: int) -> BrandUploadsResponse:
    """Return all uploads for a brand."""
    async with db.connection() as conn:
        brand = await brand_queries.get_brand_by_id(conn, brand_id)
        if not brand:
            raise AppException(
                code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
            )
        rows = await upload_queries.get_uploads_by_brand(conn, brand_id)

    uploads = [
        UploadResponse(
            id=r["id"],
            brand_id=r["brand_id"],
            file_type=r["file_type"],
            filename=r["filename"],
            file_size=r["file_size"],
            row_count=r["row_count"],
            uploaded_at=r["uploaded_at"],
        )
        for r in rows
    ]

    return BrandUploadsResponse(brand_id=brand_id, uploads=uploads)


async def get_download_url(brand_id: int, file_type: str) -> DownloadResponse:
    """Generate a signed download URL for a previously uploaded file."""
    _validate_file_type(file_type)

    async with db.connection() as conn:
        upload = await upload_queries.get_upload_by_type(conn, brand_id, file_type)

    if not upload or not upload.get("storage_path"):
        raise AppException(
            code="UPLOAD_NOT_FOUND",
            detail=f"No downloadable file for brand {brand_id}, type {file_type}",
            status_code=404,
        )

    storage = get_storage_client()
    try:
        download_url = await asyncio.to_thread(
            storage.generate_signed_download_url, upload["storage_path"]
        )
    except Exception as e:
        logger.exception("Failed to generate signed download URL for %s", upload["storage_path"])
        raise UploadException(
            code="UPLOAD_SIGNED_URL_FAILED",
            detail="Could not generate a download URL. Please try again.",
            status_code=502,
        ) from e

    return DownloadResponse(
        download_url=download_url,
        filename=upload["filename"],
    )
