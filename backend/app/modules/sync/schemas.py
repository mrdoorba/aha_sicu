"""Pydantic schemas for sync module."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class BrandFromSheet(BaseModel):
    """Raw brand data from Google Sheet."""

    external_id: str
    name: str
    category: str | None = None
    marketplace: str | None = None
    raw_data: dict[str, Any] | None = None


class SyncError(BaseModel):
    """Error detail for a single brand sync failure."""

    brand: str | None
    error: str


class SyncResult(BaseModel):
    """Result of a sync operation."""

    sync_id: int
    brands_synced: int
    errors: list[SyncError]
    success: bool


class SyncStatusResponse(BaseModel):
    """Response model for sync status endpoint."""

    id: int
    started_at: datetime
    completed_at: datetime | None
    success: bool | None
    brands_synced: int
    error_message: str | None
