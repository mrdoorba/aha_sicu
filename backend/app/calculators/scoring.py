"""Final Scoring Calculator — pure function, no I/O.

Implements the 75-row scoring system template (Fashion/Non-Fashion variants).
Combines manual inputs with Calculator 1-3 outputs to produce per-category
scores, total score, verdicts, G-column messages, email body, and WhatsApp link.

Spec: logic/scoring-system-template-sicu.md
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

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
    whatsapp_link: str               # E1
    template: str                    # "fashion" or "non_fashion"
    rule_version: int = 1            # Version of rules used for scoring


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_num(value: Any, default: float = 0.0) -> float:
    """Coerce a value to float, treating None/empty as default."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if value in ("", "-"):
            return default
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _safe_str(value: Any, default: str = "") -> str:
    """Coerce value to string."""
    if value is None:
        return default
    return str(value).strip()


def _get_nested(data: dict, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dict keys."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def _fmt_pct_1dp(value: float) -> str:
    """Format fraction as percentage with 1 decimal: 0.235 -> '23.5%'."""
    return f"{value * 100:.1f}%"


def _fmt_pct_0dp(value: float) -> str:
    """Format fraction as percentage with no decimal: 0.95 -> '95%'."""
    return f"{value * 100:.0f}%"


def _fmt_num_1dp(value: float) -> str:
    """Format as number with 1 decimal: 0.005 -> '0.5%' (percentage number)."""
    return f"{value:.1f}%"


def _fmt_num_2dp(value: float) -> str:
    """Format as number with 2 decimals."""
    return f"{value:.2f}"


def _fmt_idr(value: float) -> str:
    """Format IDR value with Indonesian thousands separator."""
    rounded = round(value)
    if rounded < 0:
        return f"-{abs(rounded):,}".replace(",", ".")
    return f"{rounded:,}".replace(",", ".")


def _rounddown(value: float, decimals: int) -> float:
    """Round DOWN to specified decimal places."""
    factor = 10 ** decimals
    return math.floor(value * factor) / factor


def _extract_pct(pattern: str, text: str) -> float:
    """Extract a percentage value from text using regex, return as fraction."""
    match = re.search(pattern, text)
    if match:
        try:
            return float(match.group(1)) / 100
        except (ValueError, IndexError):
            return 0.0
    return 0.0


# ---------------------------------------------------------------------------
# Rules helpers — extract configurable thresholds with fallback defaults
# ---------------------------------------------------------------------------

def _get_rule_category(rules: dict | None, category: str) -> dict:
    """Get a category dict from rules, or empty dict if missing."""
    if rules is None:
        return {}
    return rules.get(category, {})


def _get_rule_value(category_rules: dict, key: str, field: str, default: Any) -> Any:
    """Get a specific value from category rules, with default fallback."""
    return category_rules.get(key, {}).get(field, default)


# Default rules matching migration 010 seed data — used when rules=None
DEFAULT_FASHION_RULES: dict = {
    "operational": {
        "unfulfilled_order_rate": {"threshold": 1.0, "points": 4, "comparison": "lte"},
        "late_shipment_rate": {"threshold": 1.0, "points": 3, "comparison": "lte"},
        "preparation_time": {"threshold": 1.0, "points": 3, "comparison": "lte"},
        "chat_response_rate": {"threshold": 95.0, "comparison": "gte", "info_only": True},
        "overall_rating": {"threshold": 4.7, "comparison": "gte", "info_only": True},
    },
    "business": {
        "monthly_sales_trend": {"threshold_pct": 90.0, "points": 10, "comparison": "gte"},
        "six_month_avg_threshold": {"threshold": 100000000, "points": 10, "comparison": "gte"},
        "conversion_rate": {"threshold": 2.0, "comparison": "gte", "info_only": True},
    },
    "content": {
        "quality_ratio": {"threshold": 95.0, "comparison": "gte", "info_only": True},
    },
    "visitors": {
        "returning_visitors_pct": {"threshold": 23.0, "points": 3, "comparison": "gte"},
        "followers": {"threshold": 50000, "points": 2, "comparison": "gte"},
    },
    "promo_tools": {
        "usage_pct_threshold": {"threshold": 80.0, "opportunity_points": 5},
        "effectiveness_pct_threshold": {"threshold": 90.0, "opportunity_points": 10},
    },
    "products_status": {
        "product_count": {"threshold": 35, "points": 5, "comparison": "gte"},
        "store_status_points": {"mall": 10, "star_plus": 5, "star": 0, "regular": 0},
    },
    "ads": {
        "roi_threshold": {"threshold": 8.0, "opportunity_points": 5, "comparison": "gt"},
        "gmv_ratio_threshold": {"threshold": 84.0, "points": 5, "comparison": "lt"},
        "cost_ratio_range": {"min": 5.0, "max": 10.0, "info_only": True},
    },
    "campaign": {
        "participation_pct_threshold": {"threshold": 90.0, "opportunity_points": 10, "comparison": "gte"},
    },
    "stock": {
        "high_threshold": {"threshold": 24, "points": 10, "comparison": "gte"},
        "mid_threshold": {"threshold": 12, "points": 5, "comparison": "gte"},
        "low_penalty": {"threshold": 12, "points": -5, "comparison": "lt"},
    },
    "discount": {
        "fake_discount_flag": {"points_no_flag": 5, "points_flag": 0},
    },
    "interpretation": {
        "ranges": [
            {"min": 71, "max": None, "label": "Good Candidate", "verdict": "✔️"},
            {"min": 41, "max": 70, "label": "Needs Review", "verdict": "⭕️"},
            {"min": None, "max": 40, "label": "Not Recommended", "verdict": "❌"},
        ],
    },
}

DEFAULT_NON_FASHION_RULES: dict = {
    **DEFAULT_FASHION_RULES,
    "business": {
        **DEFAULT_FASHION_RULES["business"],
        "conversion_rate": {"threshold": 3.0, "comparison": "gte", "info_only": True},
    },
    "ads": {
        **DEFAULT_FASHION_RULES["ads"],
        "roi_threshold": {"threshold": 9.0, "opportunity_points": 5, "comparison": "gt"},
    },
}


# ---------------------------------------------------------------------------
# Promo tools configuration
# ---------------------------------------------------------------------------

# Field key → (display name, benchmark fraction)
PROMO_TOOLS: list[tuple[str, str, float]] = [
    ("promoToko", "Promo Toko", 0.08),
    ("paketDiskon", "Paket Diskon", 0.16),
    ("komboHemat", "Kombo Hemat", 0.01),
    ("flashSale", "Flash Sale Toko Saya", 0.01),
    ("voucher", "Voucher", 0.84),
    ("shopeeLive", "Shopee Live", 0.15),
    ("gameToko", "Game Toko", 0.01),
    ("brandMembership", "Brand Membership", 0.01),
    ("gratisOngkir", "Gratis Ongkir XTRA", 0.0),
    ("chatBroadcast", "Chat Broadcast", 0.01),
    ("programAfiliasi", "Program Afiliasi", 0.18),
]

# Row numbers for promo tools (rows 31-41)
PROMO_START_ROW = 31


# ---------------------------------------------------------------------------
# Per-category scoring functions
# ---------------------------------------------------------------------------

def _score_operational(manual_data: dict, rules: dict | None = None) -> CategoryScore:
    """Score rows 7-11: Kesehatan Operasional Toko.

    H7: Pesanan Tidak Terselesaikan — ✔️=4, >1%=-(value)
    H8: Keterlambatan Pengiriman — ✔️=3, >1%=-(value)
    H9: Masa Pengemasan — ✔️=3, >1=-((value-1)×100)
    Rows 10-11: F/G columns only, no H score.

    Values stored as percentage numbers (0.5 = 0.5%) for rates,
    days for preparation time.
    """
    ops = _get_nested(manual_data, "operational") or {}
    ops_rules = _get_rule_category(rules, "operational")
    rows: list[RowScore] = []

    # H7: Pesanan Tidak Terselesaikan
    d7 = _safe_num(ops.get("unfulfilledOrderRate"))
    uor_threshold = _get_rule_value(ops_rules, "unfulfilled_order_rate", "threshold", 1.0)
    uor_points = _get_rule_value(ops_rules, "unfulfilled_order_rate", "points", 4.0)
    if d7 <= uor_threshold:
        f7, h7 = "✔️", float(uor_points)
    else:
        f7, h7 = "❌", -d7
    rows.append(RowScore(
        row=7, metric="Tingkat Pesanan Tidak Terselesaikan",
        value=d7, benchmark="<1%", verdict=f7, message="", score=h7,
    ))

    # H8: Keterlambatan Pengiriman
    d8 = _safe_num(ops.get("lateShipmentRate"))
    lsr_threshold = _get_rule_value(ops_rules, "late_shipment_rate", "threshold", 1.0)
    lsr_points = _get_rule_value(ops_rules, "late_shipment_rate", "points", 3.0)
    if d8 <= lsr_threshold:
        f8, h8 = "✔️", float(lsr_points)
    else:
        f8, h8 = "❌", -d8
    rows.append(RowScore(
        row=8, metric="Tingkat Keterlambatan Pengiriman",
        value=d8, benchmark="<1%", verdict=f8, message="", score=h8,
    ))

    # H9: Masa Pengemasan
    d9 = _safe_num(ops.get("preparationTime"))
    pt_threshold = _get_rule_value(ops_rules, "preparation_time", "threshold", 1.0)
    pt_points = _get_rule_value(ops_rules, "preparation_time", "points", 3.0)
    if d9 <= pt_threshold:
        f9, h9 = "✔️", float(pt_points)
    else:
        f9, h9 = "❌", -((d9 - 1) * 100)
    rows.append(RowScore(
        row=9, metric="Masa Pengemasan",
        value=d9, benchmark="<1", verdict=f9, message="", score=h9,
    ))

    # Row 10: Chat Dibalas (no score)
    d10 = _safe_num(ops.get("chatResponseRate"))
    chat_threshold = _get_rule_value(ops_rules, "chat_response_rate", "threshold", 95.0)
    # F10 special: ROUNDUP to 2 decimals before comparing
    d10_rounded = math.ceil(d10 * 100) / 100
    f10 = "✔️" if d10_rounded >= chat_threshold else "❌"
    rows.append(RowScore(
        row=10, metric="Persentase Chat Dibalas",
        value=d10, benchmark=">95%", verdict=f10, message="", score=0.0,
    ))

    # Row 11: Overall Rating (no score)
    d11 = _safe_num(ops.get("overallRating"))
    rating_threshold = _get_rule_value(ops_rules, "overall_rating", "threshold", 4.7)
    f11 = "✔️" if d11 >= rating_threshold else "❌"
    rows.append(RowScore(
        row=11, metric="Keseluruhan Penilaian",
        value=d11, benchmark=">4.7", verdict=f11, message="", score=0.0,
    ))

    total = sum(r.score for r in rows)
    return CategoryScore(
        category="Kesehatan Operasional Toko",
        score=total, max_score=10.0, rows=rows,
    )


def _score_business(manual_data: dict, rules: dict | None = None) -> CategoryScore:
    """Score rows 13-20: Bisnis Analisis.

    H13: 10 if avg_6mo < salesMonth0 × 110%, else 0
    H19: 10 if avg_6mo > 100M IDR, else 0
    Rows 14-18, 20: no H score.
    """
    biz = _get_nested(manual_data, "business") or {}
    biz_rules = _get_rule_category(rules, "business")

    sales_months = [
        _safe_num(biz.get("salesMonth0")),
        _safe_num(biz.get("salesMonth1")),
        _safe_num(biz.get("salesMonth2")),
        _safe_num(biz.get("salesMonth3")),
        _safe_num(biz.get("salesMonth4")),
        _safe_num(biz.get("salesMonth5")),
    ]
    current_month = sales_months[0]
    avg_6mo = sum(sales_months) / 6 if any(s > 0 for s in sales_months) else 0.0
    rows: list[RowScore] = []

    # Row 13: Current month sales
    trend_pct = _get_rule_value(biz_rules, "monthly_sales_trend", "threshold_pct", 90.0)
    trend_points = float(_get_rule_value(biz_rules, "monthly_sales_trend", "points", 10.0))
    # threshold_pct=90 → multiplier=1.10: pass if avg < current × multiplier
    trend_multiplier = (200 - trend_pct) / 100
    e13 = f">{_fmt_idr(avg_6mo)}" if avg_6mo > 0 else "-"
    f13 = "✔️" if avg_6mo < current_month * trend_multiplier else "❌"
    h13 = trend_points if avg_6mo < current_month * trend_multiplier else 0.0
    rows.append(RowScore(
        row=13, metric="Penjualan",
        value=current_month, benchmark=e13, verdict=f13, message="", score=h13,
    ))

    # Rows 14-18: Past months (no score, kept for reference)
    for i in range(1, 6):
        rows.append(RowScore(
            row=13 + i, metric=f"Penjualan Bulan -{i}",
            value=sales_months[i], benchmark="-", verdict="-", message="", score=0.0,
        ))

    # Row 19: Average (computed)
    avg_threshold = _get_rule_value(biz_rules, "six_month_avg_threshold", "threshold", 100_000_000)
    avg_points = float(_get_rule_value(biz_rules, "six_month_avg_threshold", "points", 10.0))
    f19 = "✔️" if avg_6mo > avg_threshold else "❌"
    h19 = avg_points if avg_6mo > avg_threshold else 0.0
    rows.append(RowScore(
        row=19, metric="Rata² Penjualan 6 bulan terakhir",
        value=avg_6mo, benchmark="-", verdict=f19, message="", score=h19,
    ))

    # Row 20: Conversion rate (no score) — benchmark depends on template
    # Template check happens in main function; store raw value for now
    d20 = _safe_num(biz.get("conversionRate"))
    rows.append(RowScore(
        row=20, metric="Tingkat Konversi",
        value=d20, benchmark=">3%", verdict="-", message="", score=0.0,
    ))

    total = sum(r.score for r in rows)
    return CategoryScore(
        category="Bisnis Analisis",
        score=total, max_score=20.0, rows=rows,
    )


def _score_content(manual_data: dict, rules: dict | None = None) -> CategoryScore:
    """Score rows 22-24: Skor Kesehatan Konten.

    No H-column scores. F24 verdict only.
    """
    content = _get_nested(manual_data, "content") or {}
    content_rules = _get_rule_category(rules, "content")
    rows: list[RowScore] = []

    d22 = _safe_num(content.get("needsImprovement"))
    d23 = _safe_num(content.get("goodQuality"))
    d24 = d23 / (d23 + d22) if (d23 + d22) > 0 else 0.0

    rows.append(RowScore(
        row=22, metric="Perlu ditingkatkan",
        value=d22, benchmark="-", verdict="-", message="", score=0.0,
    ))
    rows.append(RowScore(
        row=23, metric="Kualitas baik",
        value=d23, benchmark="-", verdict="-", message="", score=0.0,
    ))

    quality_threshold = _get_rule_value(content_rules, "quality_ratio", "threshold", 95.0) / 100
    f24 = "✔️" if d24 >= quality_threshold else "❌"
    rows.append(RowScore(
        row=24, metric="% Konten baik",
        value=d24, benchmark=">95%", verdict=f24, message="", score=0.0,
    ))

    return CategoryScore(
        category="Skor Kesehatan Konten",
        score=0.0, max_score=0.0, rows=rows,
    )


def _score_visitors(manual_data: dict, rules: dict | None = None) -> CategoryScore:
    """Score rows 26-29: Tinjauan Pengunjung.

    H28: 3 if returning visitors > 23%
    H29: 2 if followers > 50,000
    """
    vis = _get_nested(manual_data, "visitors") or {}
    vis_rules = _get_rule_category(rules, "visitors")
    rows: list[RowScore] = []

    d26 = _safe_num(vis.get("totalVisitors"))
    d27 = _safe_num(vis.get("returningVisitors"))
    d29 = _safe_num(vis.get("totalFollowers"))

    rows.append(RowScore(
        row=26, metric="Total Pengunjung",
        value=d26, benchmark="-", verdict="-", message="", score=0.0,
    ))
    rows.append(RowScore(
        row=27, metric="Pengunjung Lama",
        value=d27, benchmark="-", verdict="-", message="", score=0.0,
    ))

    # Row 28: % Returning visitors (computed)
    rv_threshold = _get_rule_value(vis_rules, "returning_visitors_pct", "threshold", 23.0) / 100
    rv_points = float(_get_rule_value(vis_rules, "returning_visitors_pct", "points", 3.0))
    d28 = d27 / d26 if d26 > 0 else 0.0
    f28 = "✔️" if d28 > rv_threshold else "❌"
    h28 = rv_points if d28 > rv_threshold else 0.0
    rows.append(RowScore(
        row=28, metric="% Pengunjung Lama",
        value=d28, benchmark=">23%", verdict=f28, message="", score=h28,
    ))

    # Row 29: Total followers
    fl_threshold = _get_rule_value(vis_rules, "followers", "threshold", 50000)
    fl_points = float(_get_rule_value(vis_rules, "followers", "points", 2.0))
    f29 = "✔️" if d29 > fl_threshold else "❌"
    h29 = fl_points if d29 > fl_threshold else 0.0
    rows.append(RowScore(
        row=29, metric="Total Pengikut",
        value=d29, benchmark=">50000", verdict=f29, message="", score=h29,
    ))

    total = h28 + h29
    return CategoryScore(
        category="Tinjauan Pengunjung",
        score=total, max_score=5.0, rows=rows,
    )


def _promo_verdict(d_value: float, d13_sales: float, benchmark_pct: float) -> str:
    """Determine F-column verdict for a promo tool row (31-41).

    Logic:
    - D=0 → "❌" (not used)
    - D/D13 >= 50% → "❌" (too dependent)
    - D >= benchmark% × D13 → "✔️" (meets benchmark)
    - else → "❌"
    """
    if d_value == 0:
        return "❌"
    if d13_sales > 0 and d_value / d13_sales >= 0.50:
        return "❌"
    if benchmark_pct == 0.0:
        # gratisOngkir: any value > 0 passes
        return "✔️" if d_value > 0 else "❌"
    if d13_sales > 0 and d_value >= benchmark_pct * d13_sales:
        return "✔️"
    return "❌"


def _score_promo_tools(manual_data: dict, rules: dict | None = None) -> CategoryScore:
    """Score rows 31-43: Promo Toko.

    Rows 31-41: Individual promo tools (F-column only, no H score per row)
    H42: Usage rate — ✔️=0, ❌=5 (opportunity)
    H43: Effectiveness rate — ✔️=0, ❌=10 (opportunity)
    """
    promo = _get_nested(manual_data, "promoTools") or {}
    d13 = _safe_num(_get_nested(manual_data, "business", "salesMonth0"))
    promo_rules = _get_rule_category(rules, "promo_tools")
    rows: list[RowScore] = []

    used_count = 0
    pass_count = 0
    total_tools = len(PROMO_TOOLS)

    for i, (field_key, display_name, benchmark_pct) in enumerate(PROMO_TOOLS):
        row_num = PROMO_START_ROW + i
        d_value = _safe_num(promo.get(field_key))
        benchmark_str = f">{benchmark_pct * 100:g}%" if benchmark_pct > 0 else ">0"

        f_verdict = _promo_verdict(d_value, d13, benchmark_pct)

        if d_value > 0:
            used_count += 1
        if f_verdict == "✔️":
            pass_count += 1

        rows.append(RowScore(
            row=row_num, metric=display_name,
            value=d_value, benchmark=benchmark_str, verdict=f_verdict,
            message="", score=0.0,
        ))

    # Row 42: % Usage
    usage_threshold = _get_rule_value(promo_rules, "usage_pct_threshold", "threshold", 80.0) / 100
    usage_opp_pts = float(_get_rule_value(promo_rules, "usage_pct_threshold", "opportunity_points", 5.0))
    usage_rate = used_count / total_tools if total_tools > 0 else 0.0
    f42 = "✔️" if usage_rate > usage_threshold else "❌"
    h42 = 0.0 if usage_rate > usage_threshold else usage_opp_pts
    rows.append(RowScore(
        row=42, metric="% Penggunaan alat promosi",
        value=usage_rate, benchmark=">80%", verdict=f42, message="", score=h42,
    ))

    # Row 43: % Effectiveness
    eff_threshold = _get_rule_value(promo_rules, "effectiveness_pct_threshold", "threshold", 90.0) / 100
    eff_opp_pts = float(_get_rule_value(promo_rules, "effectiveness_pct_threshold", "opportunity_points", 10.0))
    effectiveness_rate = pass_count / total_tools if total_tools > 0 else 0.0
    f43 = "✔️" if effectiveness_rate > eff_threshold else "❌"
    h43 = 0.0 if effectiveness_rate > eff_threshold else eff_opp_pts
    rows.append(RowScore(
        row=43, metric="% Efektifitas alat promosi",
        value=effectiveness_rate, benchmark=">90%", verdict=f43, message="", score=h43,
    ))

    total = h42 + h43
    return CategoryScore(
        category="Promo Toko",
        score=total, max_score=15.0, rows=rows,
    )


def _score_products(manual_data: dict, rules: dict | None = None) -> CategoryScore:
    """Score rows 45-46: Jumlah Produk & Status Toko.

    H45: 5 if productCount >= 35
    H46: Mall=10, Star+=5, else 0
    """
    products = _get_nested(manual_data, "products") or {}
    ps_rules = _get_rule_category(rules, "products_status")
    rows: list[RowScore] = []

    # Row 45: Product count
    pc_threshold = _get_rule_value(ps_rules, "product_count", "threshold", 35)
    pc_points = float(_get_rule_value(ps_rules, "product_count", "points", 5.0))
    d45 = _safe_num(products.get("productCount"))
    f45 = "✔️" if d45 >= pc_threshold else "❌"
    h45 = pc_points if d45 >= pc_threshold else 0.0
    rows.append(RowScore(
        row=45, metric="Jumlah Produk",
        value=d45, benchmark=">=35", verdict=f45, message="", score=h45,
    ))

    # Row 46: Store status
    status_pts = ps_rules.get("store_status_points", {}) if ps_rules else {}
    mall_pts = float(status_pts.get("mall", 10.0))
    star_plus_pts = float(status_pts.get("star_plus", 5.0))
    d46 = _safe_str(products.get("storeStatus"))
    if d46 == "Shopee Mall":
        f46, h46 = "✔️", mall_pts
    elif d46 == "Star+":
        f46, h46 = "✔️", star_plus_pts
    elif d46:
        f46, h46 = "❌", 0.0
    else:
        f46, h46 = "-", 0.0
    rows.append(RowScore(
        row=46, metric="Status Toko",
        value=d46, benchmark="Shopee Mall", verdict=f46, message="", score=h46,
    ))

    total = h45 + h46
    return CategoryScore(
        category="Jumlah Produk & Status Toko",
        score=total, max_score=15.0, rows=rows,
    )


def _score_ads(manual_data: dict, template: str, rules: dict | None = None) -> CategoryScore:
    """Score rows 48-53: Data Iklan.

    H50: ROI — ✔️=0, ❌=5 (opportunity). Threshold: >8 Fashion, >9 Non-Fashion
    H51: GMV ratio — ✔️=5, ❌=0
    Rows 48-49, 52-53: no H score.
    """
    ads = _get_nested(manual_data, "ads") or {}
    d13 = _safe_num(_get_nested(manual_data, "business", "salesMonth0"))
    ads_rules = _get_rule_category(rules, "ads")
    rows: list[RowScore] = []

    d48 = _safe_num(ads.get("adSales"))
    d49 = _safe_num(ads.get("adCost"))

    # Row 48: Ad sales (no score)
    rows.append(RowScore(
        row=48, metric="Penjualan (iklan)",
        value=d48, benchmark="-", verdict="-", message="", score=0.0,
    ))

    # Row 49: Ad cost (no score), E49 = D49/D13
    d49_pct = d49 / d13 if d13 > 0 else 0.0
    rows.append(RowScore(
        row=49, metric="Biaya (iklan)",
        value=d49, benchmark=f"{_fmt_pct_1dp(d49_pct)}", verdict="-",
        message="", score=0.0,
    ))

    # Row 50: ROI = D48/D49
    d50 = d48 / d49 if d49 > 0 else 0.0
    roi_default = 8.0 if template == "fashion" else 9.0
    roi_threshold = _get_rule_value(ads_rules, "roi_threshold", "threshold", roi_default)
    roi_opp_pts = float(_get_rule_value(ads_rules, "roi_threshold", "opportunity_points", 5.0))
    f50 = "✔️" if d50 >= roi_threshold else "❌"
    h50 = 0.0 if d50 >= roi_threshold else roi_opp_pts
    rows.append(RowScore(
        row=50, metric="ROI",
        value=d50, benchmark=f">{roi_threshold:g}", verdict=f50,
        message="", score=h50,
    ))

    # Row 51: GMV ratio = D48/D13
    gmv_threshold = _get_rule_value(ads_rules, "gmv_ratio_threshold", "threshold", 84.0) / 100
    gmv_points = float(_get_rule_value(ads_rules, "gmv_ratio_threshold", "points", 5.0))
    d51 = d48 / d13 if d13 > 0 else 0.0
    f51 = "✔️" if d51 < gmv_threshold else "❌"
    h51 = gmv_points if d51 < gmv_threshold else 0.0
    rows.append(RowScore(
        row=51, metric="% GMV Iklan / GMV Toko",
        value=d51, benchmark="<84%", verdict=f51, message="", score=h51,
    ))

    # Row 52: Ad cost % = D49/D13
    d52 = d49 / d13 if d13 > 0 else 0.0
    if d52 < 0.01:
        f52 = "❌"
    elif d52 < 0.05:
        f52 = "❌"
    elif d52 <= 0.10:
        f52 = "✔️"
    else:
        f52 = "❌"
    rows.append(RowScore(
        row=52, metric="% Biaya Iklan / GMV Toko",
        value=d52, benchmark="<10%", verdict=f52, message="", score=0.0,
    ))

    # Row 53: Calculator 1 output (no score, just email content)
    rows.append(RowScore(
        row=53, metric="Iklan check up",
        value="", benchmark="Iklan check up", verdict="-", message="", score=0.0,
    ))

    total = h50 + h51
    return CategoryScore(
        category="Data Iklan",
        score=total, max_score=10.0, rows=rows,
    )


def _score_campaign(manual_data: dict, rules: dict | None = None) -> CategoryScore:
    """Score rows 55-57: Partisipasi Campaign.

    H57: Participation — ✔️=0, ❌=10 (opportunity)
    """
    campaign = _get_nested(manual_data, "campaign") or {}
    camp_rules = _get_rule_category(rules, "campaign")
    rows: list[RowScore] = []

    d55 = _safe_num(campaign.get("nominatedSessions"))
    d56 = _safe_num(campaign.get("availableSessions"))

    rows.append(RowScore(
        row=55, metric="Sesi dinominasikan",
        value=d55, benchmark="-", verdict="-", message="", score=0.0,
    ))
    rows.append(RowScore(
        row=56, metric="Sesi tersedia",
        value=d56, benchmark="-", verdict="-", message="", score=0.0,
    ))

    # Row 57: Participation rate = D55/D56
    part_threshold = _get_rule_value(camp_rules, "participation_pct_threshold", "threshold", 90.0) / 100
    part_opp_pts = float(_get_rule_value(camp_rules, "participation_pct_threshold", "opportunity_points", 10.0))
    d57 = d55 / d56 if d56 > 0 else 0.0
    f57 = "✔️" if d57 > part_threshold else "❌"
    h57 = 0.0 if d57 > part_threshold else part_opp_pts
    rows.append(RowScore(
        row=57, metric="% Partisipasi Campaign",
        value=d57, benchmark=">90%", verdict=f57, message="", score=h57,
    ))

    return CategoryScore(
        category="Partisipasi Campaign",
        score=h57, max_score=10.0, rows=rows,
    )


def _score_competition(
    manual_data: dict, calculator_results: dict,
) -> CategoryScore:
    """Score rows 60-63: Kompetisi TOP Produk.

    No H-column scores. G-column messages for competitiveness check.
    C61-C63: selling prices from Calculator 2 output_1[0..2].rata2_harga_jual
    F61-F63: market price (manual input)
    """
    comp = _get_nested(manual_data, "competition") or {}
    rows: list[RowScore] = []

    # Get selling prices from Calculator 2
    top_sku_details = _get_nested(calculator_results, "top_sku", "details") or {}
    output_1 = top_sku_details.get("output_1", [])

    for i in range(3):
        row_num = 61 + i
        product_key = f"product{i + 1}"
        product_data = comp.get(product_key, {}) or {}

        selling_price = 0.0
        if i < len(output_1):
            selling_price = _safe_num(output_1[i].get("rata2_harga_jual"))

        market_price = _safe_num(product_data.get("marketPrice"))

        # F: competitive if selling price <= market price × 110%
        if selling_price > 0 and market_price > 0:
            f_verdict = "❌" if selling_price > market_price * 1.10 else "✔️"
        else:
            f_verdict = "-"

        rows.append(RowScore(
            row=row_num, metric=f"Produk {i + 1}",
            value=selling_price, benchmark=f"Rp. {_fmt_idr(market_price)}" if market_price > 0 else "-",
            verdict=f_verdict, message="", score=0.0,
        ))

    return CategoryScore(
        category="Kompetisi TOP Produk",
        score=0.0, max_score=0.0, rows=rows,
    )


def _score_stock(calculator_results: dict, rules: dict | None = None) -> CategoryScore:
    """Score row 70: Stock Analysis.

    H70: >=24 → 10, >=12 → 5, <12 → -5
    Source: Calculator 2 details.average_stock
    """
    top_sku_data = _get_nested(calculator_results, "top_sku", "details")
    has_data = top_sku_data is not None and "average_stock" in (top_sku_data or {})

    if not has_data:
        row = RowScore(
            row=70, metric="Rata² Stok",
            value="N/A", benchmark=">=24", verdict="-",
            message="Calculator 2 (Top SKU) belum dijalankan", score=0.0,
        )
        return CategoryScore(
            category="Stok",
            score=0.0, max_score=10.0, rows=[row], available=False,
        )

    stock_rules = _get_rule_category(rules, "stock")
    high_threshold = _get_rule_value(stock_rules, "high_threshold", "threshold", 24)
    high_points = float(_get_rule_value(stock_rules, "high_threshold", "points", 10.0))
    mid_threshold = _get_rule_value(stock_rules, "mid_threshold", "threshold", 12)
    mid_points = float(_get_rule_value(stock_rules, "mid_threshold", "points", 5.0))
    low_points = float(_get_rule_value(stock_rules, "low_penalty", "points", -5.0))

    avg_stock = _safe_num(top_sku_data.get("average_stock"))
    # Round if decimal (spec says round to integer)
    avg_stock_int = round(avg_stock)

    if avg_stock_int >= high_threshold:
        f70, h70 = "✔️", high_points
    elif avg_stock_int >= mid_threshold:
        f70, h70 = "✔️", mid_points
    else:
        f70, h70 = "❌", low_points

    row = RowScore(
        row=70, metric="Rata² Stok",
        value=avg_stock_int, benchmark=">=24", verdict=f70,
        message="", score=h70,
    )
    return CategoryScore(
        category="Stok",
        score=h70, max_score=10.0, rows=[row],
    )


def _score_discount_row(calculator_results: dict, rules: dict | None = None) -> CategoryScore:
    """Score row 73: Discount Check Up.

    H73: 5 if no fake discount, 0 if fake discount detected
    Source: Calculator 3 details.fake_discount_flag
    """
    disc_details = _get_nested(calculator_results, "discount", "details")
    has_data = disc_details is not None

    if not has_data:
        row = RowScore(
            row=73, metric="Discount Check Up",
            value="N/A", benchmark="-", verdict="-",
            message="Calculator 3 (Discount) belum dijalankan", score=0.0,
        )
        return CategoryScore(
            category="Discount",
            score=0.0, max_score=5.0, rows=[row], available=False,
        )

    disc_rules = _get_rule_category(rules, "discount")
    pts_no_flag = float(_get_rule_value(disc_rules, "fake_discount_flag", "points_no_flag", 5.0))
    pts_flag = float(_get_rule_value(disc_rules, "fake_discount_flag", "points_flag", 0.0))

    fake_flag = disc_details.get("fake_discount_flag", False)
    disc_output = _get_nested(calculator_results, "discount", "output_text") or ""

    h73 = pts_flag if fake_flag else pts_no_flag
    f73 = "❌" if fake_flag else "✔️"

    row = RowScore(
        row=73, metric="Discount Check Up",
        value=disc_output, benchmark="-", verdict=f73,
        message="", score=h73,
    )
    return CategoryScore(
        category="Discount",
        score=h73, max_score=5.0, rows=[row],
    )


# ---------------------------------------------------------------------------
# G-column message generation
# ---------------------------------------------------------------------------

def _generate_operational_messages(cat: CategoryScore, manual_data: dict) -> None:
    """Fill G-column messages for operational rows 7-11."""
    for row in cat.rows:
        value = row.value
        if row.row == 7:
            val_str = f"{value:.1f}%"
            if row.verdict == "✔️":
                row.message = f"✔️ Tingkat Pesanan Tidak Terselesaikan = {val_str} Sudah Baik"
            else:
                row.message = f"❌ Tingkat Pesanan Tidak Terselesaikan = {val_str} Kurang Baik, nilai disarankan: <1%"
        elif row.row == 8:
            val_str = f"{value:.1f}%"
            if row.verdict == "✔️":
                row.message = f"✔️ Tingkat Keterlambatan Pengiriman = {val_str} Sudah Baik"
            else:
                row.message = f"❌ Tingkat Keterlambatan Pengiriman = {val_str} Kurang Baik, nilai disarankan: <1%"
        elif row.row == 9:
            val_str = f"{value:.2f}"
            if row.verdict == "✔️":
                row.message = f"✔️ Masa Pengemasan = {val_str} hari Sudah Baik"
            else:
                row.message = f"❌ Masa Pengemasan = {val_str} hari Kurang Baik, nilai disarankan: <1 hari"
        elif row.row == 10:
            val_str = f"{value:.0f}%"
            if row.verdict == "✔️":
                row.message = f"✔️ Persentase Chat Dibalas = {val_str} Sudah Baik"
            else:
                row.message = f"❌ Persentase Chat Dibalas = {val_str} Kurang Baik, nilai disarankan: >95%"
        elif row.row == 11:
            val_str = f"{value:.2f}"
            if row.verdict == "✔️":
                row.message = f"✔️ Keseluruhan Penilaian = {val_str} Sudah Baik"
            else:
                row.message = f"❌ Keseluruhan Penilaian = {val_str} Kurang Baik, nilai disarankan: >4.7"


def _generate_business_messages(cat: CategoryScore, manual_data: dict) -> None:
    """Fill G-column messages for business rows 13-20."""
    biz = _get_nested(manual_data, "business") or {}
    sales_months = [_safe_num(biz.get(f"salesMonth{i}")) for i in range(6)]
    current = sales_months[0]
    avg_6mo = sum(sales_months) / 6 if any(s > 0 for s in sales_months) else 0.0

    for row in cat.rows:
        if row.row == 13:
            idr_val = _fmt_idr(current)
            idr_avg = _fmt_idr(avg_6mo)
            if avg_6mo > 0 and current > 0:
                change_pct = ((current - avg_6mo) / avg_6mo) * 100
            else:
                change_pct = 0.0

            if row.verdict == "✔️":
                row.message = (
                    f"✔️ Penjualan = IDR {idr_val} "
                    f"Meningkat {abs(change_pct):.1f}% dibandingkan dengan "
                    f"rata² 6 bulan terakhir: IDR {idr_avg}"
                )
            else:
                msg = (
                    f"❌ Penjualan = IDR {idr_val} "
                    f"Menurun {abs(change_pct):.1f}% dibandingkan dengan "
                    f"rata² 6 bulan terakhir: IDR {idr_avg}"
                )
                if change_pct < -25:
                    msg += "\n❗️ Potensi peningkatan harga jual signifikan atau terdapat event abnormal."
                row.message = msg
        elif row.row == 20:
            val_str = f"{row.value:.1f}%"
            if row.verdict == "✔️":
                row.message = f"✔️ Tingkat Konversi = {val_str} Sudah Baik"
            elif row.verdict == "❌":
                row.message = f"❌ Tingkat Konversi = {val_str} Kurang Baik, nilai disarankan: {row.benchmark}"


def _generate_content_messages(cat: CategoryScore) -> None:
    """Fill G-column messages for content rows 22-24."""
    for row in cat.rows:
        if row.row == 24:
            val_str = _fmt_pct_0dp(row.value) if isinstance(row.value, float) else str(row.value)
            if row.verdict == "✔️":
                row.message = f"✔️ % Konten baik = {val_str} Sudah Baik"
            else:
                row.message = f"❌ % Konten baik = {val_str} Kurang Baik, nilai disarankan: >95%"


def _generate_visitors_messages(cat: CategoryScore) -> None:
    """Fill G-column messages for visitor rows 26-29."""
    for row in cat.rows:
        if row.row == 28:
            val_str = _fmt_pct_1dp(row.value) if isinstance(row.value, float) else str(row.value)
            if row.verdict == "✔️":
                row.message = f"✔️ % Pengunjung Lama = {val_str} Sudah Baik"
            else:
                row.message = f"❌ % Pengunjung Lama = {val_str} Kurang Baik, nilai disarankan: >23%"
        elif row.row == 29:
            val_str = f"{int(row.value):,}".replace(",", ".")
            if row.verdict == "✔️":
                row.message = f"✔️ Total Pengikut = {val_str} Sudah Baik"
            else:
                row.message = f"❌ Total Pengikut = {val_str} Kurang Baik, nilai disarankan: >50.000"


def _generate_promo_messages(cat: CategoryScore, manual_data: dict) -> None:
    """Fill G-column messages for promo tool rows 31-43."""
    d13 = _safe_num(_get_nested(manual_data, "business", "salesMonth0"))

    for row in cat.rows:
        if PROMO_START_ROW <= row.row <= PROMO_START_ROW + len(PROMO_TOOLS) - 1:
            # Individual promo tool row
            d_value = _safe_num(row.value)
            pct_of_sales = d_value / d13 if d13 > 0 else 0.0
            pct_str = _fmt_pct_1dp(pct_of_sales)

            if d_value == 0:
                row.message = f"{row.verdict} {row.metric} nil pendapatan"
            elif d13 > 0 and d_value / d13 >= 0.50:
                row.message = (
                    f"{row.verdict} {row.metric} = {pct_str} "
                    f"Terlalu mengandalkan promo, nilai disarankan: 15%-50%"
                )
            elif row.verdict == "❌":
                row.message = (
                    f"❌ {row.metric} = {pct_str} "
                    f"Kurang Efektif, nilai disarankan: {row.benchmark}"
                )
            elif row.verdict == "✔️":
                if row.metric == "Program Afiliasi":
                    row.message = f"✔️ {row.metric} ({pct_str}) digunakan"
                else:
                    row.message = f"✔️ {row.metric} ({pct_str}) digunakan & persentase penggunaan baik"

        elif row.row == 42:
            val_str = _fmt_pct_0dp(row.value) if isinstance(row.value, float) else str(row.value)
            if row.verdict == "✔️":
                row.message = f"✔️ Penggunaan alat promosi = {val_str} Sudah Baik"
            else:
                row.message = f"❌ Penggunaan alat promosi = {val_str} Kurang Baik, nilai disarankan: >80%"
        elif row.row == 43:
            val_str = _fmt_pct_0dp(row.value) if isinstance(row.value, float) else str(row.value)
            if row.verdict == "✔️":
                row.message = f"✔️ Efektifitas alat promosi = {val_str} Sudah Baik"
            else:
                row.message = f"❌ Efektifitas alat promosi = {val_str} Kurang Baik, nilai disarankan: >90%"


def _generate_products_messages(cat: CategoryScore) -> None:
    """Fill G-column messages for product/status rows 45-46."""
    for row in cat.rows:
        if row.row == 45:
            if row.verdict == "✔️":
                row.message = f"✔️ Jumlah Produk = {int(row.value)} OK"
            else:
                row.message = f"❌ Jumlah Produk = {int(row.value)} NOT OK, nilai disarankan: >=35"
        elif row.row == 46:
            if row.verdict == "✔️":
                row.message = f"✔️ Status Toko = {row.value} OK"
            elif row.verdict == "❌":
                row.message = f"❌ Status Toko = {row.value} Wajib Shopee Mall"


def _generate_ads_messages(
    cat: CategoryScore, manual_data: dict, calculator_results: dict,
) -> None:
    """Fill G-column messages for ads rows 48-53."""
    d13 = _safe_num(_get_nested(manual_data, "business", "salesMonth0"))
    ads = _get_nested(manual_data, "ads") or {}
    d48 = _safe_num(ads.get("adSales"))
    d49 = _safe_num(ads.get("adCost"))

    # Get Calculator 1 output for G53
    calc1_output = _get_nested(calculator_results, "ads_keyword", "output_text") or ""

    for row in cat.rows:
        if row.row == 50:
            val_str = f"{row.value:.1f}"
            if row.verdict == "✔️":
                row.message = f"✔️ ROI = {val_str} Sudah Baik"
            else:
                row.message = f"❌ ROI = {val_str} Kurang Baik, nilai disarankan: {row.benchmark}"
        elif row.row == 51:
            pct_str = _fmt_pct_1dp(row.value) if isinstance(row.value, float) else str(row.value)
            if d48 == 0:
                row.message = "❌ Iklan tidak aktif sama sekali"
            elif row.verdict == "✔️":
                row.message = f"✔️ % GMV Iklan / GMV Toko = {pct_str} Sudah Baik"
            else:
                row.message = (
                    f"❌ % GMV Iklan / GMV Toko = {pct_str} "
                    f"Terlalu bergantung terhadap Iklan, nilai disarankan: <84%"
                )
        elif row.row == 52:
            d52 = d49 / d13 if d13 > 0 else 0.0
            pct_str = _fmt_pct_1dp(d52)
            if d49 == 0:
                row.message = "❌ Iklan tidak aktif sama sekali"
            elif d52 < 0.05:
                row.message = (
                    f"❌ Penggunaan iklan terlalu minim ({pct_str}). "
                    f"Nilai disarankan: 5-8%."
                )
            elif row.verdict == "❌":
                row.message = (
                    f"❌ % Biaya Iklan / GMV Toko = {pct_str} "
                    f"Biaya terlalu tinggi, nilai disarankan: <10%"
                )
            elif row.verdict == "✔️":
                row.message = f"✔️ % Biaya Iklan / GMV Toko = {pct_str} Sudah Baik"
        elif row.row == 53:
            row.message = calc1_output


def _generate_campaign_messages(cat: CategoryScore) -> None:
    """Fill G-column messages for campaign rows 55-57."""
    for row in cat.rows:
        if row.row == 57:
            if isinstance(row.value, float) and row.value == 0.0:
                # IFERROR fallback: no campaign data
                row.message = "❌Tidak ada Campaign yang dipartisipasikan"
            elif row.verdict == "✔️":
                pct_str = _fmt_pct_1dp(row.value)
                row.message = f"✔️ % Partisipasi Campaign = {pct_str} Sudah Baik"
            else:
                pct_str = _fmt_pct_1dp(row.value) if isinstance(row.value, float) else str(row.value)
                row.message = (
                    f"❌ % Partisipasi Campaign = {pct_str} "
                    f"Kurang Baik, nilai disarankan: >90%"
                )


def _generate_competition_messages(cat: CategoryScore, manual_data: dict) -> None:
    """Fill G-column messages for competition rows 61-63."""
    comp = _get_nested(manual_data, "competition") or {}

    for row in cat.rows:
        i = row.row - 61
        product_key = f"product{i + 1}"
        product_data = comp.get(product_key, {}) or {}
        market_price = _safe_num(product_data.get("marketPrice"))

        if row.verdict == "❌":
            row.message = f"❌tidak kompetitif (harga kisaran pasaran: Rp. {_fmt_idr(market_price)})"
        elif row.verdict == "✔️":
            row.message = "✅kompetitif"


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


def _compute_g72(
    g68_text: str, d52: float, d73_text: str, is_fashion: bool,
) -> float:
    """G72: Recommended marketing percentage (as fraction).

    Complex MIN/MAX formula with Fashion adjustment.
    """
    if not d73_text:
        return 0.15 if is_fashion else 0.12

    t, ra, rb, v, p = _parse_d73_percentages(d73_text)

    avg = ((ra * t + v + p + d52) + (rb * t + v + p + d52)) / 2
    base = _rounddown(avg - 0.03, 2)

    upper_limit = 0.20 + (0.05 if is_fashion else 0.0)

    # Parse first percentage from G68 text
    g68_first = 0.0
    if g68_text:
        match = re.search(r"([\d.]+)%", g68_text)
        if match:
            g68_first = math.ceil(float(match.group(1))) / 100

    min_val = min(min(base, upper_limit), g68_first) if g68_first > 0 else min(base, upper_limit)
    result = max(max(min_val, 0.10), 0.15 if is_fashion else 0.12)

    return result


def _compute_g73(
    verdict: str, g72_value: float, d13: float, is_fashion: bool,
) -> str:
    """G73: Marketing budget recommendation text.

    Suppressed for ❌ and ⭕️ verdicts.
    """
    if verdict.startswith("❌") or verdict == "⭕️":
        return ""

    # Clamp to range
    display_pct = max(min(g72_value, 0.25), 0.10)
    pct_str = f"{display_pct * 100:.0f}%"

    budget = d13 * display_pct if d13 > 0 else 0
    budget_str = _fmt_idr(budget)

    return (
        f"💡Minimum anggaran marketing yang dibutuhkan AHA untuk meningkatkan "
        f"performa omzet penjualan toko = {pct_str}"
        f" (± IDR {budget_str}/bulan)"
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


def _compute_g75(verdict: str) -> str:
    """G75: Closing message based on verdict type."""
    messages = {
        "✔️": (
            "Berdasarkan data analisa diatas, potensi toko masih belum maksimal. "
            "Kami mengundang untuk berdiskusi mengenai potensi optimisasi toko melalui "
            "link berikut: cal-bd2.ahacommerce.net"
        ),
        "❌": (
            "Berdasarkan data analisa diatas, perlu mempertimbangkan potensi keuntungan. "
            "Silakan cek AHA Coventures: bit.ly/AHACoventures"
        ),
        "❌ Non Mall": (
            "Toko belum berstatus Mall. AHA dapat membantu proses pengajuan Shopee Mall. "
            "Persyaratan: HAKI (Merek Terdaftar), NIB, dan dokumen legalitas usaha."
        ),
        "❌ No Brand": (
            "Toko bukan merupakan toko yang memiliki brand sendiri. "
            "Terima kasih atas waktunya, semoga sukses selalu."
        ),
        "": (
            "Performa toko sudah cukup baik. "
            "Terima kasih atas waktunya, semoga sukses selalu."
        ),
        "❌ Opex": (
            "Tingkat keterlambatan cukup tinggi. Disarankan untuk memperbaiki pengiriman (<2%) "
            "dan masa pengemasan (<1 hari) terlebih dahulu."
        ),
        "⭕️": "",
    }
    return messages.get(verdict, "")


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

    # 3. Content
    content_msgs = _get_messages("Skor Kesehatan Konten", [24])
    if content_msgs:
        sections.append("📝 Kualitas Konten Produk:")
        sections.extend(content_msgs)
        sections.append("")

    # 4. Visitors
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
        # Add summary rows (42, 43) and store status (46)
        for r in promo_cat.rows:
            if r.row in (42, 43) and r.message:
                promo_msgs.append(r.message)

        # Include store status from products
        products_cat = next((c for c in categories if c.category == "Jumlah Produk & Status Toko"), None)
        if products_cat:
            status_row = next((r for r in products_cat.rows if r.row == 46), None)
            if status_row and status_row.message:
                promo_msgs.append(status_row.message)

        if promo_msgs:
            sections.append("🏷️ Tingkat Penggunaan Alat Promosi:")
            sections.extend(promo_msgs)
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
# WhatsApp link
# ---------------------------------------------------------------------------

def _build_whatsapp_link(store_name: str, period: str) -> str:
    """Build api.whatsapp.com link with pre-formatted message."""
    message = (
        f"Halo, ini hasil Store Internal Check Up (Store ICU) "
        f"untuk {store_name} periode {period}. "
        f"Silakan cek email untuk detail lengkapnya."
    )
    encoded = quote(message, safe="")
    return f"https://api.whatsapp.com/send?text={encoded}"


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
        template: "fashion" or "non_fashion".
        verdict: F75 user-selected verdict string.
        store_name: Store display name (G2).
        period: Period string (e.g., "Jan 2026").
        brand_name: Short brand name (H2).
        email: Optional email address (G3).
        rules: Optional rules dict from DB. Falls back to defaults when None.
        rule_version: Version of the rules used (from DB).

    Returns:
        ScoringResult with all scores, messages, email body, and WhatsApp link.
    """
    is_fashion = template == "fashion"

    # --- Per-category scoring ---
    cat_operational = _score_operational(manual_data, rules)
    cat_business = _score_business(manual_data, rules)
    cat_content = _score_content(manual_data, rules)
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
    conv_default = 2.0 if is_fashion else 3.0
    conv_threshold = _get_rule_value(biz_rules, "conversion_rate", "threshold", conv_default)
    conv_row = next((r for r in cat_business.rows if r.row == 20), None)
    if conv_row:
        conv_row.benchmark = f">{conv_threshold:.0f}%"
        conv_row.verdict = "✔️" if conv_row.value >= conv_threshold else "❌"

    all_categories = [
        cat_operational, cat_business, cat_content, cat_visitors,
        cat_promo, cat_products, cat_ads, cat_campaign,
        cat_competition, cat_stock, cat_discount,
    ]

    # --- Total score (H4) ---
    total_score = sum(cat.score for cat in all_categories)

    # --- G-column messages ---
    _generate_operational_messages(cat_operational, manual_data)
    _generate_business_messages(cat_business, manual_data)
    _generate_content_messages(cat_content)
    _generate_visitors_messages(cat_visitors)
    _generate_promo_messages(cat_promo, manual_data)
    _generate_products_messages(cat_products)
    _generate_ads_messages(cat_ads, manual_data, calculator_results)
    _generate_campaign_messages(cat_campaign)
    _generate_competition_messages(cat_competition, manual_data)

    # --- Derived formulas ---
    d13 = _safe_num(_get_nested(manual_data, "business", "salesMonth0"))
    d49 = _safe_num(_get_nested(manual_data, "ads", "adCost"))
    d52 = d49 / d13 if d13 > 0 else 0.0

    d73_text = _get_nested(calculator_results, "discount", "output_text") or ""

    g68 = _compute_g68(d73_text, d52)
    g72 = _compute_g72(g68, d52, d73_text, is_fashion)
    g73 = _compute_g73(verdict, g72, d13, is_fashion)

    marketing_label = f"📌 Estimasi persentase biaya marketing {brand_name} sekarang:"

    g66 = _compute_g66(all_categories, manual_data, g68)
    g75 = _compute_g75(verdict)

    # --- Email ---
    email_subject = f"🏥 AHA Store Internal Check Up (Store ICU) - {store_name} {period}"
    email_body = _assemble_email_body(
        all_categories, g66, marketing_label, g68, g73, g75,
    )

    # --- WhatsApp ---
    whatsapp_link = _build_whatsapp_link(store_name, period)

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
        whatsapp_link=whatsapp_link,
        template=template,
        rule_version=rule_version,
    )
