"""Integration tests for accounts API endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

AUTH_HEADERS = {"Authorization": "Bearer valid-token"}

MOCK_ADMIN = {
    "id": 1,
    "firebase_uid": "admin-uid",
    "email": "admin@company.com",
    "role": "admin",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 20, tzinfo=timezone.utc),
}

MOCK_MEMBER = {
    "id": 2,
    "firebase_uid": "member-uid",
    "email": "member@company.com",
    "role": "member",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 20, tzinfo=timezone.utc),
}

MOCK_LEADER = {
    "id": 3,
    "firebase_uid": "leader-uid",
    "email": "leader@company.com",
    "role": "leader",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 20, tzinfo=timezone.utc),
}

SAMPLE_USERS = [
    {
        "id": 1,
        "email": "admin@company.com",
        "role": "admin",
        "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
        "last_login": datetime(2026, 2, 20, tzinfo=timezone.utc),
    },
    {
        "id": 2,
        "email": "member@company.com",
        "role": "member",
        "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
        "last_login": None,
    },
]


def _setup_auth(mock_verify, mock_db, mock_user_queries, user):
    """Setup auth mocks for a given user."""
    mock_verify.return_value = {"uid": user["firebase_uid"], "email": user["email"]}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=user)
    mock_user_queries.update_last_login = AsyncMock()


# --- LIST ---


def test_list_accounts_admin_success(client):
    """Admin can list all accounts."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.accounts.service.db") as mock_svc_db,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetch = AsyncMock(return_value=SAMPLE_USERS)

        response = client.get("/api/v1/accounts", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["email"] == "admin@company.com"


def test_list_accounts_member_forbidden(client):
    """Member cannot list accounts — 403."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_MEMBER)
        response = client.get("/api/v1/accounts", headers=AUTH_HEADERS)
        assert response.status_code == 403


def test_list_accounts_leader_forbidden(client):
    """Leader cannot list accounts — 403."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)
        response = client.get("/api/v1/accounts", headers=AUTH_HEADERS)
        assert response.status_code == 403


def test_list_accounts_unauthorized(client):
    """No auth token — 401."""
    response = client.get("/api/v1/accounts")
    assert response.status_code == 401


# --- CREATE ---


def test_create_account_success(client):
    """Admin can create a new account."""
    new_user = {
        "id": 10,
        "email": "new@company.com",
        "role": "member",
        "created_at": datetime(2026, 2, 20, tzinfo=timezone.utc),
        "last_login": None,
    }
    mock_firebase_user = MagicMock()
    mock_firebase_user.uid = "new-firebase-uid"

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.accounts.service.db") as mock_svc_db,
        patch("app.modules.accounts.service.auth") as mock_auth,
        patch("app.modules.accounts.router._audit", new_callable=AsyncMock) as mock_audit,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_auth.create_user = MagicMock(return_value=mock_firebase_user)
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=new_user)

        response = client.post(
            "/api/v1/accounts",
            json={"email": "new@company.com", "password": "secret123", "role": "member"},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@company.com"
        assert data["role"] == "member"

        mock_audit.assert_called_once_with(
            "account.create",
            MOCK_ADMIN,
            "user",
            "10",
            details={"email": "new@company.com", "role": "member"},
        )


def test_create_account_duplicate_email(client):
    """Creating account with existing email — 409."""
    from firebase_admin import auth as firebase_auth

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.accounts.service.auth") as mock_auth,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_auth.create_user = MagicMock(
            side_effect=firebase_auth.EmailAlreadyExistsError(
                message="Email exists", cause=None, http_response=None
            )
        )
        mock_auth.EmailAlreadyExistsError = firebase_auth.EmailAlreadyExistsError

        response = client.post(
            "/api/v1/accounts",
            json={"email": "dup@company.com", "password": "secret123", "role": "member"},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 409
        assert response.json()["code"] == "ACCOUNT_EMAIL_EXISTS"


def test_create_account_short_password(client):
    """Password shorter than 6 chars — 422."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        response = client.post(
            "/api/v1/accounts",
            json={"email": "user@company.com", "password": "short", "role": "member"},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 422


# --- UPDATE ROLE ---


def test_update_role_success(client):
    """Admin can update another user's role."""
    updated_user = {**SAMPLE_USERS[1], "role": "leader"}

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.accounts.service.db") as mock_svc_db,
        patch("app.modules.accounts.router.db") as mock_router_db,
        patch("app.modules.accounts.router._audit", new_callable=AsyncMock) as mock_audit,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=updated_user)

        # Mock router's old-role fetch
        mock_router_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn
        mock_router_conn.fetchrow = AsyncMock(return_value=MOCK_MEMBER)

        response = client.patch(
            "/api/v1/accounts/2/role",
            json={"role": "leader"},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 200
        assert response.json()["role"] == "leader"

        mock_audit.assert_called_once_with(
            "account.role_change",
            MOCK_ADMIN,
            "user",
            "2",
            details={"old_role": "member", "new_role": "leader"},
        )


def test_update_own_role_blocked(client):
    """Admin cannot update their own role — 409."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        response = client.patch(
            "/api/v1/accounts/1/role",
            json={"role": "member"},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 409
        assert response.json()["code"] == "ACCOUNT_SELF_ACTION"


def test_update_role_invalid_value(client):
    """Invalid role value — 422."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        response = client.patch(
            "/api/v1/accounts/2/role",
            json={"role": "superadmin"},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 422


# --- RESET PASSWORD ---


def test_reset_password_success(client):
    """Admin can reset another user's password."""
    target_user = {**SAMPLE_USERS[1], "firebase_uid": "member-uid"}

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.accounts.service.db") as mock_svc_db,
        patch("app.modules.accounts.service.auth") as mock_auth,
        patch("app.modules.accounts.router._audit", new_callable=AsyncMock) as mock_audit,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=target_user)
        mock_auth.update_user = MagicMock()

        response = client.post(
            "/api/v1/accounts/2/reset-password",
            json={"password": "newpassword123"},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 204

        mock_audit.assert_called_once_with(
            "account.password_reset",
            MOCK_ADMIN,
            "user",
            "2",
        )


def test_reset_own_password_blocked(client):
    """Admin cannot reset their own password — 409."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        response = client.post(
            "/api/v1/accounts/1/reset-password",
            json={"password": "newpassword123"},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 409
        assert response.json()["code"] == "ACCOUNT_SELF_ACTION"


# --- DELETE ---


def test_delete_account_success(client):
    """Admin can delete another user's account."""
    from firebase_admin import auth as firebase_auth

    target_user = {**SAMPLE_USERS[1], "firebase_uid": "member-uid"}

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.accounts.service.db") as mock_svc_db,
        patch("app.modules.accounts.service.auth") as mock_auth,
        patch("app.modules.accounts.router.db") as mock_router_db,
        patch("app.modules.accounts.router._audit", new_callable=AsyncMock) as mock_audit,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_svc_conn.fetchrow = AsyncMock(return_value=target_user)
        mock_svc_conn.execute = AsyncMock(return_value="DELETE 1")
        mock_auth.delete_user = MagicMock()
        mock_auth.UserNotFoundError = firebase_auth.UserNotFoundError

        # Mock router's pre-delete user fetch
        mock_router_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn
        mock_router_conn.fetchrow = AsyncMock(return_value=target_user)

        response = client.delete(
            "/api/v1/accounts/2",
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 204

        mock_audit.assert_called_once_with(
            "account.delete",
            MOCK_ADMIN,
            "user",
            "2",
            details={"email": "member@company.com", "role": "member"},
        )


def test_delete_account_firebase_failure_returns_502(client):
    """Firebase deletion failure → 502, DB deletion rolled back."""
    from firebase_admin import auth as firebase_auth

    target_user = {**SAMPLE_USERS[1], "firebase_uid": "member-uid"}

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.accounts.service.db") as mock_svc_db,
        patch("app.modules.accounts.service.auth") as mock_auth,
        patch("app.modules.accounts.router.db") as mock_router_db,
        patch("app.modules.accounts.router._audit", new_callable=AsyncMock),
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_svc_conn.fetchrow = AsyncMock(return_value=target_user)
        mock_svc_conn.execute = AsyncMock(return_value="DELETE 1")
        mock_auth.delete_user = MagicMock(
            side_effect=Exception("INSUFFICIENT_PERMISSION")
        )
        mock_auth.UserNotFoundError = firebase_auth.UserNotFoundError

        mock_router_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn
        mock_router_conn.fetchrow = AsyncMock(return_value=target_user)

        response = client.delete(
            "/api/v1/accounts/2",
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 502
        assert response.json()["code"] == "FIREBASE_DELETE_FAILED"


def test_delete_account_succeeds_when_firebase_user_absent(client):
    """Deleting account where Firebase user is already gone — still 204."""
    from firebase_admin import auth as firebase_auth

    target_user = {**SAMPLE_USERS[1], "firebase_uid": "orphan-uid"}

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.accounts.service.db") as mock_svc_db,
        patch("app.modules.accounts.service.auth") as mock_auth,
        patch("app.modules.accounts.router.db") as mock_router_db,
        patch("app.modules.accounts.router._audit", new_callable=AsyncMock),
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_svc_conn.fetchrow = AsyncMock(return_value=target_user)
        mock_svc_conn.execute = AsyncMock(return_value="DELETE 1")
        mock_auth.delete_user = MagicMock(
            side_effect=firebase_auth.UserNotFoundError("user not found")
        )
        mock_auth.UserNotFoundError = firebase_auth.UserNotFoundError

        mock_router_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn
        mock_router_conn.fetchrow = AsyncMock(return_value=target_user)

        response = client.delete(
            "/api/v1/accounts/2",
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 204


def test_delete_own_account_blocked(client):
    """Admin cannot delete their own account — 409."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        response = client.delete(
            "/api/v1/accounts/1",
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 409
        assert response.json()["code"] == "ACCOUNT_SELF_ACTION"


def test_delete_account_not_found(client):
    """Deleting non-existent account — 404."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.accounts.service.db") as mock_svc_db,
        patch("app.modules.accounts.router.db") as mock_router_db,
        patch("app.modules.accounts.router._audit", new_callable=AsyncMock),
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=None)

        mock_router_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn
        mock_router_conn.fetchrow = AsyncMock(return_value=None)

        response = client.delete(
            "/api/v1/accounts/999",
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 404
        assert response.json()["code"] == "ACCOUNT_NOT_FOUND"


def test_delete_account_member_forbidden(client):
    """Member cannot delete accounts — 403."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_MEMBER)
        response = client.delete(
            "/api/v1/accounts/2",
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 403


# --- AUDIT RESILIENCE (AC-7) ---


def test_create_account_succeeds_when_audit_fails(client):
    """Mutation succeeds even when audit INSERT fails (AC-7)."""
    new_user = {
        "id": 10,
        "email": "new@company.com",
        "role": "member",
        "created_at": datetime(2026, 2, 20, tzinfo=timezone.utc),
        "last_login": None,
    }
    mock_firebase_user = MagicMock()
    mock_firebase_user.uid = "new-firebase-uid"

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.accounts.service.db") as mock_svc_db,
        patch("app.modules.accounts.service.auth") as mock_auth,
        patch("app.modules.accounts.router.db") as mock_router_db,
        patch(
            "app.modules.accounts.router.record_audit_event",
            new_callable=AsyncMock,
            side_effect=Exception("DB connection failed"),
        ),
    ):
        _setup_auth(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_auth.create_user = MagicMock(return_value=mock_firebase_user)
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=new_user)

        # Mock router's audit connection
        mock_router_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_router_conn

        response = client.post(
            "/api/v1/accounts",
            json={"email": "new@company.com", "password": "secret123", "role": "member"},
            headers=AUTH_HEADERS,
        )
        # Mutation succeeds despite audit failure
        assert response.status_code == 201
        assert response.json()["email"] == "new@company.com"
