"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import AppException
from app.core.middleware import app_exception_handler
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

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s: %(message)s")


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

# CORS — allow Firebase Hosting origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "https://aha-coms-sicu-dev.web.app",
        "https://aha-coms-sicu-dev.firebaseapp.com",
        "https://aha-coms-sicu-prod.web.app",
        "https://aha-coms-sicu-prod.firebaseapp.com",
        "https://sicu.ahabot.ai",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)

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
async def health_check() -> dict[str, str]:
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy"}
