"""Calculator results database queries using parameterized SQL."""

import json
from typing import Any

from asyncpg import Connection


async def get_results_by_brand(conn: Connection, brand_id: int) -> list[dict]:
    """Return all calculator results for a brand."""
    rows = await conn.fetch(
        """
        SELECT id, brand_id, calculator_type, details, output_text, calculated_at
        FROM calculator_results
        WHERE brand_id = $1
        ORDER BY calculated_at DESC
        """,
        brand_id,
    )
    return [dict(row) for row in rows]


async def get_result_by_type(
    conn: Connection, brand_id: int, calculator_type: str
) -> dict | None:
    """Return a single calculator result for a brand+type, or None."""
    row = await conn.fetchrow(
        """
        SELECT id, brand_id, calculator_type, details, output_text, calculated_at
        FROM calculator_results
        WHERE brand_id = $1 AND calculator_type = $2
        """,
        brand_id,
        calculator_type,
    )
    return dict(row) if row else None


async def delete_results_by_types(
    conn: Connection, brand_id: int, calculator_types: list[str]
) -> int:
    """Delete calculator results for a brand matching any of the given types.

    Returns the count of deleted rows.
    """
    result = await conn.execute(
        "DELETE FROM calculator_results WHERE brand_id = $1 AND calculator_type = ANY($2::text[])",
        brand_id,
        calculator_types,
    )
    # result format: "DELETE N"
    return int(result.split()[-1])


async def upsert_result(
    conn: Connection,
    brand_id: int,
    calculator_type: str,
    details: dict[str, Any],
    output_text: str,
) -> dict:
    """Insert or update a calculator result for a brand+type pair."""
    row = await conn.fetchrow(
        """
        INSERT INTO calculator_results
            (brand_id, calculator_type, details, output_text, calculated_at)
        VALUES ($1, $2, $3, $4, NOW())
        ON CONFLICT (brand_id, calculator_type) DO UPDATE SET
            details = EXCLUDED.details,
            output_text = EXCLUDED.output_text,
            calculated_at = NOW()
        RETURNING id, brand_id, calculator_type, details, output_text, calculated_at
        """,
        brand_id,
        calculator_type,
        json.dumps(details),
        output_text,
    )
    return dict(row)
