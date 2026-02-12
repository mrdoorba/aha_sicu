"""Integration tests for new_evaluation SSE broadcast after save."""

from contextlib import asynccontextmanager
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
    "brand_name": "Nike",
    "raw_data": {"category": "Fashion"},
    "updated_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
    "meeting_raw_data": None,
}

SAMPLE_SAVED_ROW = {
    "id": 123,
    "brand_id": 1,
    "final_score": 78.0,
    "verdict": "✔️",
    "template": "fashion",
    "created_at": datetime(2026, 2, 5, 12, 0, 0, tzinfo=timezone.utc),
}

SAVE_BODY = {
    "template": "fashion",
    "final_score": 78.0,
    "verdict": "✔️",
    "score_breakdown": [{"category": "A", "score": 10}],
    "calculator_results": {"ads_keyword": {"details": {}}},
    "manual_inputs": {"key": "value"},
    "rule_version": 1,
    "email_output": None,
}


def _make_transactional_conn():
    """Create a mock connection that supports conn.transaction() context manager."""
    mock_conn = AsyncMock()

    @asynccontextmanager
    async def mock_transaction():
        yield

    mock_conn.transaction = mock_transaction
    return mock_conn


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries):
    """Shared auth mock setup for all tests."""
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
    mock_user_queries.update_last_login = AsyncMock()


def _setup_eval_mocks(mock_eval_db, mock_brand_qs, mock_eval_qs, *, brand=SAMPLE_BRAND, saved_row=SAMPLE_SAVED_ROW):
    """Shared evaluation service mock setup — patches query functions directly."""
    mock_eval_conn = _make_transactional_conn()
    mock_eval_db.connection.return_value.__aenter__.return_value = mock_eval_conn
    mock_brand_qs.get_brand_by_id = AsyncMock(return_value=brand)
    mock_eval_qs.insert_evaluation = AsyncMock(return_value=saved_row)


def test_save_evaluation_broadcasts_new_evaluation(client):
    """Test that save_evaluation broadcasts new_evaluation event on success."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_eval_db,
        patch("app.modules.evaluations.service.brand_queries") as mock_brand_qs,
        patch("app.modules.evaluations.service.eval_queries") as mock_eval_qs,
        patch(
            "app.modules.evaluations.service.sync_broadcaster"
        ) as mock_broadcaster,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_mocks(mock_eval_db, mock_brand_qs, mock_eval_qs)
        mock_broadcaster.broadcast = AsyncMock()

        response = client.post(
            "/api/v1/evaluations/brands/1/save",
            json=SAVE_BODY,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        mock_broadcaster.broadcast.assert_called_once()
        call_args = mock_broadcaster.broadcast.call_args
        assert call_args[0][0] == "new_evaluation"


def test_broadcast_payload_includes_all_required_fields(client):
    """Test that broadcast payload includes evaluation_id, brand_name, score, evaluator, created_at."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_eval_db,
        patch("app.modules.evaluations.service.brand_queries") as mock_brand_qs,
        patch("app.modules.evaluations.service.eval_queries") as mock_eval_qs,
        patch(
            "app.modules.evaluations.service.sync_broadcaster"
        ) as mock_broadcaster,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_mocks(mock_eval_db, mock_brand_qs, mock_eval_qs)
        mock_broadcaster.broadcast = AsyncMock()

        response = client.post(
            "/api/v1/evaluations/brands/1/save",
            json=SAVE_BODY,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        call_args = mock_broadcaster.broadcast.call_args
        payload = call_args[0][1]

        assert payload["evaluation_id"] == 123
        assert payload["brand_name"] == "Nike"
        assert payload["score"] == 78.0
        assert payload["evaluator"] == "test@example.com"
        assert "created_at" in payload
        assert payload["created_at"] == "2026-02-05T12:00:00+00:00"


def test_no_broadcast_on_brand_not_found(client):
    """Test that broadcast is NOT called when brand_id doesn't exist (404 path)."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_eval_db,
        patch("app.modules.evaluations.service.brand_queries") as mock_brand_qs,
        patch("app.modules.evaluations.service.eval_queries") as mock_eval_qs,
        patch(
            "app.modules.evaluations.service.sync_broadcaster"
        ) as mock_broadcaster,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_mocks(
            mock_eval_db, mock_brand_qs, mock_eval_qs, brand=None
        )
        mock_broadcaster.broadcast = AsyncMock()

        response = client.post(
            "/api/v1/evaluations/brands/999/save",
            json=SAVE_BODY,
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 404
        mock_broadcaster.broadcast.assert_not_called()


def test_broadcast_failure_does_not_block_save(client):
    """Test that broadcast failure does not prevent save response from returning."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_eval_db,
        patch("app.modules.evaluations.service.brand_queries") as mock_brand_qs,
        patch("app.modules.evaluations.service.eval_queries") as mock_eval_qs,
        patch(
            "app.modules.evaluations.service.sync_broadcaster"
        ) as mock_broadcaster,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_mocks(mock_eval_db, mock_brand_qs, mock_eval_qs)
        # Broadcast raises an exception
        mock_broadcaster.broadcast = AsyncMock(
            side_effect=RuntimeError("SSE broadcast failed")
        )

        response = client.post(
            "/api/v1/evaluations/brands/1/save",
            json=SAVE_BODY,
            headers=AUTH_HEADERS,
        )

        # Save should still succeed despite broadcast failure
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 123
        assert data["final_score"] == 78.0
