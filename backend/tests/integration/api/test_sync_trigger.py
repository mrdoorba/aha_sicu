"""Integration tests for POST /api/v1/sync trigger endpoint."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.sync.schemas import SyncResult, SyncStatusResponse


# --- Task 5: Integration tests for POST /api/v1/sync ---

MOCK_USER_ADMIN = {
    "id": 1,
    "firebase_uid": "test-uid",
    "email": "test@example.com",
    "role": "admin",
    "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    "last_login": datetime(2026, 1, 1, tzinfo=timezone.utc),
}

MOCK_USER_MEMBER = {
    "id": 2,
    "firebase_uid": "member-uid",
    "email": "member@example.com",
    "role": "member",
    "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    "last_login": datetime(2026, 1, 1, tzinfo=timezone.utc),
}

MOCK_USER_LEADER = {
    "id": 3,
    "firebase_uid": "leader-uid",
    "email": "leader@example.com",
    "role": "leader",
    "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    "last_login": datetime(2026, 1, 1, tzinfo=timezone.utc),
}

MOCK_SYNC_STATUS = SyncStatusResponse(
    id=99,
    last_sync=datetime(2026, 2, 6, 10, 0, 5, tzinfo=timezone.utc),
    status="success",
    started_at=datetime(2026, 2, 6, 10, 0, 0, tzinfo=timezone.utc),
    completed_at=datetime(2026, 2, 6, 10, 0, 5, tzinfo=timezone.utc),
    brands_synced=42,
    error_message=None,
    sync_details=None,
)


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


def test_post_sync_returns_200_with_sync_status(client):
    """POST /api/v1/sync returns 200 with SyncStatusResponse after sync completes."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_auth_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.router.db") as mock_router_db,
        patch("app.modules.sync.router.is_sync_in_progress") as mock_in_progress,
        patch("app.modules.sync.router.sync_queries") as mock_sync_queries,
        patch("app.modules.sync.router.run_sync") as mock_run_sync,
        patch("app.modules.sync.router.get_latest_sync_status") as mock_get_status,
    ):
        # Auth mocks
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_auth_conn = AsyncMock()
        mock_auth_db.connection.return_value.__aenter__.return_value = mock_auth_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER_ADMIN)
        mock_user_queries.update_last_login = AsyncMock()

        # Router db mock (with transaction + advisory lock support)
        mock_router_conn = AsyncMock()
        mock_router_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn

        # Sync mocks
        mock_in_progress.return_value = False
        mock_sync_queries.create_sync_status = AsyncMock(return_value=99)
        mock_run_sync.return_value = SyncResult(
            sync_id=99,
            vp_result=None,
            meeting_result=None,
            total_synced=42,
            total_errors=0,
            success=True,
        )
        mock_get_status.return_value = MOCK_SYNC_STATUS

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 99
        assert data["status"] == "success"
        assert data["brands_synced"] == 42
        assert data["completed_at"] is not None
        mock_run_sync.assert_awaited_once_with(sync_id=99)


