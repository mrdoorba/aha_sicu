"""Integration tests for the evaluation list endpoint."""

from datetime import date, datetime, timezone
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


def _setup_eval_query_mocks(mock_eq, list_return, count_return):
    """Set up eval_queries mocks for list + count."""
    mock_eq.list_evaluations = AsyncMock(return_value=list_return)
    mock_eq.count_evaluations = AsyncMock(return_value=count_return)


def test_list_evaluations_success(client):
    """Test GET /evaluations returns paginated list with correct fields."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_1, EVAL_ROW_2], 2)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        mock_eq.list_evaluations = AsyncMock(
            side_effect=[[EVAL_ROW_1, EVAL_ROW_2], [EVAL_ROW_3]]
        )
        mock_eq.count_evaluations = AsyncMock(return_value=3)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_1, EVAL_ROW_2, EVAL_ROW_3], 3)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_3, EVAL_ROW_2, EVAL_ROW_1], 3)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_3, EVAL_ROW_1, EVAL_ROW_2], 3)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [], 0)

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


def test_search_evaluations_by_brand_name(client):
    """Test search=Nike returns only matching evaluations."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_1], 1)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_1], 1)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_1], 1)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [], 0)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_1], 3)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_3, EVAL_ROW_1], 2)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [], 0)

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
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_1, EVAL_ROW_2, EVAL_ROW_3], 3)

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
    """Verify that search with special chars passes escaped value to query layer."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [], 0)

        response = client.get(
            "/api/v1/evaluations?search=brand%25_test",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200

        # Verify list_evaluations was called with the search parameter
        list_call = mock_eq.list_evaluations.call_args
        assert list_call.kwargs["search"] == "brand%_test"


def test_search_query_no_where_when_empty(client):
    """Verify that empty search passes None to query layer."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_1], 1)

        response = client.get(
            "/api/v1/evaluations",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200

        # Verify list_evaluations was called without search
        list_call = mock_eq.list_evaluations.call_args
        assert list_call.kwargs["search"] is None


# --- Date filter tests (Story 4.3) ---


EVAL_ROW_JAN = {
    "id": 10,
    "brand_name": "January Brand",
    "final_score": Decimal("70.00"),
    "verdict": "✔️",
    "template": "fashion",
    "evaluator_email": "rina@company.com",
    "created_at": datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
}

EVAL_ROW_FEB_EARLY = {
    "id": 11,
    "brand_name": "Feb Early Brand",
    "final_score": Decimal("75.00"),
    "verdict": "✔️",
    "template": "non_fashion",
    "evaluator_email": "budi@company.com",
    "created_at": datetime(2026, 2, 5, 14, 0, 0, tzinfo=timezone.utc),
}

EVAL_ROW_FEB_LATE = {
    "id": 12,
    "brand_name": "Nike Indonesia",
    "final_score": Decimal("80.00"),
    "verdict": "✔️",
    "template": "fashion",
    "evaluator_email": "rina@company.com",
    "created_at": datetime(2026, 2, 28, 23, 59, 0, tzinfo=timezone.utc),
}


def test_filter_by_date_range(client):
    """Test date_from + date_to returns only evaluations within range."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_FEB_EARLY], 1)

        response = client.get(
            "/api/v1/evaluations?date_from=2026-02-01&date_to=2026-02-15",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1


def test_filter_date_from_only(client):
    """Test date_from only — returns evaluations from that date onwards."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_FEB_EARLY, EVAL_ROW_FEB_LATE], 2)

        response = client.get(
            "/api/v1/evaluations?date_from=2026-02-01",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2


def test_filter_date_to_only(client):
    """Test date_to only — returns evaluations up to and including that date."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_JAN], 1)

        response = client.get(
            "/api/v1/evaluations?date_to=2026-01-31",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1


def test_filter_date_to_inclusive_end_of_day(client):
    """Test date_to passes correct date to query layer for inclusive end-of-day."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_FEB_LATE], 1)

        response = client.get(
            "/api/v1/evaluations?date_to=2026-02-28",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200

        # Verify query layer receives the date_to for end-of-day handling
        list_call = mock_eq.list_evaluations.call_args
        assert list_call.kwargs["date_to"] == date(2026, 2, 28)


def test_filter_date_combined_with_search(client):
    """Test date filter AND search filter combine (AND logic)."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_FEB_LATE], 1)

        response = client.get(
            "/api/v1/evaluations?search=Nike&date_from=2026-02-01&date_to=2026-02-28",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["brand_name"] == "Nike Indonesia"

        # Verify both search and date params were passed to query layer
        list_call = mock_eq.list_evaluations.call_args
        assert list_call.kwargs["search"] == "Nike"
        assert list_call.kwargs["date_from"] == date(2026, 2, 1)
        assert list_call.kwargs["date_to"] == date(2026, 2, 28)


def test_filter_no_dates_returns_all(client):
    """Test omitting both date params returns all evaluations (existing behavior)."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(
            mock_eq,
            [EVAL_ROW_JAN, EVAL_ROW_FEB_EARLY, EVAL_ROW_FEB_LATE],
            3,
        )

        response = client.get(
            "/api/v1/evaluations",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3


def test_filter_invalid_date_returns_422(client):
    """Test invalid date format returns 422 Unprocessable Entity."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        response = client.get(
            "/api/v1/evaluations?date_from=not-a-date",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 422


def test_filter_invalid_date_to_returns_422(client):
    """Test invalid date_to format also returns 422."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        response = client.get(
            "/api/v1/evaluations?date_to=not-a-date",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 422


def test_filter_date_from_after_date_to_returns_422(client):
    """Test date_from > date_to returns 422 validation error."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        response = client.get(
            "/api/v1/evaluations?date_from=2026-02-28&date_to=2026-01-01",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 422
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"


def test_filter_date_with_pagination(client):
    """Test date-filtered results have correct total/pages."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)
        _setup_eval_query_mocks(mock_eq, [EVAL_ROW_FEB_EARLY], 5)

        response = client.get(
            "/api/v1/evaluations?date_from=2026-02-01&limit=2&page=1",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert data["pages"] == 3
        assert data["page"] == 1
        assert len(data["items"]) == 1


# --- Role access control tests ---


def _setup_auth_mocks_for_user(mock_verify, mock_db, mock_user_queries, mock_user):
    """Auth mock setup with a specific user."""
    mock_verify.return_value = {"uid": mock_user["firebase_uid"], "email": mock_user["email"]}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=mock_user)
    mock_user_queries.update_last_login = AsyncMock()


def test_list_evaluations_forbidden_member(client):
    """Test member cannot access evaluation list — returns 403."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks_for_user(mock_verify, mock_db, mock_user_queries, MOCK_MEMBER)

        response = client.get(
            "/api/v1/evaluations",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "RULE_ACCESS_DENIED"
