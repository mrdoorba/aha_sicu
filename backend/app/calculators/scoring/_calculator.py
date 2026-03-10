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
# ---------------------------------------------------------------------------
# Complex derived formulas: G66, G68, G72, G73, G75
# ---------------------------------------------------------------------------

def _parse_d73_percentages(d73_text: str) -> tuple[float, float, float, float, float]:
    """Parse the 5 percentage values from Calculator 3 D73 output text.

    Returns (t, ra, rb, v, p) as fractions.
    """
    t = _extract_pct(r"% Diskon TOP SKU: ([\d.]+)%", d73_text)
    ra = _extract_pct(r"Range: ([\d.]+)%", d73_text)
    rb = _extract_pct(r"~ ([\d.]+)%", d73_text)
    v = _extract_pct(r"Voucher ([\d.]+)%", d73_text)
    p = _extract_pct(r"Paket Diskon ([\d.]+)%", d73_text)
    return t, ra, rb, v, p


def _compute_g68(d73_text: str, d52: float) -> str:
    """G68: Marketing cost estimation.

    Parses D73 discount text, combines with ad cost percentage (d52 as fraction).
    """
    if not d73_text:
        return ""

    t, ra, rb, v, p = _parse_d73_percentages(d73_text)

    low = (ra * t) + v + p + d52 + 0.05
    high = (rb * t) + v + p + d52 + 0.05

    result = f"{low * 100:.1f}% ~ {high * 100:.1f}%"

    if "Berpotensi" in d73_text or "fake discount" in d73_text.lower():
        result += "\n📌 Berpotensi menggunakan 'fake discount'"

    return result


def _parse_g68_left(g68_text: str) -> float:
    """Extract raw percentage before '~' from G68 text as a fraction.

    Spreadsheet equivalent: VALUE(LEFT(G68, FIND("~", G68)-1)) / 100
    e.g. "15.3% ~ 22.7%" → 0.153
    Returns 0.0 if no "~" found or text is empty.
    """
    if not g68_text or "~" not in g68_text:
        return 0.0
    left_part = g68_text.split("~")[0].strip()
    match = re.search(r"([\d.]+)", left_part)
    if match:
        return float(match.group(1)) / 100
    return 0.0


def _compute_g72(
    g68_text: str, d52: float, d73_text: str, is_fashion: bool,
    rules: dict | None = None,
) -> float:
    """G72: Recommended marketing percentage (as fraction).

    Complex MIN/MAX formula with Fashion adjustment.
    """
    mkt_rules = _get_rule_category(rules, "marketing")
    if is_fashion:
        floor = _get_rule_value(mkt_rules, "floor_fashion", "value", 0.15)
    else:
        floor = _get_rule_value(mkt_rules, "floor", "value", 0.12)
    base_subtraction = _get_rule_value(mkt_rules, "base_subtraction", "value", 0.03)
    upper_limit_base = _get_rule_value(mkt_rules, "upper_limit_base", "value", 0.20)
    fashion_adj = _get_rule_value(mkt_rules, "fashion_adjustment", "value", 0.05) if is_fashion else 0.0
    minimum = _get_rule_value(mkt_rules, "minimum_threshold", "value", 0.10)

    if not d73_text:
        return floor

    t, ra, rb, v, p = _parse_d73_percentages(d73_text)

    avg = ((ra * t + v + p + d52) + (rb * t + v + p + d52)) / 2
    base = _rounddown(avg - base_subtraction, 2)

    upper_limit = upper_limit_base + fashion_adj

    # Parse G68 using two distinct methods (matching spreadsheet LEFT/RIGHT sides)
    g68_left = _parse_g68_left(g68_text)  # Raw fraction before "~" for MIN chain

    ceiling_g68 = 0.0  # CEILING extraction for fallback branch
    if g68_text:
        match = re.search(r"([\d.]+)%", g68_text)
        if match:
            ceiling_g68 = math.ceil(float(match.group(1))) / 100

    # Capped value: include g68_left in MIN chain only when g68 data exists
    if g68_text:
        min_val = min(min(base, upper_limit), g68_left)
    else:
        min_val = min(base, upper_limit)
    capped_value = max(max(min_val, minimum), floor)

    # G72 branching: if capped > ceiling_g68, use capped; otherwise use ceiling_g68
    if ceiling_g68 > 0 and capped_value <= ceiling_g68:
        return ceiling_g68
    return capped_value


