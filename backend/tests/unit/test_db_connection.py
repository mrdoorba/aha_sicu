"""Unit tests for DatabasePool.init retry behaviour."""

from unittest.mock import AsyncMock, patch

import asyncpg
import pytest

from app.db.connection import DatabasePool


@pytest.mark.asyncio
async def test_init_retries_then_succeeds():
    """A transient failure is retried; a later success populates the pool."""
    sentinel_pool = object()
    with (
        patch("app.db.connection.asyncpg.create_pool", new_callable=AsyncMock) as create,
        patch("app.db.connection.asyncio.sleep", new_callable=AsyncMock) as sleep,
    ):
        create.side_effect = [OSError("socket not ready"), sentinel_pool]
        pool = DatabasePool()
        await pool.init("postgresql://x", retries=4)

    assert pool.pool is sentinel_pool
    assert create.call_count == 2
    sleep.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_init_raises_after_exhausting_retries():
    """Persistent failure re-raises the last error instead of looping forever."""
    with (
        patch("app.db.connection.asyncpg.create_pool", new_callable=AsyncMock) as create,
        patch("app.db.connection.asyncio.sleep", new_callable=AsyncMock),
    ):
        create.side_effect = asyncpg.PostgresError("down")
        pool = DatabasePool()
        with pytest.raises(asyncpg.PostgresError):
            await pool.init("postgresql://x", retries=3)

    assert create.call_count == 3
