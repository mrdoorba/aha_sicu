"""Auth API endpoints."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.db.connection import db
from app.db.queries import users as user_queries
from app.modules.auth.schemas import UpdateLanguageRequest, UserResponse

router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)) -> UserResponse:
    """Get current authenticated user info."""
    return UserResponse(
        id=user["id"],
        email=user["email"],
        role=user["role"],
        language=user.get("language", "id"),
        last_login=user["last_login"],
    )


@router.patch("/me/language", response_model=UserResponse)
async def update_language(
    body: UpdateLanguageRequest,
    user: dict = Depends(get_current_user),
) -> UserResponse:
    """Update current user's language preference."""
    async with db.connection() as conn:
        updated = await user_queries.update_language(conn, user["id"], body.language)
    return UserResponse(
        id=updated["id"],
        email=updated["email"],
        role=updated["role"],
        language=updated["language"],
        last_login=updated["last_login"],
    )
