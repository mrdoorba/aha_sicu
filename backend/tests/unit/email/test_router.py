"""Tests for email router: history logging, history endpoints, RBAC."""

from unittest.mock import AsyncMock, MagicMock, patch


class TestSendEmailLogsHistory:
    """Test that send_email_endpoint logs sends to email_history."""

    async def test_logs_success_to_history(
        self, client, mock_db_conn, auth_headers
    ) -> None:
        user, headers, auth_ctx = auth_headers("leader")

        mock_eval = MagicMock()
        mock_eval.model_dump.return_value = {
            "id": 42, "brand_name": "Test", "period": "Jan 2026",
            "score_breakdown": [], "final_score": 80.0, "verdict": "Good",
        }

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.message_id = "<brevo-123>"
        mock_response.recipients = ["recipient@ahacommerce.id"]

        with auth_ctx, \
             patch("app.modules.email.router.get_evaluation_detail", new_callable=AsyncMock, return_value=mock_eval), \
             patch("app.modules.email.router.send_evaluation_email", new_callable=AsyncMock, return_value=mock_response), \
             patch("app.modules.email.router.insert_email_history", new_callable=AsyncMock) as mock_insert, \
             patch("app.modules.email.router.settings") as mock_router_settings, \
             patch("app.modules.email.schemas.settings") as mock_schema_settings:
            mock_router_settings.brevo_sender_email = "sender@aha.com"
            mock_schema_settings.email_allowed_domains = "ahacommerce.id"

            response = client.post(
                "/api/v1/email/send",
                json={
                    "evaluation_id": 42,
                    "recipients": ["recipient@ahacommerce.id"],
                    "chart_image": "",
                },
                headers=headers,
            )

        assert response.status_code == 200
        mock_insert.assert_called_once()
        call_kwargs = mock_insert.call_args[1]
        assert call_kwargs["status"] == "sent"
        assert call_kwargs["message_id"] == "<brevo-123>"

    async def test_logs_failure_to_history(
        self, client, mock_db_conn, auth_headers
    ) -> None:
        user, headers, auth_ctx = auth_headers("leader")

        mock_eval = MagicMock()
        mock_eval.model_dump.return_value = {
            "id": 42, "brand_name": "Test", "period": "Jan 2026",
            "score_breakdown": [], "final_score": 80.0, "verdict": "Good",
        }

        from app.core.exceptions import AppException

        with auth_ctx, \
             patch("app.modules.email.router.get_evaluation_detail", new_callable=AsyncMock, return_value=mock_eval), \
             patch("app.modules.email.router.send_evaluation_email", new_callable=AsyncMock, side_effect=AppException(code="BREVO_API_ERROR", detail="fail", status_code=502)), \
             patch("app.modules.email.router.insert_email_history", new_callable=AsyncMock) as mock_insert, \
             patch("app.modules.email.router.settings") as mock_router_settings, \
             patch("app.modules.email.schemas.settings") as mock_schema_settings:
            mock_router_settings.brevo_sender_email = "sender@aha.com"
            mock_schema_settings.email_allowed_domains = "ahacommerce.id"

            response = client.post(
                "/api/v1/email/send",
                json={
                    "evaluation_id": 42,
                    "recipients": ["recipient@ahacommerce.id"],
                    "chart_image": "",
                },
                headers=headers,
            )

        assert response.status_code == 502
        mock_insert.assert_called_once()
        call_kwargs = mock_insert.call_args[1]
        assert call_kwargs["status"] == "failed"
        assert "fail" in call_kwargs["error_detail"]

    async def test_history_logging_failure_does_not_crash_email_send(
        self, client, mock_db_conn, auth_headers
    ) -> None:
        user, headers, auth_ctx = auth_headers("leader")

        mock_eval = MagicMock()
        mock_eval.model_dump.return_value = {
            "id": 42, "brand_name": "Test", "period": "Jan 2026",
            "score_breakdown": [], "final_score": 80.0, "verdict": "Good",
        }

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.message_id = "<brevo-123>"
        mock_response.recipients = ["recipient@ahacommerce.id"]

        with auth_ctx, \
             patch("app.modules.email.router.get_evaluation_detail", new_callable=AsyncMock, return_value=mock_eval), \
             patch("app.modules.email.router.send_evaluation_email", new_callable=AsyncMock, return_value=mock_response), \
             patch("app.modules.email.router.insert_email_history", new_callable=AsyncMock, side_effect=Exception("DB write failed")), \
             patch("app.modules.email.router.settings") as mock_router_settings, \
             patch("app.modules.email.schemas.settings") as mock_schema_settings:
            mock_router_settings.brevo_sender_email = "sender@aha.com"
            mock_schema_settings.email_allowed_domains = "ahacommerce.id"

            response = client.post(
                "/api/v1/email/send",
                json={
                    "evaluation_id": 42,
                    "recipients": ["recipient@ahacommerce.id"],
                    "chart_image": "",
                },
                headers=headers,
            )

        # Email send still succeeds even though history logging failed
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestHistoryEndpoints:
    """Test GET /history and GET /history/{evaluation_id}."""

    async def test_returns_paginated_results_when_leader(
        self, client, mock_db_conn, auth_headers
    ) -> None:
        user, headers, auth_ctx = auth_headers("leader")

        mock_result = {
            "items": [
                {"id": 1, "evaluation_id": 1, "sender_email": "s@a.com",
                 "recipient_email": "r@b.com", "cc_emails": None, "bcc_emails": None,
                 "subject": "Sub", "status": "sent", "message_id": "m1",
                 "error_detail": None, "sent_at": "2026-03-20T10:00:00+00:00"},
            ],
            "total": 1, "page": 1, "limit": 20, "pages": 1,
        }

        with auth_ctx, \
             patch("app.modules.email.router.list_email_history", new_callable=AsyncMock, return_value=mock_result):
            response = client.get("/api/v1/email/history", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    async def test_returns_paginated_results_when_admin(
        self, client, mock_db_conn, auth_headers
    ) -> None:
        user, headers, auth_ctx = auth_headers("admin")

        mock_result = {
            "items": [], "total": 0, "page": 1, "limit": 20, "pages": 0,
        }

        with auth_ctx, \
             patch("app.modules.email.router.list_email_history", new_callable=AsyncMock, return_value=mock_result):
            response = client.get("/api/v1/email/history", headers=headers)

        assert response.status_code == 200

    async def test_returns_403_when_member(
        self, client, mock_db_conn, auth_headers
    ) -> None:
        user, headers, auth_ctx = auth_headers("member")

        with auth_ctx:
            response = client.get("/api/v1/email/history", headers=headers)

        assert response.status_code == 403

    async def test_evaluation_history_returns_records_when_leader(
        self, client, mock_db_conn, auth_headers
    ) -> None:
        user, headers, auth_ctx = auth_headers("leader")

        mock_rows = [
            {"id": 1, "evaluation_id": 42, "sender_email": "s@a.com",
             "recipient_email": "r@b.com", "cc_emails": None, "bcc_emails": None,
             "subject": "Sub", "status": "sent", "message_id": "m1",
             "error_detail": None, "sent_at": "2026-03-20T10:00:00+00:00"},
        ]

        with auth_ctx, \
             patch("app.modules.email.router.list_email_history_by_evaluation", new_callable=AsyncMock, return_value=mock_rows):
            response = client.get("/api/v1/email/history/42", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["evaluation_id"] == 42

    async def test_evaluation_history_returns_403_when_member(
        self, client, mock_db_conn, auth_headers
    ) -> None:
        user, headers, auth_ctx = auth_headers("member")

        with auth_ctx:
            response = client.get("/api/v1/email/history/42", headers=headers)

        assert response.status_code == 403
