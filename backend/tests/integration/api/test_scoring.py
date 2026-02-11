"""Integration tests for the scoring endpoint."""

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
    "brand_name": "Test Brand",
    "raw_data": {},
    "updated_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
    "meeting_raw_data": None,
}

SAMPLE_MANUAL_DATA = {
    "operational": {
        "unfulfilledOrderRate": 0.5,
        "lateShipmentRate": 0.3,
        "preparationTime": 0.8,
        "chatResponseRate": 98.0,
        "overallRating": 4.9,
    },
    "business": {
        "salesMonth0": 200_000_000,
        "salesMonth1": 180_000_000,
        "salesMonth2": 190_000_000,
        "salesMonth3": 170_000_000,
        "salesMonth4": 160_000_000,
        "salesMonth5": 150_000_000,
    },
    "visitors": {
        "totalVisitors": 100_000,
        "returningVisitors": 30_000,
        "totalFollowers": 60_000,
    },
    "products": {
        "productCount": 50,
        "storeStatus": "Shopee Mall",
    },
    "ads": {
        "adSales": 50_000_000,
        "adCost": 5_000_000,
    },
    "campaign": {
        "nominatedSessions": 18,
        "availableSessions": 20,
    },
}

SAMPLE_EVAL_INPUTS = {
    "id": 1,
    "brand_id": 1,
    "user_id": 1,
    "category_type": "fashion",
    "manual_data": SAMPLE_MANUAL_DATA,
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
}

SAMPLE_CALC_RESULTS = [
    {
        "id": 1,
        "brand_id": 1,
        "calculator_type": "top_sku",
        "details": {
            "average_stock": 30,
            "output_1": [
                {"rata2_harga_jual": 180_000},
                {"rata2_harga_jual": 140_000},
            ],
        },
        "output_text": "",
        "calculated_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    },
    {
        "id": 2,
        "brand_id": 1,
        "calculator_type": "discount",
        "details": {"fake_discount_flag": False},
        "output_text": "% Diskon TOP SKU: 25.0%\nRange: 15.0% ~ 35.0%\nVoucher 3.0%\nPaket Diskon 1.0%",
        "calculated_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    },
    {
        "id": 3,
        "brand_id": 1,
        "calculator_type": "ads_keyword",
        "details": {},
        "output_text": "Ads keyword output",
        "calculated_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    },
]

SCORING_REQUEST = {
    "template": "fashion",
    "verdict": "✔️",
    "store_name": "Test Store Official",
    "period": "Jan 2026",
    "brand_name": "TestBrand",
}


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries):
    """Shared auth mock setup."""
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
    mock_user_queries.update_last_login = AsyncMock()


def test_score_without_token(client):
    """Test POST /score returns 401 without auth token."""
    response = client.post(
        "/api/v1/evaluations/brands/1/score",
        json=SCORING_REQUEST,
    )
    assert response.status_code == 401


def test_score_with_full_data(client):
    """Test POST /score returns complete scoring result with full data."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(side_effect=[
            SAMPLE_BRAND,        # get_brand_by_id
            SAMPLE_EVAL_INPUTS,  # get_evaluation_inputs
        ])
        mock_svc_conn.fetch = AsyncMock(return_value=SAMPLE_CALC_RESULTS)

        response = client.post(
            "/api/v1/evaluations/brands/1/score",
            json=SCORING_REQUEST,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_score" in data
        assert "category_scores" in data
        assert isinstance(data["category_scores"], list)
        assert len(data["category_scores"]) == 11
        assert data["verdict"] == "✔️"
        assert data["template"] == "fashion"
        assert "email_subject" in data
        assert "email_body" in data
        assert "whatsapp_link" in data
        assert data["email_subject"].startswith("🏥")
        assert data["whatsapp_link"].startswith("https://api.whatsapp.com")


def test_score_with_missing_calculator_results(client):
    """Test POST /score returns partial scores when calculator results are missing."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(side_effect=[
            SAMPLE_BRAND,
            SAMPLE_EVAL_INPUTS,
        ])
        mock_svc_conn.fetch = AsyncMock(return_value=[])  # No calculator results

        response = client.post(
            "/api/v1/evaluations/brands/1/score",
            json=SCORING_REQUEST,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_score" in data
        # Stock category should be unavailable (no calculator data)
        stock_cat = next(
            c for c in data["category_scores"] if c["category"] == "Stok"
        )
        assert stock_cat["available"] is False
        assert stock_cat["score"] == 0.0
        # Discount category should also be unavailable
        disc_cat = next(
            c for c in data["category_scores"] if c["category"] == "Discount"
        )
        assert disc_cat["available"] is False
        assert disc_cat["score"] == 0.0


def test_score_brand_not_found(client):
    """Test POST /score returns 404 for non-existent brand."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=None)  # Brand not found

        response = client.post(
            "/api/v1/evaluations/brands/999/score",
            json=SCORING_REQUEST,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "BRAND_NOT_FOUND"


def test_score_missing_manual_data(client):
    """Test POST /score returns 400 when no manual data exists."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        eval_no_data = {**SAMPLE_EVAL_INPUTS, "manual_data": None}
        mock_svc_conn.fetchrow = AsyncMock(side_effect=[
            SAMPLE_BRAND,
            eval_no_data,
        ])

        response = client.post(
            "/api/v1/evaluations/brands/1/score",
            json=SCORING_REQUEST,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "CALC_MISSING_DATA"


def test_score_invalid_verdict(client):
    """Test POST /score returns 422 for invalid verdict value."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        bad_request = {**SCORING_REQUEST, "verdict": "INVALID_VERDICT"}
        response = client.post(
            "/api/v1/evaluations/brands/1/score",
            json=bad_request,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 422  # Pydantic validation error


def test_score_invalid_template(client):
    """Test POST /score returns 422 for invalid template value."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        bad_request = {**SCORING_REQUEST, "template": "invalid_template"}
        response = client.post(
            "/api/v1/evaluations/brands/1/score",
            json=bad_request,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 422


def test_score_available_field_in_response(client):
    """Test POST /score response includes available field on category scores."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(side_effect=[
            SAMPLE_BRAND,
            SAMPLE_EVAL_INPUTS,
        ])
        mock_svc_conn.fetch = AsyncMock(return_value=SAMPLE_CALC_RESULTS)

        response = client.post(
            "/api/v1/evaluations/brands/1/score",
            json=SCORING_REQUEST,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        # All categories should have available field
        for cat in data["category_scores"]:
            assert "available" in cat
        # With full data, stock/discount should be available
        stock_cat = next(
            c for c in data["category_scores"] if c["category"] == "Stok"
        )
        assert stock_cat["available"] is True
