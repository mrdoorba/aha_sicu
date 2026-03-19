"""Integration tests for email API endpoints (POST /send, GET /preview)."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.core.exceptions import AppException
from app.modules.email.schemas import SendEmailResponse
from app.modules.evaluations.schemas import EvaluationDetailResponse


def _make_evaluation_detail() -> EvaluationDetailResponse:
    """Create a minimal EvaluationDetailResponse for test fixtures."""
    return EvaluationDetailResponse(
        id=1,
        brand_id=10,
        brand_name="Test Brand",
        final_score=85.0,
        verdict="GOOD",
        template="fashion",
        score_breakdown=[{"section": "A", "score": 85.0}],
        calculator_results={"total": 85.0},
        manual_inputs={"notes": "test"},
        evaluator_email="evaluator@example.com",
        created_at=datetime.now(timezone.utc),
        rule_version=1,
    )


def _make_send_response() -> SendEmailResponse:
    """Create a mock SendEmailResponse."""
    return SendEmailResponse(
        success=True,
        message_id="test-msg-id",
        recipients=["recipient@example.com"],
    )


# --- POST /api/v1/email/send ---


def test_send_email_returns_200_when_authenticated_with_valid_request(client, auth_headers):
    """Happy path: authenticated user sends email with valid data."""
    user, headers, auth_ctx = auth_headers("admin")

    with (
        auth_ctx,
        patch("app.modules.email.router.send_evaluation_email", new_callable=AsyncMock) as mock_send,
        patch("app.modules.email.router.get_evaluation_detail", new_callable=AsyncMock) as mock_eval,
        patch("app.config.settings.email_allowed_domains", "example.com"),
    ):
        mock_eval.return_value = _make_evaluation_detail()
        mock_send.return_value = _make_send_response()

        response = client.post(
            "/api/v1/email/send",
            json={
                "evaluation_id": 1,
                "recipients": ["recipient@example.com"],
                "language": "id",
            },
            headers=headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message_id"] == "test-msg-id"


def test_send_email_returns_401_when_no_auth_token(client):
    """Unauthenticated request is rejected."""
    response = client.post(
        "/api/v1/email/send",
        json={
            "evaluation_id": 1,
            "recipients": ["recipient@example.com"],
            "language": "id",
        },
    )
    assert response.status_code == 401


def test_send_email_returns_422_when_invalid_recipient_domain(client, auth_headers):
    """Domain validation rejects recipients outside allowed domains."""
    user, headers, auth_ctx = auth_headers("admin")

    with (
        auth_ctx,
        patch("app.config.settings.email_allowed_domains", "example.com"),
    ):
        response = client.post(
            "/api/v1/email/send",
            json={
                "evaluation_id": 1,
                "recipients": ["someone@external-domain.com"],
                "language": "id",
            },
            headers=headers,
        )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("outside allowed domains" in str(err.get("msg", "")) for err in detail)


def test_send_email_returns_422_when_domains_not_configured(client, auth_headers):
    """Fail-closed: empty EMAIL_ALLOWED_DOMAINS rejects all sends."""
    user, headers, auth_ctx = auth_headers("admin")

    with (
        auth_ctx,
        patch("app.config.settings.email_allowed_domains", ""),
    ):
        response = client.post(
            "/api/v1/email/send",
            json={
                "evaluation_id": 1,
                "recipients": ["recipient@example.com"],
                "language": "id",
            },
            headers=headers,
        )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("not configured" in str(err.get("msg", "")) for err in detail)


def test_send_email_returns_404_when_evaluation_not_found(client, auth_headers):
    """Missing evaluation ID returns 404."""
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
            "/api/v1/email/send",
            json={
                "evaluation_id": 9999,
                "recipients": ["recipient@example.com"],
                "language": "id",
            },
            headers=headers,
        )

    assert response.status_code == 404
    assert response.json()["code"] == "EVAL_NOT_FOUND"


# --- GET /api/v1/email/preview/{evaluation_id} ---


def test_preview_email_returns_200_when_valid_evaluation(client, auth_headers):
    """Happy path: preview returns rendered HTML."""
    user, headers, auth_ctx = auth_headers("admin")

    with (
        auth_ctx,
        patch("app.modules.email.router.get_evaluation_detail", new_callable=AsyncMock) as mock_eval,
        patch("app.modules.email.router.asset_to_data_uri") as mock_asset,
        patch("app.modules.email.router.render_email_html") as mock_render,
    ):
        mock_eval.return_value = _make_evaluation_detail()
        mock_asset.return_value = "data:image/png;base64,AAAA"
        mock_render.return_value = "<html><body>Preview</body></html>"

        response = client.get("/api/v1/email/preview/1", headers=headers)

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Preview" in response.text


def test_preview_email_returns_401_when_no_auth_token(client):
    """Unauthenticated preview request is rejected."""
    response = client.get("/api/v1/email/preview/1")
    assert response.status_code == 401


def test_preview_email_returns_404_when_evaluation_not_found(client, auth_headers):
    """Missing evaluation ID on preview returns 404."""
    user, headers, auth_ctx = auth_headers("admin")

    with (
        auth_ctx,
        patch(
            "app.modules.email.router.get_evaluation_detail",
            new_callable=AsyncMock,
            side_effect=AppException(code="EVAL_NOT_FOUND", detail="Evaluation not found", status_code=404),
        ),
    ):
        response = client.get("/api/v1/email/preview/9999", headers=headers)

    assert response.status_code == 404
    assert response.json()["code"] == "EVAL_NOT_FOUND"
