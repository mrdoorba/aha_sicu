"""EventBroadcaster: application-level fan-out for SSE events."""

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class EventBroadcaster:
    """Broadcasts events to multiple async subscribers via per-client queues.

    Each subscriber gets an asyncio.Queue. On broadcast, the event is put into
    every subscriber's queue. Full queues have events silently dropped (acceptable
    for status-update workloads with only ~5 concurrent users).
    """

    def __init__(self, max_queue_size: int = 64) -> None:
        self._subscribers: list[asyncio.Queue[dict[str, Any]]] = []
        self._lock = asyncio.Lock()
        self._max_queue_size = max_queue_size

    async def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        """Register a new subscriber and return its queue."""
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(
            maxsize=self._max_queue_size
        )
        async with self._lock:
            self._subscribers.append(queue)
        logger.info("SSE subscriber added (total: %d)", len(self._subscribers))
        return queue

    async def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        """Remove a subscriber's queue."""
        async with self._lock:
            try:
                self._subscribers.remove(queue)
                logger.info(
                    "SSE subscriber removed (total: %d)", len(self._subscribers)
                )
            except ValueError:
                pass  # Already removed or never subscribed

    async def broadcast(self, event: str, data: Any) -> None:
        """Send an event to all current subscribers.

        Args:
            event: SSE event name (e.g. "sync_status").
            data: JSON-serialisable payload.
        """
        message = {"event": event, "data": data}
        async with self._lock:
            for queue in self._subscribers:
                try:
                    queue.put_nowait(message)
                except asyncio.QueueFull:
                    logger.warning("Dropping SSE event for slow client")


# Singleton instance used across the application
sync_broadcaster = EventBroadcaster()
