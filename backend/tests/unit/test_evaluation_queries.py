"""Unit tests for evaluation query functions."""

import json
from unittest.mock import AsyncMock

import pytest

from app.db.queries.evaluations import get_evaluation_inputs, upsert_evaluation_inputs


@pytest.mark.asyncio
async def test_get_evaluation_inputs_found():
    """Test get_evaluation_inputs returns dict when record exists."""
    mock_row = {
        "id": 1,
        "brand_id": 1,
        "user_id": 1,
        "category_type": "fashion",
        "manual_data": {"key": "val"},
        "created_at": "2026-02-05T10:00:00+00:00",
        "updated_at": "2026-02-05T10:00:00+00:00",
    }
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=mock_row)

    result = await get_evaluation_inputs(conn, brand_id=1, user_id=1)

    assert result is not None
    assert result["brand_id"] == 1
    assert result["category_type"] == "fashion"
    conn.fetchrow.assert_called_once()
    # Verify parameterized query
    call_args = conn.fetchrow.call_args[0]
    assert "$1" in call_args[0]
    assert call_args[1] == 1  # brand_id
    assert call_args[2] == 1  # user_id


@pytest.mark.asyncio
async def test_get_evaluation_inputs_not_found():
    """Test get_evaluation_inputs returns None when no record exists."""
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)

    result = await get_evaluation_inputs(conn, brand_id=1, user_id=1)

    assert result is None


@pytest.mark.asyncio
async def test_upsert_evaluation_inputs():
    """Test upsert_evaluation_inputs inserts/updates record."""
    mock_row = {
        "id": 1,
        "brand_id": 1,
        "user_id": 1,
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
        user_id=1,
        category_type="fashion",
        manual_data={"key": "val"},
    )

    assert result["category_type"] == "fashion"
    conn.fetchrow.assert_called_once()
    # Verify parameterized query with ON CONFLICT
    call_args = conn.fetchrow.call_args[0]
    assert "ON CONFLICT" in call_args[0]
    assert call_args[1] == 1  # brand_id
    assert call_args[2] == 1  # user_id
    assert call_args[3] == "fashion"
    assert call_args[4] == json.dumps({"key": "val"})


@pytest.mark.asyncio
async def test_upsert_evaluation_inputs_with_null_manual_data():
    """Test upsert passes None when manual_data is None."""
    mock_row = {
        "id": 1,
        "brand_id": 1,
        "user_id": 1,
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
        user_id=1,
        category_type="non_fashion",
        manual_data=None,
    )

    assert result["manual_data"] is None
    call_args = conn.fetchrow.call_args[0]
    assert call_args[4] is None  # manual_data passed as None, not json.dumps(None)
