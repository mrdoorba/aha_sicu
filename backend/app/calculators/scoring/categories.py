"""Per-category scoring functions for the 75-row scoring system."""

from __future__ import annotations

import math

from app.calculators.scoring.helpers import (
    _fmt_idr,
    _fmt_pct_1dp,
    _generate_month_labels,
    _get_nested,
    _get_rule_category,
    _get_rule_value,
    _safe_num,
    _safe_str,
)
from app.calculators.scoring.models import CategoryScore, RowScore, TranslatableText
from app.calculators.scoring.rules import PROMO_START_ROW, PROMO_TOOLS
from app.core.marketplace import MARKETPLACE_CURRENCY

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
        value=d7, benchmark=f"<{uor_threshold:g}%", verdict=f7, message="", score=h7,
        metric_i18n=TranslatableText(key="scoring.unfulfilledOrderRate", vars={}),
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
        value=d8, benchmark=f"<{lsr_threshold:g}%", verdict=f8, message="", score=h8,
        metric_i18n=TranslatableText(key="scoring.lateShipmentRate", vars={}),
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
        value=d9, benchmark=f"<{pt_threshold:g}", verdict=f9, message="", score=h9,
        metric_i18n=TranslatableText(key="scoring.preparationTime", vars={}),
    ))

    # Row 10: Chat Dibalas (no score)
    d10 = _safe_num(ops.get("chatResponseRate"))
    chat_threshold = _get_rule_value(ops_rules, "chat_response_rate", "threshold", 95.0)
    # F10 special: ROUNDUP to 2 decimals before comparing
    d10_rounded = math.ceil(d10 * 100) / 100
    f10 = "✔️" if d10_rounded >= chat_threshold else "❌"
    rows.append(RowScore(
        row=10, metric="Persentase Chat Dibalas",
        value=d10, benchmark=f">{chat_threshold:g}%", verdict=f10, message="", score=0.0,
        metric_i18n=TranslatableText(key="scoring.chatResponseRate", vars={}),
    ))

    # Row 11: Overall Rating (no score)
    d11 = _safe_num(ops.get("overallRating"))
    rating_threshold = _get_rule_value(ops_rules, "overall_rating", "threshold", 4.7)
    f11 = "✔️" if d11 >= rating_threshold else "❌"
    rows.append(RowScore(
        row=11, metric="Keseluruhan Penilaian",
        value=d11, benchmark=f">{rating_threshold:g}", verdict=f11, message="", score=0.0,
        metric_i18n=TranslatableText(key="scoring.overallRating", vars={}),
    ))

    total = sum(r.score for r in rows)
    return CategoryScore(
        category="Kesehatan Operasional Toko",
        score=total, max_score=10.0, rows=rows,
        category_i18n=TranslatableText(key="category.operational", vars={}),
    )


