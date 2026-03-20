"""Tests for Brevo webhook endpoint."""

from unittest.mock import patch

import pytest


@pytest.fixture
def webhook_headers():
    """Authorization headers with the correct webhook secret."""
    return {"Authorization": "Bearer test-webhook-secret"}


class TestBrevoWebhook:
    async def test_returns_200_when_valid_event_updates_status(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        mock_db_conn.execute.return_value = "UPDATE 1"

        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.brevo_webhook_secret = "test-webhook-secret"

            response = client.post(
                "/api/v1/webhooks/brevo",
                json={"event": "delivered", "message-id": "<brevo-abc>", "email": "r@b.com", "ts_epoch": 1710936000000},
                headers=webhook_headers,
            )

        assert response.status_code == 200
        assert response.json()["processed"] == 1
        mock_db_conn.execute.assert_called_once()

    async def test_returns_401_when_missing_auth_header(
        self, client, mock_db_conn
    ) -> None:
        response = client.post(
            "/api/v1/webhooks/brevo",
            json={"event": "delivered", "message-id": "<brevo-abc>", "email": "r@b.com"},
        )

        assert response.status_code == 422  # FastAPI rejects missing required header

    async def test_returns_401_when_wrong_secret(
        self, client, mock_db_conn
    ) -> None:
        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.brevo_webhook_secret = "real-secret"

            response = client.post(
                "/api/v1/webhooks/brevo",
                json={"event": "delivered", "message-id": "<brevo-abc>", "email": "r@b.com"},
                headers={"Authorization": "Bearer wrong-secret"},
            )

        assert response.status_code == 401

    async def test_returns_200_when_unknown_message_id(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        mock_db_conn.execute.return_value = "UPDATE 0"

        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.brevo_webhook_secret = "test-webhook-secret"

            response = client.post(
                "/api/v1/webhooks/brevo",
                json={"event": "delivered", "message-id": "<unknown>", "email": "r@b.com", "ts_epoch": 1710936000000},
                headers=webhook_headers,
            )

        assert response.status_code == 200

    async def test_handles_batched_events(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        mock_db_conn.execute.return_value = "UPDATE 1"

        events = [
            {"event": "delivered", "message-id": "<m1>", "email": "r@b.com", "ts_epoch": 1710936000000},
            {"event": "opened", "message-id": "<m2>", "email": "r@b.com", "ts_epoch": 1710936001000},
        ]

        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.brevo_webhook_secret = "test-webhook-secret"

            response = client.post(
                "/api/v1/webhooks/brevo",
                json=events,
                headers=webhook_headers,
            )

        assert response.status_code == 200
        assert response.json()["processed"] == 2

    async def test_returns_400_when_batch_exceeds_limit(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        events = [
            {"event": "delivered", "message-id": f"<m{i}>", "email": "r@b.com", "ts_epoch": 1710936000000}
            for i in range(101)
        ]

        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.brevo_webhook_secret = "test-webhook-secret"

            response = client.post(
                "/api/v1/webhooks/brevo",
                json=events,
                headers=webhook_headers,
            )

        assert response.status_code == 400

    async def test_maps_brevo_event_names_correctly(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        mock_db_conn.execute.return_value = "UPDATE 1"

        mappings = [
            ("softBounce", "bounced"),
            ("hardBounce", "bounced"),
            ("uniqueOpened", "opened"),
            ("click", "clicked"),
        ]

        for brevo_event, expected_status in mappings:
            mock_db_conn.execute.reset_mock()

            with patch("app.modules.email.webhook.settings") as mock_settings:
                mock_settings.brevo_webhook_secret = "test-webhook-secret"

                response = client.post(
                    "/api/v1/webhooks/brevo",
                    json={"event": brevo_event, "message-id": "<m1>", "email": "r@b.com", "ts_epoch": 1710936000000},
                    headers=webhook_headers,
                )

            assert response.status_code == 200
            call_args = mock_db_conn.execute.call_args[0]
            assert call_args[2] == expected_status, f"{brevo_event} should map to {expected_status}"

    async def test_rejects_when_webhook_secret_not_configured(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.brevo_webhook_secret = ""

            response = client.post(
                "/api/v1/webhooks/brevo",
                json={"event": "delivered", "message-id": "<brevo-abc>", "email": "r@b.com"},
                headers=webhook_headers,
            )

        assert response.status_code == 401

    async def test_forwards_bounce_reason_as_error_detail(
        self, client, mock_db_conn, webhook_headers
    ) -> None:
        mock_db_conn.execute.return_value = "UPDATE 1"

        with patch("app.modules.email.webhook.settings") as mock_settings:
            mock_settings.brevo_webhook_secret = "test-webhook-secret"

            response = client.post(
                "/api/v1/webhooks/brevo",
                json={
                    "event": "hardBounce",
                    "message-id": "<brevo-abc>",
                    "email": "r@b.com",
                    "ts_epoch": 1710936000000,
                    "reason": "Mailbox full",
                },
                headers=webhook_headers,
            )

        assert response.status_code == 200
        call_args = mock_db_conn.execute.call_args[0]
        assert call_args[4] == "Mailbox full"
