"""Pydantic schemas for evaluations module."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

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


VerdictType = Literal["✔️", "❌", "❌ Non Mall", "❌ No Brand", "❌ Opex", "⭕️", ""]


class ScoringRequest(BaseModel):
    """Request body for generating a final score."""

    template: CategoryType
    verdict: VerdictType
    store_name: str = Field(max_length=200)
    period: str = Field(max_length=50)
    brand_name: str = Field(max_length=200)
    email: str | None = Field(default=None, max_length=254)


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
    available: bool = True


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


# ---------------------------------------------------------------------------
# Save evaluation schemas
# ---------------------------------------------------------------------------


class EvaluationListItem(BaseModel):
    """A single evaluation in the history list."""

    id: int
    brand_name: str
    final_score: float
    verdict: str
    template: str
    evaluator_email: str
    created_at: datetime


class EvaluationListResponse(BaseModel):
    """Paginated list of evaluations."""

    items: list[EvaluationListItem]
    total: int
    page: int
    limit: int
    pages: int


class EvaluationDetailResponse(BaseModel):
    """Full evaluation detail for the detail view page."""

    id: int
    brand_id: int
    brand_name: str
    final_score: float
    verdict: str
    template: str
    score_breakdown: list[dict[str, Any]]
    calculator_results: dict[str, Any]
    manual_inputs: dict[str, Any]
    email_output: str | None = None
    evaluator_email: str
    created_at: datetime
    rule_version: int


class SaveEvaluationRequest(BaseModel):
    """Request body for saving a completed evaluation as a permanent record."""

    template: CategoryType
    final_score: float
    verdict: VerdictType
    score_breakdown: list[dict[str, Any]]
    calculator_results: dict[str, Any]
    manual_inputs: dict[str, Any]
    rule_version: int = 1
    email_output: str | None = None


class SaveEvaluationResponse(BaseModel):
    """Response after successfully saving an evaluation."""

    id: int
    brand_id: int
    final_score: float
    verdict: str
    template: str
    created_at: datetime