def _score_business(manual_data: dict, rules: dict | None = None) -> CategoryScore:
    """Score rows 13-20: Bisnis Analisis.

    H13: 10 if avg_6mo < salesMonth0 × 110%, else 0
    H19: 10 if avg_6mo > 100M IDR, else 0
    Rows 14-18, 20: no H score.
    """
    biz = _get_nested(manual_data, "business") or {}
    biz_rules = _get_rule_category(rules, "business")

    sales_start_month = biz.get("salesStartMonth")
    month_labels = _generate_month_labels(sales_start_month)

    sales_months = [
        _safe_num(biz.get("salesMonth0")),
        _safe_num(biz.get("salesMonth1")),
        _safe_num(biz.get("salesMonth2")),
        _safe_num(biz.get("salesMonth3")),
        _safe_num(biz.get("salesMonth4")),
        _safe_num(biz.get("salesMonth5")),
    ]
    current_month = sales_months[0]
    avg_6mo = round(sum(sales_months) / 6) if any(s > 0 for s in sales_months) else 0
    rows: list[RowScore] = []

    # Row 13: Current month sales
    trend_pct = _get_rule_value(biz_rules, "monthly_sales_trend", "threshold_pct", 90.0)
    trend_points = float(_get_rule_value(biz_rules, "monthly_sales_trend", "points", 10.0))
    # threshold_pct=90 → multiplier=1.10: pass if avg < current × multiplier
    trend_multiplier = (200 - trend_pct) / 100
    e13 = f">{_fmt_idr(avg_6mo)}" if avg_6mo > 0 else "-"
    f13 = "✔️" if current_month >= avg_6mo and avg_6mo > 0 else "❌"
    h13 = trend_points if avg_6mo < current_month * trend_multiplier else 0.0
    rows.append(RowScore(
        row=13, metric=f"Penjualan Bulan {month_labels[0]}",
        value=current_month, benchmark=e13, verdict=f13, message="", score=h13,
        metric_i18n=TranslatableText(key="scoring.monthlySales", vars={"month": month_labels[0]}),
    ))

    # Rows 14-18: Past months (no score, kept for reference)
    for i in range(1, 6):
        rows.append(RowScore(
            row=13 + i, metric=f"Penjualan Bulan {month_labels[i]}",
            value=sales_months[i], benchmark="-", verdict="-", message="", score=0.0,
            metric_i18n=TranslatableText(key="scoring.pastMonthlySales", vars={"month": month_labels[i]}),
        ))

    # Row 19: Average (computed)
    avg_threshold = _get_rule_value(biz_rules, "six_month_avg_threshold", "threshold", 100_000_000)
    avg_points = float(_get_rule_value(biz_rules, "six_month_avg_threshold", "points", 10.0))
    h19 = avg_points if avg_6mo > avg_threshold else 0.0
    rows.append(RowScore(
        row=19, metric="Rata² Penjualan 6 bulan terakhir",
        value=avg_6mo, benchmark="-", verdict="-", message="", score=h19,
        metric_i18n=TranslatableText(key="scoring.avgSales6mo", vars={}),
    ))

    # Row 20: Conversion rate (no score) — benchmark depends on template
    # Template check happens in main function; store raw value for now
    d20 = _safe_num(biz.get("conversionRate"))
    rows.append(RowScore(
        row=20, metric="Tingkat Konversi",
        value=d20, benchmark=">3%", verdict="-", message="", score=0.0,
        metric_i18n=TranslatableText(key="scoring.conversionRate", vars={}),
    ))

    total = sum(r.score for r in rows)
    return CategoryScore(
        category="Bisnis Analisis",
        score=total, max_score=20.0, rows=rows,
        category_i18n=TranslatableText(key="category.business", vars={}),
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
        metric_i18n=TranslatableText(key="scoring.totalVisitors", vars={}),
    ))
    rows.append(RowScore(
        row=27, metric="Pengunjung Lama",
        value=d27, benchmark="-", verdict="-", message="", score=0.0,
        metric_i18n=TranslatableText(key="scoring.returningVisitors", vars={}),
    ))

    # Row 28: % Returning visitors (computed)
    rv_threshold = _get_rule_value(vis_rules, "returning_visitors_pct", "threshold", 23.0) / 100
    rv_points = float(_get_rule_value(vis_rules, "returning_visitors_pct", "points", 3.0))
    d28 = d27 / d26 if d26 > 0 else 0.0
    f28 = "✔️" if d28 > rv_threshold else "❌"
    h28 = rv_points if d28 > rv_threshold else 0.0
    rows.append(RowScore(
        row=28, metric="% Pengunjung Lama",
        value=d28, benchmark=f">{rv_threshold * 100:g}%", verdict=f28, message="", score=h28,
        metric_i18n=TranslatableText(key="scoring.returningVisitorPct", vars={}),
    ))

    # Row 29: Total followers
    fl_threshold = _get_rule_value(vis_rules, "followers", "threshold", 50000)
    fl_points = float(_get_rule_value(vis_rules, "followers", "points", 2.0))
    f29 = "✔️" if d29 > fl_threshold else "❌"
    h29 = fl_points if d29 > fl_threshold else 0.0
    rows.append(RowScore(
        row=29, metric="Total Pengikut",
        value=d29, benchmark=f">{fl_threshold:g}", verdict=f29, message="", score=h29,
        metric_i18n=TranslatableText(key="scoring.totalFollowers", vars={}),
    ))

    total = h28 + h29
    return CategoryScore(
        category="Tinjauan Pengunjung",
        score=total, max_score=5.0, rows=rows,
        category_i18n=TranslatableText(key="category.visitors", vars={}),
    )


