"""Sync status database queries using parameterized SQL."""

from datetime import datetime
from typing import Any, TypedDict

from asyncpg import Connection

from app.db.queries.utils import fetch_one


class SyncStatusRow(TypedDict):
    id: int
    started_at: datetime
    completed_at: datetime | None
    success: bool | None
    brands_synced: int | None
    error_message: str | None
    sync_details: dict[str, Any] | None


class SyncStatusLatestRow(SyncStatusRow):
    timed_out: bool


async def create_sync_status(conn: Connection, started_at: datetime) -> int:
    """Create a new sync status record and return its ID."""
    sync_id = await conn.fetchval(
        """
        INSERT INTO sync_status (started_at)
        VALUES ($1)
        RETURNING id
        """,
        started_at,
    )
    return sync_id


async def update_sync_status(
    conn: Connection,
    sync_id: int,
    completed_at: datetime,
    success: bool,
    brands_synced: int,
    error_message: str | None = None,
    sync_details: dict[str, Any] | None = None,
) -> None:
    """Update sync status with completion details."""
    await conn.execute(
        """
        UPDATE sync_status
        SET completed_at = $2,
            success = $3,
            brands_synced = $4,
            error_message = $5,
            sync_details = $6
        WHERE id = $1
        """,
        sync_id,
        completed_at,
        success,
        brands_synced,
        error_message,
        sync_details,
    )


async def get_latest_sync_status(conn: Connection) -> SyncStatusLatestRow | None:
    """Get the most recent sync status record.

    Returns a `timed_out` flag for records that have been in progress
    for more than 10 minutes, allowing the schema layer to map them
    to a failed status.
    """
    return await fetch_one(
        conn,
        """
        SELECT id, started_at, completed_at, success, brands_synced,
               error_message, sync_details,
               (completed_at IS NULL
                AND started_at <= NOW() - INTERVAL '10 minutes') AS timed_out
        FROM sync_status
        ORDER BY started_at DESC
        LIMIT 1
        """,
    )


async def is_sync_in_progress(conn: Connection) -> bool:
    """Check if any sync is currently running (started but not completed).

    Records older than 10 minutes are considered stale and ignored,
    preventing stuck records from blocking future syncs.
    """
    row = await conn.fetchrow(
        """
        SELECT id FROM sync_status
        WHERE completed_at IS NULL
          AND started_at > NOW() - INTERVAL '10 minutes'
        LIMIT 1
        """
    )
    return row is not None


async def get_sync_status_by_id(conn: Connection, sync_id: int) -> SyncStatusRow | None:
    """Get sync status by ID."""
    return await fetch_one(
        conn,
        """
        SELECT id, started_at, completed_at, success, brands_synced,
               error_message, sync_details
        FROM sync_status
        WHERE id = $1
        """,
        sync_id,
    )
