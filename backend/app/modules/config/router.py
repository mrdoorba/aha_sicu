"""Configuration API endpoints for exposing feature flags."""

from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/api/v1/config", tags=["config"])


@router.get("/features")
async def get_features() -> dict[str, bool]:
    """Return current feature flags."""
    return {"email_enabled": settings.email_enabled}
