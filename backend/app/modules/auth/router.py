"""Auth API endpoints."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.modules.auth.schemas import UserResponse

router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)) -> UserResponse:
    """Get current authenticated user info."""
    return UserResponse(
        id=user["id"],
        email=user["email"],
        role=user["role"],
        last_login=user["last_login"],
    )
