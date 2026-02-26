"""Add square brackets to all scoring message templates

Wraps verdict/recommendation text in [...] for every scoring message template,
except "nil pendapatan" and "digunakan" messages which remain unbracketed.

Revision ID: 020
Revises: 019
Create Date: 2026-02-26
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "020"
down_revision = "019"
branch_labels = None
depends_on = None

# (json_path, old_value, new_value)
PATCHES: list[tuple[list[str], str, str]] = [
    # --- Operational ---
    (
        ["operational", "unfulfilled_order_rate", "message_pass"],
        "✔️ Tingkat Pesanan Tidak Terselesaikan = {val_str} Sudah Baik",
        "✔️ Tingkat Pesanan Tidak Terselesaikan = {val_str} [Sudah Baik]",
    ),
    (
        ["operational", "unfulfilled_order_rate", "message_fail"],
        "❌ Tingkat Pesanan Tidak Terselesaikan = {val_str} Kurang Baik, nilai disarankan: <{threshold}%",
        "❌ Tingkat Pesanan Tidak Terselesaikan = {val_str} [Kurang Baik, nilai disarankan: <{threshold}%]",
    ),
    (
        ["operational", "late_shipment_rate", "message_pass"],
        "✔️ Tingkat Keterlambatan Pengiriman = {val_str} Sudah Baik",
        "✔️ Tingkat Keterlambatan Pengiriman = {val_str} [Sudah Baik]",
    ),
    (
        ["operational", "late_shipment_rate", "message_fail"],
        "❌ Tingkat Keterlambatan Pengiriman = {val_str} Kurang Baik, nilai disarankan: <{threshold}%",
        "❌ Tingkat Keterlambatan Pengiriman = {val_str} [Kurang Baik, nilai disarankan: <{threshold}%]",
    ),
    (
        ["operational", "preparation_time", "message_pass"],
        "✔️ Masa Pengemasan = {val_str} hari Sudah Baik",
        "✔️ Masa Pengemasan = {val_str} hari [Sudah Baik]",
    ),
    (
        ["operational", "preparation_time", "message_fail"],
        "❌ Masa Pengemasan = {val_str} hari Kurang Baik, nilai disarankan: <{threshold} hari",
        "❌ Masa Pengemasan = {val_str} hari [Kurang Baik, nilai disarankan: <{threshold} hari]",
    ),
    (
        ["operational", "chat_response_rate", "message_pass"],
        "✔️ Persentase Chat Dibalas = {val_str} Sudah Baik",
        "✔️ Persentase Chat Dibalas = {val_str} [Sudah Baik]",
    ),
    (
        ["operational", "chat_response_rate", "message_fail"],
        "❌ Persentase Chat Dibalas = {val_str} Kurang Baik, nilai disarankan: >{threshold}%",
        "❌ Persentase Chat Dibalas = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]",
    ),
    (
        ["operational", "overall_rating", "message_pass"],
        "✔️ Keseluruhan Penilaian = {val_str} Sudah Baik",
        "✔️ Keseluruhan Penilaian = {val_str} [Sudah Baik]",
    ),
    (
        ["operational", "overall_rating", "message_fail"],
        "❌ Keseluruhan Penilaian = {val_str} Kurang Baik, nilai disarankan: >{threshold}",
        "❌ Keseluruhan Penilaian = {val_str} [Kurang Baik, nilai disarankan: >{threshold}]",
    ),
    # --- Business ---
    (
        ["business", "monthly_sales_trend", "message_pass"],
        "✔️ Penjualan = IDR {idr_val} Meningkat {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}",
        "✔️ Penjualan = IDR {idr_val} [Meningkat {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}]",
    ),
    (
        ["business", "monthly_sales_trend", "message_fail"],
        "❌ Penjualan = IDR {idr_val} Menurun {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}",
        "❌ Penjualan = IDR {idr_val} [Menurun {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}]",
    ),
    (
        ["business", "conversion_rate", "message_pass"],
        "✔️ Tingkat Konversi = {val_str} Sudah Baik",
        "✔️ Tingkat Konversi = {val_str} [Sudah Baik]",
    ),
    (
        ["business", "conversion_rate", "message_fail"],
        "❌ Tingkat Konversi = {val_str} Kurang Baik, nilai disarankan: {benchmark}",
        "❌ Tingkat Konversi = {val_str} [Kurang Baik, nilai disarankan: {benchmark}]",
    ),
    # --- Visitors ---
    (
        ["visitors", "returning_visitors_pct", "message_pass"],
        "✔️ % Pengunjung Lama = {val_str} Sudah Baik",
        "✔️ % Pengunjung Lama = {val_str} [Sudah Baik]",
    ),
    (
        ["visitors", "returning_visitors_pct", "message_fail"],
        "❌ % Pengunjung Lama = {val_str} Kurang Baik, nilai disarankan: >{threshold}%",
        "❌ % Pengunjung Lama = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]",
    ),
    (
        ["visitors", "followers", "message_pass"],
        "✔️ Total Pengikut = {val_str} Sudah Baik",
        "✔️ Total Pengikut = {val_str} [Sudah Baik]",
    ),
    (
        ["visitors", "followers", "message_fail"],
        "❌ Total Pengikut = {val_str} Kurang Baik, nilai disarankan: >50.000",
        "❌ Total Pengikut = {val_str} [Kurang Baik, nilai disarankan: >50.000]",
    ),
    # --- Promo Tools ---
    (
        ["promo_tools", "individual_messages", "message_dependent"],
        "{verdict} {metric} = {pct_str} Terlalu mengandalkan promo, nilai disarankan: 15%-50%",
        "{verdict} {metric} = {pct_str} [Terlalu mengandalkan promo, nilai disarankan: 15%-50%]",
    ),
    (
        ["promo_tools", "usage_pct_threshold", "message_pass"],
        "✔️ Penggunaan alat promosi = {val_str} Sudah Baik",
        "✔️ Penggunaan alat promosi = {val_str} [Sudah Baik]",
    ),
    (
        ["promo_tools", "usage_pct_threshold", "message_fail"],
        "❌ Penggunaan alat promosi = {val_str} Kurang Baik, nilai disarankan: >{threshold}%",
        "❌ Penggunaan alat promosi = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]",
    ),
    (
        ["promo_tools", "effectiveness_pct_threshold", "message_pass"],
        "✔️ Efektifitas alat promosi = {val_str} Sudah Baik",
        "✔️ Efektifitas alat promosi = {val_str} [Sudah Baik]",
    ),
    (
        ["promo_tools", "effectiveness_pct_threshold", "message_fail"],
        "❌ Efektifitas alat promosi = {val_str} Kurang Baik, nilai disarankan: >{threshold}%",
        "❌ Efektifitas alat promosi = {val_str} [Kurang Baik, nilai disarankan: >{threshold}%]",
    ),
    # --- Products & Status ---
    (
        ["products_status", "store_status_points", "message_pass"],
        "✔️ Status Toko = {store_status} OK",
        "✔️ Status Toko = {store_status} [OK]",
    ),
    (
        ["products_status", "store_status_points", "message_fail"],
        "❌ Status Toko = {store_status} Wajib Shopee Mall",
        "❌ Status Toko = {store_status} [Wajib Shopee Mall]",
    ),
    # --- Ads ---
    (
        ["ads", "roi_threshold", "message_pass"],
        "✔️ ROI = {val_str} Sudah Baik",
        "✔️ ROI = {val_str} [Sudah Baik]",
    ),
    (
        ["ads", "roi_threshold", "message_fail"],
        "❌ ROI = {val_str} Kurang Baik, nilai disarankan: {benchmark}",
        "❌ ROI = {val_str} [Kurang Baik, nilai disarankan: {benchmark}]",
    ),
    (
        ["ads", "gmv_ratio_threshold", "message_pass"],
        "✔️ % GMV Iklan / GMV Toko = {pct_str} Sudah Baik",
        "✔️ % GMV Iklan / GMV Toko = {pct_str} [Sudah Baik]",
    ),
    (
        ["ads", "gmv_ratio_threshold", "message_fail"],
        "❌ % GMV Iklan / GMV Toko = {pct_str} Terlalu bergantung terhadap Iklan, nilai disarankan: <{threshold}%",
        "❌ % GMV Iklan / GMV Toko = {pct_str} [Terlalu bergantung terhadap Iklan, nilai disarankan: <{threshold}%]",
    ),
    (
        ["ads", "gmv_ratio_threshold", "message_no_ads"],
        "❌ Iklan tidak aktif sama sekali",
        "❌ [Iklan tidak aktif sama sekali]",
    ),
    (
        ["ads", "cost_ratio_range", "message_pass"],
        "✔️ % Biaya Iklan / GMV Toko = {pct_str} Sudah Baik",
        "✔️ % Biaya Iklan / GMV Toko = {pct_str} [Sudah Baik]",
    ),
    (
        ["ads", "cost_ratio_range", "message_fail"],
        "❌ % Biaya Iklan / GMV Toko = {pct_str} Biaya terlalu tinggi, nilai disarankan: <{threshold}%",
        "❌ % Biaya Iklan / GMV Toko = {pct_str} [Biaya terlalu tinggi, nilai disarankan: <{threshold}%]",
    ),
    (
        ["ads", "cost_ratio_range", "message_no_ads"],
        "❌ Iklan tidak aktif sama sekali",
        "❌ [Iklan tidak aktif sama sekali]",
    ),
    (
        ["ads", "cost_ratio_range", "message_too_minimal"],
        "❌ Penggunaan iklan terlalu minim ({pct_str}). Nilai disarankan: {min}%-{max}%.",
        "❌ [Penggunaan iklan terlalu minim ({pct_str}). Nilai disarankan: {min}%-{max}%.]",
    ),
    # --- Campaign ---
    (
        ["campaign", "participation_pct_threshold", "message_pass"],
        "✔️ % Partisipasi Campaign = {pct_str} Sudah Baik",
        "✔️ % Partisipasi Campaign = {pct_str} [Sudah Baik]",
    ),
    (
        ["campaign", "participation_pct_threshold", "message_fail"],
        "❌ % Partisipasi Campaign = {pct_str} Kurang Baik, nilai disarankan: >{threshold}%",
        "❌ % Partisipasi Campaign = {pct_str} [Kurang Baik, nilai disarankan: >{threshold}%]",
    ),
    (
        ["campaign", "participation_pct_threshold", "message_no_data"],
        "❌Tidak ada Campaign yang dipartisipasikan",
        "❌[Tidak ada Campaign yang dipartisipasikan]",
    ),
    # --- Competition ---
    (
        ["competition", "message_pass"],
        "{name} (Rp. {selling_price}) = ✅kompetitif",
        "{name} (Rp. {selling_price}) = ✅[kompetitif]",
    ),
    (
        ["competition", "message_fail"],
        "{name} (Rp. {selling_price}) = ❌tidak kompetitif (harga kisaran pasaran: Rp. {market_price})",
        "{name} (Rp. {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: Rp. {market_price})]",
    ),
]


def _apply_patches(rules: dict, forward: bool) -> bool:
    """Apply or revert patches. Returns True if any change was made."""
    changed = False
    for path, old_val, new_val in PATCHES:
        node = rules
        for key in path[:-1]:
            node = node.get(key, {})
            if not isinstance(node, dict):
                break
        else:
            leaf_key = path[-1]
            current = node.get(leaf_key)
            expected = old_val if forward else new_val
            replacement = new_val if forward else old_val
            if current == expected:
                node[leaf_key] = replacement
                changed = True
    return changed


def upgrade() -> None:
    conn = op.get_bind()

    rows = conn.execute(
        sa.text("SELECT template, rules FROM scoring_rules")
    ).fetchall()

    for template, raw_rules in rows:
        rules = json.loads(raw_rules) if isinstance(raw_rules, str) else raw_rules

        if _apply_patches(rules, forward=True):
            conn.execute(
                sa.text(
                    "UPDATE scoring_rules "
                    "SET rules = CAST(:rules AS jsonb), "
                    "    version = version + 1 "
                    "WHERE template = :template"
                ),
                {"template": template, "rules": json.dumps(rules)},
            )


def downgrade() -> None:
    conn = op.get_bind()

    rows = conn.execute(
        sa.text("SELECT template, rules FROM scoring_rules")
    ).fetchall()

    for template, raw_rules in rows:
        rules = json.loads(raw_rules) if isinstance(raw_rules, str) else raw_rules

        if _apply_patches(rules, forward=False):
            conn.execute(
                sa.text(
                    "UPDATE scoring_rules "
                    "SET rules = CAST(:rules AS jsonb), "
                    "    version = version - 1 "
                    "WHERE template = :template"
                ),
                {"template": template, "rules": json.dumps(rules)},
            )
