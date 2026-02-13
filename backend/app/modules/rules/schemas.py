"""Pydantic schemas for rules module."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator


class ScoringRuleUpdateRequest(BaseModel):
    """Request body for updating scoring rules."""

    rules: dict[str, Any]

    @field_validator("rules")
    @classmethod
    def rules_must_have_valid_structure(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not v:
            raise ValueError("rules must be a non-empty dict")
        for key, value in v.items():
            if not isinstance(value, dict):
                raise ValueError(
                    f"rules['{key}'] must be a dict, got {type(value).__name__}"
                )
        return v


class ScoringRuleResponse(BaseModel):
    """Scoring rule response matching the scoring_rules table."""

    id: int
    template: str
    rules: dict[str, Any]
    version: int
    updated_by: int | None = None
    updated_at: datetime

    @field_validator("rules", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any]:
        if isinstance(v, str):
            return json.loads(v)
        return v
