"""Middleware: logging, error handling."""

import logging
from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions with structured JSON response."""
    # Log error with context
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