def _promo_verdict(d_value: float, d13_sales: float, benchmark_pct: float, key: str = "") -> str:
    """Determine F-column verdict for a promo tool row (31-41).

    Logic:
    - D=0 → "❌" (not used)
    - D/D13 >= 50% → "❌" (too dependent) — only for promoToko
    - D >= benchmark% × D13 → "✔️" (meets benchmark)
    - else → "❌"
    """
    if d_value == 0:
        return "❌"
    if key == "promoToko" and d13_sales > 0 and d_value / d13_sales >= 0.50:
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

        f_verdict = _promo_verdict(d_value, d13, benchmark_pct, key=field_key)

        if d_value > 0:
            used_count += 1
        if f_verdict == "✔️":
            pass_count += 1

        rows.append(RowScore(
            row=row_num, metric=display_name,
            value=d_value, benchmark=benchmark_str, verdict=f_verdict,
            message="", score=0.0,
            metric_i18n=TranslatableText(key=f"scoring.promo.{field_key}", vars={}),
        ))

    # Row 42: % Usage
    usage_threshold = _get_rule_value(promo_rules, "usage_pct_threshold", "threshold", 80.0) / 100
    usage_opp_pts = float(_get_rule_value(promo_rules, "usage_pct_threshold", "opportunity_points", 5.0))
    usage_rate = used_count / total_tools if total_tools > 0 else 0.0
    f42 = "✔️" if usage_rate > usage_threshold else "❌"
    h42 = 0.0 if usage_rate > usage_threshold else usage_opp_pts
    rows.append(RowScore(
        row=42, metric="% Penggunaan alat promosi",
        value=usage_rate, benchmark=f">{usage_threshold * 100:g}%", verdict=f42, message="", score=h42,
        metric_i18n=TranslatableText(key="scoring.promoUsageRate", vars={}),
    ))

    # Row 43: % Effectiveness
    eff_threshold = _get_rule_value(promo_rules, "effectiveness_pct_threshold", "threshold", 90.0) / 100
    eff_opp_pts = float(_get_rule_value(promo_rules, "effectiveness_pct_threshold", "opportunity_points", 10.0))
    effectiveness_rate = pass_count / total_tools if total_tools > 0 else 0.0
    f43 = "✔️" if effectiveness_rate > eff_threshold else "❌"
    h43 = 0.0 if effectiveness_rate > eff_threshold else eff_opp_pts
    rows.append(RowScore(
        row=43, metric="% Efektifitas alat promosi",
        value=effectiveness_rate, benchmark=f">{eff_threshold * 100:g}%", verdict=f43, message="", score=h43,
        metric_i18n=TranslatableText(key="scoring.promoEffectiveness", vars={}),
    ))

    total = h42 + h43
    return CategoryScore(
        category="Promo Toko",
        score=total, max_score=15.0, rows=rows,
        category_i18n=TranslatableText(key="category.promo", vars={}),
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
        value=d45, benchmark=f">={pc_threshold:g}", verdict=f45, message="", score=h45,
        metric_i18n=TranslatableText(key="scoring.productCount", vars={}),
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
        metric_i18n=TranslatableText(key="scoring.storeStatus", vars={}),
    ))

    total = h45 + h46
    return CategoryScore(
        category="Jumlah Produk & Status Toko",
        score=total, max_score=15.0, rows=rows,
        category_i18n=TranslatableText(key="category.products", vars={}),
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
        metric_i18n=TranslatableText(key="scoring.adSales", vars={}),
    ))

    # Row 49: Ad cost (no score), E49 = D49/D13
    d49_pct = d49 / d13 if d13 > 0 else 0.0
    rows.append(RowScore(
        row=49, metric="Biaya (iklan)",
        value=d49, benchmark=f"{_fmt_pct_1dp(d49_pct)}", verdict="-",
        message="", score=0.0,
        metric_i18n=TranslatableText(key="scoring.adCost", vars={}),
    ))

    # Row 50: ROI = D48/D49
    d50 = round(d48 / d49, 1) if d49 > 0 else 0.0
    roi_threshold = _get_rule_value(ads_rules, "roi_threshold", "threshold", 9.0)
    roi_opp_pts = float(_get_rule_value(ads_rules, "roi_threshold", "opportunity_points", 5.0))
    f50 = "✔️" if d50 >= roi_threshold else "❌"
    h50 = 0.0 if d50 >= roi_threshold else roi_opp_pts
    rows.append(RowScore(
        row=50, metric="ROI",
        value=d50, benchmark=f">{roi_threshold:g}", verdict=f50,
        message="", score=h50,
        metric_i18n=TranslatableText(key="scoring.adsROI", vars={}),
    ))

    # Row 51: GMV ratio = D48/D13
    gmv_threshold = _get_rule_value(ads_rules, "gmv_ratio_threshold", "threshold", 84.0) / 100
    gmv_points = float(_get_rule_value(ads_rules, "gmv_ratio_threshold", "points", 5.0))
    d51 = d48 / d13 if d13 > 0 else 0.0
    f51 = "✔️" if d51 < gmv_threshold else "❌"
    h51 = gmv_points if d51 < gmv_threshold else 0.0
    rows.append(RowScore(
        row=51, metric="% GMV Iklan / GMV Toko",
        value=d51, benchmark=f"<{gmv_threshold * 100:g}%", verdict=f51, message="", score=h51,
        metric_i18n=TranslatableText(key="scoring.adsGMVPct", vars={}),
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
        metric_i18n=TranslatableText(key="scoring.adsCostPct", vars={}),
    ))

    # Row 53: Calculator 1 output (no score, just email content)
    rows.append(RowScore(
        row=53, metric="Iklan check up",
        value="", benchmark="Iklan check up", verdict="-", message="", score=0.0,
        metric_i18n=TranslatableText(key="scoring.adsCheckup", vars={}),
    ))

    total = h50 + h51
    return CategoryScore(
        category="Data Iklan",
        score=total, max_score=10.0, rows=rows,
        category_i18n=TranslatableText(key="category.ads", vars={}),
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
        metric_i18n=TranslatableText(key="scoring.nominatedSessions", vars={}),
    ))
    rows.append(RowScore(
        row=56, metric="Sesi tersedia",
        value=d56, benchmark="-", verdict="-", message="", score=0.0,
        metric_i18n=TranslatableText(key="scoring.availableSessions", vars={}),
    ))

    # Row 57: Participation rate = D55/D56
    part_threshold = _get_rule_value(camp_rules, "participation_pct_threshold", "threshold", 90.0) / 100
    part_opp_pts = float(_get_rule_value(camp_rules, "participation_pct_threshold", "opportunity_points", 10.0))
    d57 = d55 / d56 if d56 > 0 else 0.0
    f57 = "✔️" if d57 > part_threshold else "❌"
    h57 = 0.0 if d57 > part_threshold else part_opp_pts
    rows.append(RowScore(
        row=57, metric="% Partisipasi Campaign",
        value=d57, benchmark=f">{part_threshold * 100:g}%", verdict=f57, message="", score=h57,
        metric_i18n=TranslatableText(key="scoring.campaignParticipation", vars={}),
    ))

    return CategoryScore(
        category="Partisipasi Campaign",
        score=h57, max_score=10.0, rows=rows,
        category_i18n=TranslatableText(key="category.campaign", vars={}),
    )


