"""Tests for database query utilities."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.db.queries.utils import escape_like, fetch_one, fetch_all, paginate


class TestFetchOne:
    @pytest.mark.asyncio
    async def test_returns_dict_when_row_exists(self):
        conn = AsyncMock()
        row = MagicMock()
        row.__iter__ = MagicMock(return_value=iter([("id", 1), ("name", "test")]))
        row.keys.return_value = ["id", "name"]
        conn.fetchrow.return_value = row
        result = await fetch_one(conn, "SELECT * FROM t WHERE id = $1", 1)
        assert result == dict(row)
        conn.fetchrow.assert_called_once_with("SELECT * FROM t WHERE id = $1", 1)

    @pytest.mark.asyncio
    async def test_returns_none_when_no_row(self):
        conn = AsyncMock()
        conn.fetchrow.return_value = None
        result = await fetch_one(conn, "SELECT * FROM t WHERE id = $1", 1)
        assert result is None

    @pytest.mark.asyncio
    async def test_passes_multiple_args(self):
        conn = AsyncMock()
        conn.fetchrow.return_value = None
        await fetch_one(conn, "SELECT * FROM t WHERE a = $1 AND b = $2", "x", 2)
        conn.fetchrow.assert_called_once_with(
            "SELECT * FROM t WHERE a = $1 AND b = $2", "x", 2
        )


class TestFetchAll:
    @pytest.mark.asyncio
    async def test_returns_list_of_dicts(self):
        conn = AsyncMock()
        row1 = MagicMock()
        row2 = MagicMock()
        conn.fetch.return_value = [row1, row2]
        result = await fetch_all(conn, "SELECT * FROM t")
        assert result == [dict(row1), dict(row2)]

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_rows(self):
        conn = AsyncMock()
        conn.fetch.return_value = []
        result = await fetch_all(conn, "SELECT * FROM t")
        assert result == []


class TestPaginate:
    def test_first_page(self):
        limit, offset = paginate(page=1, limit=20)
        assert limit == 20
        assert offset == 0

    def test_second_page(self):
        limit, offset = paginate(page=2, limit=20)
        assert limit == 20
        assert offset == 20

    def test_custom_limit(self):
        limit, offset = paginate(page=3, limit=10)
        assert limit == 10
        assert offset == 20