def _compute_g73(
    verdict: str, g72_value: float, d13: float,
    rules: dict | None = None,
) -> str:
    """G73: Marketing budget recommendation text.

    Suppressed for ❌ verdicts.
    """
    if verdict.startswith("❌"):
        return ""

    mkt_rules = _get_rule_category(rules, "marketing")
    display_max = _get_rule_value(mkt_rules, "display_max", "value", 0.25)
    display_min = _get_rule_value(mkt_rules, "display_min", "value", 0.10)

    # Clamp to range
    display_pct = max(min(g72_value, display_max), display_min)
    pct_str = f"{display_pct * 100:.0f}%"

    return (
        f"💡Minimum anggaran marketing yang dibutuhkan AHA untuk meningkatkan "
        f"performa omzet penjualan toko = {pct_str}"
    )


def _compute_g66(
    categories: list[CategoryScore],
    manual_data: dict,
    g68_text: str,
) -> str:
    """G66: Conclusion summary (multi-line text)."""
    biz = _get_nested(manual_data, "business") or {}
    sales_months = [_safe_num(biz.get(f"salesMonth{i}")) for i in range(6)]
    valid_sales = [s for s in sales_months if s > 0]

    lines: list[str] = []

    # Sales range
    if valid_sales:
        min_sales = min(valid_sales) / 1_000_000
        max_sales = max(valid_sales) / 1_000_000
        lines.append(
            f"- Omset toko di kisaran {min_sales:.0f} juta - {max_sales:.0f} juta "
            f"per bulan sejak 6 bulan terakhir"
        )

    # Operational quality
    ops_cat = next((c for c in categories if c.category == "Kesehatan Operasional Toko"), None)
    if ops_cat:
        chat_row = next((r for r in ops_cat.rows if r.row == 10), None)
        op_text = "- Kualitas operasional toko sudah cukup baik"
        if chat_row and chat_row.verdict == "❌":
            op_text += ", hanya tingkat response chat masih dapat ditingkatkan."
        lines.append(op_text)

    # Standard recommendations
    lines.append("- Nama produk disarankan untuk dimulai dengan nama brand")
    lines.append("- Background foto utama disarankan warna putih")

    # Promo effectiveness check
    promo_cat = next((c for c in categories if c.category == "Promo Toko"), None)
    if promo_cat:
        eff_row = next((r for r in promo_cat.rows if r.row == 43), None)
        if eff_row and isinstance(eff_row.value, float) and eff_row.value < 0.80:
            lines.append("- Beberapa fitur promosi masih belum dimanfaatkan secara efektif")

    # Campaign check
    campaign_cat = next((c for c in categories if c.category == "Partisipasi Campaign"), None)
    if campaign_cat:
        camp_row = next((r for r in campaign_cat.rows if r.row == 57), None)
        if camp_row and isinstance(camp_row.value, float) and camp_row.value < 0.80:
            lines.append("- Partisipasi Campaign Shopee belum maksimal.")

    # Stock and archival
    lines.append("- Banyak produk habis stok tidak diarsipkan.")
    lines.append("- Banyak produk tidak terjual di 30 hari terakhir.")

    # Discount range from G68
    if g68_text:
        lines.append(f"- Diskon range: {g68_text}")

    return "\n".join(lines)


