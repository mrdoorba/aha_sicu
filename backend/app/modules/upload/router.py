"""Upload API endpoints."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.dependencies import get_current_user
from app.modules.upload.schemas import (
    BrandUploadsResponse,
    ProcessRequest,
    SignedUrlRequest,
    SignedUrlResponse,
    UploadResponse,
)
from app.modules.upload.service import (
    get_brand_uploads,
    process_upload,
    request_signed_url,
)

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])


@router.post("/signed-url", response_model=SignedUrlResponse)
async def create_signed_url(
    body: SignedUrlRequest,
    current_user: dict = Depends(get_current_user),
) -> SignedUrlResponse:
    """Generate a GCS signed URL for direct file upload."""
    return await request_signed_url(
        brand_id=body.brand_id,
        file_type=body.file_type,
        filename=body.filename,
        content_type=body.content_type,
    )


@router.post("/process", response_model=UploadResponse)
async def trigger_processing(
    body: ProcessRequest,
    current_user: dict = Depends(get_current_user),
) -> UploadResponse:
    """Process an uploaded file: download from GCS, parse, validate, store."""
    return await process_upload(
        upload_id=body.upload_id,
        brand_id=body.brand_id,
        file_type=body.file_type,
        user_id=current_user["id"],
    )


@router.get("/brands/{brand_id}", response_model=BrandUploadsResponse)
async def get_uploads(
    brand_id: int,
    current_user: dict = Depends(get_current_user),
) -> BrandUploadsResponse:
    """Return all uploaded files for a brand."""
    return await get_brand_uploads(brand_id=brand_id)


@router.put("/local/{upload_id}/{filename:path}")
async def local_upload(
    upload_id: str,
    filename: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> JSONResponse:
    """Local dev endpoint: receive file bytes that would go to GCS in production.

    Only available when gcs_upload_bucket is not configured.
    """
    if settings.gcs_upload_bucket:
        return JSONResponse(
            status_code=404, content={"detail": "Local upload not available in production"}
        )

    # Sanitize filename to prevent path traversal
    import os
    safe_filename = os.path.basename(filename)
    if not safe_filename or safe_filename in (".", ".."):
        return JSONResponse(
            status_code=400, content={"detail": "Invalid filename"}
        )

    from app.modules.upload.gcs_client import LocalStorageClient, make_object_name

    body = await request.body()
    storage = LocalStorageClient()
    object_name = make_object_name(upload_id, safe_filename)
    file_path = storage._base_dir / object_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(body)
    return JSONResponse(status_code=200, content={"status": "ok"})
