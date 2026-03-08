"""Final Scoring Calculator — pure function, no I/O.

Implements the 75-row scoring system template (Fashion/Non-Fashion variants).
Combines manual inputs with Calculator 1-3 outputs to produce per-category
scores, total score, verdicts, G-column messages, and email body.

Spec: logic/scoring-system-template-sicu.md
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any


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
    template: str                    # "fashion" or "non_fashion"
    rule_version: int = 1            # Version of rules used for scoring


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

INDO_MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def _generate_month_labels(start_month: str | None) -> list[str]:
    """Given '2026-01', returns ['Jan 2026', 'Des 2025', ...] for 6 months.

    If None or invalid, returns ['Bulan Ini', 'Bulan -1', ..., 'Bulan -5'].
    """
    fallback = ["Bulan Ini", "Bulan -1", "Bulan -2", "Bulan -3", "Bulan -4", "Bulan -5"]
    if not start_month:
        return fallback
    if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", start_month):
        return fallback
    year_str, month_str = start_month.split("-")
    year = int(year_str)
    month = int(month_str)
    labels: list[str] = []
    for i in range(6):
        month_index = ((month - 1 - i) % 12 + 12) % 12
        year_offset = (month - 1 - i) // 12
        labels.append(f"{INDO_MONTHS[month_index]} {year + year_offset}")
    return labels


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
    """Format IDR value with comma thousands separator."""
    rounded = round(value)
    if rounded < 0:
        return f"-{abs(rounded):,}"
    return f"{rounded:,}"


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
#
# NOTE: The rules JSONB contains a `comparison` field per rule entry (e.g.,
# "lte", "gte", "gt") as descriptive metadata. These are NOT dynamically
# applied — each scoring function hardcodes its comparison operator because
# the comparison semantics are structural to the scoring logic, not a
# business-configurable parameter. Only thresholds and points are dynamic.
# ---------------------------------------------------------------------------

def _get_rule_category(rules: dict | None, category: str) -> dict:
    """Get a category dict from rules, or empty dict if missing."""
    if rules is None:
        return {}
    return rules.get(category, {})


def _get_rule_value(category_rules: dict, key: str, field: str, default: Any) -> Any:
    """Get a specific value from category rules, with default fallback."""
    return category_rules.get(key, {}).get(field, default)


class _SafeDict(dict):
    """Dict subclass that returns the placeholder markup for missing keys."""

    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


def _format_message_template(template: str, **kwargs: Any) -> str:
    """Format a message template safely — missing placeholders stay as-is.

    Resilient to both missing keys AND malformed format strings (unmatched
    braces from user-edited templates).
    """
    try:
        return template.format_map(_SafeDict(**kwargs))
    except (ValueError, KeyError):
        return template


# Default rules matching migration 013 unified data — used when rules=None.
# IMPORTANT: These are module-level constants — treat as immutable.
#
# NOTE (source of truth): Message templates exist in THREE places:
#   1. Migration 012/013/019 — DB seed values
#   2. DEFAULT_RULES below — runtime fallback when rules=None
#   3. Inline defaults in _generate_*_messages() — per-field fallbacks
# If changing default message text, update ALL THREE locations.
# Tests catching drift:
#   - test_default_rules_produce_identical_messages → (2) vs (3)
#   - TestMigrationTemplatesDrift → (1) vs (2)
DEFAULT_RULES: dict = {
    "operational": {
        "unfulfilled_order_rate": {
            "threshold": 1.0, "points": 4, "comparison": "lte",
            "message_pass": "✔️ Tingkat Pesanan Tidak Terselesaikan = {val_str} [Sudah Baik]",
            "message_fail": "❌ Tingkat Pesanan Tidak Terselesaikan = {val_str} [Kurang Baik, nilai disarankan: <{threshold}%]",
        },
        "late_shipment_rate": {
            "threshold": 1.0, "points": 3, "comparison": "lte",
            "message_pass": "✔️ Tingkat Keterlambatan Pengiriman = {val_str} [Sudah Baik]",
            "message_fail": "❌ Tingkat Keterlambatan Pengiriman = {val_str} [Kurang Baik, nilai disarankan: <{threshold}%]",
        },
        "preparation_time": {
            "threshold": 1.0, "points": 3, "comparison": "lte",
            "message_pass": "✔️ Masa Pengemasan = {val_str} hari [Sudah Baik]",
            "message_fail": "❌ Masa Pengemasan = {val_str} hari [Kurang Baik, nilai disarankan: <{threshold} hari]",
        },
        "chat_response_rate": {
            "threshold": 95.0, "comparison": "gte", "info_only": True,
            "message_pass": "✔️ Persentase Chat Dibalas = {val_str} [Sudah Baik]",
            "message_fail": "❌ Persentase Chat Dibalas = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]",
        },
        "overall_rating": {
            "threshold": 4.7, "comparison": "gte", "info_only": True,
            "message_pass": "✔️ Keseluruhan Penilaian = {val_str} [Sudah Baik]",
            "message_fail": "❌ Keseluruhan Penilaian = {val_str} [Kurang Baik, nilai disarankan: >{threshold}]",
        },
    },
    "business": {
        "monthly_sales_trend": {
            "threshold_pct": 90.0, "points": 10, "comparison": "gte",
            "message_pass": "✔️ Penjualan = IDR {idr_val} [Meningkat {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}]",
            "message_fail": "❌ Penjualan = IDR {idr_val} [Menurun {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}]",
            "message_fail_severe": "\n❗️ Potensi peningkatan harga jual signifikan atau terdapat event abnormal.",
        },
        "six_month_avg_threshold": {"threshold": 100000000, "points": 10, "comparison": "gte"},
        "conversion_rate": {
            "threshold": 3.0, "comparison": "gte", "info_only": True,
            "message_pass": "✔️ Tingkat Konversi = {val_str} [Sudah Baik]",
            "message_fail": "❌ Tingkat Konversi = {val_str} [Kurang Baik, nilai disarankan: {benchmark}]",
        },
    },
    "visitors": {
        "returning_visitors_pct": {
            "threshold": 23.0, "points": 3, "comparison": "gte",
            "message_pass": "✔️ % Pengunjung Lama = {val_str} [Sudah Baik]",
            "message_fail": "❌ % Pengunjung Lama = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]",
        },
        "followers": {
            "threshold": 50000, "points": 2, "comparison": "gte",
            "message_pass": "✔️ Total Pengikut = {val_str} [Sudah Baik]",
            "message_fail": "❌ Total Pengikut = {val_str} [Kurang Baik, nilai disarankan: >50.000]",
        },
    },
    "promo_tools": {
        "usage_pct_threshold": {
            "threshold": 80.0, "opportunity_points": 5,
            "message_pass": "✔️ Penggunaan alat promosi = {val_str} [Sudah Baik]",
            "message_fail": "❌ Penggunaan alat promosi = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]",
        },
        "effectiveness_pct_threshold": {
            "threshold": 90.0, "opportunity_points": 10,
            "message_pass": "✔️ Efektifitas alat promosi = {val_str} [Sudah Baik]",
            "message_fail": "❌ Efektifitas alat promosi = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]",
        },
        "individual_messages": {
            "message_zero": "{verdict} {metric} nil pendapatan",
            "message_dependent": "{verdict} {metric} = {pct_str} [Terlalu mengandalkan promo, nilai disarankan: 15%-50%]",
            "message_fail": "❌ {metric} = {pct_str} [Kurang Efektif, nilai disarankan: {benchmark}]",
            "message_pass": "✔️ {metric} ({pct_str}) digunakan & persentase penggunaan baik",
            "message_pass_afiliasi": "✔️ {metric} ({pct_str}) digunakan",
        },
    },
    "products_status": {
        "product_count": {
            "threshold": 35, "points": 5, "comparison": "gte",
            "message_pass": "✔️ Jumlah Produk = {value_int} [OK]",
            "message_fail": "❌ Jumlah Produk = {value_int} [NOT OK, nilai disarankan: >={threshold}]",
        },
        "store_status_points": {
            "mall": 10, "star_plus": 5, "star": 0, "regular": 0,
            "message_pass": "✔️ Status Toko = {store_status} [OK]",
            "message_fail": "❌ Status Toko = {store_status} [Wajib Shopee Mall]",
        },
    },
    "ads": {
        "roi_threshold": {
            "threshold": 9.0, "opportunity_points": 5, "comparison": "gt",
            "message_pass": "✔️ ROI = {val_str} [Sudah Baik]",
            "message_fail": "❌ ROI = {val_str} [Kurang Baik, nilai disarankan: {benchmark}]",
        },
        "gmv_ratio_threshold": {
            "threshold": 84.0, "points": 5, "comparison": "lt",
            "message_pass": "✔️ % GMV Iklan / GMV Toko = {pct_str} [Sudah Baik]",
            "message_fail": "❌ % GMV Iklan / GMV Toko = {pct_str} [Terlalu bergantung terhadap Iklan, nilai disarankan: <{threshold}%]",
            "message_no_ads": "❌ [Iklan tidak aktif sama sekali]",
        },
        "cost_ratio_range": {
            "min": 5.0, "max": 10.0, "info_only": True,
            "message_pass": "✔️ % Biaya Iklan / GMV Toko = {pct_str} [Sudah Baik]",
            "message_fail": "❌ % Biaya Iklan / GMV Toko = {pct_str} [Biaya terlalu tinggi, nilai disarankan: <{threshold}%]",
            "message_no_ads": "❌ [Iklan tidak aktif sama sekali]",
            "message_too_minimal": "❌ [Penggunaan iklan terlalu minim ({pct_str}). Nilai disarankan: {min}%-{max}%.]",
        },
    },
    "campaign": {
        "participation_pct_threshold": {
            "threshold": 90.0, "opportunity_points": 10, "comparison": "gte",
            "message_pass": "✔️ % Partisipasi Campaign = {pct_str} [Sudah Baik]",
            "message_fail": "❌ % Partisipasi Campaign = {pct_str} [Kurang Baik, nilai disarankan: >{threshold}%]",
            "message_no_data": "❌[Tidak ada Campaign yang dipartisipasikan]",
        },
    },
    "stock": {
        "high_threshold": {"threshold": 24, "points": 10, "comparison": "gte"},
        "mid_threshold": {"threshold": 12, "points": 5, "comparison": "gte"},
        "low_penalty": {"threshold": 12, "points": -5, "comparison": "lt"},
        "out_of_stock": {"threshold": 0.10, "penalty": -5.0},
    },
    "discount": {
        "fake_discount_flag": {"points_no_flag": 5, "points_flag": 0},
    },
    "marketing": {
        "floor": {"value": 0.12},
        "floor_fashion": {"value": 0.15},
        "base_subtraction": {"value": 0.03},
        "upper_limit_base": {"value": 0.20},
        "fashion_adjustment": {"value": 0.05},
        "minimum_threshold": {"value": 0.10},
        "display_max": {"value": 0.25},
        "display_min": {"value": 0.10},
    },
    "competition": {
        "message_pass": "{name} (IDR {selling_price}) = ✅[kompetitif]",
        "message_fail": "{name} (IDR {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: IDR {market_price})]",
    },
    "interpretation": {
        "closing_messages": {
            "✔️": (
                "Kami melihat bahwa potensi dari Toko {store_name} masih belum maksimal. "
                "Silahkan klik di link berikut ini untuk menjadwalkan sesi konsultasi yang lebih mendalam "
                "untuk menemukan solusi yang tepat bagi bisnis Anda.\n\n"
                "cal-bd2.ahacommerce.net\n\n"
                "Semoga apa yang kami bagikan dapat bermanfaat."
            ),
            "❌": (
                "Kami sangat yakin bahwa sistem AHA dapat memberikan nilai tambah kepada toko {store_name} "
                "secara langsung, namun kami perlu mempertimbangkan potensi keuntungan bagi kedua pihak "
                "untuk kerja-sama ini.\n\n"
                "Melalui pengalaman kami dengan ratusan toko online, kami mengkhawatirkan pihak brand "
                "tidak dapat mencapai level keuntungan yang diinginkan bila ditambahkan dengan biaya jasa AHA.\n"
                "Oleh karena itu, dengan berat hati, kami belum dapat bekerja-sama dengan {store_name} "
                "di tahap sekarang ini.\n\n"
                "Namun, kami memiliki skema kerjasama yang lain dimana AHA dapat menjadi partner dari brand "
                "dan memberikan pendanaan dengan timbal balik saham dari brand. Program ini bernama AHA Coventures. "
                "Untuk info lebih lanjut dapat dilihat di form pendaftaran berikut: bit.ly/AHACoventures"
            ),
            "❌ Non Mall": (
                "Kami telah melakukan analisa pada toko {store_name} secara langsung. "
                "Berdasarkan pengalaman kami, toko-toko yang berhasil dikelola oleh AHA Commerce umumnya "
                "adalah toko-toko yang telah berstatus Mall, karena status tersebut menunjukkan tingkat "
                "kepercayaan dan potensi pertumbuhan yang lebih stabil.\n\n"
                "Namun, karena saat ini toko {store_name} belum berstatus Mall, kami belum dapat memastikan "
                "bahwa sistem AHA dapat memberikan dampak peningkatan omzet yang signifikan.\n\n"
                "Meski demikian, kami dapat membantu proses pengajuan Mall apabila BRAND berencana untuk "
                "meningkat ke tahap tersebut. Terdapat beberapa persyaratan (terms) yang perlu dipenuhi, "
                "di antaranya:\n"
                "Brand sudah memiliki sertifikat merek HAKI untuk kelas produk\n"
                "Sertifikat HAKI kelas 35 (jasa penjualan), dan\n"
                "Emboss logo brand pada produk\n\n"
                "Apabila brand bersedia dan telah melengkapi persyaratan di atas, kami dengan senang hati "
                "untuk berdiskusi lebih lanjut dan akan membantu proses pengajuan status Mallnya dengan "
                "menjadwalkan meeting selanjutnya pada link calendly berikut: "
                "https://calendly.com/meeting-with-ahacommerce/2ndmeeting\n\n"
                "Kami berharap hasil evaluasi ini dapat menjadi masukan yang berguna bagi tim {store_name} "
                "dalam pengembangan toko ke depannya."
            ),
            "❌ No Brand": (
                "Kami telah melakukan analisa pada toko {store_name} secara langsung, namun berdasarkan "
                "pengalaman kami toko toko yang sukses dikelola AHA adalah toko toko yang memiliki brand "
                "sendiri dan brandnya sudah mulai dikenal di pasaran\n\n"
                "Oleh karena melihat toko {store_name} bukan merupakan toko yang memiliki brand sendiri, "
                "maka kami belum yakin apabila sistem AHA dapat memberikan dampak peningkatan omset yang "
                "signifikan.\n\n"
                "Oleh karena itu, dengan berat hati, kami belum dapat bekerja-sama dengan {store_name} "
                "di tahap sekarang ini.\n\n"
                "Bagaimanapun juga, semoga hasil evaluasi kami bermanfaat bagi tim {store_name} untuk "
                "mengidentifikasi bagian² yang perlu diperbaiki.\n\n"
                "Namun, tidak menutup kemungkinan bagi peluang kerjasama {store_name} dengan AHA Commerce "
                "di kemudian hari."
            ),
            "❌ Opex": (
                "Melalui pengalaman kami dengan ratusan toko online, omzet suatu toko online sangat bergantung "
                "pada tingkat performa operasional toko tersebut (pengiriman tepat waktu >90%, tingkat "
                "pembatalan <1%, dll.).\n\n"
                "Kami sangat yakin bahwa sistem AHA dapat memberikan nilai tambah kepada toko {store_name} "
                "dari menambah jumlah orderan masuk lebih tinggi dan meningkatkan omsetnya jauh dari angka "
                "saat ini. Tetapi kami melihat tingkat keterlambatan yang cukup tinggi sehingga kekhawatiran "
                "kami cukup besar apabila jumlah orderan bertambah dan tingkat keterlambatan meningkat akan "
                "berpotensi membuat toko terkena penalti dan berpengaruh pada performa toko.\n\n"
                "Sehingga apabila dari pihak brand bisa memaksimalkan kecepatan pengiriman dan membuat "
                "tingkat keterlambatan <2% dan masa pengemasan dibawah satu hari, kami sangat open untuk "
                "berdiskusi lebih lanjut untuk kerjasama dengan {store_name}."
            ),
        },
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
        value=d7, benchmark=f"<{uor_threshold:g}%", verdict=f7, message="", score=h7,
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
    ))

    # Row 11: Overall Rating (no score)
    d11 = _safe_num(ops.get("overallRating"))
    rating_threshold = _get_rule_value(ops_rules, "overall_rating", "threshold", 4.7)
    f11 = "✔️" if d11 >= rating_threshold else "❌"
    rows.append(RowScore(
        row=11, metric="Keseluruhan Penilaian",
        value=d11, benchmark=f">{rating_threshold:g}", verdict=f11, message="", score=0.0,
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
    f13 = "✔️" if avg_6mo < current_month * trend_multiplier else "❌"
    h13 = trend_points if avg_6mo < current_month * trend_multiplier else 0.0
    rows.append(RowScore(
        row=13, metric=f"Penjualan Bulan {month_labels[0]}",
        value=current_month, benchmark=e13, verdict=f13, message="", score=h13,
    ))

    # Rows 14-18: Past months (no score, kept for reference)
    for i in range(1, 6):
        rows.append(RowScore(
            row=13 + i, metric=f"Penjualan Bulan {month_labels[i]}",
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
        value=d28, benchmark=f">{rv_threshold * 100:g}%", verdict=f28, message="", score=h28,
    ))

    # Row 29: Total followers
    fl_threshold = _get_rule_value(vis_rules, "followers", "threshold", 50000)
    fl_points = float(_get_rule_value(vis_rules, "followers", "points", 2.0))
    f29 = "✔️" if d29 > fl_threshold else "❌"
    h29 = fl_points if d29 > fl_threshold else 0.0
    rows.append(RowScore(
        row=29, metric="Total Pengikut",
        value=d29, benchmark=f">{fl_threshold:g}", verdict=f29, message="", score=h29,
    ))

    total = h28 + h29
    return CategoryScore(
        category="Tinjauan Pengunjung",
        score=total, max_score=5.0, rows=rows,
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
        value=d45, benchmark=f">={pc_threshold:g}", verdict=f45, message="", score=h45,
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
    d50 = round(d48 / d49, 1) if d49 > 0 else 0.0
    roi_threshold = _get_rule_value(ads_rules, "roi_threshold", "threshold", 9.0)
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
        value=d51, benchmark=f"<{gmv_threshold * 100:g}%", verdict=f51, message="", score=h51,
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
        value=d57, benchmark=f">{part_threshold * 100:g}%", verdict=f57, message="", score=h57,
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
            value=selling_price, benchmark=f"IDR {_fmt_idr(market_price)}" if market_price > 0 else "-",
            verdict=f_verdict, message="", score=0.0,
        ))

    return CategoryScore(
        category="Kompetisi TOP Produk",
        score=0.0, max_score=0.0, rows=rows,
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
            row=70, metric="Rata² Stok",
            value="N/A", benchmark=f">={high_threshold:g}", verdict="-",
            message="Calculator 2 (Top SKU) belum dijalankan", score=0.0,
        )
        return CategoryScore(
            category="Stok",
            score=0.0, max_score=10.0, rows=[row], available=False,
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
        msg70 = f"✔️ Rata² Stok = {avg_stock_int} [Sudah Baik]"
    else:
        msg70 = f"❌ Rata² Stok = {avg_stock_int} [Kurang Baik, nilai disarankan: >={high_threshold:g}]"

    row70 = RowScore(
        row=70, metric="Rata² Stok",
        value=avg_stock_int, benchmark=f">={high_threshold:g}", verdict=f70,
        message=msg70, score=h70,
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
    if f71 == "✔️":
        msg71 = f"✔️ % Ketersediaan Stok = {oos_pct_display} stok habis [Sudah Baik]"
    else:
        msg71 = f"❌ % Ketersediaan Stok = {oos_pct_display} stok habis [Kurang Baik, nilai disarankan: ≤{oos_threshold * 100:.0f}%]"

    row71 = RowScore(
        row=71, metric="% Ketersediaan Stok",
        value=out_of_stock_pct,
        benchmark=f"≤{oos_threshold * 100:.0f}% stok habis",
        verdict=f71, message=msg71, score=h71,
    )

    total_score = h70 + h71
    return CategoryScore(
        category="Stok",
        score=total_score, max_score=10.0, rows=[row70, row71],
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
        if row.verdict == "✔️":
            tmpl = _get_rule_value(ops_rules, rule_key, "message_pass", pass_default)
            row.message = _format_message_template(tmpl, val_str=val_str, threshold=threshold_str)
        else:
            tmpl = _get_rule_value(ops_rules, rule_key, "message_fail", fail_default)
            row.message = _format_message_template(tmpl, val_str=val_str, threshold=threshold_str)


def _generate_business_messages(cat: CategoryScore, manual_data: dict, rules: dict | None = None) -> None:
    """Fill G-column messages for business rows 13-20."""
    biz_rules = _get_rule_category(rules, "business")
    biz = _get_nested(manual_data, "business") or {}
    sales_months = [_safe_num(biz.get(f"salesMonth{i}")) for i in range(6)]
    current = sales_months[0]
    avg_6mo = round(sum(sales_months) / 6) if any(s > 0 for s in sales_months) else 0

    for row in cat.rows:
        if row.row == 13:
            idr_val = _fmt_idr(current)
            idr_avg = _fmt_idr(avg_6mo)
            if avg_6mo > 0 and current > 0:
                change_pct = ((current - avg_6mo) / avg_6mo) * 100
            else:
                change_pct = 0.0
            change_pct_str = f"{abs(change_pct):.1f}"

            if row.verdict == "✔️":
                tmpl = _get_rule_value(biz_rules, "monthly_sales_trend", "message_pass",
                    "✔️ Penjualan = IDR {idr_val} [Meningkat {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}]")
                row.message = _format_message_template(tmpl, idr_val=idr_val, change_pct=change_pct_str, idr_avg=idr_avg)
            else:
                tmpl = _get_rule_value(biz_rules, "monthly_sales_trend", "message_fail",
                    "❌ Penjualan = IDR {idr_val} [Menurun {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}]")
                msg = _format_message_template(tmpl, idr_val=idr_val, change_pct=change_pct_str, idr_avg=idr_avg)
                if change_pct < -25:
                    severe_tmpl = _get_rule_value(biz_rules, "monthly_sales_trend", "message_fail_severe",
                        "\n❗️ Potensi peningkatan harga jual signifikan atau terdapat event abnormal.")
                    msg += severe_tmpl
                row.message = msg
        elif row.row == 20:
            val_str = f"{row.value:.1f}%"
            if row.verdict == "✔️":
                tmpl = _get_rule_value(biz_rules, "conversion_rate", "message_pass",
                    "✔️ Tingkat Konversi = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str, benchmark=row.benchmark)
            elif row.verdict == "❌":
                tmpl = _get_rule_value(biz_rules, "conversion_rate", "message_fail",
                    "❌ Tingkat Konversi = {val_str} [Kurang Baik, nilai disarankan: {benchmark}]")
                row.message = _format_message_template(tmpl, val_str=val_str, benchmark=row.benchmark)


def _generate_visitors_messages(cat: CategoryScore, rules: dict | None = None) -> None:
    """Fill G-column messages for visitor rows 26-29."""
    vis_rules = _get_rule_category(rules, "visitors")
    for row in cat.rows:
        if row.row == 28:
            val_str = _fmt_pct_1dp(row.value) if isinstance(row.value, float) else str(row.value)
            threshold = _get_rule_value(vis_rules, "returning_visitors_pct", "threshold", 23)
            if row.verdict == "✔️":
                tmpl = _get_rule_value(vis_rules, "returning_visitors_pct", "message_pass",
                    "✔️ % Pengunjung Lama = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))
            else:
                tmpl = _get_rule_value(vis_rules, "returning_visitors_pct", "message_fail",
                    "❌ % Pengunjung Lama = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))
        elif row.row == 29:
            val_str = f"{int(row.value):,}".replace(",", ".")
            if row.verdict == "✔️":
                tmpl = _get_rule_value(vis_rules, "followers", "message_pass",
                    "✔️ Total Pengikut = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str)
            else:
                tmpl = _get_rule_value(vis_rules, "followers", "message_fail",
                    "❌ Total Pengikut = {val_str} [Kurang Baik, nilai disarankan: >50.000]")
                row.message = _format_message_template(tmpl, val_str=val_str)


def _generate_promo_messages(cat: CategoryScore, manual_data: dict, rules: dict | None = None) -> None:
    """Fill G-column messages for promo tool rows 31-43."""
    promo_rules = _get_rule_category(rules, "promo_tools")
    indiv = promo_rules.get("individual_messages", {})
    d13 = _safe_num(_get_nested(manual_data, "business", "salesMonth0"))

    for row in cat.rows:
        if PROMO_START_ROW <= row.row <= PROMO_START_ROW + len(PROMO_TOOLS) - 1:
            # Individual promo tool row
            d_value = _safe_num(row.value)
            pct_of_sales = d_value / d13 if d13 > 0 else 0.0
            pct_str = _fmt_pct_1dp(pct_of_sales)

            if d_value == 0:
                tmpl = indiv.get("message_zero", "{verdict} {metric} nil pendapatan")
                row.message = _format_message_template(tmpl, verdict=row.verdict, metric=row.metric)
            elif row.row == PROMO_START_ROW and d13 > 0 and d_value / d13 >= 0.50:
                # "Terlalu mengandalkan promo" only applies to Promo Toko (row 31)
                tmpl = indiv.get("message_dependent",
                    "{verdict} {metric} = {pct_str} [Terlalu mengandalkan promo, nilai disarankan: 15%-50%]")
                row.message = _format_message_template(tmpl, verdict=row.verdict, metric=row.metric, pct_str=pct_str)
            elif row.verdict == "❌":
                tmpl = indiv.get("message_fail",
                    "❌ {metric} = {pct_str} [Kurang Efektif, nilai disarankan: {benchmark}]")
                row.message = _format_message_template(tmpl, metric=row.metric, pct_str=pct_str, benchmark=row.benchmark)
            elif row.verdict == "✔️":
                if row.metric == "Program Afiliasi":
                    tmpl = indiv.get("message_pass_afiliasi", "✔️ {metric} ({pct_str}) digunakan")
                    row.message = _format_message_template(tmpl, metric=row.metric, pct_str=pct_str)
                else:
                    tmpl = indiv.get("message_pass",
                        "✔️ {metric} ({pct_str}) digunakan & persentase penggunaan baik")
                    row.message = _format_message_template(tmpl, metric=row.metric, pct_str=pct_str)

        elif row.row == 42:
            val_str = _fmt_pct_0dp(row.value) if isinstance(row.value, float) else str(row.value)
            threshold = _get_rule_value(promo_rules, "usage_pct_threshold", "threshold", 80)
            if row.verdict == "✔️":
                tmpl = _get_rule_value(promo_rules, "usage_pct_threshold", "message_pass",
                    "✔️ Penggunaan alat promosi = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))
            else:
                tmpl = _get_rule_value(promo_rules, "usage_pct_threshold", "message_fail",
                    "❌ Penggunaan alat promosi = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))
        elif row.row == 43:
            val_str = _fmt_pct_0dp(row.value) if isinstance(row.value, float) else str(row.value)
            threshold = _get_rule_value(promo_rules, "effectiveness_pct_threshold", "threshold", 90)
            if row.verdict == "✔️":
                tmpl = _get_rule_value(promo_rules, "effectiveness_pct_threshold", "message_pass",
                    "✔️ Efektifitas alat promosi = {val_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))
            else:
                tmpl = _get_rule_value(promo_rules, "effectiveness_pct_threshold", "message_fail",
                    "❌ Efektifitas alat promosi = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))


def _generate_products_messages(cat: CategoryScore, rules: dict | None = None) -> None:
    """Fill G-column messages for product/status rows 45-46."""
    prod_rules = _get_rule_category(rules, "products_status")
    for row in cat.rows:
        if row.row == 45:
            value_int = str(int(row.value))
            threshold = _get_rule_value(prod_rules, "product_count", "threshold", 35)
            if row.verdict == "✔️":
                tmpl = _get_rule_value(prod_rules, "product_count", "message_pass",
                    "✔️ Jumlah Produk = {value_int} [OK]")
                row.message = _format_message_template(tmpl, value_int=value_int, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))
            else:
                tmpl = _get_rule_value(prod_rules, "product_count", "message_fail",
                    "❌ Jumlah Produk = {value_int} [NOT OK, nilai disarankan: >={threshold}]")
                row.message = _format_message_template(tmpl, value_int=value_int, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))
        elif row.row == 46:
            store_status = str(row.value)
            if row.verdict == "✔️":
                tmpl = _get_rule_value(prod_rules, "store_status_points", "message_pass",
                    "✔️ Status Toko = {store_status} [OK]")
                row.message = _format_message_template(tmpl, store_status=store_status)
            elif row.verdict == "❌":
                tmpl = _get_rule_value(prod_rules, "store_status_points", "message_fail",
                    "❌ Status Toko = {store_status} [Wajib Shopee Mall]")
                row.message = _format_message_template(tmpl, store_status=store_status)


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
            else:
                tmpl = _get_rule_value(ads_rules, "roi_threshold", "message_fail",
                    "❌ ROI = {val_str} [Kurang Baik, nilai disarankan: {benchmark}]")
                row.message = _format_message_template(tmpl, val_str=val_str, benchmark=row.benchmark)
        elif row.row == 51:
            pct_str = _fmt_pct_1dp(row.value) if isinstance(row.value, float) else str(row.value)
            threshold = _get_rule_value(ads_rules, "gmv_ratio_threshold", "threshold", 84)
            if d48 == 0:
                tmpl = _get_rule_value(ads_rules, "gmv_ratio_threshold", "message_no_ads",
                    "❌ [Iklan tidak aktif sama sekali]")
                row.message = _format_message_template(tmpl)
            elif row.verdict == "✔️":
                tmpl = _get_rule_value(ads_rules, "gmv_ratio_threshold", "message_pass",
                    "✔️ % GMV Iklan / GMV Toko = {pct_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))
            else:
                tmpl = _get_rule_value(ads_rules, "gmv_ratio_threshold", "message_fail",
                    "❌ % GMV Iklan / GMV Toko = {pct_str} [Terlalu bergantung terhadap Iklan, nilai disarankan: <{threshold}%]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))
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
            elif d52 < 0.05:
                tmpl = _get_rule_value(ads_rules, "cost_ratio_range", "message_too_minimal",
                    "❌ [Penggunaan iklan terlalu minim ({pct_str}). Nilai disarankan: {min}%-{max}%.]")
                row.message = _format_message_template(tmpl, pct_str=pct_str,
                    min=str(int(cost_min)), max=str(int(cost_max)))
            elif row.verdict == "❌":
                tmpl = _get_rule_value(ads_rules, "cost_ratio_range", "message_fail",
                    "❌ % Biaya Iklan / GMV Toko = {pct_str} [Biaya terlalu tinggi, nilai disarankan: <{threshold}%]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=threshold)
            elif row.verdict == "✔️":
                tmpl = _get_rule_value(ads_rules, "cost_ratio_range", "message_pass",
                    "✔️ % Biaya Iklan / GMV Toko = {pct_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=threshold)
        elif row.row == 53:
            row.message = calc1_output


def _generate_campaign_messages(cat: CategoryScore, rules: dict | None = None) -> None:
    """Fill G-column messages for campaign rows 55-57."""
    camp_rules = _get_rule_category(rules, "campaign")
    threshold = _get_rule_value(camp_rules, "participation_pct_threshold", "threshold", 90)
    for row in cat.rows:
        if row.row == 57:
            if isinstance(row.value, float) and row.value == 0.0:
                tmpl = _get_rule_value(camp_rules, "participation_pct_threshold", "message_no_data",
                    "❌[Tidak ada Campaign yang dipartisipasikan]")
                row.message = _format_message_template(tmpl)
            elif row.verdict == "✔️":
                pct_str = _fmt_pct_1dp(row.value)
                tmpl = _get_rule_value(camp_rules, "participation_pct_threshold", "message_pass",
                    "✔️ % Partisipasi Campaign = {pct_str} [Sudah Baik]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))
            else:
                pct_str = _fmt_pct_1dp(row.value) if isinstance(row.value, float) else str(row.value)
                tmpl = _get_rule_value(camp_rules, "participation_pct_threshold", "message_fail",
                    "❌ % Partisipasi Campaign = {pct_str} [Kurang Baik, nilai disarankan: >{threshold}%]")
                row.message = _format_message_template(tmpl, pct_str=pct_str, threshold=f"{threshold:g}" if isinstance(threshold, float) else str(threshold))


def _generate_competition_messages(cat: CategoryScore, manual_data: dict, rules: dict | None = None) -> None:
    """Fill G-column messages for competition rows 61-63."""
    comp_rules = _get_rule_category(rules, "competition")
    comp = _get_nested(manual_data, "competition") or {}

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
                "{name} (IDR {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: IDR {market_price})]")
            msg = _format_message_template(
                tmpl, name=product_name, selling_price=_fmt_idr(selling_price),
                market_price=_fmt_idr(market_price),
            )
            if link:
                msg += f"\n↪{link}"
            row.message = msg
        elif row.verdict == "✔️":
            tmpl = comp_rules.get("message_pass", "{name} (IDR {selling_price}) = ✅[kompetitif]")
            msg = _format_message_template(
                tmpl, name=product_name, selling_price=_fmt_idr(selling_price),
            )
            if link:
                msg += f"\n↪{link}"
            row.message = msg


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
