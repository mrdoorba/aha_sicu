"""Pydantic schemas for sync module."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


SheetType = Literal["vp", "meeting"]


class SyncError(BaseModel):
    """Error detail for a single row sync failure."""

    brand: str | None
    error: str


class SheetSyncResult(BaseModel):
    """Result of syncing a single sheet."""

    sheet_type: SheetType
    rows_synced: int
    rows_skipped: int = 0
    errors: list[SyncError]
    success: bool


class SyncResult(BaseModel):
    """Result of a full sync operation (both sheets)."""

    sync_id: int
    vp_result: SheetSyncResult | None
    meeting_result: SheetSyncResult | None
    total_synced: int
    total_errors: int
    success: bool


class SyncStatusResponse(BaseModel):
    """Response model for sync status endpoint."""

    id: int
    started_at: datetime
    completed_at: datetime | None
    success: bool | None
    brands_synced: int
    error_message: str | None
    sync_details: dict[str, Any] | None = None
