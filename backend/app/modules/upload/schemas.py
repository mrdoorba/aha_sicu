"""Pydantic schemas for upload endpoints."""

from datetime import datetime

from pydantic import BaseModel


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


class BrandUploadsResponse(BaseModel):
    brand_id: int
    uploads: list[UploadResponse]
