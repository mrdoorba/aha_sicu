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


def paginate(page: int, limit: int) -> tuple[int, int]:
    """Return (limit, offset) for SQL pagination."""
    return limit, (page - 1) * limit


class FilterBuilder:
    """Build dynamic WHERE clauses with automatic $N parameter numbering."""

    def __init__(self, start_idx: int = 1) -> None:
        self._conditions: list[str] = []
        self._params: list[Any] = []
        self._idx = start_idx

    def add(self, condition_template: str, value: Any) -> "FilterBuilder":
        """Add a condition. Use {p} as placeholder for the $N parameter."""
        self._conditions.append(condition_template.replace("{p}", f"${self._idx}"))
        self._params.append(value)
        self._idx += 1
        return self

    @property
    def where_clause(self) -> str:
        """Return the WHERE clause string, or empty string if no conditions."""
        return "WHERE " + " AND ".join(self._conditions) if self._conditions else ""

    @property
    def params(self) -> list[Any]:
        """Return the list of parameter values."""
        return self._params

    @property
    def next_idx(self) -> int:
        """Return the next available parameter index."""
        return self._idx


def escape_like(term: str) -> str:
    """Escape special LIKE/ILIKE pattern characters in search terms.

    Escapes %, _, and \\ so they are treated as literal characters
    in ILIKE queries. Must be used with ESCAPE '\\' clause in SQL.
    """
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
