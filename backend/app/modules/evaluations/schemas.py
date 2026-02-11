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


class SingleCalculatorStatus(BaseModel):
    """Readiness status for a single calculator."""

    status: str  # "ready" or "pending"
    has_result: bool
    required_files: list[str]
    required_manual: list[str] = []
    available_files: list[str]
    missing_files: list[str]
    missing_manual: list[str] = []
    calculated_at: datetime | None = None


class CalculatorStatusResponse(BaseModel):
    """Status of all calculators for a brand."""

    brand_id: int
    calculators: dict[str, SingleCalculatorStatus]


class RunCalculatorItem(BaseModel):
    """Result of running a single calculator."""

    calculator_type: str
    status: str  # "success", "skipped", "error"
    result: dict[str, Any] | None = None
    reason: str | None = None


class RunAllResponse(BaseModel):
    """Response for run-all calculators endpoint."""

    results: list[RunCalculatorItem]
