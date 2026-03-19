"""Unit tests for pending_uploads query functions."""

import pytest
from unittest.mock import AsyncMock

from app.db.queries.pending_uploads import (
    claim_pending_upload,
    cleanup_expired_uploads,
    create_pending_upload,
    delete_pending_upload,
    get_pending_upload,
)


SAMPLE_ROW = {
    "upload_id": "test-uuid-1234",
    "brand_id": 123,
    "file_type": "cpc_ad_report",
    "filename": "report.csv",
    "content_type": "text/csv",
    "object_name": "uploads/test-uuid-1234/report.csv",
    "expires_at": "2099-01-01T00:00:00+00:00",
    "created_at": "2026-03-19T00:00:00+00:00",
}


@pytest.mark.asyncio
async def test_insert_row_when_create_pending_upload_called() -> None:
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=SAMPLE_ROW)

    result = await create_pending_upload(
        conn,
        upload_id="test-uuid-1234",
        brand_id=123,
        file_type="cpc_ad_report",
        filename="report.csv",
        content_type="text/csv",
        object_name="uploads/test-uuid-1234/report.csv",
        expires_at="2099-01-01T00:00:00+00:00",
    )

    assert result is not None
    assert result["upload_id"] == "test-uuid-1234"
    conn.fetchrow.assert_called_once()
    call_args = conn.fetchrow.call_args
    assert "INSERT INTO pending_uploads" in call_args.args[0]


@pytest.mark.asyncio
async def test_row_returned_when_pending_upload_exists() -> None:
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=SAMPLE_ROW)

    result = await get_pending_upload(conn, "test-uuid-1234")

    assert result is not None
    assert result["upload_id"] == "test-uuid-1234"
    call_args = conn.fetchrow.call_args
    assert "expires_at > NOW()" in call_args.args[0]


@pytest.mark.asyncio
async def test_none_returned_when_pending_upload_missing() -> None:
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)

    result = await get_pending_upload(conn, "nonexistent-id")

    assert result is None


@pytest.mark.asyncio
async def test_row_returned_when_claim_pending_upload_exists() -> None:
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=SAMPLE_ROW)

    result = await claim_pending_upload(conn, "test-uuid-1234")

    assert result is not None
    assert result["upload_id"] == "test-uuid-1234"
    call_args = conn.fetchrow.call_args
    assert "DELETE FROM pending_uploads" in call_args.args[0]
    assert "RETURNING" in call_args.args[0]
    assert "expires_at > NOW()" in call_args.args[0]


@pytest.mark.asyncio
async def test_none_returned_when_claim_pending_upload_missing() -> None:
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)

    result = await claim_pending_upload(conn, "nonexistent-id")

    assert result is None


@pytest.mark.asyncio
async def test_delete_executed_when_delete_pending_upload_called() -> None:
    conn = AsyncMock()
    conn.execute = AsyncMock()

    await delete_pending_upload(conn, "test-uuid-1234")

    conn.execute.assert_called_once()
    call_args = conn.execute.call_args
    assert "DELETE FROM pending_uploads" in call_args.args[0]
    assert call_args.args[1] == "test-uuid-1234"


@pytest.mark.asyncio
async def test_count_returned_when_cleanup_expired_uploads_called() -> None:
    conn = AsyncMock()
    conn.execute = AsyncMock(return_value="DELETE 5")

    count = await cleanup_expired_uploads(conn)

    assert count == 5
    call_args = conn.execute.call_args
    assert "expires_at < NOW()" in call_args.args[0]