def _score_competition(
    manual_data: dict, calculator_results: dict,
    *, marketplace: str = "ID",
) -> CategoryScore:
    """Score rows 60-63: Kompetisi TOP Produk.

    No H-column scores. G-column messages for competitiveness check.
    C61-C63: selling prices from manual product data (sellingPrice)
    F61-F63: market price (manual input)
    """
    comp = _get_nested(manual_data, "competition") or {}
    rows: list[RowScore] = []

    for i in range(3):
        row_num = 61 + i
        product_key = f"product{i + 1}"
        product_data = comp.get(product_key, {}) or {}

        selling_price = _safe_num(product_data.get("sellingPrice"))
        market_price = _safe_num(product_data.get("marketPrice"))

        # F: competitive if selling price <= market price × 110%
        if selling_price > 0 and market_price > 0:
            f_verdict = "❌" if selling_price > market_price * 1.10 else "✔️"
        else:
            f_verdict = "-"

        rows.append(RowScore(
            row=row_num, metric=f"Produk {i + 1}",
            value=selling_price, benchmark=f"{MARKETPLACE_CURRENCY.get(marketplace, 'IDR')} {_fmt_idr(market_price)}" if market_price > 0 else "-",
            verdict=f_verdict, message="", score=0.0,
            metric_i18n=TranslatableText(key="scoring.competitionProduct", vars={}),
        ))

    return CategoryScore(
        category="Kompetisi TOP Produk",
        score=0.0, max_score=0.0, rows=rows,
        category_i18n=TranslatableText(key="category.competition", vars={}),
    )


