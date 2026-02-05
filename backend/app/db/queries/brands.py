"""Brand data database queries using parameterized SQL."""

import json
from typing import Any, Literal

from asyncpg import Connection

TableName = Literal["brand_vp_data", "brand_meeting_data"]


async def upsert_brand_data(
    conn: Connection,
    table: TableName,
    brand_name: str,
    raw_data: dict[str, Any],
) -> dict:
    """Upsert brand data by brand_name.

    Uses ON CONFLICT DO UPDATE to handle both insert and update cases.
    """
    # Validate table name to prevent SQL injection
    if table not in ("brand_vp_data", "brand_meeting_data"):
        raise ValueError(f"Invalid table name: {table}")

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
    if table not in ("brand_vp_data", "brand_meeting_data"):
        raise ValueError(f"Invalid table name: {table}")

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
    if table not in ("brand_vp_data", "brand_meeting_data"):
        raise ValueError(f"Invalid table name: {table}")

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
    if table not in ("brand_vp_data", "brand_meeting_data"):
        raise ValueError(f"Invalid table name: {table}")

    result = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
    return result or 0


async def delete_all_brand_data(conn: Connection, table: TableName) -> int:
    """Delete all data from a brand table. Returns count of deleted rows."""
    if table not in ("brand_vp_data", "brand_meeting_data"):
        raise ValueError(f"Invalid table name: {table}")

    result = await conn.execute(f"DELETE FROM {table}")
    # Result is like "DELETE 42"
    return int(result.split()[-1]) if result else 0
