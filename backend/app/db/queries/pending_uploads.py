"""Pending uploads database queries using parameterized SQL."""

from datetime import datetime

from asyncpg import Connection

from app.db.queries.utils import fetch_one


async def create_pending_upload(
    conn: Connection,
    upload_id: str,
    brand_id: int,
    file_type: str,
    filename: str,
    content_type: str,
    object_name: str,
    expires_at: datetime,
) -> dict | None:
    """Insert a pending upload row."""
    return await fetch_one(
        conn,
        """
        INSERT INTO pending_uploads
            (upload_id, brand_id, file_type, filename, content_type, object_name, expires_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING upload_id, brand_id, file_type, filename, content_type, object_name,
                  expires_at, created_at
        """,
        upload_id,
        brand_id,
        file_type,
        filename,
        content_type,
        object_name,
        expires_at,
    )


async def get_pending_upload(conn: Connection, upload_id: str) -> dict | None:
    """Return a pending upload by upload_id, only if not expired."""
    return await fetch_one(
        conn,
        """
        SELECT upload_id, brand_id, file_type, filename, content_type, object_name,
               expires_at, created_at
        FROM pending_uploads
        WHERE upload_id = $1 AND expires_at > NOW()
        """,
        upload_id,
    )


async def claim_pending_upload(conn: Connection, upload_id: str) -> dict | None:
    """Atomically claim a pending upload by deleting and returning it.

    Uses DELETE...RETURNING to prevent race conditions across Cloud Run
    instances. Only returns non-expired rows.
    """
    return await fetch_one(
        conn,
        """
        DELETE FROM pending_uploads
        WHERE upload_id = $1 AND expires_at > NOW()
        RETURNING upload_id, brand_id, file_type, filename, content_type, object_name,
                  expires_at, created_at
        """,
        upload_id,
    )


async def delete_pending_upload(conn: Connection, upload_id: str) -> None:
    """Delete a pending upload by upload_id."""
    await conn.execute(
        "DELETE FROM pending_uploads WHERE upload_id = $1",
        upload_id,
    )


async def cleanup_expired_uploads(conn: Connection) -> int:
    """Delete all expired pending uploads, return count deleted."""
    result = await conn.execute(
        "DELETE FROM pending_uploads WHERE expires_at < NOW()"
    )
    # asyncpg returns "DELETE N" where N is the count
    return int(result.split()[-1])
