"""Integration tests for auth API endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest


# Every endpoint that requires authentication. One parametrized test guards the
# whole surface — a new protected route only needs a line here, not a bespoke
# per-file "without_token" copy.
PROTECTED_ENDPOINTS = [
    ("GET", "/api/v1/me"),
    ("PATCH", "/api/v1/me/language"),
    ("GET", "/api/v1/brands"),
    ("GET", "/api/v1/brands/1"),
    ("GET", "/api/v1/accounts"),
    ("GET", "/api/v1/rules"),
    ("GET", "/api/v1/sync/status"),
    ("POST", "/api/v1/sync"),
    ("GET", "/api/v1/evaluations/42"),
    ("DELETE", "/api/v1/evaluations/42"),
    ("GET", "/api/v1/evaluations/brands/1"),
    ("POST", "/api/v1/evaluations/brands/1/score"),
    ("POST", "/api/v1/evaluations/brands/1/calculators/ads_keyword"),
    ("POST", "/api/v1/evaluations/brands/1/calculators/discount"),
    ("POST", "/api/v1/evaluations/brands/1/calculators/top_sku"),
    ("POST", "/api/v1/upload/signed-url"),
    ("GET", "/api/v1/upload/brands/123"),
    ("POST", "/api/v1/email/send"),
    ("POST", "/api/v1/email/send-plain"),
    ("GET", "/api/v1/email/preview/1"),
]


@pytest.mark.parametrize("method,path", PROTECTED_ENDPOINTS)
def test_protected_endpoint_rejects_missing_token(client, method, path):
    """Every protected endpoint returns 401 AUTH_TOKEN_MISSING without a token.

    Auth is enforced before request-body validation, so no payload is needed.
    """
    response = client.request(method, path)
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "AUTH_TOKEN_MISSING"
    assert data["detail"] == "Authorization header required"
    assert "timestamp" in data


def test_me_with_invalid_token(client):
    """Test /api/v1/me returns 401 with invalid token (both Firebase and OIDC fail)."""
    from app.core.exceptions import AuthException

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_firebase,
        patch("app.core.dependencies.verify_oidc_token") as mock_oidc,
    ):
        mock_firebase.side_effect = AuthException(code="AUTH_TOKEN_INVALID", detail="Token validation failed")
        mock_oidc.side_effect = AuthException(code="AUTH_TOKEN_INVALID", detail="OIDC token validation failed")

        response = client.get("/api/v1/me", headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "AUTH_TOKEN_INVALID"
        assert data["detail"] == "Token validation failed"


def test_me_with_valid_token_existing_user(client):
    """Test /api/v1/me returns user info for existing user and updates last_login."""
    initial_login = datetime.now(timezone.utc)
    updated_login = datetime.now(timezone.utc)

    mock_user_initial = {
        "id": 1,
        "firebase_uid": "test-uid",
        "email": "test@example.com",
        "role": "member",
        "created_at": datetime.now(timezone.utc),
        "last_login": initial_login,
    }
    mock_user_updated = {
        "id": 1,
        "firebase_uid": "test-uid",
        "email": "test@example.com",
        "role": "member",
        "created_at": datetime.now(timezone.utc),
        "last_login": updated_login,
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_queries,
    ):
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}

        # Mock database connection context manager
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn

        # First call returns initial user, second call (after update) returns updated user
        mock_queries.get_user_by_firebase_uid = AsyncMock(
            side_effect=[mock_user_initial, mock_user_updated]
        )
        mock_queries.update_last_login = AsyncMock()

        response = client.get("/api/v1/me", headers={"Authorization": "Bearer valid-token"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "test@example.com"
        assert data["role"] == "member"
        assert data["last_login"] is not None

        # Verify update_last_login was called with correct user ID
        mock_queries.update_last_login.assert_called_once_with(mock_conn, 1)

        # Verify get_user_by_firebase_uid was called twice (initial + re-fetch)
        assert mock_queries.get_user_by_firebase_uid.call_count == 2


def test_me_with_valid_token_new_user(client):
    """Test /api/v1/me creates new user on first login."""
    mock_new_user = {
        "id": 1,
        "firebase_uid": "new-uid",
        "email": "new@example.com",
        "role": "member",
        "created_at": datetime.now(timezone.utc),
        "last_login": datetime.now(timezone.utc),
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_queries,
    ):
        mock_verify.return_value = {"uid": "new-uid", "email": "new@example.com"}

        # Mock database connection context manager
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn

        # User doesn't exist, will be created
        mock_queries.get_user_by_firebase_uid = AsyncMock(return_value=None)
        mock_queries.create_user = AsyncMock(return_value=mock_new_user)

        response = client.get("/api/v1/me", headers={"Authorization": "Bearer valid-token"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "new@example.com"
        assert data["role"] == "member"

        # Verify create_user was called with correct arguments
        mock_queries.create_user.assert_called_once_with(mock_conn, "new-uid", "new@example.com")


def test_health_endpoint(client):
    """Test health endpoint is still accessible."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "checks" in data
