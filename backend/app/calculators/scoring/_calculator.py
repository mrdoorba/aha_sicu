"""Final Scoring Calculator — pure function, no I/O.

Implements the 75-row scoring system template (Fashion/Non-Fashion variants).
Combines manual inputs with Calculator 1-3 outputs to produce per-category
scores, total score, verdicts, G-column messages, and email body.

Spec: logic/scoring-system-template-sicu.md
"""

from __future__ import annotations

import math
import re
from typing import Any

from app.calculators.scoring.helpers import (  # noqa: F401
    INDO_MONTHS,
    _SafeDict,
    _extract_pct,
    _fmt_idr,
    _fmt_num_1dp,
    _fmt_num_2dp,
    _fmt_pct_0dp,
    _fmt_pct_1dp,
    _format_message_template,
    _generate_month_labels,
    _get_nested,
    _get_rule_category,
    _get_rule_value,
    _rounddown,
    _safe_num,
    _safe_str,
)
from app.calculators.scoring.models import CategoryScore, RowScore, ScoringResult
from app.calculators.scoring.rules import DEFAULT_RULES, PROMO_START_ROW, PROMO_TOOLS


# ---------------------------------------------------------------------------
# Per-category scoring functions
# ---------------------------------------------------------------------------


from app.calculators.scoring.categories import (  # noqa: F401
    _promo_verdict,
    _score_ads,
    _score_business,
    _score_campaign,
    _score_competition,
    _score_discount_row,
    _score_operational,
    _score_products,
    _score_promo_tools,
    _score_stock,
    _score_visitors,
)

# ---------------------------------------------------------------------------
# G-column message generation
# ---------------------------------------------------------------------------

from app.calculators.scoring.messages import (  # noqa: F401
    _generate_ads_messages,
    _generate_business_messages,
    _generate_campaign_messages,
    _generate_competition_messages,
    _generate_operational_messages,
    _generate_promo_messages,
    _generate_products_messages,
    _generate_visitors_messages,
)

from app.calculators.scoring.computations import (  # noqa: F401
    _assemble_email_body,
    _compute_g66,
    _compute_g68,
    _compute_g72,
    _compute_g73,
    _compute_g75,
    _parse_d73_percentages,
    _parse_g68_left,
)



# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def calculate_score(
    manual_data: dict,
    calculator_results: dict,
    template: str,
    verdict: str,
    store_name: str,
    period: str,
    brand_name: str,
    email: str | None = None,
    rules: dict | None = None,
    rule_version: int = 1,
) -> ScoringResult:
    """Compute the full scoring system.

    Pure function — no I/O, no database access.

    Args:
        manual_data: All manual input data (ManualData structure).
        calculator_results: Dict keyed by calculator_type with
            {details, output_text} for each.
        template: "fashion" or "non_fashion" (used only for is_fashion marketing flag).
        verdict: F75 user-selected verdict string.
        store_name: Store display name (G2).
        period: Period string (e.g., "Jan 2026").
        brand_name: Short brand name (H2).
        email: Optional email address (G3).
        rules: Optional rules dict from DB. Falls back to defaults when None.
        rule_version: Version of the rules used (from DB).

    Returns:
        ScoringResult with all scores, messages, and email body.
    """
    is_fashion = template == "fashion"

    # --- Per-category scoring ---
    cat_operational = _score_operational(manual_data, rules)
    cat_business = _score_business(manual_data, rules)
    cat_visitors = _score_visitors(manual_data, rules)
    cat_promo = _score_promo_tools(manual_data, rules)
    cat_products = _score_products(manual_data, rules)
    cat_ads = _score_ads(manual_data, template, rules)
    cat_campaign = _score_campaign(manual_data, rules)
    cat_competition = _score_competition(manual_data, calculator_results)
    cat_stock = _score_stock(calculator_results, rules)
    cat_discount = _score_discount_row(calculator_results, rules)

    # Apply Fashion-specific threshold for conversion rate (row 20)
    biz_rules = _get_rule_category(rules, "business")
    conv_threshold = _get_rule_value(biz_rules, "conversion_rate", "threshold", 3.0)
    conv_row = next((r for r in cat_business.rows if r.row == 20), None)
    if conv_row:
        conv_row.benchmark = f">{conv_threshold:.0f}%"
        conv_row.verdict = "✔️" if conv_row.value >= conv_threshold else "❌"

    all_categories = [
        cat_operational, cat_business, cat_visitors,
        cat_promo, cat_products, cat_ads, cat_campaign,
        cat_competition, cat_stock, cat_discount,
    ]

    # --- Total score (H4) ---
    total_score = sum(cat.score for cat in all_categories)

    # --- G-column messages ---
    _generate_operational_messages(cat_operational, manual_data, rules)
    _generate_business_messages(cat_business, manual_data, rules)
    _generate_visitors_messages(cat_visitors, rules)
    _generate_promo_messages(cat_promo, manual_data, rules)
    _generate_products_messages(cat_products, rules)
    _generate_ads_messages(cat_ads, manual_data, calculator_results, rules)
    _generate_campaign_messages(cat_campaign, rules)
    _generate_competition_messages(cat_competition, manual_data, rules)

    # --- Derived formulas ---
    d13 = _safe_num(_get_nested(manual_data, "business", "salesMonth0"))
    d49 = _safe_num(_get_nested(manual_data, "ads", "adCost"))
    d52 = d49 / d13 if d13 > 0 else 0.0

    d73_text = _get_nested(calculator_results, "discount", "output_text") or ""

    g68 = _compute_g68(d73_text, d52)
    g72 = _compute_g72(g68, d52, d73_text, is_fashion, rules)
    g73 = _compute_g73(verdict, g72, d13, rules)

    marketing_label = f"📌 Estimasi persentase biaya marketing {brand_name} sekarang:"

    g66 = _compute_g66(all_categories, manual_data, g68)
    g75 = _compute_g75(verdict, store_name, rules)

    # --- Email ---
    email_subject = f"🏥 AHA Store Internal Check Up (Store ICU) - {store_name} {period}"
    email_body = _assemble_email_body(
        all_categories, g66, marketing_label, g68, g73, g75,
    )

    return ScoringResult(
        total_score=total_score,
        category_scores=all_categories,
        verdict=verdict,
        conclusion=g66,
        marketing_estimation=g68,
        marketing_percentage=f"{g72 * 100:.0f}%",
        marketing_budget=g73,
        closing_message=g75,
        email_subject=email_subject,
        email_body=email_body,
        template=template,
        rule_version=rule_version,
    )
