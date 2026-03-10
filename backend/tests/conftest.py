"""Shared pytest fixtures and configuration."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_db_connection
from app.main import app


@pytest.fixture
def client():
    """Create test client for API testing with mocked DB connection."""
    mock_conn = AsyncMock()

    @asynccontextmanager
    async def _mock_transaction():
        yield

    mock_conn.transaction = _mock_transaction

    async def _override():
        yield mock_conn

    app.dependency_overrides[get_db_connection] = _override
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_connection, None)
