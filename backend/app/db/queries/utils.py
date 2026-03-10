"""Shared query utilities."""

from typing import Any

from asyncpg import Connection


async def fetch_one(conn: Connection, query: str, *args: Any) -> dict | None:
    """Execute query and return single row as dict, or None."""
    row = await conn.fetchrow(query, *args)
    return dict(row) if row else None


async def fetch_all(conn: Connection, query: str, *args: Any) -> list[dict]:
    """Execute query and return all rows as list of dicts."""
    rows = await conn.fetch(query, *args)
    return [dict(row) for row in rows]


def escape_like(term: str) -> str:
    """Escape special LIKE/ILIKE pattern characters in search terms.

    Escapes %, _, and \\ so they are treated as literal characters
    in ILIKE queries. Must be used with ESCAPE '\\' clause in SQL.
    """
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
