"""SSE endpoint for real-time event streaming."""

import asyncio
import json
import logging

from fastapi import APIRouter, Query, Request
from sse_starlette.sse import EventSourceResponse

from app.core.security import verify_firebase_token
from app.services.event_broadcaster import sync_broadcaster

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["events"])


async def _event_generator(request: Request, queue: asyncio.Queue):
    """Yield SSE events from the subscriber queue until client disconnects.

    sse-starlette cancels this generator on client disconnect, triggering the
    finally block for cleanup. No manual is_disconnected() polling needed.
    """
    try:
        while True:
            message = await queue.get()
            yield {
                "event": message["event"],
                "data": json.dumps(message["data"]),
            }
    finally:
        await sync_broadcaster.unsubscribe(queue)
        logger.info("SSE client disconnected, unsubscribed")


@router.get("/events")
async def sse_events(
    request: Request,
    token: str = Query(..., description="Firebase auth token"),
):
    """Server-Sent Events endpoint for real-time sync status updates.

    Auth via query parameter since EventSource API cannot set custom headers.
    """
    await verify_firebase_token(token)

    queue = await sync_broadcaster.subscribe()

    response = EventSourceResponse(
        _event_generator(request, queue),
        ping=15,
        headers={"X-Accel-Buffering": "no"},
    )
    return response
