"""Tests for email history query layer."""

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.db.queries.email_history import (
    _LIMIT_CAP,
    delete_email_history_by_ids,
    insert_email_history,
    list_email_history,
    list_email_history_by_evaluation,
    update_email_status_by_message_id,
)


@pytest.fixture
def mock_conn() -> AsyncMock:
    """Mock asyncpg connection."""
    conn = AsyncMock()
    return conn


class TestInsertEmailHistory:
    async def test_records_sent_email(self, mock_conn: AsyncMock) -> None:
        mock_conn.fetchrow.return_value = {
            "id": 1,
            "evaluation_id": 42,
            "sender_email": "sender@aha.com",
            "recipient_email": "recipient@example.com",
            "cc_emails": None,
            "bcc_emails": None,
            "subject": "Test Subject",
            "status": "sent",
            "message_id": "<sg-msg-123>",
            "error_detail": None,
            "sent_at": "2026-03-20T10:00:00+00:00",
            "created_at": "2026-03-20T10:00:00+00:00",
        }

        result = await insert_email_history(
            mock_conn,
            evaluation_id=42,
            sender_email="sender@aha.com",
            recipient_email="recipient@example.com",
            cc_emails=None,
            bcc_emails=None,
            subject="Test Subject",
            status="sent",
            message_id="<sg-msg-123>",
            error_detail=None,
        )

        assert result["id"] == 1
        assert result["status"] == "sent"
        assert result["message_id"] == "<sg-msg-123>"
        mock_conn.fetchrow.assert_called_once()

    async def test_records_failed_email(self, mock_conn: AsyncMock) -> None:
        mock_conn.fetchrow.return_value = {
            "id": 2,
            "evaluation_id": 42,
            "sender_email": "sender@aha.com",
            "recipient_email": "recipient@example.com",
            "cc_emails": None,
            "bcc_emails": None,
            "subject": "Test Subject",
            "status": "failed",
            "message_id": None,
            "error_detail": "SendGrid API error (500): Internal Server Error",
            "sent_at": "2026-03-20T10:00:00+00:00",
            "created_at": "2026-03-20T10:00:00+00:00",
        }

        result = await insert_email_history(
            mock_conn,
            evaluation_id=42,
            sender_email="sender@aha.com",
            recipient_email="recipient@example.com",
            cc_emails=None,
            bcc_emails=None,
            subject="Test Subject",
            status="failed",
            message_id=None,
            error_detail="SendGrid API error (500): Internal Server Error",
        )

        assert result["status"] == "failed"
        assert result["message_id"] is None
        assert "Internal Server Error" in result["error_detail"]


class TestListEmailHistory:
    async def test_returns_paginated_response(self, mock_conn: AsyncMock) -> None:
        mock_conn.fetchval.return_value = 25
        mock_conn.fetch.return_value = [
            {"id": 1, "evaluation_id": 1, "sender_email": "s@a.com",
             "recipient_email": "r@b.com", "cc_emails": None, "bcc_emails": None,
             "subject": "Sub", "status": "sent", "message_id": "m1",
             "error_detail": None, "sent_at": "2026-03-20T10:00:00+00:00"},
        ]

        result = await list_email_history(mock_conn, page=1, limit=20)

        assert result["total"] == 25
        assert result["page"] == 1
        assert result["limit"] == 20
        assert result["pages"] == 2
        assert len(result["items"]) == 1

    async def test_filters_by_status(self, mock_conn: AsyncMock) -> None:
        mock_conn.fetchval.return_value = 5
        mock_conn.fetch.return_value = []

        await list_email_history(mock_conn, status_filter="failed")

        count_query = mock_conn.fetchval.call_args[0][0]
        assert "status = $" in count_query

    async def test_filters_by_date_range(self, mock_conn: AsyncMock) -> None:
        mock_conn.fetchval.return_value = 3
        mock_conn.fetch.return_value = []

        await list_email_history(
            mock_conn,
            date_from=date(2026, 3, 1),
            date_to=date(2026, 3, 20),
        )

        count_query = mock_conn.fetchval.call_args[0][0]
        assert "sent_at >=" in count_query
        assert "sent_at <" in count_query

    async def test_filters_by_search_term(self, mock_conn: AsyncMock) -> None:
        mock_conn.fetchval.return_value = 2
        mock_conn.fetch.return_value = []

        await list_email_history(mock_conn, search="example")

        count_query = mock_conn.fetchval.call_args[0][0]
        assert "recipient_email ILIKE" in count_query
        assert "subject ILIKE" in count_query

    async def test_sort_by_validates_against_allowlist(self, mock_conn: AsyncMock) -> None:
        with pytest.raises(ValueError, match="Invalid sort column"):
            await list_email_history(mock_conn, sort_by="DROP TABLE")

    async def test_sort_order_validates_against_allowlist(self, mock_conn: AsyncMock) -> None:
        with pytest.raises(ValueError, match="Invalid sort order"):
            await list_email_history(mock_conn, sort_order="DROP TABLE")

    async def test_limit_capped_at_100(self, mock_conn: AsyncMock) -> None:
        mock_conn.fetchval.return_value = 0
        mock_conn.fetch.return_value = []

        result = await list_email_history(mock_conn, limit=500)

        assert result["limit"] == _LIMIT_CAP


