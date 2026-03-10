"""Brand service for querying brand data."""

import math

from app.core.exceptions import AppException
from app.db.connection import db
from app.db.queries.utils import paginate
from app.db.queries import brands as brand_queries
from app.modules.brands.schemas import BrandDetailResponse, BrandListItem, BrandListResponse


async def get_brands_paginated(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
) -> BrandListResponse:
    """Get paginated brand list with optional search.

    Queries brand_vp_data with LEFT JOIN to brand_meeting_data.

    Args:
        page: Page number (1-based).
        limit: Items per page.
        search: Optional search term for brand_name.

    Returns:
        BrandListResponse with paginated results.
    """
    limit, offset = paginate(page, limit)

    async with db.connection() as conn:
        rows = await brand_queries.get_brands_with_meeting(
            conn, limit=limit, offset=offset, search=search
        )
        total = await brand_queries.get_brands_count_with_search(conn, search=search)

    items = [BrandListItem(**row) for row in rows]
    pages = math.ceil(total / limit) if total > 0 else 0

    return BrandListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


async def get_brand_detail(brand_id: int) -> BrandDetailResponse:
    """Get a single brand by ID with meeting data.

    Args:
        brand_id: The brand VP data ID.

    Returns:
        BrandDetailResponse with VP and optional meeting data.

    Raises:
        AppException: If brand not found (404).
    """
    async with db.connection() as conn:
        row = await brand_queries.get_brand_by_id(conn, brand_id)

    if not row:
        raise AppException(
            code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
        )

    return BrandDetailResponse(**row)