def test_post_sync_returns_200_with_failed_status_on_sync_error(client):
    """POST /api/v1/sync returns 200 with status 'failed' when sync encounters errors."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_auth_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.router.db") as mock_router_db,
        patch("app.modules.sync.router.is_sync_in_progress") as mock_in_progress,
        patch("app.modules.sync.router.sync_queries") as mock_sync_queries,
        patch("app.modules.sync.router.run_sync") as mock_run_sync,
        patch("app.modules.sync.router.get_latest_sync_status") as mock_get_status,
    ):
        # Auth mocks
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_auth_conn = AsyncMock()
        mock_auth_db.connection.return_value.__aenter__.return_value = mock_auth_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER_ADMIN)
        mock_user_queries.update_last_login = AsyncMock()

        # Router db mock
        mock_router_conn = AsyncMock()
        mock_router_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn

        # Sync fails (e.g. Google Sheets API error caught inside run_sync)
        mock_in_progress.return_value = False
        mock_sync_queries.create_sync_status = AsyncMock(return_value=99)
        mock_run_sync.return_value = SyncResult(
            sync_id=99,
            vp_result=None,
            meeting_result=None,
            total_synced=0,
            total_errors=1,
            success=False,
        )
        mock_get_status.return_value = SyncStatusResponse(
            id=99,
            last_sync=datetime(2026, 2, 6, 10, 0, 5, tzinfo=timezone.utc),
            status="failed",
            started_at=datetime(2026, 2, 6, 10, 0, 0, tzinfo=timezone.utc),
            completed_at=datetime(2026, 2, 6, 10, 0, 5, tzinfo=timezone.utc),
            brands_synced=0,
            error_message="VP: Google Sheets API error",
            sync_details=None,
        )

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error_message"] == "VP: Google Sheets API error"
        assert data["brands_synced"] == 0


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
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER_ADMIN)
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
    """POST /api/v1/sync returns 401 with invalid token (both Firebase and OIDC fail)."""
    from app.core.exceptions import AuthException

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_firebase,
        patch("app.core.dependencies.verify_oidc_token") as mock_oidc,
    ):
        mock_firebase.side_effect = AuthException(
            code="AUTH_TOKEN_INVALID", detail="Token validation failed"
        )
        mock_oidc.side_effect = AuthException(
            code="AUTH_TOKEN_INVALID", detail="OIDC token validation failed"
        )

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "AUTH_TOKEN_INVALID"


def test_post_sync_with_oidc_token_returns_200(client):
    """POST /api/v1/sync returns 200 when authenticated via OIDC (scheduler path)."""
    from app.core.exceptions import AuthException

    scheduler_email = "aha-coms-sicu-dev-sched-sa@project.iam.gserviceaccount.com"

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_firebase,
        patch("app.core.dependencies.verify_oidc_token") as mock_oidc,
        patch("app.core.dependencies.settings") as mock_settings,
        patch("app.modules.sync.router.db") as mock_router_db,
        patch("app.modules.sync.router.is_sync_in_progress") as mock_in_progress,
        patch("app.modules.sync.router.sync_queries") as mock_sync_queries,
        patch("app.modules.sync.router.run_sync") as mock_run_sync,
        patch("app.modules.sync.router.get_latest_sync_status") as mock_get_status,
    ):
        # Firebase fails — this is a scheduler request
        mock_firebase.side_effect = AuthException(
            code="AUTH_TOKEN_INVALID", detail="Token validation failed"
        )
        # OIDC succeeds
        mock_oidc.return_value = {
            "email": scheduler_email,
            "issuer": "https://accounts.google.com",
        }
        # Allowlist includes the scheduler email (fail-closed requires this)
        mock_settings.allowed_scheduler_emails = scheduler_email

        # Router db mock (with transaction + advisory lock support)
        mock_router_conn = AsyncMock()
        mock_router_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn

        # Sync mocks
        mock_in_progress.return_value = False
        mock_sync_queries.create_sync_status = AsyncMock(return_value=100)
        mock_run_sync.return_value = SyncResult(
            sync_id=100,
            vp_result=None,
            meeting_result=None,
            total_synced=0,
            total_errors=0,
            success=True,
        )
        mock_get_status.return_value = SyncStatusResponse(
            id=100,
            last_sync=datetime(2026, 2, 6, 10, 0, 5, tzinfo=timezone.utc),
            status="success",
            started_at=datetime(2026, 2, 6, 10, 0, 0, tzinfo=timezone.utc),
            completed_at=datetime(2026, 2, 6, 10, 0, 5, tzinfo=timezone.utc),
            brands_synced=0,
            error_message=None,
            sync_details=None,
        )

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer oidc-scheduler-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 100
        assert data["status"] == "success"
        mock_run_sync.assert_awaited_once()


def test_post_sync_oidc_rejected_when_email_not_in_allowlist(client):
    """POST /api/v1/sync returns 401 when OIDC email is not in scheduler allowlist."""
    from app.core.exceptions import AuthException

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_firebase,
        patch("app.core.dependencies.verify_oidc_token") as mock_oidc,
        patch("app.core.dependencies.settings") as mock_settings,
    ):
        mock_firebase.side_effect = AuthException(
            code="AUTH_TOKEN_INVALID", detail="Token validation failed"
        )
        mock_oidc.return_value = {
            "email": "unauthorized-sa@project.iam.gserviceaccount.com",
            "issuer": "https://accounts.google.com",
        }
        mock_settings.allowed_scheduler_emails = "aha-coms-sicu-dev-sched-sa@project.iam.gserviceaccount.com"

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer oidc-token"},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "AUTH_TOKEN_INVALID"
        assert data["detail"] == "Service account not authorized"


def test_post_sync_oidc_skips_db_user_lookup(client):
    """POST /api/v1/sync with OIDC token does NOT query the users table."""
    from app.core.exceptions import AuthException

    scheduler_email = "aha-coms-sicu-dev-sched-sa@project.iam.gserviceaccount.com"

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_firebase,
        patch("app.core.dependencies.verify_oidc_token") as mock_oidc,
        patch("app.core.dependencies.settings") as mock_settings,
        patch("app.core.dependencies.db") as mock_auth_db,  # noqa: F841
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.router.db") as mock_router_db,
        patch("app.modules.sync.router.is_sync_in_progress") as mock_in_progress,
        patch("app.modules.sync.router.sync_queries") as mock_sync_queries,
        patch("app.modules.sync.router.run_sync") as mock_run_sync,
        patch("app.modules.sync.router.get_latest_sync_status") as mock_get_status,
    ):
        # Firebase fails, OIDC succeeds
        mock_firebase.side_effect = AuthException(
            code="AUTH_TOKEN_INVALID", detail="Token validation failed"
        )
        mock_oidc.return_value = {
            "email": scheduler_email,
            "issuer": "https://accounts.google.com",
        }
        mock_settings.allowed_scheduler_emails = scheduler_email

        # Router db mock
        mock_router_conn = AsyncMock()
        mock_router_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn

        mock_in_progress.return_value = False
        mock_sync_queries.create_sync_status = AsyncMock(return_value=101)
        mock_run_sync.return_value = SyncResult(
            sync_id=101,
            vp_result=None,
            meeting_result=None,
            total_synced=0,
            total_errors=0,
            success=True,
        )
        mock_get_status.return_value = SyncStatusResponse(
            id=101,
            last_sync=datetime(2026, 2, 6, 10, 0, 5, tzinfo=timezone.utc),
            status="success",
            started_at=datetime(2026, 2, 6, 10, 0, 0, tzinfo=timezone.utc),
            completed_at=datetime(2026, 2, 6, 10, 0, 5, tzinfo=timezone.utc),
            brands_synced=0,
            error_message=None,
            sync_details=None,
        )

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer oidc-scheduler-token"},
        )

        assert response.status_code == 200
        # Verify no user DB queries were made
        mock_user_queries.get_user_by_firebase_uid.assert_not_called()
        mock_user_queries.create_user.assert_not_called()


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
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER_ADMIN)
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


def test_sync_returns_403_when_member_role(client):
    """POST /api/v1/sync returns 403 when user has member role (not authorized)."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_auth_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        mock_verify.return_value = {"uid": "member-uid", "email": "member@example.com"}
        mock_auth_conn = AsyncMock()
        mock_auth_db.connection.return_value.__aenter__.return_value = mock_auth_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER_MEMBER)
        mock_user_queries.update_last_login = AsyncMock()

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer member-token"},
        )

        assert response.status_code == 403


