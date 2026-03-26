"""Add ❌ Stock verdict closing message to scoring_rules

Adds the "❌ Stock" key to interpretation.closing_messages in all
scoring_rules rows (default, fashion, non_fashion).

Revision ID: 036
Revises: 035
Create Date: 2026-03-26
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "036"
down_revision = "035"
branch_labels = None
depends_on = None

STOCK_MESSAGE = (
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
)


def upgrade() -> None:
    conn = op.get_bind()

    for template in ("default", "fashion", "non_fashion"):
        row = conn.execute(
            sa.text("SELECT rules FROM scoring_rules WHERE template = :t"),
            {"t": template},
        ).fetchone()
        if row is None:
            continue

        rules = json.loads(row[0]) if isinstance(row[0], str) else row[0]

        if "interpretation" not in rules:
            rules["interpretation"] = {}
        closing = rules["interpretation"].setdefault("closing_messages", {})
        closing["❌ Stock"] = STOCK_MESSAGE

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

    for template in ("default", "fashion", "non_fashion"):
        row = conn.execute(
            sa.text("SELECT rules FROM scoring_rules WHERE template = :t"),
            {"t": template},
        ).fetchone()
        if row is None:
            continue

        rules = json.loads(row[0]) if isinstance(row[0], str) else row[0]

        closing = rules.get("interpretation", {}).get("closing_messages")
        if closing and "❌ Stock" in closing:
            del closing["❌ Stock"]

        conn.execute(
            sa.text(
                "UPDATE scoring_rules "
                "SET rules = CAST(:rules AS jsonb), "
                "    version = version - 1 "
                "WHERE template = :template"
            ),
            {"template": template, "rules": json.dumps(rules)},
        )
