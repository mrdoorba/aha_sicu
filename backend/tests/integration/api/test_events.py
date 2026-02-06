"""Integration tests for SSE events endpoint."""

from unittest.mock import patch


def test_events_endpoint_requires_token(client):
    """Test GET /api/v1/events returns 422 without token query param."""
    response = client.get("/api/v1/events")
    assert response.status_code == 422  # Missing required query param


def test_events_endpoint_rejects_invalid_token(client):
    """Test GET /api/v1/events returns 401 with invalid token."""
    with patch("app.modules.events.router.verify_firebase_token") as mock_verify:
        from app.core.exceptions import AuthException

        mock_verify.side_effect = AuthException(
            code="AUTH_TOKEN_INVALID", detail="Token validation failed"
        )

        response = client.get("/api/v1/events?token=bad-token")
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "AUTH_TOKEN_INVALID"
