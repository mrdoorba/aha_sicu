"""G-column message generators for each scoring category."""

from __future__ import annotations

from app.calculators.scoring.helpers import (
    _fmt_currency,
    _fmt_pct_0dp,
    _fmt_pct_1dp,
    _format_message_template,
    _get_nested,
    _get_rule_category,
    _get_rule_value,
    _safe_num,
    _safe_str,
)
from app.calculators.scoring.models import CategoryScore, TranslatableText
from app.calculators.scoring.rules import PROMO_START_ROW, PROMO_TOOLS
from app.core.marketplace import MARKETPLACE_CURRENCY

def _generate_operational_messages(cat: CategoryScore, manual_data: dict, rules: dict | None = None) -> None:
    """Fill G-column messages for operational rows 7-11.

    Inline fallback defaults must match DEFAULT_RULES message templates.
    """
    ops_rules = _get_rule_category(rules, "operational")

    # (rule_key, default_threshold, formatter, pass_default, fail_default)
    _ROW_DEFAULTS = {
        7: ("unfulfilled_order_rate", 1.0, lambda v: f"{v:.1f}%",
            "✔️ Tingkat Pesanan Tidak Terselesaikan = {val_str} [Sudah Baik]",
            "❌ Tingkat Pesanan Tidak Terselesaikan = {val_str} [Kurang Baik, nilai disarankan: <{threshold}%]"),
        8: ("late_shipment_rate", 1.0, lambda v: f"{v:.1f}%",
            "✔️ Tingkat Keterlambatan Pengiriman = {val_str} [Sudah Baik]",
            "❌ Tingkat Keterlambatan Pengiriman = {val_str} [Kurang Baik, nilai disarankan: <{threshold}%]"),
        9: ("preparation_time", 1.0, lambda v: f"{v:.2f}",
            "✔️ Masa Pengemasan = {val_str} hari [Sudah Baik]",
            "❌ Masa Pengemasan = {val_str} hari [Kurang Baik, nilai disarankan: <{threshold} hari]"),
        10: ("chat_response_rate", 95.0, lambda v: f"{v:.0f}%",
            "✔️ Persentase Chat Dibalas = {val_str} [Sudah Baik]",
            "❌ Persentase Chat Dibalas = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]"),
        11: ("overall_rating", 4.7, lambda v: f"{v:.2f}",
            "✔️ Keseluruhan Penilaian = {val_str} [Sudah Baik]",
            "❌ Keseluruhan Penilaian = {val_str} [Kurang Baik, nilai disarankan: >{threshold}]"),
    }

    for row in cat.rows:
        if row.row not in _ROW_DEFAULTS:
            continue
        rule_key, default_threshold, fmt_fn, pass_default, fail_default = _ROW_DEFAULTS[row.row]
        val_str = fmt_fn(row.value)
        threshold = _get_rule_value(ops_rules, rule_key, "threshold", default_threshold)
        threshold_str = f"{threshold:g}" if isinstance(threshold, float) else str(threshold)
        # Map rule_key back to camelCase field key for i18n
        _RULE_TO_FIELD = {
            "unfulfilled_order_rate": "unfulfilledOrderRate",
            "late_shipment_rate": "lateShipmentRate",
            "preparation_time": "preparationTime",
            "chat_response_rate": "chatResponseRate",
            "overall_rating": "overallRating",
        }
        field_key = _RULE_TO_FIELD[rule_key]
        if row.verdict == "✔️":
            tmpl = _get_rule_value(ops_rules, rule_key, "message_pass", pass_default)
            row.message = _format_message_template(tmpl, val_str=val_str, threshold=threshold_str)
            row.message_i18n = TranslatableText(
                key=f"scoring.{field_key}.pass",
                vars={"value": val_str, "threshold": threshold_str},
            )
        else:
            tmpl = _get_rule_value(ops_rules, rule_key, "message_fail", fail_default)
            row.message = _format_message_template(tmpl, val_str=val_str, threshold=threshold_str)
            row.message_i18n = TranslatableText(
                key=f"scoring.{field_key}.fail",
                vars={"value": val_str, "threshold": threshold_str},
            )


