"""Unit tests for sync status database queries."""

from unittest.mock import AsyncMock

import pytest

from app.db.queries.sync_status import is_sync_in_progress


@pytest.mark.asyncio
async def test_is_sync_in_progress_returns_true_when_incomplete_sync():
    """is_sync_in_progress returns True when a sync with completed_at=NULL exists."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 42}

    result = await is_sync_in_progress(mock_conn)

    assert result is True
    mock_conn.fetchrow.assert_called_once()
    # Verify the query checks for completed_at IS NULL
    call_args = mock_conn.fetchrow.call_args[0][0]
    assert "completed_at IS NULL" in call_args


@pytest.mark.asyncio
async def test_is_sync_in_progress_returns_false_when_no_active_sync():
    """is_sync_in_progress returns False when no incomplete sync exists."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None

    result = await is_sync_in_progress(mock_conn)

    assert result is False
    mock_conn.fetchrow.assert_called_once()