def _compute_g75(verdict: str, store_name: str = "", rules: dict | None = None) -> str:
    """G75: Closing message based on verdict type.

    Templates may contain {store_name} which is interpolated with the store name.
    """
    # Try to read from rules first
    interp_rules = _get_rule_category(rules, "interpretation")
    closing = interp_rules.get("closing_messages")

    if closing:
        template = closing.get(verdict, "")
    else:
        # Fallback to hardcoded defaults (same as DEFAULT_RULES)
        messages = DEFAULT_RULES["interpretation"]["closing_messages"]
        template = messages.get(verdict, "")

    return template.replace("{store_name}", store_name) if template else ""


# ---------------------------------------------------------------------------
# Email assembly
# ---------------------------------------------------------------------------

def _assemble_email_body(
    categories: list[CategoryScore],
    conclusion: str,
    marketing_label: str,
    g68: str,
    g73: str,
    g75: str,
) -> str:
    """Assemble G1: structured email body from all G-column outputs."""
    sections: list[str] = []

    def _get_messages(cat_name: str, row_nums: list[int] | None = None) -> list[str]:
        cat = next((c for c in categories if c.category == cat_name), None)
        if not cat:
            return []
        msgs: list[str] = []
        for r in cat.rows:
            if row_nums and r.row not in row_nums:
                continue
            if r.message:
                msgs.append(r.message)
        return msgs

    # 1. Operational
    op_msgs = _get_messages("Kesehatan Operasional Toko")
    if op_msgs:
        sections.append("📊 Performa Operasional Toko:")
        sections.extend(op_msgs)
        sections.append("")

    # 2. Business / Sales
    biz_msgs = _get_messages("Bisnis Analisis", [13, 20])
    if biz_msgs:
        sections.append("📈 Performa Penjualan Toko:")
        sections.extend(biz_msgs)
        sections.append("")

    # 3. Visitors
    visitor_msgs = _get_messages("Tinjauan Pengunjung", [28, 29])
    if visitor_msgs:
        sections.append("👥 Tinjauan Pengunjung:")
        sections.extend(visitor_msgs)
        sections.append("")

    # 5. Promo Tools
    promo_cat = next((c for c in categories if c.category == "Promo Toko"), None)
    if promo_cat:
        promo_msgs: list[str] = []
        for r in promo_cat.rows:
            if PROMO_START_ROW <= r.row <= PROMO_START_ROW + len(PROMO_TOOLS) - 1:
                if r.message:
                    promo_msgs.append(r.message)
        # Add summary rows (42, 43)
        for r in promo_cat.rows:
            if r.row in (42, 43) and r.message:
                promo_msgs.append(r.message)

        if promo_msgs:
            sections.append("🏷️ Tingkat Penggunaan Alat Promosi:")
            sections.extend(promo_msgs)
            sections.append("")

    # 5b. Jumlah Produk & Status Toko
    products_msgs = _get_messages("Jumlah Produk & Status Toko")
    if products_msgs:
        sections.append("📦 Jumlah Produk & Status Toko:")
        sections.extend(products_msgs)
        sections.append("")

    # 6. Ads
    ads_msgs = _get_messages("Data Iklan", [50, 51, 52, 53])
    if ads_msgs:
        sections.append("📣 Performa Iklan:")
        sections.extend(ads_msgs)
        sections.append("")

    # 7. Campaign
    campaign_msgs = _get_messages("Partisipasi Campaign", [57])
    if campaign_msgs:
        sections.append("🎯 Partisipasi Campaign:")
        sections.extend(campaign_msgs)
        sections.append("")

    # 8. Competition
    comp_msgs = _get_messages("Kompetisi TOP Produk")
    if comp_msgs:
        sections.append("🏆 Kompetisi TOP Produk:")
        sections.extend(comp_msgs)
        sections.append("")

    # 9. Conclusion
    if conclusion:
        sections.append("📋 Kesimpulan:")
        sections.append(conclusion)
        sections.append("")

    # 10. Marketing estimation
    if g68:
        sections.append(f"📌 {marketing_label}")
        sections.append(g68)
        sections.append("")

    # 11. Marketing budget
    if g73:
        sections.append(g73)
        sections.append("")

    # 12. Closing
    if g75:
        sections.append(g75)

    return "\n".join(sections)


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
