"""Integration tests for the evaluation detail endpoint (Story 4.5)."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

AUTH_HEADERS = {"Authorization": "Bearer valid-token"}

MOCK_USER = {
    "id": 1,
    "firebase_uid": "test-uid",
    "email": "test@example.com",
    "role": "leader",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 5, tzinfo=timezone.utc),
}

MOCK_MEMBER = {
    "id": 3,
    "firebase_uid": "member-uid",
    "email": "member@example.com",
    "role": "member",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 5, tzinfo=timezone.utc),
}

EVAL_DETAIL_ROW = {
    "id": 42,
    "brand_id": 10,
    "brand_name": "Nike Indonesia",
    "raw_data": {
        "Email": "pic@nike.com",
        "Nama PIC/ Jabatan*": "Budi Santoso",
        "Link Shopee Mall / LazMall": "https://shopee.co.id/nike",
        "Kategori": "Fashion",
        "Other Field": "ignored",
    },
    "final_score": Decimal("78.50"),
    "verdict": "✔️",
    "template": "fashion",
    "score_breakdown": [
        {"category": "Operational", "score": 10.0, "max_score": 10.0, "rows": [], "available": True},
        {"category": "Business", "score": 18.0, "max_score": 20.0, "rows": [], "available": True},
    ],
    "calculator_results": {
        "ads_keyword": {"details": {}, "output_text": "AK analysis text"},
        "top_sku": {"details": {"output_1": [], "output_2": [], "average_stock": 150}, "output_text": "Top SKU text"},
        "discount": {"details": {}, "output_text": "Discount text"},
    },
    "manual_inputs": {
        "operational": {"pesanan_tidak_terselesaikan": 0.5, "keterlambatan": 0.3},
        "business": {"monthly_sales": [100000000, 120000000], "conversion_rate": 2.5},
    },
    "email_output": "Dear Team,\n\nBrand evaluation for Nike Indonesia...",
    "evaluator_email": "rina@company.com",
    "created_at": datetime(2026, 2, 10, 10, 30, 0, tzinfo=timezone.utc),
    "rule_version": 1,
}


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries):
    """Shared auth mock setup."""
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
    mock_user_queries.update_last_login = AsyncMock()


def test_get_evaluation_detail_success(client):
    """Test GET /evaluations/{id} returns full evaluation with all fields."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=EVAL_DETAIL_ROW)

        response = client.get(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 42
        assert data["brand_id"] == 10
        assert data["final_score"] == 78.5
        assert data["verdict"] == "✔️"
        assert data["template"] == "fashion"
        assert data["rule_version"] == 1
        assert data["created_at"] is not None


def test_get_evaluation_detail_has_brand_name(client):
    """Test brand_name from brand_vp_data join is present."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=EVAL_DETAIL_ROW)

        response = client.get(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["brand_name"] == "Nike Indonesia"


def test_get_evaluation_detail_has_evaluator_email(client):
    """Test evaluator_email from users join is present."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=EVAL_DETAIL_ROW)

        response = client.get(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["evaluator_email"] == "rina@company.com"


def test_get_evaluation_detail_jsonb_fields(client):
    """Test JSONB fields are properly serialized: score_breakdown is list, calculator_results and manual_inputs are dicts."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=EVAL_DETAIL_ROW)

        response = client.get(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()

        # score_breakdown is a list of dicts
        assert isinstance(data["score_breakdown"], list)
        assert len(data["score_breakdown"]) == 2
        assert data["score_breakdown"][0]["category"] == "Operational"

        # calculator_results is a dict
        assert isinstance(data["calculator_results"], dict)
        assert "ads_keyword" in data["calculator_results"]
        assert "top_sku" in data["calculator_results"]
        assert "discount" in data["calculator_results"]

        # manual_inputs is a dict
        assert isinstance(data["manual_inputs"], dict)
        assert "operational" in data["manual_inputs"]
        assert "business" in data["manual_inputs"]


def test_get_evaluation_detail_not_found(client):
    """Test non-existent ID returns 404 with EVAL_NOT_FOUND code."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=None)

        response = client.get(
            "/api/v1/evaluations/99999",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "EVAL_NOT_FOUND"
        assert data["detail"] == "Evaluation not found"


def test_get_evaluation_detail_unauthenticated(client):
    """Test unauthenticated request returns 401."""
    response = client.get("/api/v1/evaluations/42")
    assert response.status_code == 401


def test_get_evaluation_detail_has_brand_raw_data(client):
    """Test brand_raw_data maps VP sheet keys to clean keys."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=EVAL_DETAIL_ROW)

        response = client.get(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        raw = data["brand_raw_data"]
        assert raw["email"] == "pic@nike.com"
        assert raw["pic_name"] == "Budi Santoso"
        assert raw["store_link"] == "https://shopee.co.id/nike"
        assert raw["kategori"] == "Fashion"


def test_get_evaluation_detail_brand_raw_data_partial(client):
    """Test brand_raw_data returns null for missing VP sheet fields."""
    partial_row = {
        **EVAL_DETAIL_ROW,
        "raw_data": {"Email": "pic@brand.com"},
    }
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=partial_row)

        response = client.get(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        raw = response.json()["brand_raw_data"]
        assert raw["email"] == "pic@brand.com"
        assert raw["pic_name"] is None
        assert raw["store_link"] is None
        assert raw["kategori"] is None


def test_get_evaluation_detail_brand_raw_data_null(client):
    """Test brand_raw_data defaults when raw_data is None."""
    null_row = {**EVAL_DETAIL_ROW, "raw_data": None}
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=null_row)

        response = client.get(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        raw = response.json()["brand_raw_data"]
        assert raw["email"] is None
        assert raw["pic_name"] is None
        assert raw["store_link"] is None
        assert raw["kategori"] is None


# --- Role access control tests ---


def _setup_auth_mocks_for_user(mock_verify, mock_db, mock_user_queries, mock_user):
    """Auth mock setup with a specific user."""
    mock_verify.return_value = {"uid": mock_user["firebase_uid"], "email": mock_user["email"]}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=mock_user)
    mock_user_queries.update_last_login = AsyncMock()


def test_get_evaluation_detail_forbidden_member(client):
    """Test member cannot access evaluation detail — returns 403."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks_for_user(mock_verify, mock_db, mock_user_queries, MOCK_MEMBER)

        response = client.get(
            "/api/v1/evaluations/42",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "RULE_ACCESS_DENIED"
