"""Pydantic schemas for evaluations module."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

CategoryType = Literal["fashion", "non_fashion"]


class EvaluationStateResponse(BaseModel):
    """Current evaluation state for a brand+user pair."""

    brand_id: int
    category_type: CategoryType | None = None
    manual_data: dict[str, Any] | None = None
    updated_at: datetime | None = None


class EvaluationInputsUpdate(BaseModel):
    """Request body for saving evaluation inputs."""

    category_type: CategoryType | None = None
    manual_data: dict[str, Any] | None = None


class CalculatorResultResponse(BaseModel):
    """Response for calculator execution."""

    calculator_type: str
    output_text: str
    details: dict[str, Any]
    calculated_at: datetime
