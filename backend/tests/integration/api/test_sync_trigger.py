"""Integration tests for POST /api/v1/sync trigger endpoint."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.sync.schemas import SyncTriggerResponse


# --- Task 2: Schema validation tests ---


def test_sync_trigger_response_schema():
    """SyncTriggerResponse schema has correct fields."""
    resp = SyncTriggerResponse(status="started", sync_id=42)
    assert resp.status == "started"
    assert resp.sync_id == 42


# --- Task 5: Integration tests for POST /api/v1/sync ---

MOCK_USER = {
    "id": 1,
    "firebase_uid": "test-uid",
    "email": "test@example.com",
    "role": "member",
    "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    "last_login": datetime(2026, 1, 1, tzinfo=timezone.utc),
}


def _auth_mocks():
    """Return common auth mock context managers."""
    return (
        patch("app.core.dependencies.verify_firebase_token"),
        patch("app.core.dependencies.db"),
        patch("app.core.dependencies.user_queries"),
    )


def test_post_sync_requires_authentication(client):
    """POST /api/v1/sync returns 401 without Authorization header."""
    response = client.post("/api/v1/sync")
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "AUTH_TOKEN_MISSING"


def test_post_sync_returns_202_with_sync_id(client):
    """POST /api/v1/sync returns 202 Accepted with sync_id when no sync in progress."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_auth_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.router.db") as mock_router_db,
        patch("app.modules.sync.router.is_sync_in_progress") as mock_in_progress,
        patch("app.modules.sync.router.sync_queries") as mock_sync_queries,
        patch("app.modules.sync.router.run_sync") as mock_run_sync,
    ):
        # Auth mocks
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_auth_conn = AsyncMock()
        mock_auth_db.connection.return_value.__aenter__.return_value = mock_auth_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
        mock_user_queries.update_last_login = AsyncMock()

        # Router db mock (with transaction + advisory lock support)
        mock_router_conn = AsyncMock()
        mock_router_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn

        # Sync mocks
        mock_in_progress.return_value = False
        mock_sync_queries.create_sync_status = AsyncMock(return_value=99)

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "started"
        assert data["sync_id"] == 99


def test_post_sync_returns_409_when_sync_in_progress(client):
    """POST /api/v1/sync returns 409 Conflict when a sync is already running."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_auth_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.router.db") as mock_router_db,
        patch("app.modules.sync.router.is_sync_in_progress") as mock_in_progress,
    ):
        # Auth mocks
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_auth_conn = AsyncMock()
        mock_auth_db.connection.return_value.__aenter__.return_value = mock_auth_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
        mock_user_queries.update_last_login = AsyncMock()

        # Router db mock (with transaction + advisory lock support)
        mock_router_conn = AsyncMock()
        mock_router_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn

        # Sync in progress
        mock_in_progress.return_value = True

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 409
        data = response.json()
        assert data["code"] == "SYNC_IN_PROGRESS"
        assert data["detail"] == "A sync is already running"
        assert "timestamp" in data


def test_post_sync_with_invalid_token(client):
    """POST /api/v1/sync returns 401 with invalid token."""
    with patch("app.core.dependencies.verify_firebase_token") as mock_verify:
        from app.core.exceptions import AuthException

        mock_verify.side_effect = AuthException(
            code="AUTH_TOKEN_INVALID", detail="Token validation failed"
        )

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "AUTH_TOKEN_INVALID"


def test_get_sync_status_after_trigger(client):
    """GET /api/v1/sync/status returns updated status reflecting sync state."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.service.db") as mock_sync_db,
        patch("app.modules.sync.service.sync_queries") as mock_sync_queries,
    ):
        # Auth mocks
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
        mock_user_queries.update_last_login = AsyncMock()

        # Mock in-progress sync status (sync was triggered, not yet complete)
        mock_sync_conn = AsyncMock()
        mock_sync_db.connection.return_value.__aenter__.return_value = mock_sync_conn
        mock_sync_queries.get_latest_sync_status = AsyncMock(
            return_value={
                "id": 99,
                "started_at": datetime(2026, 2, 6, 10, 0, 0, tzinfo=timezone.utc),
                "completed_at": None,
                "success": None,
                "brands_synced": 0,
                "error_message": None,
                "sync_details": None,
            }
        )

        response = client.get(
            "/api/v1/sync/status",
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 99
        assert data["completed_at"] is None
        assert data["status"] == "in_progress"
        assert data["last_sync"] is not None
