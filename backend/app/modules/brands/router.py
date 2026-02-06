"""Brands API endpoints."""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user
from app.modules.brands.schemas import BrandListResponse
from app.modules.brands.service import get_brands_paginated

router = APIRouter(prefix="/api/v1/brands", tags=["brands"])


@router.get("", response_model=BrandListResponse)
async def list_brands(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search by brand name"),
    current_user: dict = Depends(get_current_user),
) -> BrandListResponse:
    """Get paginated list of brands with optional search.

    Returns brands from VP data enriched with Meeting data when available.
    Supports pagination and case-insensitive brand name search.
    """
    return await get_brands_paginated(page=page, limit=limit, search=search)
