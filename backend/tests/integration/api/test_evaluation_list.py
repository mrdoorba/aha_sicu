"""Integration tests for the evaluation list endpoint."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, call, patch

AUTH_HEADERS = {"Authorization": "Bearer valid-token"}

MOCK_USER = {
    "id": 1,
    "firebase_uid": "test-uid",
    "email": "test@example.com",
    "role": "member",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 5, tzinfo=timezone.utc),
}

EVAL_ROW_1 = {
    "id": 1,
    "brand_name": "Nike Indonesia",
    "final_score": Decimal("78.50"),
    "verdict": "✔️",
    "template": "fashion",
    "evaluator_email": "rina@company.com",
    "created_at": datetime(2026, 2, 10, 10, 30, 0, tzinfo=timezone.utc),
}

EVAL_ROW_2 = {
    "id": 2,
    "brand_name": "Unilever ID",
    "final_score": Decimal("65.00"),
    "verdict": "❌",
    "template": "non_fashion",
    "evaluator_email": "budi@company.com",
    "created_at": datetime(2026, 2, 9, 14, 0, 0, tzinfo=timezone.utc),
}

EVAL_ROW_3 = {
    "id": 3,
    "brand_name": "Adidas SEA",
    "final_score": Decimal("82.25"),
    "verdict": "✔️",
    "template": "fashion",
    "evaluator_email": "rina@company.com",
    "created_at": datetime(2026, 2, 8, 9, 0, 0, tzinfo=timezone.utc),
}


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries):
    """Shared auth mock setup."""
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
    mock_user_queries.update_last_login = AsyncMock()


def test_list_evaluations_success(client):
    """Test GET /evaluations returns paginated list with correct fields."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetch = AsyncMock(return_value=[EVAL_ROW_1, EVAL_ROW_2])
        mock_svc_conn.fetchval = AsyncMock(return_value=2)

        response = client.get(
            "/api/v1/evaluations",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["limit"] == 20
        assert data["pages"] == 1
        assert len(data["items"]) == 2

        item = data["items"][0]
        assert item["id"] == 1
        assert item["brand_name"] == "Nike Indonesia"
        assert item["final_score"] == 78.5
        assert item["verdict"] == "✔️"
        assert item["template"] == "fashion"
        assert item["evaluator_email"] == "rina@company.com"
        assert "created_at" in item


def test_list_evaluations_pagination(client):
    """Test pagination: page=1 vs page=2 return different results."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        # Page 1: returns first 2, Page 2: returns 3rd item
        mock_svc_conn.fetch = AsyncMock(
            side_effect=[[EVAL_ROW_1, EVAL_ROW_2], [EVAL_ROW_3]]
        )
        mock_svc_conn.fetchval = AsyncMock(return_value=3)

        # Page 1 with limit=2
        response1 = client.get(
            "/api/v1/evaluations?page=1&limit=2",
            headers=AUTH_HEADERS,
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["items"]) == 2
        assert data1["total"] == 3
        assert data1["pages"] == 2
        assert data1["page"] == 1

        # Page 2 with limit=2
        response2 = client.get(
            "/api/v1/evaluations?page=2&limit=2",
            headers=AUTH_HEADERS,
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["items"]) == 1
        assert data2["page"] == 2
        assert data2["items"][0]["id"] != data1["items"][0]["id"]


def test_list_evaluations_sort_date_desc(client):
    """Test default sort: newest first (created_at desc)."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        # Return in desc order (newest first)
        mock_svc_conn.fetch = AsyncMock(return_value=[EVAL_ROW_1, EVAL_ROW_2, EVAL_ROW_3])
        mock_svc_conn.fetchval = AsyncMock(return_value=3)

        response = client.get(
            "/api/v1/evaluations",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        # Verify order: id 1 (Feb 10) > id 2 (Feb 9) > id 3 (Feb 8)
        assert items[0]["id"] == 1
        assert items[1]["id"] == 2
        assert items[2]["id"] == 3


def test_list_evaluations_sort_date_asc(client):
    """Test sort_order=asc returns oldest first."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        # Return in asc order (oldest first)
        mock_svc_conn.fetch = AsyncMock(return_value=[EVAL_ROW_3, EVAL_ROW_2, EVAL_ROW_1])
        mock_svc_conn.fetchval = AsyncMock(return_value=3)

        response = client.get(
            "/api/v1/evaluations?sort_order=asc",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        # Oldest first
        assert items[0]["id"] == 3
        assert items[2]["id"] == 1


def test_list_evaluations_sort_score(client):
    """Test sort_by=final_score sorts by score."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        # Return sorted by score desc
        mock_svc_conn.fetch = AsyncMock(return_value=[EVAL_ROW_3, EVAL_ROW_1, EVAL_ROW_2])
        mock_svc_conn.fetchval = AsyncMock(return_value=3)

        response = client.get(
            "/api/v1/evaluations?sort_by=final_score&sort_order=desc",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        # Highest score first: 82.25 > 78.50 > 65.00
        assert items[0]["final_score"] == 82.25
        assert items[1]["final_score"] == 78.5
        assert items[2]["final_score"] == 65.0


def test_list_evaluations_invalid_sort(client):
    """Test sort_by=invalid_column returns 422."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        response = client.get(
            "/api/v1/evaluations?sort_by=invalid_column",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 422


def test_list_evaluations_empty(client):
    """Test no evaluations returns empty response with correct shape."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetch = AsyncMock(return_value=[])
        mock_svc_conn.fetchval = AsyncMock(return_value=0)

        response = client.get(
            "/api/v1/evaluations",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["limit"] == 20
        assert data["pages"] == 0


def test_list_evaluations_auth_required(client):
    """Test GET /evaluations without auth returns 401."""
    response = client.get("/api/v1/evaluations")
    assert response.status_code == 401


# --- Search tests (Story 4.2) ---


def _setup_search_mocks(mock_verify, mock_db, mock_user_queries, mock_svc_db, fetch_return, fetchval_return):
    """Shared setup for search tests."""
    _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
    mock_svc_conn = AsyncMock()
    mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
    mock_svc_conn.fetch = AsyncMock(return_value=fetch_return)
    mock_svc_conn.fetchval = AsyncMock(return_value=fetchval_return)
    return mock_svc_conn


def test_search_evaluations_by_brand_name(client):
    """Test search=Nike returns only matching evaluations."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_search_mocks(
            mock_verify, mock_db, mock_user_queries, mock_svc_db,
            fetch_return=[EVAL_ROW_1], fetchval_return=1,
        )

        response = client.get(
            "/api/v1/evaluations?search=Nike",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["brand_name"] == "Nike Indonesia"


def test_search_partial_match(client):
    """Test partial match: search=Nik matches 'Nike Indonesia'."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_search_mocks(
            mock_verify, mock_db, mock_user_queries, mock_svc_db,
            fetch_return=[EVAL_ROW_1], fetchval_return=1,
        )

        response = client.get(
            "/api/v1/evaluations?search=Nik",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["brand_name"] == "Nike Indonesia"


def test_search_case_insensitive(client):
    """Test case-insensitive: search=nike matches 'Nike Indonesia'."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_search_mocks(
            mock_verify, mock_db, mock_user_queries, mock_svc_db,
            fetch_return=[EVAL_ROW_1], fetchval_return=1,
        )

        response = client.get(
            "/api/v1/evaluations?search=nike",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["brand_name"] == "Nike Indonesia"


def test_search_no_results(client):
    """Test no matches returns empty list with total=0, pages=0."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_search_mocks(
            mock_verify, mock_db, mock_user_queries, mock_svc_db,
            fetch_return=[], fetchval_return=0,
        )

        response = client.get(
            "/api/v1/evaluations?search=NonExistentBrand",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["pages"] == 0


def test_search_with_pagination(client):
    """Test search results have correct total/pages for filtered set."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_search_mocks(
            mock_verify, mock_db, mock_user_queries, mock_svc_db,
            fetch_return=[EVAL_ROW_1], fetchval_return=3,
        )

        response = client.get(
            "/api/v1/evaluations?search=Nike&limit=1&page=1",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["pages"] == 3
        assert data["page"] == 1
        assert len(data["items"]) == 1


def test_search_with_sorting(client):
    """Test sorting applies within search-filtered results."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_search_mocks(
            mock_verify, mock_db, mock_user_queries, mock_svc_db,
            fetch_return=[EVAL_ROW_3, EVAL_ROW_1], fetchval_return=2,
        )

        response = client.get(
            "/api/v1/evaluations?search=a&sort_by=final_score&sort_order=desc",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        # Sorted by score desc: 82.25 > 78.50
        assert data["items"][0]["final_score"] == 82.25
        assert data["items"][1]["final_score"] == 78.5


def test_search_special_characters_escaped(client):
    """Test special characters in search don't break the query."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_search_mocks(
            mock_verify, mock_db, mock_user_queries, mock_svc_db,
            fetch_return=[], fetchval_return=0,
        )

        response = client.get(
            "/api/v1/evaluations?search=brand%25test",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0


def test_search_empty_returns_all(client):
    """Test empty/omitted search returns all evaluations."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        _setup_search_mocks(
            mock_verify, mock_db, mock_user_queries, mock_svc_db,
            fetch_return=[EVAL_ROW_1, EVAL_ROW_2, EVAL_ROW_3], fetchval_return=3,
        )

        # Empty search string
        response = client.get(
            "/api/v1/evaluations?search=",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3


# --- Query construction verification tests (Review M2) ---


def test_search_query_passes_escaped_params(client):
    """Verify that search with special chars calls DB with escaped value and correct param order."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        mock_svc_conn = _setup_search_mocks(
            mock_verify, mock_db, mock_user_queries, mock_svc_db,
            fetch_return=[], fetchval_return=0,
        )

        response = client.get(
            "/api/v1/evaluations?search=brand%25_test",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200

        # Verify conn.fetch was called with escaped search as $1, limit as $2, offset as $3
        fetch_call = mock_svc_conn.fetch.call_args
        query_sql = fetch_call.args[0]
        query_params = fetch_call.args[1:]

        # SQL must contain ILIKE with ESCAPE clause
        assert "ILIKE" in query_sql
        assert "ESCAPE" in query_sql

        # First param must be the escaped search term (% → \%, _ → \_)
        assert query_params[0] == "brand\\%\\_test"
        # Second param is limit, third is offset
        assert query_params[1] == 20  # default limit
        assert query_params[2] == 0   # page 1 → offset 0


def test_search_query_no_where_when_empty(client):
    """Verify that empty search doesn't include WHERE clause — only limit/offset params."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_svc_db,
    ):
        mock_svc_conn = _setup_search_mocks(
            mock_verify, mock_db, mock_user_queries, mock_svc_db,
            fetch_return=[EVAL_ROW_1], fetchval_return=1,
        )

        response = client.get(
            "/api/v1/evaluations",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200

        # Verify conn.fetch was called with only 2 params (limit, offset) — no search param
        fetch_call = mock_svc_conn.fetch.call_args
        query_sql = fetch_call.args[0]
        query_params = fetch_call.args[1:]

        assert "ILIKE" not in query_sql
        assert len(query_params) == 2  # limit and offset only