class TestUpdateEmailStatus:
    async def test_updates_status_when_priority_higher(self, mock_conn: AsyncMock) -> None:
        mock_conn.execute.return_value = "UPDATE 1"

        result = await update_email_status_by_message_id(
            mock_conn,
            message_id="<sg-msg-abc>",
            new_status="delivered",
            event_at=datetime(2026, 3, 20, 12, 0, 0, tzinfo=timezone.utc),
        )

        assert result is True
        mock_conn.execute.assert_called_once()

    async def test_skips_update_when_priority_lower(self, mock_conn: AsyncMock) -> None:
        mock_conn.execute.return_value = "UPDATE 0"

        result = await update_email_status_by_message_id(
            mock_conn,
            message_id="<sg-msg-abc>",
            new_status="sent",
            event_at=datetime(2026, 3, 20, 12, 0, 0, tzinfo=timezone.utc),
        )

        assert result is False

    async def test_returns_false_when_message_id_not_found(self, mock_conn: AsyncMock) -> None:
        mock_conn.execute.return_value = "UPDATE 0"

        result = await update_email_status_by_message_id(
            mock_conn,
            message_id="<unknown>",
            new_status="delivered",
            event_at=datetime(2026, 3, 20, 12, 0, 0, tzinfo=timezone.utc),
        )

        assert result is False

    async def test_rejects_invalid_status_value(self, mock_conn: AsyncMock) -> None:
        with pytest.raises(ValueError, match="Invalid status"):
            await update_email_status_by_message_id(
                mock_conn,
                message_id="<sg-msg-abc>",
                new_status="hacked",
                event_at=datetime(2026, 3, 20, 12, 0, 0, tzinfo=timezone.utc),
            )

    async def test_idempotent_when_same_event_arrives_twice(self, mock_conn: AsyncMock) -> None:
        mock_conn.execute.return_value = "UPDATE 0"

        result = await update_email_status_by_message_id(
            mock_conn,
            message_id="<sg-msg-abc>",
            new_status="delivered",
            event_at=datetime(2026, 3, 20, 12, 0, 0, tzinfo=timezone.utc),
        )

        assert result is False

    async def test_updates_error_detail_on_bounce(self, mock_conn: AsyncMock) -> None:
        mock_conn.execute.return_value = "UPDATE 1"

        result = await update_email_status_by_message_id(
            mock_conn,
            message_id="<sg-msg-abc>",
            new_status="bounced",
            event_at=datetime(2026, 3, 20, 12, 0, 0, tzinfo=timezone.utc),
            error_detail="Mailbox full",
        )

        assert result is True
        call_args = mock_conn.execute.call_args[0]
        assert call_args[4] == "Mailbox full"


class TestListEmailHistoryByEvaluation:
    async def test_returns_matching_records(self, mock_conn: AsyncMock) -> None:
        mock_conn.fetch.return_value = [
            {"id": 1, "evaluation_id": 42, "sender_email": "s@a.com",
             "recipient_email": "r@b.com", "cc_emails": None, "bcc_emails": None,
             "subject": "Sub", "status": "sent", "message_id": "m1",
             "error_detail": None, "sent_at": "2026-03-20T10:00:00+00:00"},
            {"id": 2, "evaluation_id": 42, "sender_email": "s@a.com",
             "recipient_email": "r2@b.com", "cc_emails": None, "bcc_emails": None,
             "subject": "Sub2", "status": "failed", "message_id": None,
             "error_detail": "err", "sent_at": "2026-03-20T11:00:00+00:00"},
        ]

        result = await list_email_history_by_evaluation(mock_conn, evaluation_id=42)

        assert len(result) == 2
        query = mock_conn.fetch.call_args[0][0]
        assert "evaluation_id = $1" in query


class TestDeleteEmailHistoryByIds:
    async def test_deletes_entries_when_ids_provided(self, mock_conn: AsyncMock) -> None:
        mock_conn.execute.return_value = "DELETE 3"

        result = await delete_email_history_by_ids(mock_conn, ids=[1, 2, 3])

        assert result == 3
        mock_conn.execute.assert_called_once()

    async def test_returns_zero_when_empty_ids(self, mock_conn: AsyncMock) -> None:
        result = await delete_email_history_by_ids(mock_conn, ids=[])

        assert result == 0
        mock_conn.execute.assert_not_called()

    async def test_rejects_batch_exceeding_limit(self, mock_conn: AsyncMock) -> None:
        with pytest.raises(ValueError, match="exceeds limit"):
            await delete_email_history_by_ids(mock_conn, ids=list(range(101)))

    async def test_returns_zero_when_ids_not_found(self, mock_conn: AsyncMock) -> None:
        mock_conn.execute.return_value = "DELETE 0"

        result = await delete_email_history_by_ids(mock_conn, ids=[999])

        assert result == 0
