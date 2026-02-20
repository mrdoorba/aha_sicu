"""Pydantic schemas for accounts module."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UserListResponse(BaseModel):
    """Single user in the accounts list."""

    id: int
    email: str
    role: str
    created_at: datetime
    last_login: datetime | None = None


class CreateAccountRequest(BaseModel):
    """Request body for creating a new account."""

    email: str
    password: str = Field(min_length=6)
    role: Literal["member", "leader", "admin"] = "member"


class UpdateRoleRequest(BaseModel):
    """Request body for updating a user's role."""

    role: Literal["member", "leader", "admin"]


class ResetPasswordRequest(BaseModel):
    """Request body for resetting a user's password."""

    password: str = Field(min_length=6)
