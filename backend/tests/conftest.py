"""Shared pytest fixtures and configuration."""

import os
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_db_connection
from app.main import app


def create_test_token(
    role: str = "member",
    email: str = "test@example.com",
    uid: str = "test-uid",
) -> dict:
    """Create a mock user dict for authentication fixtures.

    Returns the user dict that get_current_user would return.
    """
    return {
        "id": 1,
        "firebase_uid": uid,
        "email": email,
        "role": role,
    }


@pytest.fixture
def mock_db_conn():
    """Create a mock database connection with transaction support."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow = AsyncMock(return_value=None)
    mock_conn.fetch = AsyncMock(return_value=[])
    mock_conn.fetchval = AsyncMock(return_value=0)
    mock_conn.execute = AsyncMock(return_value="OK")

    @asynccontextmanager
    async def _mock_transaction():
        yield

    mock_conn.transaction = _mock_transaction
    return mock_conn


@pytest.fixture
def client(mock_db_conn):
    """Create test client for API testing with mocked DB connection."""

    async def _override():
        yield mock_db_conn

    app.dependency_overrides[get_db_connection] = _override
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_connection, None)


@pytest.fixture
def authenticated_client(client, mock_db_conn):
    """Create an authenticated test client with a default member user.

    Patches Firebase token verification and user lookup to return
    a mock user. Use `auth_client_as` for specific roles.
    """
    user = create_test_token(role="member")
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_queries,
    ):
        mock_verify.return_value = {"uid": user["firebase_uid"], "email": user["email"]}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_queries.get_user_by_firebase_uid = AsyncMock(return_value=user)
        mock_queries.update_last_login = AsyncMock()
        yield client


@pytest.fixture
def auth_headers():
    """Fixture factory that returns auth headers + patches for a given role.

    Usage:
        def test_something(client, auth_headers):
            user, headers, patches = auth_headers("admin")
            with patches:
                response = client.get("/api/v1/me", headers=headers)
    """

    def _make(role: str = "member", email: str = "test@example.com", uid: str = "test-uid"):
        user = create_test_token(role=role, email=email, uid=uid)
        headers = {"Authorization": "Bearer mock-token"}

        mock_verify = patch("app.core.dependencies.verify_firebase_token")
        mock_db = patch("app.core.dependencies.db")
        mock_queries = patch("app.core.dependencies.user_queries")

        class _AuthContext:
            """Context manager that patches auth dependencies."""

            def __enter__(self):
                self._verify = mock_verify.start()
                self._db = mock_db.start()
                self._queries = mock_queries.start()

                self._verify.return_value = {"uid": uid, "email": email}
                mock_conn = AsyncMock()
                self._db.connection.return_value.__aenter__.return_value = mock_conn
                self._queries.get_user_by_firebase_uid = AsyncMock(return_value=user)
                self._queries.update_last_login = AsyncMock()
                return self

            def __exit__(self, *args):
                mock_verify.stop()
                mock_db.stop()
                mock_queries.stop()

        return user, headers, _AuthContext()

    return _make


@pytest.fixture
async def pg_conn():
    """A real Postgres connection inside a transaction that is always rolled back.

    Skips when DATABASE_URL is unset or unreachable, so the suite still runs on a
    machine with no database. Use this only for behaviour that lives in SQL --
    ordering, filtering, constraints -- where a mocked connection proves nothing.
    """
    import asyncpg

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        pytest.skip("DATABASE_URL not set")

    try:
        conn = await asyncpg.connect(dsn)
    except (OSError, asyncpg.PostgresError) as exc:
        pytest.skip(f"Postgres unreachable: {exc}")

    txn = conn.transaction()
    await txn.start()
    try:
        yield conn
    finally:
        await txn.rollback()
        await conn.close()
