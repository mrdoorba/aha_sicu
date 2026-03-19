"""Tests for main FastAPI application."""

from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_health_check_returns_healthy():
    """Test that health check endpoint returns healthy status."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "checks" in data


async def test_generic_500_when_unhandled_exception():
    """Unhandled exceptions return generic 500 with no internal details (F-07-005)."""
    from fastapi import APIRouter

    _err_router = APIRouter()

    @_err_router.get("/_test/crash")
    async def _crash() -> None:
        raise RuntimeError("deliberate test crash")

    app.include_router(_err_router)
    try:
        # raise_app_exceptions=False: Starlette's ServerErrorMiddleware re-raises
        # after sending response; we need httpx to capture the response, not the re-raise.
        async with AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            response = await client.get("/_test/crash")

        assert response.status_code == 500
        body = response.json()
        assert body == {"error": "Internal server error"}

        raw = response.text
        assert "Traceback" not in raw
        assert "File " not in raw
        assert ".py" not in raw
        assert "RuntimeError" not in raw
    finally:
        app.routes[:] = [r for r in app.routes if getattr(r, "path", "") != "/_test/crash"]
