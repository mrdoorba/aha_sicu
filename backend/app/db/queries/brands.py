"""Brand data database queries using parameterized SQL."""

import json
from datetime import datetime
from typing import Any, Literal, TypedDict

from asyncpg import Connection

from app.db.queries.utils import escape_like, fetch_all, fetch_one


class BrandRow(TypedDict):
    id: int
    brand_name: str
    raw_data: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class BrandWithMeetingRow(TypedDict):
    id: int
    brand_name: str
    raw_data: dict[str, Any]
    updated_at: datetime
    marketplace: str
    meeting_raw_data: dict[str, Any] | None


TableName = Literal["brand_vp_data", "brand_meeting_data"]

_VALID_TABLES: frozenset[str] = frozenset({"brand_vp_data", "brand_meeting_data"})


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
    marketplace: str = "ID",
) -> BrandRow:
    """Upsert brand data by brand_name and marketplace.

    Uses ON CONFLICT DO UPDATE to handle both insert and update cases.
    """
    table = _validate_table(table)

    return await fetch_one(
        conn,
        f"""
        INSERT INTO {table} (brand_name, marketplace, raw_data, updated_at)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT (brand_name, marketplace) DO UPDATE SET
            raw_data = EXCLUDED.raw_data,
            updated_at = NOW()
        RETURNING id, brand_name, raw_data, created_at, updated_at
        """,
        brand_name,
        marketplace,
        raw_data,
    )


async def batch_upsert_brand_data(
    conn: Connection,
    table: TableName,
    brand_names: list[str],
    raw_data_list: list[dict[str, Any]],
    marketplace: str = "ID",
) -> int:
    """Batch upsert brand data using unnest arrays.

    Uses a single INSERT...ON CONFLICT with unnest for O(1) round-trips
    regardless of batch size.

    Args:
        conn: Database connection (should be within a transaction).
        table: Target table name.
        brand_names: List of brand names (parallel with raw_data_list).
        raw_data_list: List of raw data dicts (parallel with brand_names).
        marketplace: Marketplace code ('ID' or 'TH').

    Returns:
        Count of upserted rows.
    """
    table = _validate_table(table)

    if not brand_names:
        return 0

    raw_data_json = [json.dumps(d) for d in raw_data_list]
    marketplace_list = [marketplace] * len(brand_names)

    status = await conn.execute(
        f"""
        INSERT INTO {table} (brand_name, marketplace, raw_data, updated_at)
        SELECT unnest($1::text[]), unnest($2::text[]), unnest($3::jsonb[]), NOW()
        ON CONFLICT (brand_name, marketplace) DO UPDATE SET
            raw_data = EXCLUDED.raw_data,
            updated_at = NOW()
        """,
        brand_names,
        marketplace_list,
        raw_data_json,
    )
    return int(status.split()[-1])


async def get_brand_data(
    conn: Connection,
    table: TableName,
    limit: int = 50,
    offset: int = 0,
) -> list[BrandRow]:
    """Get brand data with pagination."""
    table = _validate_table(table)

    return await fetch_all(
        conn,
        f"""
        SELECT id, brand_name, raw_data, created_at, updated_at
        FROM {table}
        ORDER BY brand_name ASC
        LIMIT $1 OFFSET $2
        """,
        limit,
        offset,
    )


async def get_brand_by_name(
    conn: Connection,
    table: TableName,
    brand_name: str,
) -> BrandRow | None:
    """Get brand data by brand name."""
    table = _validate_table(table)

    return await fetch_one(
        conn,
        f"""
        SELECT id, brand_name, raw_data, created_at, updated_at
        FROM {table}
        WHERE brand_name = $1
        """,
        brand_name,
    )


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
    marketplaces: list[str] | None = None,
) -> list[BrandWithMeetingRow]:
    """Get VP brands with LEFT JOIN to meeting data, with optional search and marketplace filter.

    Ordered by match tier when searching -- exact name, then prefix, then
    substring, alphabetical within each tier. Without a search term every row
    shares tier 0, so browsing stays plain alphabetical.
    """
    search_escaped = escape_like(search) if search else None
    return await fetch_all(
        conn,
        """
        SELECT
            v.id, v.brand_name, v.raw_data, v.updated_at, v.marketplace,
            m.raw_data AS meeting_raw_data
        FROM brand_vp_data v
        LEFT JOIN brand_meeting_data m
            ON v.brand_name = m.brand_name AND v.marketplace = m.marketplace
        WHERE ($1::text IS NULL OR v.brand_name ILIKE '%' || $1 || '%' ESCAPE '\')
          AND ($2::text[] IS NULL OR v.marketplace = ANY($2))
        ORDER BY
            CASE
                WHEN $1::text IS NULL THEN 0
                WHEN v.brand_name ILIKE $1 ESCAPE '\' THEN 0
                WHEN v.brand_name ILIKE $1 || '%' ESCAPE '\' THEN 1
                ELSE 2
            END,
            v.brand_name ASC
        LIMIT $3 OFFSET $4
        """,
        search_escaped,
        marketplaces,
        limit,
        offset,
    )


async def get_brand_by_id(conn: Connection, brand_id: int) -> BrandWithMeetingRow | None:
    """Get a single brand by ID with LEFT JOIN to meeting data."""
    return await fetch_one(
        conn,
        """
        SELECT
            v.id, v.brand_name, v.raw_data, v.updated_at, v.marketplace,
            m.raw_data AS meeting_raw_data
        FROM brand_vp_data v
        LEFT JOIN brand_meeting_data m
            ON v.brand_name = m.brand_name AND v.marketplace = m.marketplace
        WHERE v.id = $1
        """,
        brand_id,
    )


async def get_brands_count_with_search(
    conn: Connection,
    search: str | None = None,
    marketplaces: list[str] | None = None,
) -> int:
    """Get total count of VP brands with optional search and marketplace filter."""
    search_escaped = escape_like(search) if search else None
    result = await conn.fetchval(
        """
        SELECT COUNT(*)
        FROM brand_vp_data
        WHERE ($1::text IS NULL OR brand_name ILIKE '%' || $1 || '%' ESCAPE '\')
          AND ($2::text[] IS NULL OR marketplace = ANY($2))
        """,
        search_escaped,
        marketplaces,
    )
    return result or 0
