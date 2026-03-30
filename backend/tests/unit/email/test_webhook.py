"""Tests for SendGrid Event Webhook endpoint."""

from unittest.mock import patch

import pytest


@pytest.fixture
def webhook_headers():
    """Authorization headers with the correct webhook secret."""
    return {"Authorization": "Bearer test-webhook-secret"}


class TestSendGridWebhook:
    async def test_returns_200_when_valid_event_updates_status(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        mock_db_conn.execute.return_value = "UPDATE 1"

        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.sendgrid_webhook_secret = "test-webhook-secret"

            response = client.post(
                "/api/v1/webhooks/sendgrid",
                json=[{"event": "delivered", "sg_message_id": "sg-abc", "email": "r@b.com", "timestamp": 1710936000}],
                headers=webhook_headers,
            )

        assert response.status_code == 200
        assert response.json()["processed"] == 1
        mock_db_conn.execute.assert_called_once()

    async def test_returns_401_when_missing_auth_header(
        self, client, mock_db_conn
    ) -> None:
        response = client.post(
            "/api/v1/webhooks/sendgrid",
            json=[{"event": "delivered", "sg_message_id": "sg-abc", "email": "r@b.com"}],
        )

        assert response.status_code == 422  # FastAPI rejects missing required header

    async def test_returns_401_when_wrong_secret(
        self, client, mock_db_conn
    ) -> None:
        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.sendgrid_webhook_secret = "real-secret"

            response = client.post(
                "/api/v1/webhooks/sendgrid",
                json=[{"event": "delivered", "sg_message_id": "sg-abc", "email": "r@b.com"}],
                headers={"Authorization": "Bearer wrong-secret"},
            )

        assert response.status_code == 401

    async def test_returns_200_when_unknown_message_id(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        mock_db_conn.execute.return_value = "UPDATE 0"

        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.sendgrid_webhook_secret = "test-webhook-secret"

            response = client.post(
                "/api/v1/webhooks/sendgrid",
                json=[{"event": "delivered", "sg_message_id": "unknown-id", "email": "r@b.com", "timestamp": 1710936000}],
                headers=webhook_headers,
            )

        assert response.status_code == 200

    async def test_handles_batched_events(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        mock_db_conn.execute.return_value = "UPDATE 1"

        events = [
            {"event": "delivered", "sg_message_id": "m1", "email": "r@b.com", "timestamp": 1710936000},
            {"event": "open", "sg_message_id": "m2", "email": "r@b.com", "timestamp": 1710936001},
        ]

        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.sendgrid_webhook_secret = "test-webhook-secret"

            response = client.post(
                "/api/v1/webhooks/sendgrid",
                json=events,
                headers=webhook_headers,
            )

        assert response.status_code == 200
        assert response.json()["processed"] == 2

    async def test_returns_400_when_batch_exceeds_limit(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        events = [
            {"event": "delivered", "sg_message_id": f"m{i}", "email": "r@b.com", "timestamp": 1710936000}
            for i in range(101)
        ]

        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.sendgrid_webhook_secret = "test-webhook-secret"

            response = client.post(
                "/api/v1/webhooks/sendgrid",
                json=events,
                headers=webhook_headers,
            )

        assert response.status_code == 400

    async def test_maps_sendgrid_event_names_correctly(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        mock_db_conn.execute.return_value = "UPDATE 1"

        mappings = [
            ("processed", "sent"),
            ("bounce", "bounced"),
            ("dropped", "blocked"),
            ("open", "opened"),
            ("click", "clicked"),
            ("spamreport", "spam"),
            ("deferred", "deferred"),
        ]

        for sg_event, expected_status in mappings:
            mock_db_conn.execute.reset_mock()

            with patch("app.modules.email.webhook.settings") as mock_settings:
                mock_settings.sendgrid_webhook_secret = "test-webhook-secret"

                response = client.post(
                    "/api/v1/webhooks/sendgrid",
                    json=[{"event": sg_event, "sg_message_id": "m1", "email": "r@b.com", "timestamp": 1710936000}],
                    headers=webhook_headers,
                )

            assert response.status_code == 200
            call_args = mock_db_conn.execute.call_args[0]
            assert call_args[2] == expected_status, f"{sg_event} should map to {expected_status}"

    async def test_rejects_when_webhook_secret_not_configured(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.sendgrid_webhook_secret = ""

            response = client.post(
                "/api/v1/webhooks/sendgrid",
                json=[{"event": "delivered", "sg_message_id": "sg-abc", "email": "r@b.com"}],
                headers=webhook_headers,
            )

        assert response.status_code == 401

    async def test_forwards_bounce_reason_as_error_detail(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        mock_db_conn.execute.return_value = "UPDATE 1"

        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.sendgrid_webhook_secret = "test-webhook-secret"

            response = client.post(
                "/api/v1/webhooks/sendgrid",
                json=[{
                    "event": "bounce",
                    "sg_message_id": "sg-abc",
                    "email": "r@b.com",
                    "timestamp": 1710936000,
                    "reason": "Mailbox full",
                    "type": "blocked",
                }],
                headers=webhook_headers,
            )

        assert response.status_code == 200
        call_args = mock_db_conn.execute.call_args[0]
        assert call_args[4] == "Mailbox full"
