"""Brand service for querying brand data."""

import math

from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.modules.brands.schemas import BrandListItem, BrandListResponse


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
    offset = (page - 1) * limit

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