def test_sync_returns_200_when_admin_role(client):
    """POST /api/v1/sync returns 200 when user has admin role."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_auth_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.router.db") as mock_router_db,
        patch("app.modules.sync.router.is_sync_in_progress") as mock_in_progress,
        patch("app.modules.sync.router.sync_queries") as mock_sync_queries,
        patch("app.modules.sync.router.run_sync") as mock_run_sync,
        patch("app.modules.sync.router.get_latest_sync_status") as mock_get_status,
    ):
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_auth_conn = AsyncMock()
        mock_auth_db.connection.return_value.__aenter__.return_value = mock_auth_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER_ADMIN)
        mock_user_queries.update_last_login = AsyncMock()

        mock_router_conn = AsyncMock()
        mock_router_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn

        mock_in_progress.return_value = False
        mock_sync_queries.create_sync_status = AsyncMock(return_value=200)
        mock_run_sync.return_value = SyncResult(
            sync_id=200, vp_result=None, meeting_result=None,
            total_synced=10, total_errors=0, success=True,
        )
        mock_get_status.return_value = MOCK_SYNC_STATUS

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer admin-token"},
        )

        assert response.status_code == 200


def test_sync_returns_200_when_leader_role(client):
    """POST /api/v1/sync returns 200 when user has leader role."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_auth_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.sync.router.db") as mock_router_db,
        patch("app.modules.sync.router.is_sync_in_progress") as mock_in_progress,
        patch("app.modules.sync.router.sync_queries") as mock_sync_queries,
        patch("app.modules.sync.router.run_sync") as mock_run_sync,
        patch("app.modules.sync.router.get_latest_sync_status") as mock_get_status,
    ):
        mock_verify.return_value = {"uid": "leader-uid", "email": "leader@example.com"}
        mock_auth_conn = AsyncMock()
        mock_auth_db.connection.return_value.__aenter__.return_value = mock_auth_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER_LEADER)
        mock_user_queries.update_last_login = AsyncMock()

        mock_router_conn = AsyncMock()
        mock_router_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn

        mock_in_progress.return_value = False
        mock_sync_queries.create_sync_status = AsyncMock(return_value=201)
        mock_run_sync.return_value = SyncResult(
            sync_id=201, vp_result=None, meeting_result=None,
            total_synced=5, total_errors=0, success=True,
        )
        mock_get_status.return_value = MOCK_SYNC_STATUS

        response = client.post(
            "/api/v1/sync",
            headers={"Authorization": "Bearer leader-token"},
        )

        assert response.status_code == 200
