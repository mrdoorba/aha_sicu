"""Pydantic schemas for brands module."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator


def _parse_json(v: Any) -> dict[str, Any] | None:
    """Parse JSONB value that asyncpg may return as a string."""
    if v is None:
        return None
    if isinstance(v, str):
        return json.loads(v)
    return v


class BrandListItem(BaseModel):
    """Individual brand item in paginated list."""

    id: int
    brand_name: str
    raw_data: dict[str, Any]
    updated_at: datetime
    marketplace: str = "ID"
    meeting_raw_data: dict[str, Any] | None = None

    @field_validator("raw_data", "meeting_raw_data", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any] | None:
        return _parse_json(v)


class BrandDetailResponse(BaseModel):
    """Single brand detail response."""

    id: int
    brand_name: str
    raw_data: dict[str, Any]
    updated_at: datetime
    marketplace: str = "ID"
    meeting_raw_data: dict[str, Any] | None = None

    @field_validator("raw_data", "meeting_raw_data", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any] | None:
        return _parse_json(v)


class BrandListResponse(BaseModel):
    """Paginated response for brand list."""

    items: list[BrandListItem]
    total: int
    page: int
    limit: int
    pages: int
