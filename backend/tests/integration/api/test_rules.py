"""Integration tests for rules API endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

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

DEFAULT_RULES = {
    "operational": {
        "unfulfilled_order_rate": {"threshold": 1.0, "points": 4, "comparison": "lte"},
        "late_shipment_rate": {"threshold": 1.0, "points": 3, "comparison": "lte"},
        "preparation_time": {"threshold": 1.0, "points": 3, "comparison": "lte"},
        "chat_response_rate": {"threshold": 95.0, "comparison": "gte", "info_only": True},
        "overall_rating": {"threshold": 4.7, "comparison": "gte", "info_only": True},
    },
    "business": {
        "monthly_sales_trend": {"threshold_pct": 90.0, "points": 10, "comparison": "gte"},
        "six_month_avg_threshold": {"threshold": 100000000, "points_above": 15, "points_below": 10, "comparison": "gt"},
        "conversion_rate": {"threshold": 3.0, "comparison": "gte", "info_only": True},
    },
    "content": {
        "quality_ratio": {"threshold": 95.0, "comparison": "gte", "info_only": True},
    },
    "visitors": {
        "returning_visitors_pct": {"threshold": 23.0, "points": 3, "comparison": "gte"},
        "followers": {"threshold": 50000, "points": 2, "comparison": "gte"},
    },
    "promo_tools": {
        "usage_pct_threshold": {"threshold": 80.0, "opportunity_points": 5},
        "effectiveness_pct_threshold": {"threshold": 90.0, "opportunity_points": 10},
    },
    "products_status": {
        "product_count": {"threshold": 35, "points": 5, "comparison": "gte"},
        "store_status_points": {"mall": 10, "star_plus": 5, "star": 0, "regular": 0},
    },
    "ads": {
        "roi_threshold": {"threshold": 9.0, "opportunity_points": 5, "comparison": "gt"},
        "gmv_ratio_threshold": {"threshold": 84.0, "points": 5, "comparison": "lt"},
        "cost_ratio_range": {"min": 5.0, "max": 10.0, "info_only": True},
    },
    "campaign": {
        "participation_pct_threshold": {"threshold": 90.0, "opportunity_points": 10, "comparison": "gte"},
    },
    "stock": {
        "high_threshold": {"threshold": 24, "points": 10, "comparison": "gte"},
        "mid_threshold": {"threshold": 12, "points": 5, "comparison": "gte"},
        "low_penalty": {"threshold": 12, "points": -5, "comparison": "lt"},
    },
    "interpretation": {
        "ranges": [
            {"min": 71, "max": None, "label": "Good Candidate", "verdict": "\u2714\ufe0f"},
            {"min": 41, "max": 70, "label": "Needs Review", "verdict": "\u2b55\ufe0f"},
            {"min": None, "max": 40, "label": "Not Recommended", "verdict": "\u274c"},
        ],
    },
}

SAMPLE_RULES = [
    {
        "id": 1,
        "template": "default",
        "rules": DEFAULT_RULES,
        "version": 1,
        "updated_by": None,
        "updated_at": datetime(2026, 2, 12, tzinfo=timezone.utc),
    },
]

EXPECTED_CATEGORIES = [
    "operational",
    "business",
    "content",
    "visitors",
    "promo_tools",
    "products_status",
    "ads",
    "campaign",
    "stock",
    "interpretation",
]


def _setup_mocks(mock_verify, mock_db, mock_user_queries, mock_rules_db, user):
    """Set up common mocks for rules tests."""
    mock_verify.return_value = {"uid": user["firebase_uid"], "email": user["email"]}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=user)
    mock_user_queries.update_last_login = AsyncMock()

    mock_rules_conn = AsyncMock()
    mock_rules_db.connection.return_value.__aenter__.return_value = mock_rules_conn
    mock_rules_conn.fetch = AsyncMock(return_value=SAMPLE_RULES)
    return mock_rules_conn


def test_get_rules_without_token(client):
    """Test GET /api/v1/rules returns 401 without Authorization header."""
    response = client.get("/api/v1/rules")
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "AUTH_TOKEN_MISSING"


def test_get_rules_leader_role_allowed(client):
    """Test GET /api/v1/rules returns 200 for leader role."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_rules_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, mock_rules_db, MOCK_LEADER)
        response = client.get("/api/v1/rules", headers=AUTH_HEADERS)
        assert response.status_code == 200


def test_get_rules_admin_role_allowed(client):
    """Test GET /api/v1/rules returns 200 for admin role."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_rules_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, mock_rules_db, MOCK_ADMIN)
        response = client.get("/api/v1/rules", headers=AUTH_HEADERS)
        assert response.status_code == 200


def test_get_rules_member_role_forbidden(client):
    """Test GET /api/v1/rules returns 403 for member role with RULE_ACCESS_DENIED."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        mock_verify.return_value = {"uid": "member-uid", "email": "member@example.com"}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_MEMBER)
        mock_user_queries.update_last_login = AsyncMock()

        response = client.get("/api/v1/rules", headers=AUTH_HEADERS)
        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "RULE_ACCESS_DENIED"
        assert "leaders and admins" in data["detail"].lower()


def test_get_rules_returns_default_template(client):
    """Test GET /api/v1/rules returns 200 with one rule object (default template)."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_rules_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, mock_rules_db, MOCK_LEADER)
        response = client.get("/api/v1/rules", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["template"] == "default"


def test_get_rules_schema_structure(client):
    """Test response fields match: id, template, rules, version, updated_by, updated_at."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_rules_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, mock_rules_db, MOCK_LEADER)
        response = client.get("/api/v1/rules", headers=AUTH_HEADERS)

        data = response.json()
        for rule in data:
            assert "id" in rule
            assert "template" in rule
            assert "rules" in rule
            assert "version" in rule
            assert "updated_by" in rule
            assert "updated_at" in rule
            assert isinstance(rule["rules"], dict)
            assert rule["version"] == 1


def test_get_rules_default_thresholds(client):
    """Test default rules have correct threshold values."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_rules_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, mock_rules_db, MOCK_LEADER)
        response = client.get("/api/v1/rules", headers=AUTH_HEADERS)

        data = response.json()
        default_rules = data[0]["rules"]

        # Check key thresholds in default template
        assert default_rules["business"]["conversion_rate"]["threshold"] == 3.0
        assert default_rules["ads"]["roi_threshold"]["threshold"] == 9.0
        assert default_rules["operational"]["unfulfilled_order_rate"]["threshold"] == 1.0
        assert default_rules["visitors"]["followers"]["threshold"] == 50000


def test_get_rules_jsonb_categories(client):
    """Test rules JSONB contains all expected categories."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.rules.service.db") as mock_rules_db,
    ):
        _setup_mocks(mock_verify, mock_db, mock_user_queries, mock_rules_db, MOCK_LEADER)
        response = client.get("/api/v1/rules", headers=AUTH_HEADERS)

        data = response.json()
        for rule in data:
            rule_categories = set(rule["rules"].keys())
            for expected in EXPECTED_CATEGORIES:
                assert expected in rule_categories, (
                    f"Missing category '{expected}' in {rule['template']} rules"
                )
