"""Upload service — orchestrates signed URL generation, parsing, and storage."""

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.calculators.engine import clear_dependent_results, run_calculators_for_upload
from app.core.exceptions import AppException, UploadException
from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.db.queries import uploads as upload_queries
from app.modules.upload.gcs_client import get_storage_client, make_object_name
from app.modules.upload.parser import (
    dataframe_to_json,
    parse_csv,
    parse_excel,
    validate_columns,
)
from app.modules.upload.schemas import (
    AutoCalculatedItem,
    BrandUploadsResponse,
    ProcessUploadResponse,
    SignedUrlResponse,
    UploadResponse,
)
from app.modules.upload.zip_handler import process_zip

logger = logging.getLogger(__name__)

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
    content_type: str
    object_name: str
    expires_at: datetime


# In-memory store for pending uploads (sufficient for single Cloud Run instance)
_pending_uploads: dict[str, PendingUpload] = {}


def _cleanup_expired_uploads() -> None:
    """Remove expired entries from _pending_uploads to prevent unbounded growth."""
    now = datetime.now(timezone.utc)
    expired = [uid for uid, p in _pending_uploads.items() if now > p.expires_at]
    for uid in expired:
        _pending_uploads.pop(uid, None)


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
    _cleanup_expired_uploads()
    _validate_file_type(file_type)
    _validate_extension(filename, file_type)

    # Verify brand exists
    async with db.connection() as conn:
        brand = await brand_queries.get_brand_by_id(conn, brand_id)
    if not brand:
        raise AppException(
            code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
        )

    upload_id = str(uuid.uuid4())
    object_name = make_object_name(upload_id, filename)
    expiry_minutes = 15
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)

    storage = get_storage_client()
    upload_url = await asyncio.to_thread(
        storage.generate_signed_upload_url, object_name, content_type, expiry_minutes
    )

    _pending_uploads[upload_id] = PendingUpload(
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


async def process_upload(
    upload_id: str,
    brand_id: int,
    file_type: str,
    user_id: int,
) -> ProcessUploadResponse:
    """Download file from storage, parse, validate, store parsed data, auto-execute calculators, cleanup."""
    _validate_file_type(file_type)

    pending = _pending_uploads.get(upload_id)
    if not pending:
        raise UploadException(
            code="UPLOAD_SIGNED_URL_EXPIRED",
            detail="Upload ID not found or expired",
        )

    if pending.brand_id != brand_id or pending.file_type != file_type:
        raise UploadException(
            code="UPLOAD_PROCESSING_FAILED",
            detail="Upload ID does not match brand_id/file_type",
        )

    if datetime.now(timezone.utc) > pending.expires_at:
        _pending_uploads.pop(upload_id, None)
        raise UploadException(
            code="UPLOAD_SIGNED_URL_EXPIRED",
            detail="Signed URL has expired (15 min window exceeded)",
        )

    # Fetch brand to prefix filename
    async with db.connection() as conn:
        brand = await brand_queries.get_brand_by_id(conn, brand_id)
    if not brand:
        raise AppException(
            code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
        )
    pending.filename = f"{brand['brand_name']}_{pending.filename}"

    storage = get_storage_client()

    # Download from storage
    try:
        file_bytes = await asyncio.to_thread(storage.download_file, pending.object_name)
    except Exception as e:
        raise UploadException(
            code="UPLOAD_PROCESSING_FAILED",
            detail=f"Failed to download file from storage: {e}",
        ) from e

    file_size = len(file_bytes)
    filename_lower = pending.filename.lower()

    # Parse based on file extension
    source_language = "id"
    try:
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
                detail=f"Unsupported file extension: {pending.filename}",
            )
    except UploadException:
        raise
    except Exception as e:
        raise UploadException(
            code="UPLOAD_PARSE_FAILED",
            detail=f"Failed to parse file: {e}",
        ) from e

    # Free raw file bytes — no longer needed after parsing
    del file_bytes

    # Validate columns
    validate_columns(df, file_type)

    # Convert to JSONB-ready format
    row_count = len(df)
    parsed_data = dataframe_to_json(df, source_language=source_language)
    del df  # Free DataFrame — parsed_data holds the JSON-ready structure now
    calculator_target = _CALCULATOR_TARGETS[file_type]

    # Store in database (upsert) + clear dependent results + auto-execute calculators
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
            )

        # Clear dependent calculator results + auto-execute (outside transaction — already committed)
        # Wrapped in try/except so upload success is preserved even if auto-execute fails
        try:
            await clear_dependent_results(brand_id, file_type, conn)
            auto_calc_raw = await run_calculators_for_upload(
                brand_id, file_type, conn
            )
        except Exception as e:
            logger.warning(
                "Auto-execute failed after upload for brand %d, file_type %s: %s",
                brand_id, file_type, e, exc_info=True,
            )
            auto_calc_raw = []

    # Delete from storage (best-effort cleanup)
    try:
        await asyncio.to_thread(storage.delete_file, pending.object_name)
    except Exception as e:
        logger.warning("Failed to delete file from storage: %s", e)

    # Remove from pending
    _pending_uploads.pop(upload_id, None)

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
