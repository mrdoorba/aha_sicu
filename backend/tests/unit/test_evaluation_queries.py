"""Unit tests for evaluation query functions."""

from datetime import date
from unittest.mock import AsyncMock

import pytest

from app.db.queries.evaluations import (
    _build_filter_clauses,
    get_evaluation_inputs,
    list_evaluations,
    upsert_evaluation_inputs,
)



async def test_get_evaluation_inputs_found():
    """Test get_evaluation_inputs returns dict when record exists."""
    mock_row = {
        "id": 1,
        "brand_id": 1,
        "last_edited_by": 1,
        "category_type": "fashion",
        "manual_data": {"key": "val"},
        "created_at": "2026-02-05T10:00:00+00:00",
        "updated_at": "2026-02-05T10:00:00+00:00",
    }
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=mock_row)

    result = await get_evaluation_inputs(conn, brand_id=1)

    assert result is not None
    assert result["brand_id"] == 1
    assert result["category_type"] == "fashion"
    conn.fetchrow.assert_called_once()
    # Verify parameterized query — brand_id only
    call_args = conn.fetchrow.call_args[0]
    assert "$1" in call_args[0]
    assert call_args[1] == 1  # brand_id



async def test_get_evaluation_inputs_not_found():
    """Test get_evaluation_inputs returns None when no record exists."""
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)

    result = await get_evaluation_inputs(conn, brand_id=1)

    assert result is None



async def test_upsert_evaluation_inputs():
    """Test upsert_evaluation_inputs inserts/updates record."""
    mock_row = {
        "id": 1,
        "brand_id": 1,
        "last_edited_by": 1,
        "category_type": "fashion",
        "manual_data": {"key": "val"},
        "created_at": "2026-02-05T10:00:00+00:00",
        "updated_at": "2026-02-05T10:00:00+00:00",
    }
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=mock_row)

    result = await upsert_evaluation_inputs(
        conn,
        brand_id=1,
        last_edited_by=1,
        category_type="fashion",
        manual_data={"key": "val"},
    )

    assert result["category_type"] == "fashion"
    conn.fetchrow.assert_called_once()
    # Verify parameterized query with ON CONFLICT (brand_id)
    call_args = conn.fetchrow.call_args[0]
    assert "ON CONFLICT" in call_args[0]
    assert call_args[1] == 1  # brand_id
    assert call_args[2] == 1  # last_edited_by
    assert call_args[3] == "fashion"
    assert call_args[4] == {"key": "val"}



async def test_upsert_evaluation_inputs_with_null_manual_data():
    """Test upsert passes None when manual_data is None."""
    mock_row = {
        "id": 1,
        "brand_id": 1,
        "last_edited_by": 1,
        "category_type": "non_fashion",
        "manual_data": None,
        "created_at": "2026-02-05T10:00:00+00:00",
        "updated_at": "2026-02-05T10:00:00+00:00",
    }
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=mock_row)

    result = await upsert_evaluation_inputs(
        conn,
        brand_id=1,
        last_edited_by=1,
        category_type="non_fashion",
        manual_data=None,
    )

    assert result["manual_data"] is None
    call_args = conn.fetchrow.call_args[0]
    assert call_args[4] is None  # manual_data passed as None, not json.dumps(None)


# --- Shared model tests ---



async def test_upsert_last_write_wins():
    """Second user saving inputs for same brand overwrites first — last_edited_by reflects second user."""
    first_row = {
        "id": 1,
        "brand_id": 1,
        "last_edited_by": 10,
        "category_type": "fashion",
        "manual_data": {"key": "first"},
        "created_at": "2026-02-05T10:00:00+00:00",
        "updated_at": "2026-02-05T10:00:00+00:00",
    }
    second_row = {
        **first_row,
        "last_edited_by": 20,
        "manual_data": {"key": "second"},
        "updated_at": "2026-02-05T11:00:00+00:00",
    }
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(side_effect=[first_row, second_row])

    # First user saves
    result1 = await upsert_evaluation_inputs(
        conn, brand_id=1, last_edited_by=10,
        category_type="fashion", manual_data={"key": "first"},
    )
    assert result1["last_edited_by"] == 10

    # Second user overwrites (same brand)
    result2 = await upsert_evaluation_inputs(
        conn, brand_id=1, last_edited_by=20,
        category_type="fashion", manual_data={"key": "second"},
    )
    assert result2["last_edited_by"] == 20
    assert result2["manual_data"] == {"key": "second"}



