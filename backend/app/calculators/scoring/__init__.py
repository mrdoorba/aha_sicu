"""Scoring calculator package.

Re-exports all public names so that existing imports like
``from app.calculators.scoring import calculate_score`` continue to work.
"""

from app.calculators.scoring._calculator import calculate_score  # noqa: F401
from app.calculators.scoring.categories import (  # noqa: F401
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
)
from app.calculators.scoring.computations import (  # noqa: F401
    _compute_g68,
    _compute_g72,
    _compute_g73,
    _compute_g75,
    _parse_d73_percentages,
    _parse_g68_left,
)
from app.calculators.scoring.helpers import (  # noqa: F401
    _format_message_template,
    _generate_month_labels,
)
from app.calculators.scoring.messages import (  # noqa: F401
    _generate_business_messages,
)
from app.calculators.scoring.models import (  # noqa: F401
    CategoryScore,
    RowScore,
    ScoringResult,
)
from app.calculators.scoring.rules import (  # noqa: F401
    DEFAULT_RULES,
    PROMO_START_ROW,
    PROMO_TOOLS,
)
