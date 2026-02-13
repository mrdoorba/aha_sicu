"""Neon connection pool management using asyncpg."""

import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Set up JSON/JSONB codecs so asyncpg returns dicts instead of strings."""
    await conn.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )
    await conn.set_type_codec(
        "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )


class DatabasePool:
    """Manages the asyncpg connection pool for Neon PostgreSQL."""

    def __init__(self) -> None:
        self.pool: asyncpg.Pool | None = None

    async def init(self, dsn: str, min_size: int = 5, max_size: int = 20) -> None:
        """Initialize the connection pool."""
        self.pool = await asyncpg.create_pool(
            dsn, min_size=min_size, max_size=max_size, init=_init_connection
        )

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