def _score_stock(calculator_results: dict, rules: dict | None = None) -> CategoryScore:
    """Score rows 70-71: Stock Analysis.

    H70: >=24 → 10, >=12 → 5, <12 → -5
    H71: out_of_stock_pct > threshold → penalty (-5), else 0
    Source: Calculator 2 details.average_stock, details.out_of_stock_pct
    """
    top_sku_data = _get_nested(calculator_results, "top_sku", "details")
    has_data = top_sku_data is not None and "average_stock" in (top_sku_data or {})

    stock_rules = _get_rule_category(rules, "stock")
    high_threshold = _get_rule_value(stock_rules, "high_threshold", "threshold", 24)

    if not has_data:
        row = RowScore(
            row=70, metric="Rata² Stok TOP 20% SKU",
            value="N/A", benchmark=f">={high_threshold:g}", verdict="-",
            message="Calculator 2 (Top SKU) belum dijalankan", score=0.0,
            metric_i18n=TranslatableText(key="scoring.avgStockTop20", vars={}),
        )
        return CategoryScore(
            category="Stok",
            score=0.0, max_score=10.0, rows=[row], available=False,
            category_i18n=TranslatableText(key="category.stock", vars={}),
        )
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

    if avg_stock_int >= high_threshold:
        msg70 = f"✔️ Rata² Stok TOP 20% SKU = {avg_stock_int} [Sudah Baik]"
        msg70_key = "scoring.avgStockTop20.pass"
    else:
        msg70 = f"❌ Rata² Stok TOP 20% SKU = {avg_stock_int} [Kurang Baik, nilai disarankan: >={high_threshold:g}]"
        msg70_key = "scoring.avgStockTop20.fail"

    stock_vars = {"value": str(avg_stock_int), "threshold": f"{high_threshold:g}"}

    row70 = RowScore(
        row=70, metric="Rata² Stok TOP 20% SKU",
        value=avg_stock_int, benchmark=f">={high_threshold:g}", verdict=f70,
        message=msg70, score=h70,
        metric_i18n=TranslatableText(key="scoring.avgStockTop20", vars={}),
        message_i18n=TranslatableText(key=msg70_key, vars=stock_vars),
        benchmark_i18n=TranslatableText(key="scoring.avgStockTop20.benchmark", vars={"threshold": f"{high_threshold:g}"}),
    )

    # Row 71: Stock availability penalty
    oos_threshold = float(_get_rule_value(stock_rules, "out_of_stock", "threshold", 0.10))
    oos_penalty = float(_get_rule_value(stock_rules, "out_of_stock", "penalty", -5.0))
    out_of_stock_pct = _safe_num(top_sku_data.get("out_of_stock_pct", 0.0))

    if out_of_stock_pct > oos_threshold:
        f71, h71 = "❌", oos_penalty
    else:
        f71, h71 = "✔️", 0.0

    oos_pct_display = f"{out_of_stock_pct * 100:.0f}%"
    oos_threshold_display = f"{oos_threshold * 100:.0f}"
    if f71 == "✔️":
        msg71 = f"✔️ % Ketersediaan Stok = {oos_pct_display} stok habis [Sudah Baik]"
        msg71_key = "scoring.stockAvailability.pass"
    else:
        msg71 = f"❌ % Ketersediaan Stok = {oos_pct_display} stok habis [Kurang Baik, nilai disarankan: ≤{oos_threshold_display}%]"
        msg71_key = "scoring.stockAvailability.fail"

    oos_vars = {"value": oos_pct_display, "threshold": oos_threshold_display}

    row71 = RowScore(
        row=71, metric="% Ketersediaan Stok",
        value=out_of_stock_pct,
        benchmark=f"≤{oos_threshold_display}% stok habis",
        verdict=f71, message=msg71, score=h71,
        metric_i18n=TranslatableText(key="scoring.stockAvailability", vars={}),
        message_i18n=TranslatableText(key=msg71_key, vars=oos_vars),
        benchmark_i18n=TranslatableText(key="scoring.stockAvailability.benchmark", vars={"threshold": oos_threshold_display}),
    )

    total_score = h70 + h71
    return CategoryScore(
        category="Stok",
        score=total_score, max_score=10.0, rows=[row70, row71],
        category_i18n=TranslatableText(key="category.stock", vars={}),
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
            metric_i18n=TranslatableText(key="scoring.discountCheckup", vars={}),
        )
        return CategoryScore(
            category="Discount",
            score=0.0, max_score=5.0, rows=[row], available=False,
            category_i18n=TranslatableText(key="category.discount", vars={}),
        )

    disc_rules = _get_rule_category(rules, "discount")
    pts_no_flag = float(_get_rule_value(disc_rules, "fake_discount_flag", "points_no_flag", 5.0))
    pts_flag = float(_get_rule_value(disc_rules, "fake_discount_flag", "points_flag", 0.0))

    fake_flag = disc_details.get("fake_discount_flag", False)
    disc_output = _get_nested(calculator_results, "discount", "output_text") or ""

    h73 = pts_flag if fake_flag else pts_no_flag
    f73 = "❌" if fake_flag else "✔️"

    # Extract structured details for i18n
    discount_pct = str(disc_details.get("discount_pct", "0.0%"))
    range_min = str(disc_details.get("range_min", "0.0%"))
    range_max = str(disc_details.get("range_max", "0.0%"))
    voucher_pct = str(disc_details.get("voucher_pct", "0.0%"))
    paket_pct = str(disc_details.get("paket_pct", "0.0%"))

    i18n_key = "scoring.discountCheckup.fail" if fake_flag else "scoring.discountCheckup.pass"
    i18n_vars = {
        "discountPct": discount_pct,
        "rangeMin": range_min,
        "rangeMax": range_max,
        "voucherPct": voucher_pct,
        "paketPct": paket_pct,
    }

    row = RowScore(
        row=73, metric="Discount Check Up",
        value=disc_output, benchmark="-", verdict=f73,
        message="", score=h73,
        metric_i18n=TranslatableText(key="scoring.discountCheckup", vars={}),
        value_i18n=TranslatableText(key=i18n_key, vars=i18n_vars),
    )
    return CategoryScore(
        category="Discount",
        score=h73, max_score=5.0, rows=[row],
        category_i18n=TranslatableText(key="category.discount", vars={}),
    )


