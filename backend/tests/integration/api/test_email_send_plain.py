"""Integration tests for POST /api/v1/email/send-plain (Gmail SMTP path)."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.core.exceptions import AppException
from app.modules.evaluations.schemas import EvaluationDetailResponse


def _make_evaluation_detail() -> EvaluationDetailResponse:
    return EvaluationDetailResponse(
        id=1,
        brand_id=10,
        brand_name="Test Brand",
        final_score=85.0,
        verdict="✔️",
        template="fashion",
        score_breakdown=[{"section": "A", "score": 85.0}],
        calculator_results={"total": 85.0},
        manual_inputs={"notes": "test"},
        evaluator_email="evaluator@example.com",
        created_at=datetime.now(timezone.utc),
        rule_version=1,
    )


def _valid_body() -> dict:
    return {
        "evaluation_id": 1,
        "recipients": ["pic@example.com"],
        "subject": "Hello",
        "body": "Body content",
    }


def test_send_plain_returns_200_on_happy_path(client, auth_headers):
    user, headers, auth_ctx = auth_headers("admin")

    with (
        auth_ctx,
        patch("app.modules.email.router.get_evaluation_detail", new_callable=AsyncMock) as mock_eval,
        patch("app.modules.email.router.gmail_smtp_send", new_callable=AsyncMock) as mock_send,
        patch("app.modules.email.router.insert_email_history", new_callable=AsyncMock) as mock_history,
        patch("app.config.settings.email_allowed_domains", "example.com"),
        patch("app.modules.email.router.settings") as mock_router_settings,
    ):
        mock_eval.return_value = _make_evaluation_detail()
        mock_send.return_value = "msg-id-123@ahacommerce.id"
        mock_router_settings.gmail_smtp_enabled = True
        mock_router_settings.gmail_smtp_user = "bot@ahacommerce.net"
        mock_router_settings.email_from_name = "AHA Commerce"

        response = client.post("/api/v1/email/send-plain", json=_valid_body(), headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message_id"] == "msg-id-123@ahacommerce.id"
    assert data["recipients"] == ["pic@example.com"]
    mock_send.assert_awaited_once()
    mock_history.assert_awaited_once()
    history_kwargs = mock_history.await_args.kwargs
    assert history_kwargs["status"] == "sent"
    assert history_kwargs["sender_email"] == "bot@ahacommerce.net"
    assert history_kwargs["subject"] == "Hello"


def test_send_plain_returns_422_when_invalid_recipient_domain(client, auth_headers):
    user, headers, auth_ctx = auth_headers("admin")

    with (
        auth_ctx,
        patch("app.config.settings.email_allowed_domains", "example.com"),
    ):
        response = client.post(
            "/api/v1/email/send-plain",
            json={**_valid_body(), "recipients": ["someone@blocked.com"]},
            headers=headers,
        )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("outside allowed domains" in str(err.get("msg", "")) for err in detail)


def test_send_plain_returns_404_when_evaluation_not_found(client, auth_headers):
    user, headers, auth_ctx = auth_headers("admin")

    with (
        auth_ctx,
        patch("app.config.settings.email_allowed_domains", "example.com"),
        patch(
            "app.modules.email.router.get_evaluation_detail",
            new_callable=AsyncMock,
            side_effect=AppException(code="EVAL_NOT_FOUND", detail="Evaluation not found", status_code=404),
        ),
    ):
        response = client.post(
            "/api/v1/email/send-plain",
            json={**_valid_body(), "evaluation_id": 9999},
            headers=headers,
        )

    assert response.status_code == 404
    assert response.json()["code"] == "EVAL_NOT_FOUND"


def test_send_plain_debug_mode_writes_preview_and_skips_smtp(client, auth_headers, tmp_path, monkeypatch):
    user, headers, auth_ctx = auth_headers("admin")
    monkeypatch.chdir(tmp_path)  # not strictly used; preview lives in /tmp

    with (
        auth_ctx,
        patch("app.modules.email.router.get_evaluation_detail", new_callable=AsyncMock) as mock_eval,
        patch("app.modules.email.router.gmail_smtp_send", new_callable=AsyncMock) as mock_send,
        patch("app.modules.email.router.insert_email_history", new_callable=AsyncMock),
        patch("app.config.settings.email_allowed_domains", "example.com"),
        patch("app.modules.email.router.settings") as mock_router_settings,
    ):
        mock_eval.return_value = _make_evaluation_detail()
        mock_router_settings.gmail_smtp_enabled = False
        mock_router_settings.gmail_smtp_user = "bot@ahacommerce.net"

        response = client.post("/api/v1/email/send-plain", json=_valid_body(), headers=headers)

    assert response.status_code == 200
    assert response.json()["message_id"] == "debug-file"
    mock_send.assert_not_awaited()


def test_send_plain_ignores_email_enabled_flag(client, auth_headers):
    """Gmail SMTP gate is independent of email_enabled (SendGrid's gate).

    With email_enabled=False and gmail_smtp_enabled=True, SMTP must still fire.
    """
    user, headers, auth_ctx = auth_headers("admin")

    with (
        auth_ctx,
        patch("app.modules.email.router.get_evaluation_detail", new_callable=AsyncMock) as mock_eval,
        patch("app.modules.email.router.gmail_smtp_send", new_callable=AsyncMock) as mock_send,
        patch("app.modules.email.router.insert_email_history", new_callable=AsyncMock),
        patch("app.config.settings.email_allowed_domains", "example.com"),
        patch("app.modules.email.router.settings") as mock_router_settings,
    ):
        mock_eval.return_value = _make_evaluation_detail()
        mock_send.return_value = "msg-id@ahacommerce.id"
        mock_router_settings.email_enabled = False  # SendGrid stays gated
        mock_router_settings.gmail_smtp_enabled = True
        mock_router_settings.gmail_smtp_user = "bot@ahacommerce.net"
        mock_router_settings.email_from_name = "AHA Commerce"

        response = client.post("/api/v1/email/send-plain", json=_valid_body(), headers=headers)

    assert response.status_code == 200
    mock_send.assert_awaited_once()


def test_send_plain_logs_failed_history_when_send_raises(client, auth_headers):
    user, headers, auth_ctx = auth_headers("admin")

    with (
        auth_ctx,
        patch("app.modules.email.router.get_evaluation_detail", new_callable=AsyncMock) as mock_eval,
        patch(
            "app.modules.email.router.gmail_smtp_send",
            new_callable=AsyncMock,
            side_effect=AppException(
                code="GMAIL_SMTP_AUTH_ERROR",
                detail="bad password",
                status_code=502,
            ),
        ),
        patch("app.modules.email.router.insert_email_history", new_callable=AsyncMock) as mock_history,
        patch("app.config.settings.email_allowed_domains", "example.com"),
        patch("app.modules.email.router.settings") as mock_router_settings,
    ):
        mock_eval.return_value = _make_evaluation_detail()
        mock_router_settings.gmail_smtp_enabled = True
        mock_router_settings.gmail_smtp_user = "bot@ahacommerce.net"
        mock_router_settings.email_from_name = "AHA Commerce"

        response = client.post("/api/v1/email/send-plain", json=_valid_body(), headers=headers)

    assert response.status_code == 502
    assert response.json()["code"] == "GMAIL_SMTP_AUTH_ERROR"
    mock_history.assert_awaited_once()
    assert mock_history.await_args.kwargs["status"] == "failed"
    assert "bad password" in mock_history.await_args.kwargs["error_detail"]
