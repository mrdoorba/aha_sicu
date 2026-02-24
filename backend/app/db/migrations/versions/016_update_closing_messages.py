"""Update G75 closing messages with full templates and {store_name} placeholder

Replaces the short closing messages with the full messages that match the
spreadsheet formula, using {store_name} as a runtime placeholder.

Revision ID: 016
Revises: 015
Create Date: 2026-02-24
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None

NEW_CLOSING_MESSAGES: dict = {
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
    "": (
        "Kami telah melakukan analisa pada toko {store_name} secara langsung, namun kami perlu "
        "mempertimbangkan potensi keuntungan bagi kedua pihak untuk kerja-sama ini.\n\n"
        "Oleh karena tingkat performa toko {store_name} sudah cukup baik, maka kami belum yakin "
        "apabila sistem AHA dapat memberikan dampak peningkatan omset yang signifikan.\n\n"
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
    "⭕️": "",
}

OLD_CLOSING_MESSAGES: dict = {
    "✔️": "Berdasarkan data analisa diatas, potensi toko masih belum maksimal. Kami mengundang untuk berdiskusi mengenai potensi optimisasi toko melalui link berikut: cal-bd2.ahacommerce.net",
    "❌": "Berdasarkan data analisa diatas, perlu mempertimbangkan potensi keuntungan. Silakan cek AHA Coventures: bit.ly/AHACoventures",
    "❌ Non Mall": "Toko belum berstatus Mall. AHA dapat membantu proses pengajuan Shopee Mall. Persyaratan: HAKI (Merek Terdaftar), NIB, dan dokumen legalitas usaha.",
    "❌ No Brand": "Toko bukan merupakan toko yang memiliki brand sendiri. Terima kasih atas waktunya, semoga sukses selalu.",
    "": "Performa toko sudah cukup baik. Terima kasih atas waktunya, semoga sukses selalu.",
    "❌ Opex": "Tingkat keterlambatan cukup tinggi. Disarankan untuk memperbaiki pengiriman (<2%) dan masa pengemasan (<1 hari) terlebih dahulu.",
    "⭕️": "",
}


def upgrade() -> None:
    conn = op.get_bind()

    for template in ("fashion", "non_fashion"):
        row = conn.execute(
            sa.text("SELECT rules FROM scoring_rules WHERE template = :t"),
            {"t": template},
        ).fetchone()
        if row is None:
            continue

        rules = json.loads(row[0]) if isinstance(row[0], str) else row[0]

        if "interpretation" not in rules:
            rules["interpretation"] = {}
        rules["interpretation"]["closing_messages"] = NEW_CLOSING_MESSAGES

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

    for template in ("fashion", "non_fashion"):
        row = conn.execute(
            sa.text("SELECT rules FROM scoring_rules WHERE template = :t"),
            {"t": template},
        ).fetchone()
        if row is None:
            continue

        rules = json.loads(row[0]) if isinstance(row[0], str) else row[0]

        if "interpretation" in rules:
            rules["interpretation"]["closing_messages"] = OLD_CLOSING_MESSAGES

        conn.execute(
            sa.text(
                "UPDATE scoring_rules "
                "SET rules = CAST(:rules AS jsonb), "
                "    version = version - 1 "
                "WHERE template = :template"
            ),
            {"template": template, "rules": json.dumps(rules)},
        )
