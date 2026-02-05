"""Brand database queries using parameterized SQL."""

import json
from typing import Any

from asyncpg import Connection


async def upsert_brand(
    conn: Connection,
    external_id: str,
    name: str,
    category: str | None = None,
    marketplace: str | None = None,
    raw_data: dict[str, Any] | None = None,
) -> dict:
    """Upsert brand by external_id (from Google Sheet).

    Uses ON CONFLICT DO UPDATE to handle both insert and update cases.
    """
    row = await conn.fetchrow(
        """
        INSERT INTO brands (external_id, name, category, marketplace, raw_data, updated_at)
        VALUES ($1, $2, $3, $4, $5, NOW())
        ON CONFLICT (external_id) DO UPDATE SET
            name = EXCLUDED.name,
            category = EXCLUDED.category,
            marketplace = EXCLUDED.marketplace,
            raw_data = EXCLUDED.raw_data,
            updated_at = NOW()
        RETURNING id, external_id, name, category, marketplace, raw_data, created_at, updated_at
        """,
        external_id,
        name,
        category,
        marketplace,
        json.dumps(raw_data) if raw_data else None,
    )
    return dict(row)


async def get_brands(
    conn: Connection,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Get brands with pagination."""
    rows = await conn.fetch(
        """
        SELECT id, external_id, name, category, marketplace, raw_data, created_at, updated_at
        FROM brands
        ORDER BY name ASC
        LIMIT $1 OFFSET $2
        """,
        limit,
        offset,
    )
    return [dict(row) for row in rows]


async def get_brand_by_external_id(conn: Connection, external_id: str) -> dict | None:
    """Get brand by external ID."""
    row = await conn.fetchrow(
        """
        SELECT id, external_id, name, category, marketplace, raw_data, created_at, updated_at
        FROM brands
        WHERE external_id = $1
        """,
        external_id,
    )
    return dict(row) if row else None


async def get_brands_count(conn: Connection) -> int:
    """Get total count of brands."""
    result = await conn.fetchval("SELECT COUNT(*) FROM brands")
    return result or 0
