"""Derived formula computations (G66, G68, G72, G73, G75) and email assembly."""

from __future__ import annotations

import math
import re

from app.calculators.scoring.helpers import (
    _extract_pct,
    _get_nested,
    _get_rule_category,
    _get_rule_value,
    _rounddown,
    _safe_num,
)
from app.calculators.scoring.models import CategoryScore, TranslatableText
from app.calculators.scoring.rules import DEFAULT_RULES, PROMO_START_ROW, PROMO_TOOLS

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


def _compute_g68(
    d73_text: str,
    d52: float,
    *,
    discount_details: dict | None = None,
) -> str:
    """G68: Marketing cost estimation.

    When discount_details with raw numeric fields is provided, reads values
    directly from the dict. Otherwise falls back to regex parsing of d73_text.
    """
    if not d73_text:
        return ""

    if discount_details and "discount_pct_raw" in discount_details:
        t = discount_details["discount_pct_raw"]
        ra = discount_details["range_min_raw"]
        rb = discount_details["range_max_raw"]
        v = discount_details["voucher_pct_raw"]
        p = discount_details["paket_pct_raw"]
        fake_discount = discount_details.get("fake_discount_flag", False)
    else:
        t, ra, rb, v, p = _parse_d73_percentages(d73_text)
        fake_discount = "Berpotensi" in d73_text or "fake discount" in d73_text.lower()

    low = (ra * t) + v + p + d52 + 0.05
    high = (rb * t) + v + p + d52 + 0.05

    result = f"{low * 100:.1f}% ~ {high * 100:.1f}%"

    if fake_discount:
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
    *,
    discount_details: dict | None = None,
) -> float:
    """G72: Recommended marketing percentage (as fraction).

    Complex MIN/MAX formula with Fashion adjustment.
    When discount_details with raw numeric fields is provided, reads values
    directly from the dict. Otherwise falls back to regex parsing of d73_text.
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

    if discount_details and "discount_pct_raw" in discount_details:
        t = discount_details["discount_pct_raw"]
        ra = discount_details["range_min_raw"]
        rb = discount_details["range_max_raw"]
        v = discount_details["voucher_pct_raw"]
        p = discount_details["paket_pct_raw"]
    else:
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
    """G73: Marketing budget recommendation text."""

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
    *,
    marketplace: str = "ID",
) -> str:
    """G66: Conclusion summary (multi-line text)."""
    biz = _get_nested(manual_data, "business") or {}
    sales_months = [_safe_num(biz.get(f"salesMonth{i}")) for i in range(6)]
    valid_sales = [s for s in sales_months if s > 0]

    lines: list[str] = []

    # Sales range
    if valid_sales:
        if marketplace == "TH":
            min_s = f"{min(valid_sales):,.0f}"
            max_s = f"{max(valid_sales):,.0f}"
            lines.append(
                f"- Omset toko di kisaran {min_s} - {max_s} "
                f"per bulan sejak 6 bulan terakhir"
            )
        else:
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
    lines.append("- Nama produk disarankan untuk dimulai dengan nama brand dan mencantumkan FAB produk (Feature, Advantage, & Benefit).")
    lines.append("- Background foto utama disarankan warna putih & menampilkan logo brand.")

    # Promo effectiveness check
    promo_cat = next((c for c in categories if c.category == "Promo Toko"), None)
    if promo_cat:
        eff_row = next((r for r in promo_cat.rows if r.row == 43), None)
        if eff_row and isinstance(eff_row.value, float) and eff_row.value < 0.80:
            lines.append("- Beberapa fitur promosi masih belum optimal.")

    # Campaign check
    campaign_cat = next((c for c in categories if c.category == "Partisipasi Campaign"), None)
    if campaign_cat:
        camp_row = next((r for r in campaign_cat.rows if r.row == 57), None)
        if camp_row and isinstance(camp_row.value, float) and camp_row.value < 0.80:
            lines.append("- Partisipasi Campaign Shopee belum maksimal.")

    # Stock and archival
    lines.append("- Pastikan produk yang stoknya habis diarsipkan")
    lines.append("- Banyak produk tidak terjual di 30 hari terakhir.")

    # Discount range from G68
    if g68_text:
        lines.append(f"- Range diskon: {g68_text}")

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


def _compute_g66_i18n(
    categories: list[CategoryScore],
    manual_data: dict,
    g68_text: str,
    *,
    marketplace: str = "ID",
) -> list[TranslatableText]:
    """G66 i18n: return structured list of conclusion items."""
    items: list[TranslatableText] = []
    biz = _get_nested(manual_data, "business") or {}
    sales_months = [_safe_num(biz.get(f"salesMonth{i}")) for i in range(6)]
    valid_sales = [s for s in sales_months if s > 0]

    if valid_sales:
        if marketplace == "TH":
            items.append(TranslatableText(
                key="conclusion.salesRange",
                vars={"min": f"{min(valid_sales):,.0f}", "max": f"{max(valid_sales):,.0f}"},
            ))
        else:
            items.append(TranslatableText(
                key="conclusion.salesRange",
                vars={"min": f"{min(valid_sales) / 1_000_000:.0f}", "max": f"{max(valid_sales) / 1_000_000:.0f}"},
            ))

    ops_cat = next((c for c in categories if c.category == "Kesehatan Operasional Toko"), None)
    if ops_cat:
        chat_row = next((r for r in ops_cat.rows if r.row == 10), None)
        if chat_row and chat_row.verdict == "❌":
            items.append(TranslatableText(key="conclusion.operationalChatIssue", vars={}))
        else:
            items.append(TranslatableText(key="conclusion.operationalGood", vars={}))

    items.append(TranslatableText(key="conclusion.productNaming", vars={}))
    items.append(TranslatableText(key="conclusion.photoBackground", vars={}))

    promo_cat = next((c for c in categories if c.category == "Promo Toko"), None)
    if promo_cat:
        eff_row = next((r for r in promo_cat.rows if r.row == 43), None)
        if eff_row and isinstance(eff_row.value, (int, float)) and eff_row.value < 0.80:
            items.append(TranslatableText(key="conclusion.promoUnderutilized", vars={}))

    campaign_cat = next((c for c in categories if c.category == "Partisipasi Campaign"), None)
    if campaign_cat:
        camp_row = next((r for r in campaign_cat.rows if r.row == 57), None)
        if camp_row and isinstance(camp_row.value, (int, float)) and camp_row.value < 0.80:
            items.append(TranslatableText(key="conclusion.campaignLow", vars={}))

    items.append(TranslatableText(key="conclusion.stockNotArchived", vars={}))
    items.append(TranslatableText(key="conclusion.unsoldProducts", vars={}))

    if g68_text:
        range_only = g68_text.split("\n")[0]
        items.append(TranslatableText(key="conclusion.discountRange", vars={"range": range_only}))
        if "Berpotensi" in g68_text or "fake discount" in g68_text.lower():
            items.append(TranslatableText(key="conclusion.fakeDiscount", vars={}))

    return items


def _compute_g73_i18n(
    verdict: str, g72_value: float, d13: float,
    rules: dict | None = None,
) -> TranslatableText | None:
    """G73 i18n: marketing budget recommendation as TranslatableText."""
    mkt_rules = _get_rule_category(rules, "marketing")
    display_max = _get_rule_value(mkt_rules, "display_max", "value", 0.25)
    display_min = _get_rule_value(mkt_rules, "display_min", "value", 0.10)
    display_pct = max(min(g72_value, display_max), display_min)
    return TranslatableText(key="marketing.budgetRecommendation", vars={"pct": f"{display_pct * 100:.0f}%"})


def _compute_g75_i18n(
    verdict: str, store_name: str = "", rules: dict | None = None,
) -> TranslatableText | None:
    """G75 i18n: closing message as TranslatableText."""
    verdict_key_map = {
        "✔️": "closing.potential",
        "❌": "closing.valueAdd",
        "❌ Non Mall": "closing.directAnalysis",
        "❌ No Brand": "closing.noBrand",
        "❌ Opex": "closing.experience",
        "❌ Stock": "closing.stockInsufficient",
    }
    key = verdict_key_map.get(verdict)
    if not key:
        return None
    return TranslatableText(key=key, vars={"store_name": store_name})


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
