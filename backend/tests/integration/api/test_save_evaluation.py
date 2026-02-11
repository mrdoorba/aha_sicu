"""Integration tests for the save evaluation endpoint."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

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

SAVE_REQUEST = {
    "template": "fashion",
    "final_score": 72.5,
    "verdict": "✔️",
    "score_breakdown": [
        {"category": "Operational", "score": 8.0, "max_score": 10.0},
        {"category": "Business", "score": 15.0, "max_score": 20.0},
    ],
    "calculator_results": {
        "ads_keyword": {"details": {}, "output_text": "Ads output"},
        "discount": {"details": {"fake_discount_flag": False}, "output_text": "Disc output"},
        "top_sku": {"details": {"average_stock": 30}, "output_text": "SKU output"},
    },
    "manual_inputs": {
        "operational": {"unfulfilledOrderRate": 0.5},
        "business": {"salesMonth0": 200_000_000},
    },
    "rule_version": 1,
    "email_output": "Email body text here",
}

SAVED_ROW = {
    "id": 1,
    "brand_id": 1,
    "final_score": Decimal("72.50"),
    "verdict": "✔️",
    "template": "fashion",
    "created_at": datetime(2026, 2, 11, 12, 0, 0, tzinfo=timezone.utc),
}


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries):
    """Shared auth mock setup."""
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
    mock_user_queries.update_last_login = AsyncMock()


def test_save_evaluation_success(client):
    """Test POST /save with full valid data returns 200 with id, brand_id, final_score, verdict, template, created_at."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(side_effect=[
            SAMPLE_BRAND,  # get_brand_by_id
            SAVED_ROW,     # insert_evaluation
        ])

        response = client.post(
            "/api/v1/evaluations/brands/1/save",
            json=SAVE_REQUEST,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["brand_id"] == 1
        assert data["final_score"] == 72.5
        assert data["verdict"] == "✔️"
        assert data["template"] == "fashion"
        assert "created_at" in data


def test_save_evaluation_missing_fields(client):
    """Test POST /save without required fields returns 422."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # Missing final_score and template
        incomplete_request = {
            "verdict": "✔️",
            "score_breakdown": [],
            "calculator_results": {},
            "manual_inputs": {},
        }
        response = client.post(
            "/api/v1/evaluations/brands/1/save",
            json=incomplete_request,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 422


def test_save_evaluation_invalid_brand(client):
    """Test POST /save with non-existent brand_id returns 404."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=None)  # Brand not found

        response = client.post(
            "/api/v1/evaluations/brands/999/save",
            json=SAVE_REQUEST,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "BRAND_NOT_FOUND"


def test_save_evaluation_auth_required(client):
    """Test POST /save without auth header returns 401."""
    response = client.post(
        "/api/v1/evaluations/brands/1/save",
        json=SAVE_REQUEST,
    )
    assert response.status_code == 401


def test_save_creates_new_record_each_time(client):
    """Test two saves for same brand create two separate records with different id and created_at."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        saved_row_1 = {
            **SAVED_ROW,
            "id": 1,
            "created_at": datetime(2026, 2, 11, 12, 0, 0, tzinfo=timezone.utc),
        }
        saved_row_2 = {
            **SAVED_ROW,
            "id": 2,
            "created_at": datetime(2026, 2, 11, 12, 5, 0, tzinfo=timezone.utc),
        }

        mock_svc_conn = AsyncMock()
        mock_svc_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(side_effect=[
            SAMPLE_BRAND, saved_row_1,  # First save
            SAMPLE_BRAND, saved_row_2,  # Second save
        ])

        response1 = client.post(
            "/api/v1/evaluations/brands/1/save",
            json=SAVE_REQUEST,
            headers=AUTH_HEADERS,
        )
        response2 = client.post(
            "/api/v1/evaluations/brands/1/save",
            json=SAVE_REQUEST,
            headers=AUTH_HEADERS,
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        data1 = response1.json()
        data2 = response2.json()
        assert data1["id"] != data2["id"]
        assert data1["created_at"] != data2["created_at"]


def test_save_evaluation_negative_score(client):
    """Test POST /save with negative final_score succeeds."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        negative_saved = {
            **SAVED_ROW,
            "final_score": Decimal("-15.50"),
        }
        mock_svc_conn = AsyncMock()
        mock_svc_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(side_effect=[
            SAMPLE_BRAND,
            negative_saved,
        ])

        negative_request = {**SAVE_REQUEST, "final_score": -15.5}
        response = client.post(
            "/api/v1/evaluations/brands/1/save",
            json=negative_request,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["final_score"] == -15.5


def test_save_preserves_jsonb_data(client):
    """Test that insert_evaluation is called with correct JSONB data."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
        patch("app.db.queries.evaluations.insert_evaluation") as mock_insert,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_conn.transaction = MagicMock(return_value=AsyncMock())
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn

        # get_brand_by_id returns brand; insert_evaluation is patched separately
        mock_svc_conn.fetchrow = AsyncMock(return_value=SAMPLE_BRAND)
        mock_insert.return_value = SAVED_ROW

        response = client.post(
            "/api/v1/evaluations/brands/1/save",
            json=SAVE_REQUEST,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        mock_insert.assert_called_once()
        call_kwargs = mock_insert.call_args
        # Verify JSONB fields were passed correctly
        assert call_kwargs.kwargs["score_breakdown"] == SAVE_REQUEST["score_breakdown"]
        assert call_kwargs.kwargs["calculator_results"] == SAVE_REQUEST["calculator_results"]
        assert call_kwargs.kwargs["manual_inputs"] == SAVE_REQUEST["manual_inputs"]
        assert call_kwargs.kwargs["email_output"] == "Email body text here"
