"""Tests for database query utilities."""

from app.db.queries.utils import paginate, FilterBuilder


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
