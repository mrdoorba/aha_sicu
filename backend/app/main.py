"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.config import settings
from app.core.exceptions import AppException
from app.core.middleware import app_exception_handler
from app.core.security import init_firebase
from app.db.connection import db
from app.modules.auth.router import router as auth_router
from app.modules.brands.router import router as brands_router
from app.modules.events.router import router as events_router
from app.modules.evaluations.router import router as evaluations_router
from app.modules.sync.router import router as sync_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    # Startup
    if settings.firebase_credentials_path or settings.firebase_credentials_json:
        init_firebase(settings)
    if settings.database_url:
        await db.init(settings.database_url, settings.database_pool_min, settings.database_pool_max)
    yield
    # Shutdown
    await db.close()


app = FastAPI(title="Store ICU API", version="0.1.0", lifespan=lifespan)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)

# Register routers
app.include_router(auth_router)
app.include_router(brands_router)
app.include_router(evaluations_router)
app.include_router(events_router)
app.include_router(sync_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy"}
