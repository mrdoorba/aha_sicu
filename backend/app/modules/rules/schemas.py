"""Pydantic schemas for rules module."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ScoringRuleResponse(BaseModel):
    """Scoring rule response matching the scoring_rules table."""

    id: int
    template: str
    rules: dict[str, Any]
    version: int
    updated_by: int | None = None
    updated_at: datetime
