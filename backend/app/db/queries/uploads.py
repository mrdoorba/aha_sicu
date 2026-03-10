"""Brand uploads database queries using parameterized SQL."""

from datetime import datetime
from typing import Any, TypedDict

from asyncpg import Connection

from app.db.queries.utils import fetch_all, fetch_one


class UploadRow(TypedDict):
    id: int
    brand_id: int
    file_type: str
    calculator_target: str
    filename: str
    file_size: int
    row_count: int
    uploaded_at: datetime
    storage_path: str | None


class UploadWithDataRow(UploadRow):
    parsed_data: dict[str, Any]


async def get_uploads_by_brand(conn: Connection, brand_id: int) -> list[UploadRow]:
    """Return all uploads for a brand."""
    return await fetch_all(
        conn,
        """
        SELECT id, brand_id, file_type, calculator_target, filename,
               file_size, row_count, uploaded_at, storage_path
        FROM brand_uploads
        WHERE brand_id = $1
        ORDER BY uploaded_at DESC
        """,
        brand_id,
    )


async def get_upload_by_type(
    conn: Connection, brand_id: int, file_type: str
) -> UploadWithDataRow | None:
    """Return a single upload for a brand+file_type, or None."""
    return await fetch_one(
        conn,
        """
        SELECT id, brand_id, file_type, calculator_target, filename,
               file_size, row_count, parsed_data, uploaded_at, storage_path
        FROM brand_uploads
        WHERE brand_id = $1 AND file_type = $2
        """,
        brand_id,
        file_type,
    )


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
    storage_path: str | None = None,
) -> UploadRow:
    """Insert or update an upload for a brand+file_type pair."""
    return await fetch_one(
        conn,
        """
        INSERT INTO brand_uploads
            (brand_id, file_type, calculator_target, filename, file_size,
             row_count, parsed_data, uploaded_by, uploaded_at, storage_path)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), $9)
        ON CONFLICT (brand_id, file_type) DO UPDATE SET
            calculator_target = EXCLUDED.calculator_target,
            filename = EXCLUDED.filename,
            file_size = EXCLUDED.file_size,
            row_count = EXCLUDED.row_count,
            parsed_data = EXCLUDED.parsed_data,
            uploaded_by = EXCLUDED.uploaded_by,
            uploaded_at = NOW(),
            storage_path = EXCLUDED.storage_path
        RETURNING id, brand_id, file_type, calculator_target, filename,
                  file_size, row_count, uploaded_at, storage_path
        """,
        brand_id,
        file_type,
        calculator_target,
        filename,
        file_size,
        row_count,
        parsed_data,
        uploaded_by,
        storage_path,
    )


async def delete_upload(conn: Connection, brand_id: int, file_type: str) -> None:
    """Delete an upload for a brand+file_type pair."""
    await conn.execute(
        "DELETE FROM brand_uploads WHERE brand_id = $1 AND file_type = $2",
        brand_id,
        file_type,
    )
