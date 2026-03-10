"""Integration tests for grouped evaluation endpoints."""

from datetime import datetime, timezone
from decimal import Decimal
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

GROUPED_ROW_1 = {
    "brand_id": 10,
    "brand_name": "Nike Indonesia",
    "evaluation_count": 5,
    "top_score": Decimal("82.50"),
    "top_verdict": "✔️",
    "latest_date": datetime(2026, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
}

GROUPED_ROW_2 = {
    "brand_id": 20,
    "brand_name": "Adidas SEA",
    "evaluation_count": 3,
    "top_score": Decimal("75.00"),
    "top_verdict": "✔️",
    "latest_date": datetime(2026, 2, 14, 14, 0, 0, tzinfo=timezone.utc),
}

GROUPED_ROW_3 = {
    "brand_id": 30,
    "brand_name": "Unilever ID",
    "evaluation_count": 1,
    "top_score": Decimal("60.00"),
    "top_verdict": "❌",
    "latest_date": datetime(2026, 2, 10, 9, 0, 0, tzinfo=timezone.utc),
}

BRAND_EVAL_1 = {
    "id": 101,
    "final_score": Decimal("82.50"),
    "verdict": "✔️",
    "template": "fashion",
    "evaluator_email": "rina@company.com",
    "created_at": datetime(2026, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
}

BRAND_EVAL_2 = {
    "id": 102,
    "final_score": Decimal("78.00"),
    "verdict": "✔️",
    "template": "fashion",
    "evaluator_email": "budi@company.com",
    "created_at": datetime(2026, 2, 12, 14, 0, 0, tzinfo=timezone.utc),
}

BRAND_EVAL_3 = {
    "id": 103,
    "final_score": Decimal("70.00"),
    "verdict": "❌",
    "template": "fashion",
    "evaluator_email": "rina@company.com",
    "created_at": datetime(2026, 2, 10, 9, 0, 0, tzinfo=timezone.utc),
}


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries, mock_user=None):
    """Shared auth mock setup."""
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(
        return_value=mock_user or MOCK_USER
    )
    mock_user_queries.update_last_login = AsyncMock()


# --- GET /api/v1/evaluations/grouped tests ---


def test_grouped_evaluations_success(client):
    """Test GET /evaluations/grouped returns paginated brand-level summary."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.list_grouped_evaluations = AsyncMock(
            return_value=[GROUPED_ROW_1, GROUPED_ROW_2, GROUPED_ROW_3]
        )
        mock_eq.count_grouped_evaluations = AsyncMock(return_value=3)

        response = client.get(
            "/api/v1/evaluations/grouped",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["limit"] == 20
        assert data["pages"] == 1
        assert len(data["items"]) == 3

        item = data["items"][0]
        assert item["brand_id"] == 10
        assert item["brand_name"] == "Nike Indonesia"
        assert item["evaluation_count"] == 5
        assert item["top_score"] == 82.5
        assert item["top_verdict"] == "✔️"
        assert "latest_date" in item


def test_grouped_evaluations_pagination(client):
    """Test pagination with limit=2 returns correct pages."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.list_grouped_evaluations = AsyncMock(
            side_effect=[[GROUPED_ROW_1, GROUPED_ROW_2], [GROUPED_ROW_3]]
        )
        mock_eq.count_grouped_evaluations = AsyncMock(return_value=3)

        # Page 1
        r1 = client.get(
            "/api/v1/evaluations/grouped?page=1&limit=2",
            headers=AUTH_HEADERS,
        )
        assert r1.status_code == 200
        d1 = r1.json()
        assert len(d1["items"]) == 2
        assert d1["total"] == 3
        assert d1["pages"] == 2

        # Page 2
        r2 = client.get(
            "/api/v1/evaluations/grouped?page=2&limit=2",
            headers=AUTH_HEADERS,
        )
        assert r2.status_code == 200
        d2 = r2.json()
        assert len(d2["items"]) == 1


def test_grouped_evaluations_search(client):
    """Test search filter returns matching brands only."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.list_grouped_evaluations = AsyncMock(return_value=[GROUPED_ROW_1])
        mock_eq.count_grouped_evaluations = AsyncMock(return_value=1)

        response = client.get(
            "/api/v1/evaluations/grouped?search=Nike",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["brand_name"] == "Nike Indonesia"


def test_grouped_evaluations_date_filter(client):
    """Test date filter narrows results."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.list_grouped_evaluations = AsyncMock(return_value=[GROUPED_ROW_1])
        mock_eq.count_grouped_evaluations = AsyncMock(return_value=1)

        response = client.get(
            "/api/v1/evaluations/grouped?date_from=2026-02-14&date_to=2026-02-16",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


def test_grouped_evaluations_empty(client):
    """Test no matching brands returns empty with correct shape."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.list_grouped_evaluations = AsyncMock(return_value=[])
        mock_eq.count_grouped_evaluations = AsyncMock(return_value=0)

        response = client.get(
            "/api/v1/evaluations/grouped",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["pages"] == 0


def test_grouped_evaluations_auth_required(client):
    """Test GET /evaluations/grouped without auth returns 401."""
    response = client.get("/api/v1/evaluations/grouped")
    assert response.status_code == 401


# --- GET /api/v1/evaluations/grouped/{brand_id} tests ---


def test_brand_evaluations_with_limit(client):
    """Test GET /evaluations/grouped/{brand_id}?limit=5 returns limited results."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.list_evaluations_by_brand = AsyncMock(
            return_value=([BRAND_EVAL_1, BRAND_EVAL_2, BRAND_EVAL_3], 8)
        )

        response = client.get(
            "/api/v1/evaluations/grouped/10?limit=5",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 8
        assert len(data["items"]) == 3

        item = data["items"][0]
        assert item["id"] == 101
        assert item["final_score"] == 82.5
        assert item["verdict"] == "✔️"
        assert item["evaluator_email"] == "rina@company.com"
        assert "created_at" in item


def test_brand_evaluations_without_limit(client):
    """Test GET /evaluations/grouped/{brand_id} without limit returns all."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.list_evaluations_by_brand = AsyncMock(
            return_value=([BRAND_EVAL_1, BRAND_EVAL_2, BRAND_EVAL_3], 3)
        )

        response = client.get(
            "/api/v1/evaluations/grouped/10",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3


def test_brand_evaluations_date_filter(client):
    """Test date filter on brand evaluations."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.list_evaluations_by_brand = AsyncMock(
            return_value=([BRAND_EVAL_1], 1)
        )

        response = client.get(
            "/api/v1/evaluations/grouped/10?date_from=2026-02-14&date_to=2026-02-16",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1


def test_brand_evaluations_empty(client):
    """Test brand with no evaluations returns empty list."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.list_evaluations_by_brand = AsyncMock(
            return_value=([], 0)
        )

        response = client.get(
            "/api/v1/evaluations/grouped/999",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


def test_brand_evaluations_auth_required(client):
    """Test GET /evaluations/grouped/{brand_id} without auth returns 401."""
    response = client.get("/api/v1/evaluations/grouped/10")
    assert response.status_code == 401
