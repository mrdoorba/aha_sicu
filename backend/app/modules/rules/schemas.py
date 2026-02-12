"""Pydantic schemas for rules module."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, field_validator


class ScoringRuleUpdateRequest(BaseModel):
    """Request body for updating scoring rules."""

    rules: dict[str, Any]

    @field_validator("rules")
    @classmethod
    def rules_must_be_non_empty(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not v:
            raise ValueError("rules must be a non-empty dict")
        return v


class ScoringRuleResponse(BaseModel):
    """Scoring rule response matching the scoring_rules table."""

    id: int
    template: Literal["fashion", "non_fashion"]
    rules: dict[str, Any]
    version: int
    updated_by: int | None = None
    updated_at: datetime
