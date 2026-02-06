"""Sync API endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.dependencies import get_current_user
from app.core.exceptions import SyncException
from app.db.connection import db
from app.db.queries import sync_status as sync_queries
from app.db.queries.sync_status import is_sync_in_progress
from app.modules.sync.schemas import SyncStatusResponse, SyncTriggerResponse
from app.modules.sync.service import get_latest_sync_status, run_sync

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


@router.post("", status_code=202, response_model=SyncTriggerResponse)
async def trigger_sync(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
) -> SyncTriggerResponse:
    """Trigger a manual sync of brand data.

    Starts the sync process asynchronously and returns immediately.
    Returns 409 if a sync is already in progress.
    """
    async with db.connection() as conn:
        async with conn.transaction():
            # Advisory lock prevents TOCTOU race between check and insert
            await conn.execute("SELECT pg_advisory_xact_lock(1)")
            if await is_sync_in_progress(conn):
                raise SyncException(
                    code="SYNC_IN_PROGRESS",
                    detail="A sync is already running",
                    status_code=409,
                )
            sync_id = await sync_queries.create_sync_status(
                conn, started_at=datetime.now(timezone.utc)
            )

    background_tasks.add_task(run_sync, sync_id=sync_id)
    return SyncTriggerResponse(status="started", sync_id=sync_id)


@router.get("/status", response_model=SyncStatusResponse | None)
async def get_sync_status(
    current_user: dict = Depends(get_current_user),
) -> SyncStatusResponse | None:
    """Get the latest sync status.

    Requires authentication. Returns the most recent sync operation's status
    including whether it succeeded, how many brands were synced, and any errors.
    """
    status = await get_latest_sync_status()
    return status
