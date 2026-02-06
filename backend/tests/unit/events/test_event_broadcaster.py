"""Unit tests for EventBroadcaster service."""

import asyncio

import pytest

from app.services.event_broadcaster import EventBroadcaster, sync_broadcaster


@pytest.fixture
def broadcaster():
    """Create a fresh EventBroadcaster for each test."""
    return EventBroadcaster(max_queue_size=4)


@pytest.mark.asyncio
async def test_subscribe_returns_queue(broadcaster):
    """Test subscribe() returns an asyncio.Queue."""
    queue = await broadcaster.subscribe()
    assert isinstance(queue, asyncio.Queue)


@pytest.mark.asyncio
async def test_unsubscribe_removes_queue(broadcaster):
    """Test unsubscribe() removes the queue from subscribers."""
    queue = await broadcaster.subscribe()
    await broadcaster.unsubscribe(queue)
    # Broadcasting after unsubscribe should not put anything in queue
    await broadcaster.broadcast("sync_status", {"status": "in_progress"})
    assert queue.empty()


@pytest.mark.asyncio
async def test_broadcast_sends_to_all_subscribers(broadcaster):
    """Test broadcast() sends event to all subscribed queues."""
    q1 = await broadcaster.subscribe()
    q2 = await broadcaster.subscribe()

    await broadcaster.broadcast("sync_status", {"status": "in_progress"})

    event1 = q1.get_nowait()
    event2 = q2.get_nowait()
    assert event1 == {"event": "sync_status", "data": {"status": "in_progress"}}
    assert event2 == {"event": "sync_status", "data": {"status": "in_progress"}}


@pytest.mark.asyncio
async def test_broadcast_drops_events_for_full_queue(broadcaster):
    """Test broadcast() drops events when a subscriber's queue is full."""
    queue = await broadcaster.subscribe()

    # Fill the queue (max_queue_size=4)
    for i in range(4):
        await broadcaster.broadcast("sync_status", {"count": i})

    # This should NOT raise — it drops the event for the full queue
    await broadcaster.broadcast("sync_status", {"count": "overflow"})

    # Queue should still have exactly 4 items (the first 4)
    assert queue.qsize() == 4
    first = queue.get_nowait()
    assert first["data"]["count"] == 0


@pytest.mark.asyncio
async def test_unsubscribe_nonexistent_queue_is_safe(broadcaster):
    """Test unsubscribe() with a queue not in subscribers doesn't raise."""
    fake_queue = asyncio.Queue()
    # Should not raise
    await broadcaster.unsubscribe(fake_queue)


@pytest.mark.asyncio
async def test_multiple_subscribe_unsubscribe_cycles(broadcaster):
    """Test multiple subscribe/unsubscribe cycles work correctly."""
    q1 = await broadcaster.subscribe()
    q2 = await broadcaster.subscribe()

    await broadcaster.unsubscribe(q1)
    await broadcaster.broadcast("sync_status", {"status": "success"})

    # q1 should be empty (unsubscribed), q2 should have the event
    assert q1.empty()
    event = q2.get_nowait()
    assert event["data"]["status"] == "success"


@pytest.mark.asyncio
async def test_singleton_instance_exists():
    """Test sync_broadcaster singleton is an EventBroadcaster instance."""
    assert isinstance(sync_broadcaster, EventBroadcaster)
