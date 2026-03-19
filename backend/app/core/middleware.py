"""Middleware: request logging, correlation IDs, error handling."""

import logging
import time
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.core.exceptions import AppException
from app.core.logging import request_id_var

logger = logging.getLogger(__name__)

# Paths excluded from access logging (readiness probes, etc.)
_SILENT_PATHS: frozenset[str] = frozenset({"/health"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Assign correlation IDs and emit structured access logs for every request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        rid = request.headers.get("x-request-id") or str(uuid4())
        token = request_id_var.set(rid)
        start = time.monotonic()
        status_code = 500  # default if call_next never returns

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            # BaseHTTPMiddleware may re-raise app exceptions even after the
            # exception handler has produced a response.  Return our own 500
            # so the correlation header is always present.
            logger.exception("Unexpected error in middleware dispatch")
            response = JSONResponse(
                status_code=500,
                content={"error": "Internal server error"},
            )
        finally:
            duration_ms = round((time.monotonic() - start) * 1000, 1)
            if request.url.path not in _SILENT_PATHS:
                _log_access(request.method, request.url.path, status_code, duration_ms)
            request_id_var.reset(token)

        response.headers["X-Request-ID"] = rid
        return response


def _log_access(method: str, path: str, status_code: int, duration_ms: float) -> None:
    """Emit a structured access log entry at the appropriate severity."""
    msg = "%s %s %d %.1fms"
    args = (method, path, status_code, duration_ms)
    if status_code >= 500:
        logger.error(msg, *args)
    elif status_code >= 400:
        logger.warning(msg, *args)
    else:
        logger.info(msg, *args)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions with structured JSON response."""
    logger.error(
        "Application error: code=%s detail=%s path=%s method=%s",
        exc.code,
        exc.detail,
        request.url.path,
        request.method,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "detail": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
