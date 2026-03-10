"""Pydantic schemas for upload endpoints."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator


class SignedUrlRequest(BaseModel):
    filename: str
    content_type: str
    file_type: str
    brand_id: int


class SignedUrlResponse(BaseModel):
    upload_url: str
    upload_id: str
    expires_at: datetime


class ProcessRequest(BaseModel):
    upload_id: str
    brand_id: int
    file_type: str


class UploadResponse(BaseModel):
    id: int
    brand_id: int
    file_type: str
    filename: str
    file_size: int
    row_count: int
    uploaded_at: datetime


class AutoCalculatedItem(BaseModel):
    calculator_type: str
    status: str  # "success", "skipped", "error"
    result: dict[str, Any] | None = None
    reason: str | None = None

    @field_validator("result", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any] | None:
        if v is None:
            return None
        if isinstance(v, str):
            return json.loads(v)
        return v


class ProcessUploadResponse(BaseModel):
    upload: UploadResponse
    auto_calculated: list[AutoCalculatedItem]


class BrandUploadsResponse(BaseModel):
    brand_id: int
    uploads: list[UploadResponse]


class DownloadResponse(BaseModel):
    download_url: str
    filename: str
