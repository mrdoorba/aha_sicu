"""Integration tests for brand detail API endpoint."""

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
    "meeting_raw_data": {"notes": "Good meeting"},
}


def test_brand_detail_without_token(client):
    """Test GET /api/v1/brands/1 returns 401 without Authorization header."""
    response = client.get("/api/v1/brands/1")
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "AUTH_TOKEN_MISSING"


def test_brand_detail_returns_brand_with_meeting(client):
    """Test GET /api/v1/brands/1 returns brand with meeting data."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.brands.service.db") as mock_brands_db,
    ):
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
        mock_user_queries.update_last_login = AsyncMock()

        mock_brands_conn = AsyncMock()
        mock_brands_db.connection.return_value.__aenter__.return_value = mock_brands_conn
        mock_brands_conn.fetchrow = AsyncMock(return_value=SAMPLE_BRAND)

        response = client.get("/api/v1/brands/1", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["brand_name"] == "Brand ABC"
        assert data["raw_data"] == {"category": "Electronics"}
        assert data["meeting_raw_data"] == {"notes": "Good meeting"}


def test_brand_detail_without_meeting_data(client):
    """Test GET /api/v1/brands/2 returns brand without meeting data."""
    brand_no_meeting = {
        "id": 2,
        "brand_name": "Brand DEF",
        "raw_data": {"category": "Fashion"},
        "updated_at": datetime(2026, 2, 5, 11, 0, 0, tzinfo=timezone.utc),
        "meeting_raw_data": None,
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.brands.service.db") as mock_brands_db,
    ):
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
        mock_user_queries.update_last_login = AsyncMock()

        mock_brands_conn = AsyncMock()
        mock_brands_db.connection.return_value.__aenter__.return_value = mock_brands_conn
        mock_brands_conn.fetchrow = AsyncMock(return_value=brand_no_meeting)

        response = client.get("/api/v1/brands/2", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["brand_name"] == "Brand DEF"
        assert data["meeting_raw_data"] is None


def test_brand_detail_not_found(client):
    """Test GET /api/v1/brands/999 returns 404 for unknown brand."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.brands.service.db") as mock_brands_db,
    ):
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
        mock_user_queries.update_last_login = AsyncMock()

        mock_brands_conn = AsyncMock()
        mock_brands_db.connection.return_value.__aenter__.return_value = mock_brands_conn
        mock_brands_conn.fetchrow = AsyncMock(return_value=None)

        response = client.get("/api/v1/brands/999", headers=AUTH_HEADERS)

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "BRAND_NOT_FOUND"
