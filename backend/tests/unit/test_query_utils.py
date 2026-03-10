"""Tests for database query utilities."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.db.queries.utils import fetch_one, fetch_all, paginate, FilterBuilder


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


class TestFilterBuilder:
    def test_empty_builder_returns_empty_where(self):
        fb = FilterBuilder()
        assert fb.where_clause == ""
        assert fb.params == []
        assert fb.next_idx == 1

    def test_single_condition(self):
        fb = FilterBuilder()
        fb.add("name = {p}", "Alice")
        assert fb.where_clause == "WHERE name = $1"
        assert fb.params == ["Alice"]
        assert fb.next_idx == 2

    def test_multiple_conditions(self):
        fb = FilterBuilder()
        fb.add("name = {p}", "Alice")
        fb.add("age > {p}", 25)
        assert fb.where_clause == "WHERE name = $1 AND age > $2"
        assert fb.params == ["Alice", 25]
        assert fb.next_idx == 3

    def test_custom_start_idx(self):
        fb = FilterBuilder(start_idx=3)
        fb.add("name = {p}", "Alice")
        assert fb.where_clause == "WHERE name = $3"
        assert fb.params == ["Alice"]
        assert fb.next_idx == 4

    def test_chaining(self):
        fb = FilterBuilder()
        result = fb.add("a = {p}", 1).add("b = {p}", 2)
        assert result is fb
        assert fb.where_clause == "WHERE a = $1 AND b = $2"

    def test_ilike_pattern(self):
        fb = FilterBuilder()
        fb.add("name ILIKE '%' || {p} || '%' ESCAPE '\\'", "test")
        assert fb.where_clause == "WHERE name ILIKE '%' || $1 || '%' ESCAPE '\\'"
        assert fb.params == ["test"]
