"""Brand uploads database queries using parameterized SQL."""

from typing import Any

from asyncpg import Connection


async def get_uploads_by_brand(conn: Connection, brand_id: int) -> list[dict]:
    """Return all uploads for a brand."""
    rows = await conn.fetch(
        """
        SELECT id, brand_id, file_type, calculator_target, filename,
               file_size, row_count, uploaded_at
        FROM brand_uploads
        WHERE brand_id = $1
        ORDER BY uploaded_at DESC
        """,
        brand_id,
    )
    return [dict(row) for row in rows]


async def get_upload_by_type(
    conn: Connection, brand_id: int, file_type: str
) -> dict | None:
    """Return a single upload for a brand+file_type, or None."""
    row = await conn.fetchrow(
        """
        SELECT id, brand_id, file_type, calculator_target, filename,
               file_size, row_count, parsed_data, uploaded_at
        FROM brand_uploads
        WHERE brand_id = $1 AND file_type = $2
        """,
        brand_id,
        file_type,
    )
    return dict(row) if row else None


async def upsert_upload(
    conn: Connection,
    brand_id: int,
    file_type: str,
    calculator_target: str,
    filename: str,
    file_size: int,
    row_count: int,
    parsed_data: dict[str, Any],
    uploaded_by: int,
) -> dict:
    """Insert or update an upload for a brand+file_type pair."""
    row = await conn.fetchrow(
        """
        INSERT INTO brand_uploads
            (brand_id, file_type, calculator_target, filename, file_size,
             row_count, parsed_data, uploaded_by, uploaded_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
        ON CONFLICT (brand_id, file_type) DO UPDATE SET
            calculator_target = EXCLUDED.calculator_target,
            filename = EXCLUDED.filename,
            file_size = EXCLUDED.file_size,
            row_count = EXCLUDED.row_count,
            parsed_data = EXCLUDED.parsed_data,
            uploaded_by = EXCLUDED.uploaded_by,
            uploaded_at = NOW()
        RETURNING id, brand_id, file_type, calculator_target, filename,
                  file_size, row_count, uploaded_at
        """,
        brand_id,
        file_type,
        calculator_target,
        filename,
        file_size,
        row_count,
        parsed_data,
        uploaded_by,
    )
    return dict(row)


async def delete_upload(conn: Connection, brand_id: int, file_type: str) -> None:
    """Delete an upload for a brand+file_type pair."""
    await conn.execute(
        "DELETE FROM brand_uploads WHERE brand_id = $1 AND file_type = $2",
        brand_id,
        file_type,
    )
