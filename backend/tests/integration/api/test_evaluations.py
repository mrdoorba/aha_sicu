"""Integration tests for evaluations API endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch


AUTH_HEADERS = {"Authorization": "Bearer valid-token"}

MOCK_USER = {
    "id": 1,
    "firebase_uid": "test-uid",
    "email": "test@example.com",
    "role": "member",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 5, tzinfo=timezone.utc),
}

SAMPLE_BRAND = {
    "id": 1,
    "brand_name": "Brand ABC",
    "raw_data": {"category": "Electronics"},
    "updated_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
    "meeting_raw_data": None,
}

SAMPLE_EVAL_INPUTS = {
    "id": 1,
    "brand_id": 1,
    "last_edited_by": 1,
    "category_type": "fashion",
    "manual_data": {"key": "value"},
    "created_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
}


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries):
    """Shared auth mock setup for all tests."""
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
    mock_user_queries.update_last_login = AsyncMock()


def test_get_evaluation_without_token(client):
    """Test GET /api/v1/evaluations/brands/1 returns 401 without token."""
    response = client.get("/api/v1/evaluations/brands/1")
    assert response.status_code == 401


def test_get_evaluation_new_state(client):
    """Test GET returns null state when no evaluation exists."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.get_evaluation_inputs = AsyncMock(return_value=None)

        response = client.get("/api/v1/evaluations/brands/1", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["brand_id"] == 1
        assert data["category_type"] is None
        assert data["manual_data"] is None
        assert data["updated_at"] is None


def test_get_evaluation_existing_state(client):
    """Test GET returns saved state when evaluation exists."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.get_evaluation_inputs = AsyncMock(return_value=SAMPLE_EVAL_INPUTS)

        response = client.get("/api/v1/evaluations/brands/1", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["brand_id"] == 1
        assert data["category_type"] == "fashion"
        assert data["manual_data"] == {"key": "value"}
        assert data["updated_at"] is not None


def test_put_evaluation_creates_new(client):
    """Test PUT creates new evaluation inputs."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.brand_queries") as mock_bq,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_bq.get_brand_by_id = AsyncMock(return_value=SAMPLE_BRAND)
        mock_eq.upsert_evaluation_inputs = AsyncMock(return_value=SAMPLE_EVAL_INPUTS)

        response = client.put(
            "/api/v1/evaluations/brands/1",
            json={"category_type": "fashion", "manual_data": {"key": "value"}},
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["brand_id"] == 1
        assert data["category_type"] == "fashion"


def test_put_evaluation_updates_existing(client):
    """Test PUT updates existing evaluation inputs."""
    updated_inputs = {
        **SAMPLE_EVAL_INPUTS,
        "category_type": "non_fashion",
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.brand_queries") as mock_bq,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_bq.get_brand_by_id = AsyncMock(return_value=SAMPLE_BRAND)
        mock_eq.upsert_evaluation_inputs = AsyncMock(return_value=updated_inputs)

        response = client.put(
            "/api/v1/evaluations/brands/1",
            json={"category_type": "non_fashion"},
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["category_type"] == "non_fashion"


def test_put_evaluation_brand_not_found(client):
    """Test PUT returns 404 when brand doesn't exist."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.brand_queries") as mock_bq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_bq.get_brand_by_id = AsyncMock(return_value=None)

        response = client.put(
            "/api/v1/evaluations/brands/999",
            json={"category_type": "fashion"},
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "BRAND_NOT_FOUND"
