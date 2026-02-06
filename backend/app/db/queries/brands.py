"""Brand data database queries using parameterized SQL."""

import json
from typing import Any, Literal

from asyncpg import Connection

TableName = Literal["brand_vp_data", "brand_meeting_data"]

_VALID_TABLES: frozenset[str] = frozenset({"brand_vp_data", "brand_meeting_data"})


def _escape_like(term: str) -> str:
    """Escape special LIKE/ILIKE pattern characters in search terms."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _validate_table(table: str) -> str:
    """Validate table name against allowlist to prevent SQL injection."""
    if table not in _VALID_TABLES:
        raise ValueError(f"Invalid table name: {table}")
    return table


async def upsert_brand_data(
    conn: Connection,
    table: TableName,
    brand_name: str,
    raw_data: dict[str, Any],
) -> dict:
    """Upsert brand data by brand_name.

    Uses ON CONFLICT DO UPDATE to handle both insert and update cases.
    """
    table = _validate_table(table)

    row = await conn.fetchrow(
        f"""
        INSERT INTO {table} (brand_name, raw_data, updated_at)
        VALUES ($1, $2, NOW())
        ON CONFLICT (brand_name) DO UPDATE SET
            raw_data = EXCLUDED.raw_data,
            updated_at = NOW()
        RETURNING id, brand_name, raw_data, created_at, updated_at
        """,
        brand_name,
        json.dumps(raw_data),
    )
    return dict(row)


async def get_brand_data(
    conn: Connection,
    table: TableName,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Get brand data with pagination."""
    table = _validate_table(table)

    rows = await conn.fetch(
        f"""
        SELECT id, brand_name, raw_data, created_at, updated_at
        FROM {table}
        ORDER BY brand_name ASC
        LIMIT $1 OFFSET $2
        """,
        limit,
        offset,
    )
    return [dict(row) for row in rows]


async def get_brand_by_name(
    conn: Connection,
    table: TableName,
    brand_name: str,
) -> dict | None:
    """Get brand data by brand name."""
    table = _validate_table(table)

    row = await conn.fetchrow(
        f"""
        SELECT id, brand_name, raw_data, created_at, updated_at
        FROM {table}
        WHERE brand_name = $1
        """,
        brand_name,
    )
    return dict(row) if row else None


async def get_brand_count(conn: Connection, table: TableName) -> int:
    """Get total count of brands in a table."""
    table = _validate_table(table)

    result = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
    return result or 0


async def get_brands_with_meeting(
    conn: Connection,
    limit: int = 20,
    offset: int = 0,
    search: str | None = None,
) -> list[dict]:
    """Get VP brands with LEFT JOIN to meeting data, with optional search."""
    search_escaped = _escape_like(search) if search else None
    rows = await conn.fetch(
        """
        SELECT
            v.id, v.brand_name, v.raw_data, v.updated_at,
            m.raw_data AS meeting_raw_data
        FROM brand_vp_data v
        LEFT JOIN brand_meeting_data m ON v.brand_name = m.brand_name
        WHERE ($1::text IS NULL OR v.brand_name ILIKE '%' || $1 || '%' ESCAPE '\')
        ORDER BY v.brand_name ASC
        LIMIT $2 OFFSET $3
        """,
        search_escaped,
        limit,
        offset,
    )
    return [dict(row) for row in rows]


async def get_brands_count_with_search(
    conn: Connection,
    search: str | None = None,
) -> int:
    """Get total count of VP brands with optional search filter."""
    search_escaped = _escape_like(search) if search else None
    result = await conn.fetchval(
        """
        SELECT COUNT(*)
        FROM brand_vp_data
        WHERE ($1::text IS NULL OR brand_name ILIKE '%' || $1 || '%' ESCAPE '\')
        """,
        search_escaped,
    )
    return result or 0