async def test_get_evaluation_inputs_returns_data_regardless_of_editor():
    """Fetching evaluation inputs returns data by brand_id only — editor identity is irrelevant."""
    mock_row = {
        "id": 1,
        "brand_id": 42,
        "last_edited_by": 99,
        "category_type": "non_fashion",
        "manual_data": {"products": {"productCount": 50}},
        "created_at": "2026-02-20T10:00:00+00:00",
        "updated_at": "2026-02-20T10:00:00+00:00",
    }
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=mock_row)

    result = await get_evaluation_inputs(conn, brand_id=42)

    assert result is not None
    assert result["brand_id"] == 42
    assert result["manual_data"]["products"]["productCount"] == 50
    # Query uses brand_id only — no user filtering
    call_args = conn.fetchrow.call_args[0]
    assert "user_id" not in call_args[0].lower().replace("last_edited_by", "")
    assert call_args[1] == 42


# --- _build_filter_clauses tests (Review M2/M5) ---


def test_build_filter_clauses_no_filters():
    """No filters → empty WHERE, no params, next param is $1."""
    where, params, idx = _build_filter_clauses()
    assert where == ""
    assert params == []
    assert idx == 1


def test_build_filter_clauses_search_only():
    """Search only → ILIKE clause with escaped value as $1."""
    where, params, idx = _build_filter_clauses(search="Nike")
    assert "ILIKE" in where
    assert "$1" in where
    assert "ESCAPE" in where
    assert params == ["Nike"]
    assert idx == 2


def test_build_filter_clauses_date_from_only():
    """date_from only → >= clause with date object as $1."""
    d = date(2026, 1, 1)
    where, params, idx = _build_filter_clauses(date_from=d)
    assert "created_at >= $1" in where
    assert params == [d]
    assert idx == 2


def test_build_filter_clauses_date_to_only():
    """date_to only → < (date + interval) clause with date object as $1."""
    d = date(2026, 1, 31)
    where, params, idx = _build_filter_clauses(date_to=d)
    assert "created_at < ($1 + interval '1 day')" in where
    assert params == [d]
    assert idx == 2


def test_build_filter_clauses_all_three_filters():
    """search + date_from + date_to → 3 AND conditions, correct param order."""
    d_from = date(2026, 1, 1)
    d_to = date(2026, 1, 31)
    where, params, idx = _build_filter_clauses(
        search="Nike", date_from=d_from, date_to=d_to,
    )
    assert "ILIKE" in where
    assert "$1" in where
    assert "created_at >= $2" in where
    assert "created_at < ($3 + interval '1 day')" in where
    assert " AND " in where
    assert params == ["Nike", d_from, d_to]
    assert idx == 4


def test_build_filter_clauses_date_from_and_date_to():
    """date_from + date_to (no search) → 2 AND conditions, $1 and $2."""
    d_from = date(2026, 2, 1)
    d_to = date(2026, 2, 28)
    where, params, idx = _build_filter_clauses(date_from=d_from, date_to=d_to)
    assert "created_at >= $1" in where
    assert "created_at < ($2 + interval '1 day')" in where
    assert "ILIKE" not in where
    assert params == [d_from, d_to]
    assert idx == 3


def test_build_filter_clauses_search_with_special_chars():
    """Search with LIKE special chars → escaped in params."""
    where, params, idx = _build_filter_clauses(search="brand%_test")
    assert params == ["brand\\%\\_test"]
    assert idx == 2


# --- Sort column allowlist tests (PB-02-001) ---



async def test_list_evaluations_raises_when_invalid_sort_column():
    """list_evaluations raises ValueError when sort_by is not in allowlist."""
    conn = AsyncMock()
    with pytest.raises(ValueError, match="Invalid sort column"):
        await list_evaluations(
            conn, limit=10, offset=0,
            sort_by="malicious",  # type: ignore[arg-type]
            sort_order="desc",
        )



async def test_list_evaluations_raises_when_invalid_sort_order():
    """list_evaluations raises ValueError when sort_order is not in allowlist."""
    conn = AsyncMock()
    with pytest.raises(ValueError, match="Invalid sort order"):
        await list_evaluations(
            conn, limit=10, offset=0,
            sort_by="created_at",
            sort_order="DROP",  # type: ignore[arg-type]
        )



async def test_list_evaluations_succeeds_when_valid_sort():
    """list_evaluations does not raise when sort_by and sort_order are valid."""
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[])
    result = await list_evaluations(
        conn, limit=10, offset=0,
        sort_by="created_at",
        sort_order="desc",
    )
    assert result == []
    conn.fetch.assert_awaited_once()
