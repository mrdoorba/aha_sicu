"""Integration tests for sync API endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch



def test_sync_status_with_invalid_token(client):
    """Test /api/v1/sync/status returns 401 with invalid token (both Firebase and OIDC fail)."""
    from app.core.exceptions import AuthException

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_firebase,
        patch("app.core.dependencies.verify_oidc_token") as mock_oidc,
    ):
        mock_firebase.side_effect = AuthException(code="AUTH_TOKEN_INVALID", detail="Token validation failed")
        mock_oidc.side_effect = AuthException(code="AUTH_TOKEN_INVALID", detail="OIDC token validation failed")

        response = client.get("/api/v1/sync/status", headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "AUTH_TOKEN_INVALID"


def test_sync_status_returns_latest_sync(client):
    """Test /api/v1/sync/status returns the most recent sync status."""
    mock_user = {
        "id": 1,
        "firebase_uid": "test-uid",
        "email": "test@example.com",
        "role": "member",
        "created_at": datetime.now(timezone.utc),
        "last_login": datetime.now(timezone.utc),
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.service.db") as mock_sync_db,
        patch("app.modules.sync.service.sync_queries") as mock_sync_queries,
    ):
        # Mock auth
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=mock_user)
        mock_user_queries.update_last_login = AsyncMock()

        # Mock sync status
        mock_sync_conn = AsyncMock()
        mock_sync_db.connection.return_value.__aenter__.return_value = mock_sync_conn
        mock_sync_queries.get_latest_sync_status = AsyncMock(
            return_value={
                "id": 5,
                "started_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
                "completed_at": datetime(2026, 2, 5, 10, 5, 0, tzinfo=timezone.utc),
                "success": True,
                "brands_synced": 150,
                "error_message": None,
            }
        )

        response = client.get("/api/v1/sync/status", headers={"Authorization": "Bearer valid-token"})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 5
        assert data["status"] == "success"
        assert data["last_sync"] is not None
        assert data["brands_synced"] == 150
        assert data["error_message"] is None


def test_sync_status_returns_null_when_no_syncs(client):
    """Test /api/v1/sync/status returns null when no syncs exist."""
    mock_user = {
        "id": 1,
        "firebase_uid": "test-uid",
        "email": "test@example.com",
        "role": "member",
        "created_at": datetime.now(timezone.utc),
        "last_login": datetime.now(timezone.utc),
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.service.db") as mock_sync_db,
        patch("app.modules.sync.service.sync_queries") as mock_sync_queries,
    ):
        # Mock auth
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=mock_user)
        mock_user_queries.update_last_login = AsyncMock()

        # Mock no sync status
        mock_sync_conn = AsyncMock()
        mock_sync_db.connection.return_value.__aenter__.return_value = mock_sync_conn
        mock_sync_queries.get_latest_sync_status = AsyncMock(return_value=None)

        response = client.get("/api/v1/sync/status", headers={"Authorization": "Bearer valid-token"})

        assert response.status_code == 200
        assert response.json() is None


def test_sync_status_returns_failed_sync(client):
    """Test /api/v1/sync/status correctly returns failed sync with error message."""
    mock_user = {
        "id": 1,
        "firebase_uid": "test-uid",
        "email": "test@example.com",
        "role": "member",
        "created_at": datetime.now(timezone.utc),
        "last_login": datetime.now(timezone.utc),
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.service.db") as mock_sync_db,
        patch("app.modules.sync.service.sync_queries") as mock_sync_queries,
    ):
        # Mock auth
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=mock_user)
        mock_user_queries.update_last_login = AsyncMock()

        # Mock failed sync status
        mock_sync_conn = AsyncMock()
        mock_sync_db.connection.return_value.__aenter__.return_value = mock_sync_conn
        mock_sync_queries.get_latest_sync_status = AsyncMock(
            return_value={
                "id": 3,
                "started_at": datetime(2026, 2, 5, 9, 0, 0, tzinfo=timezone.utc),
                "completed_at": datetime(2026, 2, 5, 9, 1, 0, tzinfo=timezone.utc),
                "success": False,
                "brands_synced": 0,
                "error_message": "Connection timeout",
            }
        )

        response = client.get("/api/v1/sync/status", headers={"Authorization": "Bearer valid-token"})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 3
        assert data["status"] == "failed"
        assert data["last_sync"] is not None
        assert data["brands_synced"] == 0
        assert data["error_message"] == "Connection timeout"
