"""Tests for RequestLoggingMiddleware — correlation IDs and access logging."""

import logging

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.logging import request_id_var
from app.main import app


@pytest.fixture()
def client() -> AsyncClient:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    return AsyncClient(transport=transport, base_url="http://test")



async def test_response_includes_request_id_when_none_sent(client: AsyncClient) -> None:
    resp = await client.get("/health")

    assert "x-request-id" in resp.headers
    # Should be a UUID-like string
    rid = resp.headers["x-request-id"]
    assert len(rid) == 36  # UUID format: 8-4-4-4-12



async def test_response_echoes_client_request_id(client: AsyncClient) -> None:
    resp = await client.get("/health", headers={"X-Request-ID": "my-trace-123"})

    assert resp.headers["x-request-id"] == "my-trace-123"



async def test_health_excluded_from_access_log(
    client: AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="app.core.middleware"):
        await client.get("/health")

    access_messages = [r.message for r in caplog.records if "GET /health" in r.message]
    assert access_messages == []



async def test_access_log_contains_required_fields(
    client: AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="app.core.middleware"):
        await client.get("/api/v1/brands?q=test")

    access_records = [
        r for r in caplog.records if "GET /api/v1/brands" in r.message
    ]
    assert len(access_records) == 1

    msg = access_records[0].message
    # Format: "GET /api/v1/brands 401 3.2ms" (or similar status)
    parts = msg.split()
    assert parts[0] == "GET"
    assert "/api/v1/brands" in parts[1]
    # Status code is a number
    assert parts[2].isdigit()
    # Duration ends with "ms"
    assert parts[3].endswith("ms")



async def test_access_log_emitted_on_500_error(
    client: AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    """Middleware must log access even when handler raises (AC-3a)."""
    from fastapi import APIRouter

    # Add a route that raises an unhandled exception
    _error_router = APIRouter()

    @_error_router.get("/test-500-logging")
    async def _raise_error() -> None:
        raise RuntimeError("deliberate test error")

    app.include_router(_error_router)

    try:
        with caplog.at_level(logging.ERROR, logger="app.core.middleware"):
            resp = await client.get("/test-500-logging")

        assert resp.status_code == 500
        assert "x-request-id" in resp.headers

        # Access log should contain a 500 entry
        access_records = [
            r
            for r in caplog.records
            if "GET /test-500-logging" in r.message and "500" in r.message
        ]
        assert len(access_records) == 1
    finally:
        # Clean up injected route
        app.routes[:] = [r for r in app.routes if getattr(r, "path", "") != "/test-500-logging"]



async def test_correlation_id_cleaned_up_between_requests(
    client: AsyncClient,
) -> None:
    """Context var must not leak between requests."""
    # After request completes, request_id_var should be back to default
    await client.get("/health", headers={"X-Request-ID": "leak-check-123"})

    assert request_id_var.get() == "no-request"
