"""Ads Keyword Calculator — pure function, no I/O.

Processes CPC Ad Report (Sheet 1) and Keyword/Placement Report (Sheet 2)
to produce the combined ads keyword analysis text for the scoring system.

Spec: logic/calculator-1-kata-kunci-iklan-shopee.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.marketplace import MARKETPLACE_CURRENCY


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class AdsKeywordResult:
    """Structured result from the ads keyword calculator."""

    output_text: str
    details: dict[str, Any]


# ---------------------------------------------------------------------------
# i18n value mapping — CSV Indonesian values → i18n keys for $t() resolution
# ---------------------------------------------------------------------------

_VALUE_I18N_KEYS: dict[str, str] = {
    "Iklan Produk": "ads.value.iklanProduk",
    "Iklan Toko": "ads.value.iklanToko",
    "Semua Penempatan": "ads.value.semuaPenempatan",
    "Halaman Pencarian": "ads.value.halamanPencarian",
    "Halaman Rekomendasi": "ads.value.halamanRekomendasi",
    "Bidding Otomatis": "ads.value.biddingOtomatis",
    "Bidding Manual": "ads.value.biddingManual",
    "GMV Max Auto": "ads.value.gmvMaxAuto",
    "GMV Max ROAS": "ads.value.gmvMaxRoas",
}


def _i18n_value(raw: str) -> str:
    """Return i18n key for a known CSV value, or the raw string."""
    return _VALUE_I18N_KEYS.get(raw, raw)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_name(ad_name: str) -> str:
    """Remove text from first ``[`` onward (strip trailing whitespace)."""
    if not ad_name:
        return ""
    idx = ad_name.find("[")
    if idx == -1:
        return ad_name.strip()
    return ad_name[:idx].strip()


def _format_idr(value: int | float, currency: str = "IDR") -> str:
    """Format number as ``IDR 26,433,781`` (or THB, etc.)."""
    return f"{currency} {int(value):,}"


def _format_roas(value: float | int) -> str:
    """Format ROAS stripping trailing zeros: 5.68, 6, 5.9."""
    return f"{float(value):g}"


def _format_pct(fraction: float) -> str:
    """Format fraction as percentage: 0.05 → '5.0%'."""
    return f"{fraction * 100:.1f}%"


def _safe_num(value: Any) -> float:
    """Coerce a value to float, treating None/'-'/'' as 0."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if value in ("", "-"):
            return 0.0
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _safe_str(value: Any) -> str:
    """Coerce a value to string, treating None as empty string."""
    if value is None:
        return ""
    return str(value).strip()


# ---------------------------------------------------------------------------
# Sheet 1 — CPC Ad Report
# ---------------------------------------------------------------------------

def calculate_sheet1(
    rows: list[dict], total_products: int, *, language: str = "id", marketplace: str = "ID"
) -> dict[str, str]:
    """Calculate AK2, AK3, AK4 from CPC Ad Report data.

    Args:
        rows: Parsed CPC ad report rows (list of dicts with CSV column names).
        total_products: AK1 — total products in the store.
        language: ``"id"`` or ``"en"`` — controls AK3/AK4 variant logic.

    Returns:
        Dict with keys ``ak2``, ``ak3``, ``ak4`` containing formatted text.
    """
    # --- AK2: Ad Overview Summary (same for both languages) ---
    count_active = 0
    count_paused = 0
    count_ended = 0
    total_ads = len(rows)

    # For unique product counting (non-ended, Iklan Produk, CleanName dedup)
    unique_products: set[str] = set()

    for row in rows:
        status = _safe_str(row.get("Status"))
        jenis = _safe_str(row.get("Jenis Iklan"))
        nama = _safe_str(row.get("Nama Iklan"))

        if status == "Berjalan":
            count_active += 1
        elif status == "Dijeda":
            count_paused += 1
        elif status == "Berakhir":
            count_ended += 1

        # Unique products: non-ended + Iklan Produk + CleanName dedup
        if status != "Berakhir" and jenis == "Iklan Produk" and nama:
            unique_products.add(clean_name(nama))

    unique_count = len(unique_products)
    product_pct = unique_count / total_products if total_products > 0 else 0.0

    ak2 = (
        f"• Total Iklan: {count_active} Aktif, {count_paused} Dijeda "
        f"dan {count_ended} Berakhir.\n"
        f"• Melibatkan {unique_count} ({_format_pct(product_pct)}) "
        f"produk dari total jumlah produk: {total_products}."
    )

    # --- AK3: Ad Type Breakdown (non-ended only) ---
    search_total = 0
    search_auto = 0
    search_manual = 0
    reco_total = 0
    reco_auto = 0
    reco_manual = 0
    semua_total = 0
    toko_total = 0
    toko_auto = 0
    toko_manual = 0

    for row in rows:
        status = _safe_str(row.get("Status"))
        if status == "Berakhir":
            continue

        jenis = _safe_str(row.get("Jenis Iklan"))
        penempatan = _safe_str(row.get("Penempatan Iklan"))
        bidding = _safe_str(row.get("Mode Bidding"))

        if jenis == "Iklan Produk" and penempatan == "Halaman Pencarian":
            search_total += 1
            if bidding == "Bidding Otomatis":
                search_auto += 1
            elif bidding == "Bidding Manual":
                search_manual += 1

        if jenis == "Iklan Produk" and penempatan == "Halaman Rekomendasi":
            reco_total += 1
            if bidding == "Bidding Otomatis":
                reco_auto += 1
            elif bidding == "Bidding Manual":
                reco_manual += 1

        if penempatan == "Semua Penempatan":
            semua_total += 1

        if jenis == "Iklan Toko":
            toko_total += 1
            if bidding == "Bidding Otomatis":
                toko_auto += 1
            elif bidding == "Bidding Manual":
                toko_manual += 1

    # Indonesian AK3: 2 categories (Semua Penempatan + Iklan Toko)
    # English AK3: 4 categories (Search, Recommendation, All, Shop Ad)
    ak3 = (
        "• Jenis Iklan yang aktif digunakan:\n"
        f"  {semua_total} Iklan Produk Otomatis Semua Halaman.\n"
        f"  {toko_total} Iklan Toko "
        f"({toko_auto} Otomatis & {toko_manual} Manual)."
    )

    # --- AK4: Recommendation Flags ---
    # Indonesian: 3 flags | English: 9 flags
    flags: list[str] = []

    active_ratio = count_active / total_ads if total_ads > 0 else 0.0

    # Flag 1: Product participation (both languages)
    if product_pct < 0.5:
        flags.append(
            "📌 Jumlah produk yang dipartisipasikan ke dalam iklan "
            "kurang maksimal (saran >50%)."
        )
    else:
        flags.append(
            "📌 Jumlah produk yang dipartisipasikan ke dalam iklan "
            "sudah cukup baik."
        )

    # Flag 2: Active ad ratio (both languages)
    if active_ratio < 0.5:
        flags.append(
            "📌 Jumlah iklan dengan status aktif "
            "kurang maksimal (saran >50%)."
        )
    elif product_pct >= 0.5:
        flags.append(
            "📌 Jumlah iklan dengan status aktif sudah cukup baik."
        )
    # else: suppressed

    # Remaining flags check ALL rows (including ended)
    all_jenis = [_safe_str(r.get("Jenis Iklan")) for r in rows]

    # Iklan Toko flag (both languages — flag 3)
    if not any(j == "Iklan Toko" for j in all_jenis):
        flags.append("📌 Iklan Toko belum dimanfaatkan.")

    ak4 = "\n".join(flags)

    # --- i18n structured data ---
    ak2_i18n = {
        "key": "ads.summary",
        "vars": {
            "active": str(count_active),
            "paused": str(count_paused),
            "ended": str(count_ended),
            "unique_count": str(unique_count),
            "product_pct": _format_pct(product_pct) if product_pct else "0%",
            "total_products": str(total_products),
        },
    }

    ak3_i18n = {
        "key": "ads.typeBreakdown",
        "vars": {
            "semua_total": str(semua_total),
            "toko_total": str(toko_total),
            "toko_auto": str(toko_auto),
            "toko_manual": str(toko_manual),
        },
    }

    # --- AK4 i18n: individual flag objects ---
    ak4_i18n_flags: list[dict[str, Any]] = []

    if product_pct < 0.5:
        ak4_i18n_flags.append({"key": "ads.flag.productLow", "vars": {}})
    else:
        ak4_i18n_flags.append({"key": "ads.flag.productGood", "vars": {}})

    if active_ratio < 0.5:
        ak4_i18n_flags.append({"key": "ads.flag.activeLow", "vars": {}})
    elif product_pct >= 0.5:
        ak4_i18n_flags.append({"key": "ads.flag.activeGood", "vars": {}})

    if not any(j == "Iklan Toko" for j in all_jenis):
        ak4_i18n_flags.append({"key": "ads.flag.noShopAd", "vars": {}})

    ak4_i18n = ak4_i18n_flags

    return {
        "ak2": ak2, "ak3": ak3, "ak4": ak4,
        "ak2_i18n": ak2_i18n, "ak3_i18n": ak3_i18n, "ak4_i18n": ak4_i18n,
    }


# ---------------------------------------------------------------------------
# Sheet 2 — Keyword/Placement Report
# ---------------------------------------------------------------------------

def _calculate_thresholds(rows: list[dict]) -> dict[str, int]:
    """Calculate AM6, AM7, AM9, AM10 from ALL rows (including shop-level).

    AM6 = ROUND(AVERAGEIF(GMV > 0))
    AM7 = MIN(ROUND(AVERAGEIF(ROAS > 0)), 10)
    AM9 = ROUND(AVERAGEIF(Cost > 0))
    AM10 = MIN(ROUND(AVERAGEIF(ROAS > 0)), 3)
    """
    gmv_values = [
        _safe_num(r.get("Omzet Penjualan"))
        for r in rows
        if _safe_num(r.get("Omzet Penjualan")) > 0
    ]
    roas_values = [
        _safe_num(r.get("Efektifitas Iklan"))
        for r in rows
        if _safe_num(r.get("Efektifitas Iklan")) > 0
    ]
    cost_values = [
        _safe_num(r.get("Biaya"))
        for r in rows
        if _safe_num(r.get("Biaya")) > 0
    ]

    avg_gmv = round(sum(gmv_values) / len(gmv_values)) if gmv_values else 0
    avg_roas = round(sum(roas_values) / len(roas_values)) if roas_values else 0
    avg_cost = round(sum(cost_values) / len(cost_values)) if cost_values else 0

    return {
        "am6": avg_gmv,
        "am7": min(avg_roas, 10),
        "am9": avg_cost,
        "am10": min(avg_roas, 3),
    }


def _format_top_ad(row: dict, currency: str = "IDR") -> str:
    """Format a single TOP ad entry (4-line format)."""
    name = clean_name(_safe_str(row.get("Nama Iklan")))
    gmv = _safe_num(row.get("Omzet Penjualan"))
    roas = _safe_num(row.get("Efektifitas Iklan"))
    bidding = _safe_str(row.get("Mode Bidding"))
    jenis = _safe_str(row.get("Jenis Iklan"))
    penempatan = _safe_str(row.get("Penempatan Iklan"))
    kata = _safe_str(row.get("Kata Pencarian/Penempatan"))

    return (
        f"  ▶ {name}\n"
        f"    GMV: {_format_idr(gmv, currency)} {{ROAS: {_format_roas(roas)}}}\n"
        f"    {bidding}\n"
        f"    {jenis} {penempatan}: {kata}"
    )


def _format_bottom_ad(row: dict, is_fallback: bool, currency: str = "IDR") -> str:
    """Format a single BOTTOM ad entry.

    Primary: 4-line format (Mode Bidding on separate line).
    Fallback: 3-line format (Mode Bidding merged with Jenis line).
    """
    name = clean_name(_safe_str(row.get("Nama Iklan")))
    cost = _safe_num(row.get("Biaya"))
    roas = _safe_num(row.get("Efektifitas Iklan"))
    bidding = _safe_str(row.get("Mode Bidding"))
    jenis = _safe_str(row.get("Jenis Iklan"))
    penempatan = _safe_str(row.get("Penempatan Iklan"))
    kata = _safe_str(row.get("Kata Pencarian/Penempatan"))

    if is_fallback:
        return (
            f"  ▶ {name}\n"
            f"    Biaya: {_format_idr(cost, currency)} {{ROAS: {_format_roas(roas)}}}\n"
            f"    {bidding} {jenis} {penempatan}: {kata}"
        )
    return (
        f"  ▶ {name}\n"
        f"    Biaya: {_format_idr(cost, currency)} {{ROAS: {_format_roas(roas)}}}\n"
        f"    {bidding}\n"
        f"    {jenis} {penempatan}: {kata}"
    )


def calculate_sheet2(rows: list[dict], *, language: str = "id", marketplace: str = "ID") -> dict[str, Any]:
    """Calculate AL2, AL3, AL5, AL6-AL9 and thresholds from Keyword Report.

    Args:
        rows: Parsed keyword/placement report rows (list of dicts).
        language: ``"id"`` or ``"en"`` — controls threshold/fallback/AL6 variants.
        marketplace: ``"ID"`` or ``"TH"`` — controls currency display.

    Returns:
        Dict with keys ``al2``, ``al3``, ``al5``, ``al6``-``al9``,
        ``thresholds``, and ``is_top_fallback``, ``is_bottom_fallback``.
    """
    currency = MARKETPLACE_CURRENCY.get(marketplace, "IDR")

    thresholds = _calculate_thresholds(rows)
    am6 = thresholds["am6"]
    am7 = thresholds["am7"]
    am9 = thresholds["am9"]
    am10 = thresholds["am10"]

    # Filter rows with non-empty Jenis Iklan (D<>'')
    product_rows = [
        r for r in rows if _safe_str(r.get("Jenis Iklan")) != ""
    ]

    # --- AL2: TOP Ads ---
    # Primary: D<>'' AND GMV > AM6 AND ROAS > AM7, order by GMV desc, limit 5
    top_primary = sorted(
        [
            r for r in product_rows
            if _safe_num(r.get("Omzet Penjualan")) > am6
            and _safe_num(r.get("Efektifitas Iklan")) > am7
        ],
        key=lambda r: _safe_num(r.get("Omzet Penjualan")),
        reverse=True,
    )[:5]

    is_top_fallback = False
    if top_primary:
        top_ads = top_primary
    else:
        # Fallback query (both languages)
        fallback_roas_threshold = max(am7 / 2, 6)
        top_ads = sorted(
            [
                r for r in product_rows
                if _safe_num(r.get("Omzet Penjualan")) > am6 / 2
                and _safe_num(r.get("Efektifitas Iklan")) > fallback_roas_threshold
            ],
            key=lambda r: _safe_num(r.get("Omzet Penjualan")),
            reverse=True,
        )[:5]
        is_top_fallback = True

    if top_ads:
        header = "• TOP Iklan (GMV tertinggi dengan ROAS terbaik):"
        if is_top_fallback:
            header = "• TOP Iklan [fallback] (GMV tertinggi dengan ROAS terbaik):"
        ad_texts = [_format_top_ad(ad, currency) for ad in top_ads]
        al2 = header + "\n" + "\n".join(ad_texts)
    else:
        al2 = ""

    # --- AL2 i18n ---
    if top_ads:
        header_key = "ads.topHeaderFallback" if is_top_fallback else "ads.topHeader"
        al2_i18n: dict[str, Any] | None = {
            "header": {"key": header_key, "vars": {}},
            "ads": [
                {
                    "key": "ads.topAd",
                    "vars": {
                        "name": clean_name(_safe_str(ad.get("Nama Iklan"))),
                        "gmv": _format_idr(_safe_num(ad.get("Omzet Penjualan")), currency),
                        "roas": _format_roas(_safe_num(ad.get("Efektifitas Iklan"))),
                        "biddingKey": _i18n_value(_safe_str(ad.get("Mode Bidding"))),
                        "jenisKey": _i18n_value(_safe_str(ad.get("Jenis Iklan"))),
                        "penempatanKey": _i18n_value(_safe_str(ad.get("Penempatan Iklan"))),
                        "keyword": _safe_str(ad.get("Kata Pencarian/Penempatan")),
                    },
                }
                for ad in top_ads
            ],
        }
    else:
        al2_i18n = None

    # --- AL3: Top Ads Recommendation ---
    auto_count = al2.count("Bidding Otomatis")
    gmv_max_count = al2.count("GMV Max")

    if auto_count >= 3:
        al3 = (
            "📌 Iklan dengan performa terbaik mengandalkan pengaturan "
            "otomatis (Iklan toko manual berpotensi belum dimanfaatkan)."
        )
    elif gmv_max_count >= 3:
        al3 = (
            "📌 Iklan dengan performa terbaik mengandalkan pengaturan "
            "otomatis (Iklan toko manual berpotensi belum dimanfaatkan)."
        )
    else:
        al3 = "📌 Iklan dengan performa terbaik sudah mengandalkan pengaturan manual."

    # --- AL3 i18n ---
    if auto_count >= 3 or gmv_max_count >= 3:
        al3_i18n = {"key": "ads.topRecommendation.auto", "vars": {}}
    else:
        al3_i18n = {"key": "ads.topRecommendation.manual", "vars": {}}

    # --- AL5: BOTTOM Ads ---
    # Thresholds (same for all languages):
    #   Cost > 100000, fallback ROAS cap min(round(AM10*2), 5)
    min_cost = 100000 if marketplace != "TH" else 190
    fallback_roas_cap_limit = 5

    bottom_primary = sorted(
        [
            r for r in product_rows
            if _safe_num(r.get("Biaya")) > min_cost
            and _safe_num(r.get("Biaya")) > am9
            and _safe_num(r.get("Efektifitas Iklan")) < am10
            and _safe_num(r.get("Efektifitas Iklan")) < 5
        ],
        key=lambda r: _safe_num(r.get("Biaya")),
        reverse=True,
    )[:5]

    is_bottom_fallback = False
    if bottom_primary:
        bottom_ads = bottom_primary
    else:
        fallback_roas_cap = min(round(am10 * 2), fallback_roas_cap_limit)
        bottom_ads = sorted(
            [
                r for r in product_rows
                if _safe_num(r.get("Biaya")) > min_cost
                and _safe_num(r.get("Biaya")) > am9
                and _safe_num(r.get("Efektifitas Iklan")) < fallback_roas_cap
                and _safe_num(r.get("Efektifitas Iklan")) < 5
            ],
            key=lambda r: _safe_num(r.get("Biaya")),
            reverse=True,
        )[:5]
        is_bottom_fallback = True

    if bottom_ads:
        if is_bottom_fallback:
            header = "• BOTTOM Iklan [fallback] (biaya tertinggi dengan ROAS terendah):"
        else:
            header = "• BOTTOM Iklan (biaya tertinggi dengan ROAS terendah):"
        ad_texts = [_format_bottom_ad(ad, is_bottom_fallback, currency) for ad in bottom_ads]
        al5 = header + "\n" + "\n".join(ad_texts)
    else:
        al5 = ""

    # --- AL5 i18n ---
    if bottom_ads:
        header_key = "ads.bottomHeaderFallback" if is_bottom_fallback else "ads.bottomHeader"
        ad_key = "ads.bottomAdFallback" if is_bottom_fallback else "ads.bottomAd"
        al5_i18n: dict[str, Any] | None = {
            "header": {"key": header_key, "vars": {}},
            "ads": [
                {
                    "key": ad_key,
                    "vars": {
                        "name": clean_name(_safe_str(ad.get("Nama Iklan"))),
                        "cost": _format_idr(_safe_num(ad.get("Biaya")), currency),
                        "roas": _format_roas(_safe_num(ad.get("Efektifitas Iklan"))),
                        "biddingKey": _i18n_value(_safe_str(ad.get("Mode Bidding"))),
                        "jenisKey": _i18n_value(_safe_str(ad.get("Jenis Iklan"))),
                        "penempatanKey": _i18n_value(_safe_str(ad.get("Penempatan Iklan"))),
                        "keyword": _safe_str(ad.get("Kata Pencarian/Penempatan")),
                    },
                }
                for ad in bottom_ads
            ],
        }
    else:
        al5_i18n = None

    # --- AL6-AL9: Bottom Flags (substring checks on AL5 text) ---
    # AL6: checks "Otomatis" substring (all languages)
    al6 = ""
    al6_substring = "Otomatis"
    if al5.count(al6_substring) >= 1:
        al6 = (
            "📌 Terdapat iklan dengan pengaturan otomatis yang tidak "
            "terkontrol biayanya (disarankan dimonitor 1-2x setiap hari)."
        )

    al7 = ""
    if al5.count("Bidding Manual") >= 1:
        al7 = (
            "📌 Terdapat iklan dengan pengaturan manual yang tidak "
            "terkontrol biayanya (disarankan dimonitor 1-2x setiap hari)."
        )

    al8 = ""
    if al5.count("Iklan Pencarian Produk: ") >= 3:
        al8 = (
            "📌 Terdapat kata kunci dengan pengaturan manual yang tidak "
            "terkontrol biayanya (disarankan dipantau 1-2x setiap hari)."
        )

    al9 = ""
    if al5.count("Auto Bidding") >= 1:
        al9 = (
            "📌 Terdapat iklan dengan pengaturan otomatis yang tidak "
            "terkontrol biayanya (disarankan dimonitor 1-2x setiap hari)."
        )

    # --- AL6-AL9 i18n ---
    al6_i18n = {"key": "ads.flag.autoUncontrolled", "vars": {}} if al6 else None
    al7_i18n = {"key": "ads.flag.manualUncontrolled", "vars": {}} if al7 else None
    al8_i18n = {"key": "ads.flag.keywordUncontrolled", "vars": {}} if al8 else None
    al9_i18n = {"key": "ads.flag.autoBiddingUncontrolled", "vars": {}} if al9 else None

    return {
        "al2": al2,
        "al3": al3,
        "al5": al5,
        "al6": al6,
        "al7": al7,
        "al8": al8,
        "al9": al9,
        "al2_i18n": al2_i18n,
        "al3_i18n": al3_i18n,
        "al5_i18n": al5_i18n,
        "al6_i18n": al6_i18n,
        "al7_i18n": al7_i18n,
        "al8_i18n": al8_i18n,
        "al9_i18n": al9_i18n,
        "thresholds": thresholds,
        "is_top_fallback": is_top_fallback,
        "is_bottom_fallback": is_bottom_fallback,
    }


# ---------------------------------------------------------------------------
# Combine output
# ---------------------------------------------------------------------------

def combine_output(sheet1: dict[str, str], sheet2: dict[str, Any]) -> str:
    """Combine Sheet 1 and Sheet 2 results in correct order for G53.

    Order: AK2, AK3, AK4, AL2, AL3, AL5, AL6, AL7, AL8, AL9
    """
    sections: list[str] = []

    for key in ("ak2", "ak3", "ak4"):
        text = sheet1.get(key, "")
        if text:
            sections.append(text)

    for key in ("al2", "al3", "al5", "al6", "al7", "al8", "al9"):
        text = sheet2.get(key, "")
        if text:
            sections.append(text)

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Main calculator entry point
# ---------------------------------------------------------------------------

def calculate_ads_keyword(
    cpc_data: list[dict],
    keyword_data: list[dict],
    total_products: int,
    *,
    language: str = "id",
    marketplace: str = "ID",
) -> AdsKeywordResult:
    """Execute the Ads Keyword Calculator.

    Pure function — no I/O, no database access.

    Args:
        cpc_data: Parsed rows from cpc_ad_report (list of dicts).
        keyword_data: Parsed rows from keyword_report (list of dicts).
        total_products: AK1 — total products in the store.
        language: ``"id"`` or ``"en"`` — controls variant logic.
        marketplace: ``"ID"`` or ``"TH"`` — controls currency display.

    Returns:
        AdsKeywordResult with output_text and details.
    """
    sheet1 = calculate_sheet1(cpc_data, total_products, language=language, marketplace=marketplace)
    sheet2 = calculate_sheet2(keyword_data, language=language, marketplace=marketplace)
    output_text = combine_output(sheet1, sheet2)

    details = {
        "ak2": sheet1["ak2"],
        "ak3": sheet1["ak3"],
        "ak4": sheet1["ak4"],
        "ak2_i18n": sheet1["ak2_i18n"],
        "ak3_i18n": sheet1["ak3_i18n"],
        "ak4_i18n": sheet1["ak4_i18n"],
        "al2": sheet2["al2"],
        "al3": sheet2["al3"],
        "al5": sheet2["al5"],
        "al6": sheet2["al6"],
        "al7": sheet2["al7"],
        "al8": sheet2["al8"],
        "al9": sheet2["al9"],
        "al2_i18n": sheet2["al2_i18n"],
        "al3_i18n": sheet2["al3_i18n"],
        "al5_i18n": sheet2["al5_i18n"],
        "al6_i18n": sheet2["al6_i18n"],
        "al7_i18n": sheet2["al7_i18n"],
        "al8_i18n": sheet2["al8_i18n"],
        "al9_i18n": sheet2["al9_i18n"],
        "thresholds": sheet2["thresholds"],
    }

    return AdsKeywordResult(output_text=output_text, details=details)
