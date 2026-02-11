"""Pydantic schemas for evaluations module."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class EvaluationStateResponse(BaseModel):
    """Current evaluation state for a brand+user pair."""

    brand_id: int
    category_type: str | None = None
    manual_data: dict[str, Any] | None = None
    updated_at: datetime | None = None


class EvaluationInputsUpdate(BaseModel):
    """Request body for saving evaluation inputs."""

    category_type: str | None = None
    manual_data: dict[str, Any] | None = None
