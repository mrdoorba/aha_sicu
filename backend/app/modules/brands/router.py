"""Brands API endpoints."""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user
from app.modules.brands.schemas import BrandDetailResponse, BrandListResponse
from app.modules.brands.service import get_brand_detail, get_brands_paginated

router = APIRouter(prefix="/api/v1/brands", tags=["brands"])


@router.get("", response_model=BrandListResponse)
async def list_brands(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, max_length=200, description="Search by brand name"),
    marketplace: str | None = Query(None, description="Comma-separated marketplace filter (e.g., 'ID,TH')"),
    current_user: dict = Depends(get_current_user),
) -> BrandListResponse:
    """Get paginated list of brands with optional search and marketplace filter.

    Returns brands from VP data enriched with Meeting data when available.
    Supports pagination, case-insensitive brand name search, and marketplace filtering.
    """
    marketplaces = [m.strip() for m in marketplace.split(",")] if marketplace else None
    return await get_brands_paginated(page=page, limit=limit, search=search, marketplaces=marketplaces)


@router.get("/{brand_id}", response_model=BrandDetailResponse)
async def get_brand(
    brand_id: int,
    current_user: dict = Depends(get_current_user),
) -> BrandDetailResponse:
    """Get a single brand by ID with meeting data enrichment."""
    return await get_brand_detail(brand_id=brand_id)
