"""Pydantic schemas for brands module."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class BrandListItem(BaseModel):
    """Individual brand item in paginated list."""

    id: int
    brand_name: str
    raw_data: dict[str, Any]
    updated_at: datetime
    meeting_raw_data: dict[str, Any] | None = None


class BrandListResponse(BaseModel):
    """Paginated response for brand list."""

    items: list[BrandListItem]
    total: int
    page: int
    limit: int
    pages: int
