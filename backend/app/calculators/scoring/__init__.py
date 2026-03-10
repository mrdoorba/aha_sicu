"""Scoring calculator package.

Re-exports all public names from the original scoring module so that
existing imports like ``from app.calculators.scoring import calculate_score``
continue to work.
"""

from app.calculators.scoring._calculator import (  # noqa: F401
    DEFAULT_RULES,
    PROMO_START_ROW,
    PROMO_TOOLS,
    _compute_g68,
    _compute_g72,
    _compute_g73,
    _compute_g75,
    _format_message_template,
    _generate_business_messages,
    _generate_month_labels,
    _parse_d73_percentages,
    _parse_g68_left,
    _promo_verdict,
    _score_ads,
    _score_business,
    _score_campaign,
    _score_discount_row,
    _score_operational,
    _score_products,
    _score_promo_tools,
    _score_stock,
    _score_visitors,
    calculate_score,
)
from app.calculators.scoring.models import (  # noqa: F401
    CategoryScore,
    RowScore,
    ScoringResult,
)