def _generate_business_messages(cat: CategoryScore, manual_data: dict, rules: dict | None = None, *, marketplace: str = "ID") -> None:
    """Fill G-column messages for business rows 13-20."""
    biz_rules = _get_rule_category(rules, "business")
    biz = _get_nested(manual_data, "business") or {}
    sales_months = [_safe_num(biz.get(f"salesMonth{i}")) for i in range(6)]
    current = sales_months[0]
    avg_6mo = round(sum(sales_months) / 6) if any(s > 0 for s in sales_months) else 0
    currency_code = MARKETPLACE_CURRENCY.get(marketplace, "IDR")

    for row in cat.rows:
        if row.row == 13:
            idr_val = _fmt_currency(current, marketplace)
            idr_avg = _fmt_currency(avg_6mo, marketplace)
            if avg_6mo > 0 and current > 0:
                change_pct = ((current - avg_6mo) / avg_6mo) * 100
            else:
                change_pct = 0.0
            change_pct_str = f"{abs(change_pct):.1f}"

            if row.verdict == "✔️":
                tmpl = _get_rule_value(biz_rules, "monthly_sales_trend", "message_pass",
                    "✔️ Penjualan = {currency} {idr_val} [Meningkat {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: {currency} {idr_avg}]")
                row.message = _format_message_template(tmpl, idr_val=idr_val, change_pct=change_pct_str, idr_avg=idr_avg, currency=currency_code)
                row.message_i18n = TranslatableText(
                    key="scoring.monthlySales.pass",
                    vars={"value": idr_val, "changePct": change_pct_str, "avg": idr_avg, "currency": currency_code},
                )
            else:
                tmpl = _get_rule_value(biz_rules, "monthly_sales_trend", "message_fail",
                    "❌ Penjualan = {currency} {idr_val} [Menurun {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: {currency} {idr_avg}]")
                msg = _format_message_template(tmpl, idr_val=idr_val, change_pct=change_pct_str, idr_avg=idr_avg, currency=currency_code)
                if change_pct < -25:
                    severe_tmpl = _get_rule_value(biz_rules, "monthly_sales_trend", "message_fail_severe",
                        "\n❗️ Potensi peningkatan harga jual signifikan atau terdapat event abnormal.")
                    msg += severe_tmpl
                row.message = msg
                row.message_i18n = TranslatableText(
                    key="scoring.monthlySales.fail",
                    vars={"value": idr_val, "changePct": change_pct_str, "avg": idr_avg, "currency": currency_code},
                )
        elif row.row == 20:
            val_str = f"{row.value:.1f}%"
            if row.verdict == "✔️":
                tmpl = _get_rule_value(biz_rules, "conversion_rate", "message_pass",
                    "✔️ Tingkat Konversi = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str, benchmark=row.benchmark)
                row.message_i18n = TranslatableText(
                    key="scoring.conversionRate.pass",
                    vars={"value": val_str, "benchmark": row.benchmark},
                )
            elif row.verdict == "❌":
                tmpl = _get_rule_value(biz_rules, "conversion_rate", "message_fail",
                    "❌ Tingkat Konversi = {val_str} [Kurang Baik, nilai disarankan: {benchmark}]")
                row.message = _format_message_template(tmpl, val_str=val_str, benchmark=row.benchmark)
                row.message_i18n = TranslatableText(
                    key="scoring.conversionRate.fail",
                    vars={"value": val_str, "benchmark": row.benchmark},
                )


def _generate_visitors_messages(cat: CategoryScore, rules: dict | None = None) -> None:
    """Fill G-column messages for visitor rows 26-29."""
    vis_rules = _get_rule_category(rules, "visitors")
    for row in cat.rows:
        if row.row == 28:
            val_str = _fmt_pct_1dp(row.value) if isinstance(row.value, float) else str(row.value)
            threshold = _get_rule_value(vis_rules, "returning_visitors_pct", "threshold", 23)
            threshold_str = f"{threshold:g}" if isinstance(threshold, float) else str(threshold)
            if row.verdict == "✔️":
                tmpl = _get_rule_value(vis_rules, "returning_visitors_pct", "message_pass",
                    "✔️ % Pengunjung Lama = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.returningVisitorPct.pass",
                    vars={"value": val_str, "threshold": threshold_str},
                )
            else:
                tmpl = _get_rule_value(vis_rules, "returning_visitors_pct", "message_fail",
                    "❌ % Pengunjung Lama = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.returningVisitorPct.fail",
                    vars={"value": val_str, "threshold": threshold_str},
                )
        elif row.row == 29:
            val_str = f"{int(row.value):,}"
            if row.verdict == "✔️":
                tmpl = _get_rule_value(vis_rules, "followers", "message_pass",
                    "✔️ Total Pengikut = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str)
                row.message_i18n = TranslatableText(
                    key="scoring.totalFollowers.pass",
                    vars={"value": val_str},
                )
            else:
                tmpl = _get_rule_value(vis_rules, "followers", "message_fail",
                    "❌ Total Pengikut = {val_str} [Kurang Baik, nilai disarankan: >50,000]")
                row.message = _format_message_template(tmpl, val_str=val_str)
                row.message_i18n = TranslatableText(
                    key="scoring.totalFollowers.fail",
                    vars={"value": val_str},
                )


def _generate_promo_messages(cat: CategoryScore, manual_data: dict, rules: dict | None = None) -> None:
    """Fill G-column messages for promo tool rows 31-43."""
    promo_rules = _get_rule_category(rules, "promo_tools")
    indiv = promo_rules.get("individual_messages", {})
    d13 = _safe_num(_get_nested(manual_data, "business", "salesMonth0"))

    for row in cat.rows:
        if PROMO_START_ROW <= row.row <= PROMO_START_ROW + len(PROMO_TOOLS) - 1:
            # Individual promo tool row
            idx = row.row - PROMO_START_ROW
            field_key = PROMO_TOOLS[idx][0]
            d_value = _safe_num(row.value)
            pct_of_sales = d_value / d13 if d13 > 0 else 0.0
            pct_str = _fmt_pct_1dp(pct_of_sales)

            metric_key = f"scoring.promo.{field_key}"
            if d_value == 0:
                tmpl = indiv.get("message_zero", "{verdict} {metric} nil pendapatan")
                row.message = _format_message_template(tmpl, verdict=row.verdict, metric=row.metric)
                row.message_i18n = TranslatableText(
                    key="scoring.promoIndividual.zero",
                    vars={"verdict": row.verdict, "metricKey": metric_key},
                )
            elif row.row == PROMO_START_ROW and d13 > 0 and d_value / d13 >= 0.50:
                # "Terlalu mengandalkan promo" only applies to Promo Toko (row 31)
                tmpl = indiv.get("message_dependent",
                    "{verdict} {metric} = {pct_str} [Terlalu mengandalkan promo, nilai disarankan: 15%-50%] — Terindikasi Menggunakan Fake Discount")
                row.message = _format_message_template(tmpl, verdict=row.verdict, metric=row.metric, pct_str=pct_str)
                row.message_i18n = TranslatableText(
                    key="scoring.promoIndividual.dependent",
                    vars={"verdict": row.verdict, "metricKey": metric_key, "pct": pct_str},
                )
            elif row.verdict == "❌":
                tmpl = indiv.get("message_fail",
                    "❌ {metric} = {pct_str} [Kurang Efektif, nilai disarankan: {benchmark}]")
                row.message = _format_message_template(tmpl, metric=row.metric, pct_str=pct_str, benchmark=row.benchmark)
                row.message_i18n = TranslatableText(
                    key="scoring.promoIndividual.fail",
                    vars={"metricKey": metric_key, "pct": pct_str, "benchmark": row.benchmark},
                )
            elif row.verdict == "✔️":
                if row.metric == "Program Afiliasi":
                    tmpl = indiv.get("message_pass_afiliasi", "✔️ {metric} ({pct_str}) digunakan")
                    row.message = _format_message_template(tmpl, metric=row.metric, pct_str=pct_str)
                    row.message_i18n = TranslatableText(
                        key="scoring.promoIndividual.passAffiliate",
                        vars={"metricKey": metric_key, "pct": pct_str},
                    )
                else:
                    tmpl = indiv.get("message_pass",
                        "✔️ {metric} ({pct_str}) digunakan & persentase penggunaan baik")
                    row.message = _format_message_template(tmpl, metric=row.metric, pct_str=pct_str)
                    row.message_i18n = TranslatableText(
                        key="scoring.promoIndividual.pass",
                        vars={"metricKey": metric_key, "pct": pct_str},
                    )

        elif row.row == 42:
            val_str = _fmt_pct_0dp(row.value) if isinstance(row.value, float) else str(row.value)
            threshold = _get_rule_value(promo_rules, "usage_pct_threshold", "threshold", 80)
            threshold_str = f"{threshold:g}" if isinstance(threshold, float) else str(threshold)
            if row.verdict == "✔️":
                tmpl = _get_rule_value(promo_rules, "usage_pct_threshold", "message_pass",
                    "✔️ Penggunaan alat promosi = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.promoUsageRate.pass",
                    vars={"value": val_str, "threshold": threshold_str},
                )
            else:
                tmpl = _get_rule_value(promo_rules, "usage_pct_threshold", "message_fail",
                    "❌ Penggunaan alat promosi = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.promoUsageRate.fail",
                    vars={"value": val_str, "threshold": threshold_str},
                )
        elif row.row == 43:
            val_str = _fmt_pct_0dp(row.value) if isinstance(row.value, float) else str(row.value)
            threshold = _get_rule_value(promo_rules, "effectiveness_pct_threshold", "threshold", 90)
            threshold_str = f"{threshold:g}" if isinstance(threshold, float) else str(threshold)
            if row.verdict == "✔️":
                tmpl = _get_rule_value(promo_rules, "effectiveness_pct_threshold", "message_pass",
                    "✔️ Efektifitas alat promosi = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.promoEffectiveness.pass",
                    vars={"value": val_str, "threshold": threshold_str},
                )
            else:
                tmpl = _get_rule_value(promo_rules, "effectiveness_pct_threshold", "message_fail",
                    "❌ Efektifitas alat promosi = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.promoEffectiveness.fail",
                    vars={"value": val_str, "threshold": threshold_str},
                )


def _generate_products_messages(cat: CategoryScore, rules: dict | None = None) -> None:
    """Fill G-column messages for product/status rows 45-46."""
    prod_rules = _get_rule_category(rules, "products_status")
    for row in cat.rows:
        if row.row == 45:
            value_int = str(int(row.value))
            threshold = _get_rule_value(prod_rules, "product_count", "threshold", 35)
            threshold_str = f"{threshold:g}" if isinstance(threshold, float) else str(threshold)
            if row.verdict == "✔️":
                tmpl = _get_rule_value(prod_rules, "product_count", "message_pass",
                    "✔️ Jumlah Produk = {value_int} [OK]")
                row.message = _format_message_template(tmpl, value_int=value_int, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.productCount.pass",
                    vars={"value": value_int, "threshold": threshold_str},
                )
            else:
                tmpl = _get_rule_value(prod_rules, "product_count", "message_fail",
                    "❌ Jumlah Produk = {value_int} [NOT OK, nilai disarankan: >={threshold}]")
                row.message = _format_message_template(tmpl, value_int=value_int, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.productCount.fail",
                    vars={"value": value_int, "threshold": threshold_str},
                )
        elif row.row == 46:
            store_status = str(row.value)
            if row.verdict == "✔️":
                tmpl = _get_rule_value(prod_rules, "store_status_points", "message_pass",
                    "✔️ Status Toko = {store_status} [OK]")
                row.message = _format_message_template(tmpl, store_status=store_status)
                row.message_i18n = TranslatableText(
                    key="scoring.storeStatus.pass",
                    vars={"value": store_status},
                )
            elif row.verdict == "❌":
                tmpl = _get_rule_value(prod_rules, "store_status_points", "message_fail",
                    "❌ Status Toko = {store_status} [Wajib Shopee Mall]")
                row.message = _format_message_template(tmpl, store_status=store_status)
                row.message_i18n = TranslatableText(
                    key="scoring.storeStatus.fail",
                    vars={"value": store_status},
                )


def _generate_ads_messages(
    cat: CategoryScore, manual_data: dict, calculator_results: dict,
    rules: dict | None = None,
) -> None:
    """Fill G-column messages for ads rows 48-53."""
    ads_rules = _get_rule_category(rules, "ads")
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
                tmpl = _get_rule_value(ads_rules, "roi_threshold", "message_pass",
                    "✔️ ROI = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str, benchmark=row.benchmark)
                row.message_i18n = TranslatableText(
                    key="scoring.adsROI.pass",
                    vars={"value": val_str, "benchmark": row.benchmark},
                )
            else:
                tmpl = _get_rule_value(ads_rules, "roi_threshold", "message_fail",
                    "❌ ROI = {val_str} [Kurang Baik, nilai disarankan: {benchmark}]")
                row.message = _format_message_template(tmpl, val_str=val_str, benchmark=row.benchmark)
                row.message_i18n = TranslatableText(
                    key="scoring.adsROI.fail",
                    vars={"value": val_str, "benchmark": row.benchmark},
                )
        elif row.row == 51:
            pct_str = _fmt_pct_1dp(row.value) if isinstance(row.value, float) else str(row.value)
            threshold = _get_rule_value(ads_rules, "gmv_ratio_threshold", "threshold", 84)
            threshold_str = f"{threshold:g}" if isinstance(threshold, float) else str(threshold)
            if d48 == 0:
                tmpl = _get_rule_value(ads_rules, "gmv_ratio_threshold", "message_no_ads",
                    "❌ [Iklan tidak aktif sama sekali]")
                row.message = _format_message_template(tmpl)
                row.message_i18n = TranslatableText(
                    key="scoring.adsGMVPct.noAds",
                    vars={},
                )
            elif row.verdict == "✔️":
                tmpl = _get_rule_value(ads_rules, "gmv_ratio_threshold", "message_pass",
                    "✔️ % GMV Iklan / GMV Toko = {pct_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.adsGMVPct.pass",
                    vars={"value": pct_str, "threshold": threshold_str},
                )
            else:
                tmpl = _get_rule_value(ads_rules, "gmv_ratio_threshold", "message_fail",
                    "❌ % GMV Iklan / GMV Toko = {pct_str} [Terlalu bergantung terhadap Iklan, nilai disarankan: <{threshold}%]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.adsGMVPct.fail",
                    vars={"value": pct_str, "threshold": threshold_str},
                )
        elif row.row == 52:
            d52 = d49 / d13 if d13 > 0 else 0.0
            pct_str = _fmt_pct_1dp(d52)
            cost_min = _get_rule_value(ads_rules, "cost_ratio_range", "min", 5.0)
            cost_max = _get_rule_value(ads_rules, "cost_ratio_range", "max", 10.0)
            threshold = str(int(cost_max))
            if d49 == 0:
                tmpl = _get_rule_value(ads_rules, "cost_ratio_range", "message_no_ads",
                    "❌ [Iklan tidak aktif sama sekali]")
                row.message = _format_message_template(tmpl)
                row.message_i18n = TranslatableText(
                    key="scoring.adsCostPct.noAds",
                    vars={},
                )
            elif d52 < 0.05:
                tmpl = _get_rule_value(ads_rules, "cost_ratio_range", "message_too_minimal",
                    "❌ [Penggunaan iklan terlalu minim ({pct_str}). Nilai disarankan: {min}%-{max}%.]")
                row.message = _format_message_template(tmpl, pct_str=pct_str,
                    min=str(int(cost_min)), max=str(int(cost_max)))
                row.message_i18n = TranslatableText(
                    key="scoring.adsCostPct.tooMinimal",
                    vars={"value": pct_str, "min": str(int(cost_min)), "max": str(int(cost_max))},
                )
            elif row.verdict == "❌":
                tmpl = _get_rule_value(ads_rules, "cost_ratio_range", "message_fail",
                    "❌ % Biaya Iklan / GMV Toko = {pct_str} [Biaya terlalu tinggi, nilai disarankan: <{threshold}%]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=threshold)
                row.message_i18n = TranslatableText(
                    key="scoring.adsCostPct.fail",
                    vars={"value": pct_str, "threshold": threshold},
                )
            elif row.verdict == "✔️":
                tmpl = _get_rule_value(ads_rules, "cost_ratio_range", "message_pass",
                    "✔️ % Biaya Iklan / GMV Toko = {pct_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=threshold)
                row.message_i18n = TranslatableText(
                    key="scoring.adsCostPct.pass",
                    vars={"value": pct_str, "threshold": threshold},
                )
        elif row.row == 53:
            row.message = calc1_output


def _generate_campaign_messages(cat: CategoryScore, rules: dict | None = None) -> None:
    """Fill G-column messages for campaign rows 55-57."""
    camp_rules = _get_rule_category(rules, "campaign")
    threshold = _get_rule_value(camp_rules, "participation_pct_threshold", "threshold", 90)
    threshold_str = f"{threshold:g}" if isinstance(threshold, float) else str(threshold)
    for row in cat.rows:
        if row.row == 57:
            if isinstance(row.value, float) and row.value == 0.0:
                tmpl = _get_rule_value(camp_rules, "participation_pct_threshold", "message_no_data",
                    "❌[Tidak ada Campaign yang dipartisipasikan]")
                row.message = _format_message_template(tmpl)
                row.message_i18n = TranslatableText(
                    key="scoring.campaignParticipation.noData",
                    vars={},
                )
            elif row.verdict == "✔️":
                pct_str = _fmt_pct_1dp(row.value)
                tmpl = _get_rule_value(camp_rules, "participation_pct_threshold", "message_pass",
                    "✔️ % Partisipasi Campaign = {pct_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.campaignParticipation.pass",
                    vars={"value": pct_str, "threshold": threshold_str},
                )
            else:
                pct_str = _fmt_pct_1dp(row.value) if isinstance(row.value, float) else str(row.value)
                tmpl = _get_rule_value(camp_rules, "participation_pct_threshold", "message_fail",
                    "❌ % Partisipasi Campaign = {pct_str} [Kurang Baik, nilai disarankan: >{threshold}%]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=threshold_str)
                row.message_i18n = TranslatableText(
                    key="scoring.campaignParticipation.fail",
                    vars={"value": pct_str, "threshold": threshold_str},
                )


def _generate_competition_messages(cat: CategoryScore, manual_data: dict, rules: dict | None = None, *, marketplace: str = "ID") -> None:
    """Fill G-column messages for competition rows 61-63."""
    comp_rules = _get_rule_category(rules, "competition")
    comp = _get_nested(manual_data, "competition") or {}
    currency_code = MARKETPLACE_CURRENCY.get(marketplace, "IDR")

    for row in cat.rows:
        i = row.row - 61
        product_key = f"product{i + 1}"
        product_data = comp.get(product_key, {}) or {}
        market_price = _safe_num(product_data.get("marketPrice"))
        selling_price = _safe_num(product_data.get("sellingPrice"))
        product_name = _safe_str(product_data.get("productName")) or f"Produk {i + 1}"
        link = _safe_str(product_data.get("link"))

        if row.verdict == "❌":
            tmpl = comp_rules.get("message_fail",
                "{name} ({currency} {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: {currency} {market_price})]")
            msg = _format_message_template(
                tmpl, name=product_name, selling_price=_fmt_currency(selling_price, marketplace),
                market_price=_fmt_currency(market_price, marketplace), currency=currency_code,
            )
            i18n_vars: dict[str, str] = {
                "name": product_name,
                "sellingPrice": _fmt_currency(selling_price, marketplace),
                "marketPrice": _fmt_currency(market_price, marketplace),
                "currency": currency_code,
            }
            if link:
                msg += f"\n↪{link}"
                i18n_vars["link"] = link
            row.message = msg
            row.message_i18n = TranslatableText(
                key="scoring.competitionProduct.fail",
                vars=i18n_vars,
            )
        elif row.verdict == "✔️":
            tmpl = comp_rules.get("message_pass", "{name} ({currency} {selling_price}) = ✅[kompetitif]")
            msg = _format_message_template(
                tmpl, name=product_name, selling_price=_fmt_currency(selling_price, marketplace),
                currency=currency_code,
            )
            i18n_vars = {
                "name": product_name,
                "sellingPrice": _fmt_currency(selling_price, marketplace),
                "currency": currency_code,
            }
            if link:
                msg += f"\n↪{link}"
                i18n_vars["link"] = link
            row.message = msg
            row.message_i18n = TranslatableText(
                key="scoring.competitionProduct.pass",
                vars=i18n_vars,
            )

