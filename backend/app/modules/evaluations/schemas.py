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


class CalculatorResultItem(BaseModel):
    """A single stored calculator result."""

    calculator_type: str
    output_text: str
    details: dict[str, Any]
    calculated_at: datetime


class CalculatorResultsListResponse(BaseModel):
    """Response for fetching all stored calculator results for a brand."""

    brand_id: int
    results: list[CalculatorResultItem]


class RunCalculatorItem(BaseModel):
    """Result of running a single calculator."""

    calculator_type: str
    status: str  # "success", "skipped", "error"
    result: dict[str, Any] | None = None
    reason: str | None = None


class RunAllResponse(BaseModel):
    """Response for run-all calculators endpoint."""

    results: list[RunCalculatorItem]


# ---------------------------------------------------------------------------
# Scoring schemas
# ---------------------------------------------------------------------------


class ScoringRequest(BaseModel):
    """Request body for generating a final score."""

    template: CategoryType
    verdict: str
    store_name: str
    period: str
    brand_name: str
    email: str | None = None


class RowScoreItem(BaseModel):
    """A single metric row score."""

    row: int
    metric: str
    value: Any
    benchmark: str
    verdict: str
    message: str
    score: float


class CategoryScoreItem(BaseModel):
    """Per-category score breakdown."""

    category: str
    score: float
    max_score: float
    rows: list[RowScoreItem]


class ScoringResponse(BaseModel):
    """Response for scoring endpoint — complete scoring result."""

    total_score: float
    category_scores: list[CategoryScoreItem]
    verdict: str
    conclusion: str
    marketing_estimation: str
    marketing_percentage: str
    marketing_budget: str
    closing_message: str
    email_subject: str
    email_body: str
    whatsapp_link: str
    template: str
