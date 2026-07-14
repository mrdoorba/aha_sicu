"""Cloud SQL connection pool management using asyncpg."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg

logger = logging.getLogger(__name__)


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Set up JSON/JSONB codecs so asyncpg returns dicts instead of strings."""
    await conn.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )
    await conn.set_type_codec(
        "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )


class DatabasePool:
    """Manages the asyncpg connection pool for Cloud SQL PostgreSQL."""

    def __init__(self) -> None:
        self.pool: asyncpg.Pool | None = None

    async def init(
        self, dsn: str, min_size: int = 1, max_size: int = 5, retries: int = 4
    ) -> None:
        """Initialize the connection pool, retrying transient startup failures.

        On Cloud Run cold start the Cloud SQL socket may not be ready yet; a
        single failed create_pool crashes the whole revision. Retry with
        exponential backoff (1s, 2s, 4s, 8s) before giving up.
        """
        for attempt in range(1, retries + 1):
            try:
                self.pool = await asyncpg.create_pool(
                    dsn, min_size=min_size, max_size=max_size, init=_init_connection
                )
                return
            except (OSError, asyncpg.PostgresError) as e:
                if attempt == retries:
                    raise
                delay = 2 ** (attempt - 1)
                logger.warning(
                    "DB pool init failed (attempt %d/%d): %s — retrying in %ds",
                    attempt, retries, e, delay,
                )
                await asyncio.sleep(delay)

    async def close(self) -> None:
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Acquire a connection from the pool."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        async with self.pool.acquire() as conn:
            yield conn


db = DatabasePool()
