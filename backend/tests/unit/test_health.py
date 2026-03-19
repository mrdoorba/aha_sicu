"""Tests for the /health endpoint."""

from unittest.mock import AsyncMock, MagicMock, patch

from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_health_returns_healthy_when_db_ok():
    """Health check returns 200 with database ok when pool is available."""
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value=1)

    mock_pool = MagicMock()
    mock_pool.__bool__ = MagicMock(return_value=True)

    with patch("app.main.db") as mock_db:
        mock_db.pool = mock_pool
        mock_db.connection = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_conn),
            __aexit__=AsyncMock(return_value=False),
        ))

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["checks"]["database"] == "ok"


async def test_health_returns_503_when_db_unreachable():
    """Health check returns 503 with database unreachable when connection fails."""
    mock_pool = MagicMock()
    mock_pool.__bool__ = MagicMock(return_value=True)

    with patch("app.main.db") as mock_db:
        mock_db.pool = mock_pool
        mock_db.connection = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(side_effect=OSError("Connection refused")),
            __aexit__=AsyncMock(return_value=False),
        ))

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["checks"]["database"] == "unreachable"


async def test_health_returns_healthy_when_no_pool():
    """Health check returns 200 with not_configured when pool is None."""
    with patch("app.main.db") as mock_db:
        mock_db.pool = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["checks"]["database"] == "not_configured"
