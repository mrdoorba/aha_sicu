"""Integration tests for rules PUT endpoint."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

AUTH_HEADERS = {"Authorization": "Bearer valid-token"}

MOCK_LEADER = {
    "id": 1,
    "firebase_uid": "leader-uid",
    "email": "leader@example.com",
    "role": "leader",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 5, tzinfo=timezone.utc),
}

MOCK_ADMIN = {
    "id": 2,
    "firebase_uid": "admin-uid",
    "email": "admin@example.com",
    "role": "admin",
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

UPDATED_RULES = {
    "operational": {
        "unfulfilled_order_rate": {"threshold": 2.0, "points": 5, "comparison": "lte"},
    },
}

UPDATED_ROW = {
    "id": 1,
    "template": "fashion",
    "rules": UPDATED_RULES,
    "version": 2,
    "updated_by": 1,
    "updated_at": datetime(2026, 2, 12, 10, 0, 0, tzinfo=timezone.utc),
}

UPDATED_ROW_NF = {
    "id": 2,
    "template": "non_fashion",
    "rules": UPDATED_RULES,
    "version": 2,
    "updated_by": 2,
    "updated_at": datetime(2026, 2, 12, 10, 0, 0, tzinfo=timezone.utc),
}


def _setup_mocks(mock_verify, mock_db, mock_user_queries, user):
    """Set up common auth mocks."""
    mock_verify.return_value = {"uid": user["firebase_uid"], "email": user["email"]}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=user)
    mock_user_queries.update_last_login = AsyncMock()


def _setup_service_mock(mock_service_db, return_row):
    """Set up service-layer DB mock."""
    mock_conn = AsyncMock()
    mock_service_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_conn.fetchrow = AsyncMock(return_value=return_row)
    return mock_conn


def test_update_rules_fashion_leader(client):
    """Test PUT /api/v1/rules/fashion returns 200 with updated rules for leader role."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_service_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)
        _setup_service_mock(mock_service_db, UPDATED_ROW)

        response = client.put(
            "/api/v1/rules/fashion",
            headers=AUTH_HEADERS,
            json={"rules": UPDATED_RULES},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["template"] == "fashion"
        assert data["rules"] == UPDATED_RULES


def test_update_rules_non_fashion_admin(client):
    """Test PUT /api/v1/rules/non_fashion returns 200 for admin role."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_service_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_ADMIN)
        _setup_service_mock(mock_service_db, UPDATED_ROW_NF)

        response = client.put(
            "/api/v1/rules/non_fashion",
            headers=AUTH_HEADERS,
            json={"rules": UPDATED_RULES},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["template"] == "non_fashion"


def test_update_rules_version_increments(client):
    """Test version is incremented by 1 after update."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_service_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)
        _setup_service_mock(mock_service_db, UPDATED_ROW)

        response = client.put(
            "/api/v1/rules/fashion",
            headers=AUTH_HEADERS,
            json={"rules": UPDATED_RULES},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 2


def test_update_rules_updated_by_set(client):
    """Test updated_by is set to current user id."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_service_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)
        _setup_service_mock(mock_service_db, UPDATED_ROW)

        response = client.put(
            "/api/v1/rules/fashion",
            headers=AUTH_HEADERS,
            json={"rules": UPDATED_RULES},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["updated_by"] == MOCK_LEADER["id"]


def test_update_rules_updated_at_refreshed(client):
    """Test updated_at is set in response."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_service_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)
        _setup_service_mock(mock_service_db, UPDATED_ROW)

        response = client.put(
            "/api/v1/rules/fashion",
            headers=AUTH_HEADERS,
            json={"rules": UPDATED_RULES},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["updated_at"] is not None
        assert "2026-02-12" in data["updated_at"]


def test_update_rules_member_forbidden(client):
    """Test member role gets 403 with RULE_ACCESS_DENIED."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_MEMBER)

        response = client.put(
            "/api/v1/rules/fashion",
            headers=AUTH_HEADERS,
            json={"rules": UPDATED_RULES},
        )

        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "RULE_ACCESS_DENIED"


def test_update_rules_no_auth(client):
    """Test no auth token gets 401."""
    response = client.put(
        "/api/v1/rules/fashion",
        json={"rules": UPDATED_RULES},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "AUTH_TOKEN_MISSING"


def test_update_rules_invalid_template(client):
    """Test invalid template gets 422."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)

        response = client.put(
            "/api/v1/rules/invalid",
            headers=AUTH_HEADERS,
            json={"rules": UPDATED_RULES},
        )

        assert response.status_code == 422


def test_update_rules_response_schema(client):
    """Test response matches ScoringRuleResponse schema fields."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_service_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)
        _setup_service_mock(mock_service_db, UPDATED_ROW)

        response = client.put(
            "/api/v1/rules/fashion",
            headers=AUTH_HEADERS,
            json={"rules": UPDATED_RULES},
        )

        assert response.status_code == 200
        data = response.json()
        expected_fields = {"id", "template", "rules", "version", "updated_by", "updated_at"}
        assert set(data.keys()) == expected_fields


def test_update_rules_empty_body(client):
    """Test empty rules dict gets 422."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)

        response = client.put(
            "/api/v1/rules/fashion",
            headers=AUTH_HEADERS,
            json={"rules": {}},
        )

        assert response.status_code == 422


def test_update_rules_invalid_structure(client):
    """Test invalid rules structure (non-dict values) gets 422."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)

        response = client.put(
            "/api/v1/rules/fashion",
            headers=AUTH_HEADERS,
            json={"rules": {"bad_key": "not_a_dict"}},
        )

        assert response.status_code == 422


def test_update_rules_preserves_jsonb_structure(client):
    """Test updated rules JSONB is correctly stored and returned."""
    complex_rules = {
        "operational": {
            "unfulfilled_order_rate": {"threshold": 1.5, "points": 4, "comparison": "lte"},
            "late_shipment_rate": {"threshold": 0.8, "points": 3, "comparison": "lte"},
        },
        "business": {
            "monthly_sales_trend": {"threshold_pct": 95.0, "points": 10, "comparison": "gte"},
        },
    }
    updated_row = {
        **UPDATED_ROW,
        "rules": complex_rules,
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_service_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, MOCK_LEADER)
        _setup_service_mock(mock_service_db, updated_row)

        response = client.put(
            "/api/v1/rules/fashion",
            headers=AUTH_HEADERS,
            json={"rules": complex_rules},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rules"] == complex_rules
        assert data["rules"]["operational"]["unfulfilled_order_rate"]["threshold"] == 1.5
        assert data["rules"]["business"]["monthly_sales_trend"]["threshold_pct"] == 95.0
