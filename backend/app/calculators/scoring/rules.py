"""Default scoring rules, promo tool configuration, and constants."""

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
            "message_pass": "✔️ Penjualan = {currency} {idr_val} [Meningkat {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: {currency} {idr_avg}]",
            "message_fail": "❌ Penjualan = {currency} {idr_val} [Menurun {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: {currency} {idr_avg}]",
            "message_fail_severe": "\n❗️ Potensi peningkatan harga jual signifikan atau terdapat event abnormal.",
        },
        "six_month_avg_threshold": {"threshold": 100000000, "points_above": 15, "points_below": 10, "comparison": "gt"},
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
            "message_fail": "❌ Total Pengikut = {val_str} [Kurang Baik, nilai disarankan: >50,000]",
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
        "message_pass": "{name} ({currency} {selling_price}) = ✅[kompetitif]",
        "message_fail": "{name} ({currency} {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: {currency} {market_price})]",
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
            "❌ Stock": (
                "Kami sangat yakin bahwa sistem AHA dapat memberikan nilai tambah kepada toko {store_name} "
                "secara langsung. Namun, untuk memastikan kerja sama ini berjalan optimal bagi kedua belah "
                "pihak, kami juga perlu mempertimbangkan kesiapan operasional dari sisi brand.\n\n"
                "Berdasarkan evaluasi kami, saat ini jumlah stok per varian masih tergolong minim "
                "(di bawah 24 pcs/varian), sehingga dikhawatirkan dapat membatasi performa penjualan "
                "dan efektivitas strategi yang dijalankan oleh AHA.\n\n"
                "Oleh karena itu, dengan berat hati, kami belum dapat bekerja-sama dengan {store_name} "
                "di tahap sekarang ini.\n\n"
                "Namun, apabila ke depannya stok per varian sudah dapat ditingkatkan ke level yang lebih "
                "ideal (minimal 24 pcs/varian), kami sangat terbuka untuk kembali melanjutkan pembahasan "
                "kerja sama ini."
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
