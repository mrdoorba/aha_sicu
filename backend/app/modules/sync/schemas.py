"""Pydantic schemas for sync module."""

import json
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, field_validator, model_validator


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


class SyncTriggerResponse(BaseModel):
    """Response model for POST /sync trigger endpoint."""

    status: Literal["started"]
    sync_id: int


class SyncStatusResponse(BaseModel):
    """Response model for sync status endpoint."""

    id: int
    last_sync: datetime
    status: Literal["success", "failed", "in_progress"]
    started_at: datetime
    completed_at: datetime | None
    brands_synced: int
    error_message: str | None
    sync_details: dict[str, Any] | None = None

    @field_validator("sync_details", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any] | None:
        if v is None:
            return None
        if isinstance(v, str):
            return json.loads(v)
        return v

    @model_validator(mode="before")
    @classmethod
    def compute_derived_fields(cls, data: Any) -> Any:
        """Compute last_sync and status from raw DB fields."""
        if isinstance(data, dict):
            # Pop DB-only fields not in schema
            success = data.pop("success", None)
            timed_out = data.pop("timed_out", False)

            # Compute status from success and timed_out fields
            if "status" not in data:
                if timed_out:
                    data["status"] = "failed"
                    if not data.get("error_message"):
                        data["error_message"] = "Sync timed out after 10 minutes"
                elif success is None:
                    data["status"] = "in_progress"
                elif success:
                    data["status"] = "success"
                else:
                    data["status"] = "failed"
            # Compute last_sync from completed_at or started_at
            if "last_sync" not in data:
                data["last_sync"] = data.get("completed_at") or data.get("started_at")
        return data
