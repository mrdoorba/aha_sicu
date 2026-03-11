"""Scoring result types — pure data, no logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TranslatableText:
    """Structured data for frontend i18n rendering."""

    key: str                         # i18n translation key
    vars: dict[str, str]             # interpolation variables


@dataclass
class RowScore:
    """Score for a single metric row."""

    row: int
    metric: str
    value: Any           # D column: raw value
    benchmark: str       # E column: threshold
    verdict: str         # F column: "✔️" or "❌" or "-"
    message: str         # G column: text output
    score: float         # H column: points


@dataclass
class CategoryScore:
    """Aggregated score for a category."""

    category: str
    score: float
    max_score: float
    rows: list[RowScore] = field(default_factory=list)
    available: bool = True  # False when required calculator data is missing


@dataclass
class ScoringResult:
    """Complete result of the scoring system."""

    total_score: float
    category_scores: list[CategoryScore]
    verdict: str                     # F75 value
    conclusion: str                  # G66
    marketing_estimation: str        # G68
    marketing_percentage: str        # G72
    marketing_budget: str            # G73
    closing_message: str             # G75
    email_subject: str
    email_body: str                  # G1 assembled
    template: str                    # "fashion" or "non_fashion"
    rule_version: int = 1            # Version of rules used for scoring
