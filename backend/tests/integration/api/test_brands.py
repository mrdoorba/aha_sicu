"""Integration tests for brands API endpoints."""

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

SAMPLE_BRANDS = [
    {
        "id": 1,
        "brand_name": "Brand ABC",
        "raw_data": {"category": "Electronics"},
        "updated_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
        "meeting_raw_data": {"notes": "Positive review"},
    },
    {
        "id": 2,
        "brand_name": "Brand DEF",
        "raw_data": {"category": "Fashion"},
        "updated_at": datetime(2026, 2, 5, 11, 0, 0, tzinfo=timezone.utc),
        "meeting_raw_data": None,
    },
]


def test_brands_without_token(client):
    """Test GET /api/v1/brands returns 401 without Authorization header."""
    response = client.get("/api/v1/brands")
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "AUTH_TOKEN_MISSING"


def test_brands_returns_paginated_response(client):
    """Test GET /api/v1/brands returns paginated brand list."""
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
        mock_brands_conn.fetch = AsyncMock(return_value=SAMPLE_BRANDS)
        mock_brands_conn.fetchval = AsyncMock(return_value=2)

        response = client.get("/api/v1/brands", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["limit"] == 20
        assert data["pages"] == 1
        assert len(data["items"]) == 2
        assert data["items"][0]["brand_name"] == "Brand ABC"
        assert data["items"][0]["meeting_raw_data"] == {"notes": "Positive review"}
        assert data["items"][1]["brand_name"] == "Brand DEF"
        assert data["items"][1]["meeting_raw_data"] is None


def test_brands_pagination_params(client):
    """Test GET /api/v1/brands respects page and limit query params."""
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
        mock_brands_conn.fetch = AsyncMock(return_value=[SAMPLE_BRANDS[0]])
        mock_brands_conn.fetchval = AsyncMock(return_value=50)

        response = client.get("/api/v1/brands?page=2&limit=10", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["limit"] == 10
        assert data["total"] == 50
        assert data["pages"] == 5


def test_brands_empty_state(client):
    """Test GET /api/v1/brands returns empty list when no brands exist."""
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
        mock_brands_conn.fetch = AsyncMock(return_value=[])
        mock_brands_conn.fetchval = AsyncMock(return_value=0)

        response = client.get("/api/v1/brands", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["pages"] == 0


def test_brands_search_with_results(client):
    """Test GET /api/v1/brands?search=ABC filters by brand name."""
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
        mock_brands_conn.fetch = AsyncMock(return_value=[SAMPLE_BRANDS[0]])
        mock_brands_conn.fetchval = AsyncMock(return_value=1)

        response = client.get("/api/v1/brands?search=ABC", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["brand_name"] == "Brand ABC"


def test_brands_search_no_results(client):
    """Test GET /api/v1/brands?search=nonexistent returns empty list with total=0."""
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
        mock_brands_conn.fetch = AsyncMock(return_value=[])
        mock_brands_conn.fetchval = AsyncMock(return_value=0)

        response = client.get("/api/v1/brands?search=nonexistent", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


def test_brands_with_meeting_data(client):
    """Test response includes Meeting data when available for a brand."""
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

        brand_with_meeting = {
            "id": 1,
            "brand_name": "Brand ABC",
            "raw_data": {"category": "Electronics"},
            "updated_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
            "meeting_raw_data": {"notes": "Good meeting", "score": 8},
        }

        mock_brands_conn = AsyncMock()
        mock_brands_db.connection.return_value.__aenter__.return_value = mock_brands_conn
        mock_brands_conn.fetch = AsyncMock(return_value=[brand_with_meeting])
        mock_brands_conn.fetchval = AsyncMock(return_value=1)

        response = client.get("/api/v1/brands", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["meeting_raw_data"] == {"notes": "Good meeting", "score": 8}


def test_brands_without_meeting_data(client):
    """Test response handles brands with no Meeting data (null)."""
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

        brand_no_meeting = {
            "id": 2,
            "brand_name": "Brand DEF",
            "raw_data": {"category": "Fashion"},
            "updated_at": datetime(2026, 2, 5, 11, 0, 0, tzinfo=timezone.utc),
            "meeting_raw_data": None,
        }

        mock_brands_conn = AsyncMock()
        mock_brands_db.connection.return_value.__aenter__.return_value = mock_brands_conn
        mock_brands_conn.fetch = AsyncMock(return_value=[brand_no_meeting])
        mock_brands_conn.fetchval = AsyncMock(return_value=1)

        response = client.get("/api/v1/brands", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["meeting_raw_data"] is None
