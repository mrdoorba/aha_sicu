"""Add message templates to scoring_rules JSONB

Adds message_pass / message_fail (and multi-variant) template strings to each
rule entry that generates a G-column message.  Also adds promo individual row
templates and G75 closing messages under interpretation.

Revision ID: 012
Revises: 011
Create Date: 2026-02-12
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None

# ---------------------------------------------------------------------------
# Message template patches — keyed by category, then rule key, then new fields
#
# NOTE (source of truth): These messages are also defined as defaults in:
#   - backend/app/calculators/scoring.py DEFAULT_FASHION_RULES / DEFAULT_NON_FASHION_RULES
#   - Inline fallback defaults in each _generate_*_messages() function
# ---------------------------------------------------------------------------

# Shared across both Fashion and Non-Fashion (identical messages)
SHARED_MESSAGES: dict = {
    "operational": {
        "unfulfilled_order_rate": {
            "message_pass": "✔️ Tingkat Pesanan Tidak Terselesaikan = {val_str} Sudah Baik",
            "message_fail": "❌ Tingkat Pesanan Tidak Terselesaikan = {val_str} Kurang Baik, nilai disarankan: <{threshold}%",
        },
        "late_shipment_rate": {
            "message_pass": "✔️ Tingkat Keterlambatan Pengiriman = {val_str} Sudah Baik",
            "message_fail": "❌ Tingkat Keterlambatan Pengiriman = {val_str} Kurang Baik, nilai disarankan: <{threshold}%",
        },
        "preparation_time": {
            "message_pass": "✔️ Masa Pengemasan = {val_str} hari Sudah Baik",
            "message_fail": "❌ Masa Pengemasan = {val_str} hari Kurang Baik, nilai disarankan: <{threshold} hari",
        },
        "chat_response_rate": {
            "message_pass": "✔️ Persentase Chat Dibalas = {val_str} Sudah Baik",
            "message_fail": "❌ Persentase Chat Dibalas = {val_str} Kurang Baik, nilai disarankan: >{threshold}%",
        },
        "overall_rating": {
            "message_pass": "✔️ Keseluruhan Penilaian = {val_str} Sudah Baik",
            "message_fail": "❌ Keseluruhan Penilaian = {val_str} Kurang Baik, nilai disarankan: >{threshold}",
        },
    },
    "business": {
        "monthly_sales_trend": {
            "message_pass": "✔️ Penjualan = IDR {idr_val} Meningkat {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}",
            "message_fail": "❌ Penjualan = IDR {idr_val} Menurun {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}",
            "message_fail_severe": "\n❗️ Potensi peningkatan harga jual signifikan atau terdapat event abnormal.",
        },
        "conversion_rate": {
            "message_pass": "✔️ Tingkat Konversi = {val_str} Sudah Baik",
            "message_fail": "❌ Tingkat Konversi = {val_str} Kurang Baik, nilai disarankan: {benchmark}",
        },
    },
    "content": {
        "quality_ratio": {
            "message_pass": "✔️ % Konten baik = {val_str} Sudah Baik",
            "message_fail": "❌ % Konten baik = {val_str} Kurang Baik, nilai disarankan: >{threshold}%",
        },
    },
    "visitors": {
        "returning_visitors_pct": {
            "message_pass": "✔️ % Pengunjung Lama = {val_str} Sudah Baik",
            "message_fail": "❌ % Pengunjung Lama = {val_str} Kurang Baik, nilai disarankan: >{threshold}%",
        },
        "followers": {
            "message_pass": "✔️ Total Pengikut = {val_str} Sudah Baik",
            "message_fail": "❌ Total Pengikut = {val_str} Kurang Baik, nilai disarankan: >50.000",
        },
    },
    "promo_tools": {
        "usage_pct_threshold": {
            "message_pass": "✔️ Penggunaan alat promosi = {val_str} Sudah Baik",
            "message_fail": "❌ Penggunaan alat promosi = {val_str} Kurang Baik, nilai disarankan: >{threshold}%",
        },
        "effectiveness_pct_threshold": {
            "message_pass": "✔️ Efektifitas alat promosi = {val_str} Sudah Baik",
            "message_fail": "❌ Efektifitas alat promosi = {val_str} Kurang Baik, nilai disarankan: >{threshold}%",
        },
        "individual_messages": {
            "message_zero": "{verdict} {metric} nil pendapatan",
            "message_dependent": "{verdict} {metric} = {pct_str} Terlalu mengandalkan promo, nilai disarankan: 15%-50%",
            "message_fail": "❌ {metric} = {pct_str} Kurang Efektif, nilai disarankan: {benchmark}",
            "message_pass": "✔️ {metric} ({pct_str}) digunakan & persentase penggunaan baik",
            "message_pass_afiliasi": "✔️ {metric} ({pct_str}) digunakan",
        },
    },
    "products_status": {
        "product_count": {
            "message_pass": "✔️ Jumlah Produk = {value_int} OK",
            "message_fail": "❌ Jumlah Produk = {value_int} NOT OK, nilai disarankan: >={threshold}",
        },
        "store_status_points": {
            "message_pass": "✔️ Status Toko = {store_status} OK",
            "message_fail": "❌ Status Toko = {store_status} Wajib Shopee Mall",
        },
    },
    "ads": {
        "roi_threshold": {
            "message_pass": "✔️ ROI = {val_str} Sudah Baik",
            "message_fail": "❌ ROI = {val_str} Kurang Baik, nilai disarankan: {benchmark}",
        },
        "gmv_ratio_threshold": {
            "message_pass": "✔️ % GMV Iklan / GMV Toko = {pct_str} Sudah Baik",
            "message_fail": "❌ % GMV Iklan / GMV Toko = {pct_str} Terlalu bergantung terhadap Iklan, nilai disarankan: <{threshold}%",
            "message_no_ads": "❌ Iklan tidak aktif sama sekali",
        },
        "cost_ratio_range": {
            "message_pass": "✔️ % Biaya Iklan / GMV Toko = {pct_str} Sudah Baik",
            "message_fail": "❌ % Biaya Iklan / GMV Toko = {pct_str} Biaya terlalu tinggi, nilai disarankan: <{threshold}%",
            "message_no_ads": "❌ Iklan tidak aktif sama sekali",
            "message_too_minimal": "❌ Penggunaan iklan terlalu minim ({pct_str}). Nilai disarankan: {min}%-{max}%.",
        },
    },
    "campaign": {
        "participation_pct_threshold": {
            "message_pass": "✔️ % Partisipasi Campaign = {pct_str} Sudah Baik",
            "message_fail": "❌ % Partisipasi Campaign = {pct_str} Kurang Baik, nilai disarankan: >{threshold}%",
            "message_no_data": "❌Tidak ada Campaign yang dipartisipasikan",
        },
    },
}

# Competition messages (shared)
COMPETITION_MESSAGES: dict = {
    "message_pass": "✅kompetitif",
    "message_fail": "❌tidak kompetitif (harga kisaran pasaran: Rp. {market_price})",
}

# G75 closing messages (shared)
CLOSING_MESSAGES: dict = {
    "✔️": "Berdasarkan data analisa diatas, potensi toko masih belum maksimal. Kami mengundang untuk berdiskusi mengenai potensi optimisasi toko melalui link berikut: cal-bd2.ahacommerce.net",
    "❌": "Berdasarkan data analisa diatas, perlu mempertimbangkan potensi keuntungan. Silakan cek AHA Coventures: bit.ly/AHACoventures",
    "❌ Non Mall": "Toko belum berstatus Mall. AHA dapat membantu proses pengajuan Shopee Mall. Persyaratan: HAKI (Merek Terdaftar), NIB, dan dokumen legalitas usaha.",
    "❌ No Brand": "Toko bukan merupakan toko yang memiliki brand sendiri. Terima kasih atas waktunya, semoga sukses selalu.",
    "": "Performa toko sudah cukup baik. Terima kasih atas waktunya, semoga sukses selalu.",
    "❌ Opex": "Tingkat keterlambatan cukup tinggi. Disarankan untuk memperbaiki pengiriman (<2%) dan masa pengemasan (<1 hari) terlebih dahulu.",
    "⭕️": "",
}


def _build_patch(messages: dict, competition: dict, closing: dict) -> dict:
    """Build a single JSON patch dict that merges message fields into existing rules."""
    return {
        "category_messages": messages,
        "competition_messages": competition,
        "closing_messages": closing,
    }


def upgrade() -> None:
    conn = op.get_bind()

    for template in ("fashion", "non_fashion"):
        # Fetch current rules
        row = conn.execute(
            sa.text("SELECT rules FROM scoring_rules WHERE template = :t"),
            {"t": template},
        ).fetchone()
        if row is None:
            continue

        rules = json.loads(row[0]) if isinstance(row[0], str) else row[0]

        # Merge message fields into each category/rule
        for category, rule_messages in SHARED_MESSAGES.items():
            if category not in rules:
                continue
            for rule_key, msg_fields in rule_messages.items():
                if rule_key in rules[category]:
                    rules[category][rule_key].update(msg_fields)
                else:
                    # New key (e.g., individual_messages under promo_tools)
                    rules[category][rule_key] = msg_fields

        # Add competition messages as a top-level key
        rules["competition"] = COMPETITION_MESSAGES

        # Add closing_messages under interpretation
        if "interpretation" not in rules:
            rules["interpretation"] = {}
        rules["interpretation"]["closing_messages"] = CLOSING_MESSAGES

        # Write back
        op.execute(
            sa.text(
                "UPDATE scoring_rules "
                "SET rules = :rules::jsonb, "
                "    version = version + 1 "
                "WHERE template = :template"
            ),
            {"template": template, "rules": json.dumps(rules)},
        )


def downgrade() -> None:
    conn = op.get_bind()

    # Fields to remove from each category/rule
    message_fields = {
        "message_pass", "message_fail", "message_fail_severe",
        "message_no_ads", "message_too_minimal", "message_no_data",
        "message_zero", "message_dependent", "message_pass_afiliasi",
    }

    for template in ("fashion", "non_fashion"):
        row = conn.execute(
            sa.text("SELECT rules FROM scoring_rules WHERE template = :t"),
            {"t": template},
        ).fetchone()
        if row is None:
            continue

        rules = json.loads(row[0]) if isinstance(row[0], str) else row[0]

        # Remove message fields from each category
        for category in SHARED_MESSAGES:
            if category not in rules:
                continue
            for rule_key in list(rules[category].keys()):
                if rule_key == "individual_messages":
                    del rules[category][rule_key]
                    continue
                if isinstance(rules[category][rule_key], dict):
                    for field_name in message_fields:
                        rules[category][rule_key].pop(field_name, None)

        # Remove competition messages
        rules.pop("competition", None)

        # Remove closing_messages from interpretation
        if "interpretation" in rules:
            rules["interpretation"].pop("closing_messages", None)

        # Write back with decremented version
        op.execute(
            sa.text(
                "UPDATE scoring_rules "
                "SET rules = :rules::jsonb, "
                "    version = version - 1 "
                "WHERE template = :template"
            ),
            {"template": template, "rules": json.dumps(rules)},
        )
