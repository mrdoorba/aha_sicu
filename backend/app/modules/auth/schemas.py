"""Auth API schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Response schema for authenticated user info."""

    id: int
    email: str
    role: str
    language: str = "id"
    last_login: datetime | None


class UpdateLanguageRequest(BaseModel):
    """Request body for updating language preference."""

    language: Literal["id", "en", "th"]
