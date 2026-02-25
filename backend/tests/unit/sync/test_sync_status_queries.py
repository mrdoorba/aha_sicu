"""Unit tests for sync status database queries."""

from unittest.mock import AsyncMock

import pytest

from app.db.queries.sync_status import get_latest_sync_status, is_sync_in_progress


@pytest.mark.asyncio
async def test_is_sync_in_progress_returns_true_when_incomplete_sync():
    """is_sync_in_progress returns True when a recent sync with completed_at=NULL exists."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 42}

    result = await is_sync_in_progress(mock_conn)

    assert result is True
    mock_conn.fetchrow.assert_called_once()
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


@pytest.mark.asyncio
async def test_is_sync_in_progress_returns_false_for_stale_records():
    """is_sync_in_progress returns False when sync record is older than 10 minutes.

    The query includes a staleness check so that records with started_at
    older than 10 minutes are not matched, even if completed_at IS NULL.
    When no fresh in-progress record exists, fetchrow returns None.
    """
    mock_conn = AsyncMock()
    # Stale record would not match the query — DB returns no rows
    mock_conn.fetchrow.return_value = None

    result = await is_sync_in_progress(mock_conn)

    assert result is False
    mock_conn.fetchrow.assert_called_once()
    # Verify the query includes the 10-minute staleness check
    call_args = mock_conn.fetchrow.call_args[0][0]
    assert "10 minutes" in call_args
    assert "started_at" in call_args


@pytest.mark.asyncio
async def test_get_latest_sync_status_returns_timed_out_flag():
    """get_latest_sync_status returns a timed_out flag for stale records."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {
        "id": 1,
        "started_at": "2026-02-24T18:57:00",
        "completed_at": None,
        "success": None,
        "brands_synced": 0,
        "error_message": None,
        "sync_details": None,
        "timed_out": True,
    }

    result = await get_latest_sync_status(mock_conn)

    assert result is not None
    assert result["timed_out"] is True
    # Verify the query computes the timed_out column
    call_args = mock_conn.fetchrow.call_args[0][0]
    assert "timed_out" in call_args
    assert "10 minutes" in call_args
