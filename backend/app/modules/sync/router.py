"""Sync API endpoints."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.modules.sync.schemas import SyncStatusResponse
from app.modules.sync.service import get_latest_sync_status

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


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
