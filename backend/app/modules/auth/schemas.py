"""Auth API schemas."""

from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Response schema for authenticated user info."""

    id: int
    email: str
    role: str
    last_login: datetime | None
