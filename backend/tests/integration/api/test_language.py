"""Integration tests for language preference endpoint."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch


def _mock_auth(mock_verify, mock_db, mock_queries, user_dict):
    """Set up common auth mocks for an existing Firebase user."""
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_queries.get_user_by_firebase_uid = AsyncMock(
        side_effect=[user_dict, user_dict],
    )
    mock_queries.update_last_login = AsyncMock()
    return mock_conn


def _make_user(language: str = "id") -> dict:
    return {
        "id": 1,
        "firebase_uid": "test-uid",
        "email": "test@example.com",
        "role": "member",
        "language": language,
        "created_at": datetime.now(timezone.utc),
        "last_login": datetime.now(timezone.utc),
    }


def test_language_updated_when_valid_code(client):
    """PATCH /api/v1/me/language returns 200 and updated language."""
    user = _make_user("id")
    updated_user = _make_user("en")

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_queries,
        patch("app.modules.auth.router.db") as mock_router_db,
        patch("app.modules.auth.router.user_queries") as mock_router_queries,
    ):
        _mock_auth(mock_verify, mock_db, mock_queries, user)

        mock_router_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn
        mock_router_queries.update_language = AsyncMock(return_value=updated_user)

        response = client.patch(
            "/api/v1/me/language",
            json={"language": "en"},
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 200
        assert response.json()["language"] == "en"


def test_422_when_invalid_language_code(client):
    """PATCH /api/v1/me/language rejects unsupported language codes."""
    user = _make_user()

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_queries,
    ):
        _mock_auth(mock_verify, mock_db, mock_queries, user)

        response = client.patch(
            "/api/v1/me/language",
            json={"language": "fr"},
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 422
