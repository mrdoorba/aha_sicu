"""Pydantic schemas for evaluations module."""

import json
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

CategoryType = Literal["fashion", "non_fashion"]


def _parse_json(v: Any) -> Any:
    if isinstance(v, str):
        return json.loads(v)
    return v


class EvaluationStateResponse(BaseModel):
    """Current evaluation state for a brand+user pair."""

    brand_id: int
    category_type: CategoryType | None = None
    manual_data: dict[str, Any] | None = None
    updated_at: datetime | None = None

    @field_validator("manual_data", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any] | None:
        if v is None:
            return None
        return _parse_json(v)


class EvaluationInputsUpdate(BaseModel):
    """Request body for saving evaluation inputs."""

    category_type: CategoryType | None = None
    manual_data: dict[str, Any] | None = None
    marketplace: str = "ID"


class CalculatorResultResponse(BaseModel):
    """Response for calculator execution."""

    calculator_type: str
    output_text: str
    details: dict[str, Any]
    calculated_at: datetime

    @field_validator("details", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any]:
        return _parse_json(v)


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

    @field_validator("details", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any]:
        return _parse_json(v)


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

    @field_validator("result", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any] | None:
        if v is None:
            return None
        return _parse_json(v)


class RunAllResponse(BaseModel):
    """Response for run-all calculators endpoint."""

    results: list[RunCalculatorItem]


# ---------------------------------------------------------------------------
# Scoring schemas
# ---------------------------------------------------------------------------


VerdictType = Literal["✔️", "❌", "❌ Non Mall", "❌ No Brand", "❌ Opex"]


class ScoringRequest(BaseModel):
    """Request body for generating a final score."""

    template: CategoryType
    verdict: VerdictType = ""
    store_name: str = Field(default="", max_length=200)
    period: str = Field(default="", max_length=50)
    brand_name: str = Field(default="", max_length=200)
    email: str | None = Field(default=None, max_length=254)


class TranslatableTextSchema(BaseModel):
    """i18n structured data for frontend translation."""

    key: str
    vars: dict[str, str] = {}


class RowScoreItem(BaseModel):
    """A single metric row score."""

    row: int
    metric: str
    value: Any
    benchmark: str
    verdict: str
    message: str
    score: float
    metric_i18n: TranslatableTextSchema | None = None
    value_i18n: TranslatableTextSchema | None = None
    message_i18n: TranslatableTextSchema | None = None
    benchmark_i18n: TranslatableTextSchema | None = None


class CategoryScoreItem(BaseModel):
    """Per-category score breakdown."""

    category: str
    score: float
    max_score: float
    rows: list[RowScoreItem]
    available: bool = True
    category_i18n: TranslatableTextSchema | None = None


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
    template: str
    rule_version: int
    conclusion_i18n: list[TranslatableTextSchema] | None = None
    marketing_budget_i18n: TranslatableTextSchema | None = None
    closing_message_i18n: TranslatableTextSchema | None = None
    email_subject_i18n: TranslatableTextSchema | None = None


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
    period: str = ""


class EvaluationListResponse(BaseModel):
    """Paginated list of evaluations."""

    items: list[EvaluationListItem]
    total: int
    page: int
    limit: int
    pages: int


class GroupedEvaluationItem(BaseModel):
    """A single brand in the grouped evaluation list."""

    brand_id: int
    brand_name: str
    evaluation_count: int
    top_score: float
    top_verdict: str
    latest_date: datetime


class GroupedEvaluationListResponse(BaseModel):
    """Paginated list of evaluations grouped by brand."""

    items: list[GroupedEvaluationItem]
    total: int
    page: int
    limit: int
    pages: int


class BrandEvaluationItem(BaseModel):
    """A single evaluation within a brand's evaluation list."""

    id: int
    final_score: float
    verdict: str
    template: str
    evaluator_email: str
    created_at: datetime
    period: str = ""


class BrandEvaluationListResponse(BaseModel):
    """List of evaluations for a specific brand."""

    items: list[BrandEvaluationItem]
    total: int


class BrandRawData(BaseModel):
    """Extracted brand raw_data fields needed for email composition."""

    email: str | None = None
    pic_name: str | None = None
    store_link: str | None = None
    kategori: str | None = None


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
    period: str = ""
    marketplace: str = "ID"
    brand_raw_data: BrandRawData = Field(default_factory=BrandRawData)

    @field_validator("score_breakdown", "calculator_results", "manual_inputs", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> Any:
        return _parse_json(v)


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
    period: str = ""
    marketplace: str = "ID"


class SaveEvaluationResponse(BaseModel):
    """Response after successfully saving an evaluation."""

    id: int
    brand_id: int
    final_score: float
    verdict: str
    template: str
    created_at: datetime
    period: str = ""
