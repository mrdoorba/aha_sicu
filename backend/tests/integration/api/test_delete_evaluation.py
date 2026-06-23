"""Integration tests for the delete evaluation endpoint."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

AUTH_HEADERS = {"Authorization": "Bearer valid-token"}

MOCK_LEADER = {
    "id": 1,
    "firebase_uid": "test-uid",
    "email": "leader@company.com",
    "role": "leader",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 5, tzinfo=timezone.utc),
}

MOCK_ADMIN = {
    "id": 2,
    "firebase_uid": "admin-uid",
    "email": "admin@company.com",
    "role": "admin",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 5, tzinfo=timezone.utc),
}

MOCK_MEMBER = {
    "id": 3,
    "firebase_uid": "member-uid",
    "email": "member@company.com",
    "role": "member",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 5, tzinfo=timezone.utc),
}


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries, mock_user):
    """Shared auth mock setup."""
    mock_verify.return_value = {"uid": mock_user["firebase_uid"], "email": mock_user["email"]}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=mock_user)
    mock_user_queries.update_last_login = AsyncMock()


def test_delete_evaluation_success_leader(client):
    """Test leader can delete evaluation — returns 204."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)
        mock_eq.get_evaluation_brand_info = AsyncMock(
            return_value={"brand_id": 1, "brand_name": "Test Brand"}
        )
        mock_eq.delete_evaluation = AsyncMock(return_value=True)
        mock_eq.count_evaluations_by_brand_id = AsyncMock(return_value=1)

        response = client.delete(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 204


def test_delete_evaluation_success_admin(client):
    """Test admin can delete evaluation — returns 204."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        mock_eq.get_evaluation_brand_info = AsyncMock(
            return_value={"brand_id": 1, "brand_name": "Test Brand"}
        )
        mock_eq.delete_evaluation = AsyncMock(return_value=True)
        mock_eq.count_evaluations_by_brand_id = AsyncMock(return_value=1)

        response = client.delete(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 204


def test_delete_evaluation_forbidden_member(client):
    """Test member cannot delete evaluation — returns 403."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries, MOCK_MEMBER)

        response = client.delete(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "RULE_ACCESS_DENIED"


def test_delete_evaluation_not_found(client):
    """Test deleting non-existent evaluation returns 404."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)
        mock_eq.get_evaluation_brand_info = AsyncMock(return_value=None)
        mock_eq.delete_evaluation = AsyncMock(return_value=False)

        response = client.delete(
            "/api/v1/evaluations/99999",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "EVAL_NOT_FOUND"


def test_delete_evaluation_cleans_up_email_history(client):
    """Test that linked email history rows are deleted before the evaluation."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
        patch("app.modules.evaluations.service.email_history_queries") as mock_ehq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)
        mock_eq.get_evaluation_brand_info = AsyncMock(
            return_value={"brand_id": 1, "brand_name": "Salt"}
        )
        mock_eq.delete_evaluation = AsyncMock(return_value=True)
        mock_eq.count_evaluations_by_brand_id = AsyncMock(return_value=1)
        mock_ehq.list_email_history_by_evaluation = AsyncMock(
            return_value=[{"id": 10}, {"id": 11}]
        )
        mock_ehq.delete_email_history_by_ids = AsyncMock(return_value=2)

        response = client.delete(
            "/api/v1/evaluations/86",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 204
        mock_ehq.delete_email_history_by_ids.assert_awaited_once()
        _, kwargs = mock_ehq.delete_email_history_by_ids.await_args
        assert kwargs["ids"] == [10, 11]
