"""Final Scoring Calculator — pure function, no I/O.

Implements the 75-row scoring system template (Fashion/Non-Fashion variants).
Combines manual inputs with Calculator 1-3 outputs to produce per-category
scores, total score, verdicts, G-column messages, and email body.

Spec: logic/scoring-system-template-sicu.md
"""

from __future__ import annotations

from app.calculators.scoring.categories import (
    _score_ads,
    _score_business,
    _score_campaign,
    _score_competition,
    _score_operational,
    _score_products,
    _score_promo_tools,
    _score_stock,
    _score_visitors,
)
from app.calculators.scoring.computations import (
    _assemble_email_body,
    _compute_g66,
    _compute_g66_i18n,
    _compute_g68,
    _compute_g72,
    _compute_g73,
    _compute_g73_i18n,
    _compute_g75,
    _compute_g75_i18n,
)
from app.calculators.scoring.helpers import (
    _get_nested,
    _get_rule_category,
    _get_rule_value,
    _safe_num,
)
from app.calculators.scoring.messages import (
    _generate_ads_messages,
    _generate_business_messages,
    _generate_campaign_messages,
    _generate_competition_messages,
    _generate_operational_messages,
    _generate_promo_messages,
    _generate_products_messages,
    _generate_visitors_messages,
)
from app.calculators.scoring.models import ScoringResult, TranslatableText

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
    marketplace: str = "ID",
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
    cat_competition = _score_competition(manual_data, calculator_results, marketplace=marketplace)
    cat_stock = _score_stock(calculator_results, rules)

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
        cat_competition, cat_stock,
    ]

    # --- Total score (H4) ---
    total_score = sum(cat.score for cat in all_categories)

    # --- G-column messages ---
    _generate_operational_messages(cat_operational, manual_data, rules)
    _generate_business_messages(cat_business, manual_data, rules, marketplace=marketplace)
    _generate_visitors_messages(cat_visitors, rules)
    _generate_promo_messages(cat_promo, manual_data, rules)
    _generate_products_messages(cat_products, rules)
    _generate_ads_messages(cat_ads, manual_data, calculator_results, rules)
    _generate_campaign_messages(cat_campaign, rules)
    _generate_competition_messages(cat_competition, manual_data, rules, marketplace=marketplace)

    # --- Derived formulas ---
    d13 = _safe_num(_get_nested(manual_data, "business", "salesMonth0"))
    d49 = _safe_num(_get_nested(manual_data, "ads", "adCost"))
    d52 = d49 / d13 if d13 > 0 else 0.0

    d73_text = _get_nested(calculator_results, "discount", "output_text") or ""
    discount_details = _get_nested(calculator_results, "discount", "details")

    g68 = _compute_g68(d73_text, d52, discount_details=discount_details)
    g72 = _compute_g72(g68, d52, d73_text, is_fashion, rules, discount_details=discount_details)
    g73 = _compute_g73(verdict, g72, d13, rules)

    marketing_label = f"📌 Estimasi persentase biaya marketing {brand_name} sekarang:"

    g66 = _compute_g66(all_categories, manual_data, g68, marketplace=marketplace)
    g75 = _compute_g75(verdict, store_name, rules)

    # --- i18n companions ---
    g66_i18n = _compute_g66_i18n(all_categories, manual_data, g68, marketplace=marketplace)
    g73_i18n = _compute_g73_i18n(verdict, g72, d13, rules)
    g75_i18n = _compute_g75_i18n(verdict, store_name, rules)
    email_subject_i18n = TranslatableText(
        key="email.subject",
        vars={"store": store_name, "period": period},
    )

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
        conclusion_i18n=g66_i18n,
        marketing_budget_i18n=g73_i18n,
        closing_message_i18n=g75_i18n,
        email_subject_i18n=email_subject_i18n,
    )
