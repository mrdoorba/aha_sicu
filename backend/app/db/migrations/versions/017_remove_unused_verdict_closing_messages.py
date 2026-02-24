"""Remove unused verdict closing messages (⭕️ and empty string)

Drops the ⭕️ (Special) and "" (empty) keys from
interpretation.closing_messages in all scoring_rules rows.

Revision ID: 017
Revises: 016
Create Date: 2026-02-24
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None

KEYS_TO_REMOVE = ("⭕️", "")


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

        closing = (
            rules.get("interpretation", {}).get("closing_messages")
        )
        if not closing:
            continue

        changed = False
        for key in KEYS_TO_REMOVE:
            if key in closing:
                del closing[key]
                changed = True

        if changed:
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

    restore = {
        "⭕️": "",
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
    }

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
        closing.update(restore)

        conn.execute(
            sa.text(
                "UPDATE scoring_rules "
                "SET rules = CAST(:rules AS jsonb), "
                "    version = version - 1 "
                "WHERE template = :template"
            ),
            {"template": template, "rules": json.dumps(rules)},
        )
