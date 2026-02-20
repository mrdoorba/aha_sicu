"""Unit tests for accounts queries."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.modules.accounts.queries import (
    create_user,
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user_role,
)


@pytest.fixture
def mock_conn():
    return AsyncMock()


SAMPLE_USER = {
    "id": 1,
    "email": "user@example.com",
    "role": "member",
    "created_at": datetime(2026, 2, 20, tzinfo=timezone.utc),
    "last_login": None,
}

SAMPLE_USER_FULL = {
    **SAMPLE_USER,
    "firebase_uid": "fb-uid-123",
}


@pytest.mark.asyncio
async def test_get_all_users(mock_conn):
    """Returns list of user dicts."""
    mock_conn.fetch = AsyncMock(return_value=[SAMPLE_USER])
    result = await get_all_users(mock_conn)
    assert result == [SAMPLE_USER]
    mock_conn.fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_users_empty(mock_conn):
    """Returns empty list when no users."""
    mock_conn.fetch = AsyncMock(return_value=[])
    result = await get_all_users(mock_conn)
    assert result == []


@pytest.mark.asyncio
async def test_create_user(mock_conn):
    """Creates user with specified role and returns dict."""
    mock_conn.fetchrow = AsyncMock(return_value=SAMPLE_USER)
    result = await create_user(mock_conn, "fb-uid-123", "user@example.com", "member")
    assert result == SAMPLE_USER
    mock_conn.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_role(mock_conn):
    """Updates role and returns updated user dict."""
    updated = {**SAMPLE_USER, "role": "admin"}
    mock_conn.fetchrow = AsyncMock(return_value=updated)
    result = await update_user_role(mock_conn, 1, "admin")
    assert result["role"] == "admin"


@pytest.mark.asyncio
async def test_update_user_role_not_found(mock_conn):
    """Returns None when user doesn't exist."""
    mock_conn.fetchrow = AsyncMock(return_value=None)
    result = await update_user_role(mock_conn, 999, "admin")
    assert result is None


@pytest.mark.asyncio
async def test_get_user_by_id(mock_conn):
    """Returns user dict when found."""
    mock_conn.fetchrow = AsyncMock(return_value=SAMPLE_USER_FULL)
    result = await get_user_by_id(mock_conn, 1)
    assert result["id"] == 1
    assert result["firebase_uid"] == "fb-uid-123"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(mock_conn):
    """Returns None when not found."""
    mock_conn.fetchrow = AsyncMock(return_value=None)
    result = await get_user_by_id(mock_conn, 999)
    assert result is None


@pytest.mark.asyncio
async def test_delete_user_success(mock_conn):
    """Returns True when user deleted."""
    mock_conn.execute = AsyncMock(return_value="DELETE 1")
    result = await delete_user(mock_conn, 1)
    assert result is True


@pytest.mark.asyncio
async def test_delete_user_not_found(mock_conn):
    """Returns False when user doesn't exist."""
    mock_conn.execute = AsyncMock(return_value="DELETE 0")
    result = await delete_user(mock_conn, 999)
    assert result is False
