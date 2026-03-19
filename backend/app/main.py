"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware, app_exception_handler
from app.core.security import init_firebase
from app.db.connection import db
from app.modules.accounts.router import router as accounts_router
from app.modules.auth.router import router as auth_router
from app.modules.brands.router import router as brands_router
from app.modules.evaluations.router import router as evaluations_router
from app.modules.sync.router import router as sync_router
from app.modules.rules.router import router as rules_router
from app.modules.email.router import router as email_router
from app.modules.config.router import router as config_router
from app.modules.upload.router import router as upload_router

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    # Startup
    init_firebase(settings)
    if settings.effective_database_url:
        await db.init(settings.effective_database_url, settings.database_pool_min, settings.database_pool_max)
    yield
    # Shutdown
    await db.close()


app = FastAPI(title="Store ICU API", version="0.1.0", lifespan=lifespan)

# Request logging + correlation IDs (outermost — wraps all requests)
app.add_middleware(RequestLoggingMiddleware)

# CORS — origins from CORS_ORIGINS env var (defaults to localhost for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions — no internal details to client (F-07-005)."""
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


app.add_exception_handler(Exception, global_exception_handler)

# Register routers
app.include_router(accounts_router)
app.include_router(auth_router)
app.include_router(brands_router)
app.include_router(config_router)
app.include_router(email_router)
app.include_router(evaluations_router)
app.include_router(rules_router)
app.include_router(sync_router)
app.include_router(upload_router)


@app.get("/health")
async def health_check() -> dict:
    """Health check — verifies DB connectivity for Cloud Run readiness."""
    checks: dict[str, str] = {}
    healthy = True

    if db.pool:
        try:
            async with db.connection() as conn:
                await conn.fetchval("SELECT 1")
            checks["database"] = "ok"
        except Exception:
            logger.warning("Health check DB probe failed", exc_info=True)
            checks["database"] = "unreachable"
            healthy = False
    else:
        checks["database"] = "not_configured"

    if not healthy:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "checks": checks},
        )
    return {"status": "healthy", "checks": checks}
