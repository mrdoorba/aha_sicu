"""Update TH approved closing-message consultation link

Replaces the approved verdict consultation link in TH scoring_rules rows so
TH brands use th-bd2.ahacommerce.net while ID brands keep cal-bd2.ahacommerce.net.

Revision ID: 037
Revises: 036
Create Date: 2026-04-30
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "037"
down_revision = "036"
branch_labels = None
depends_on = None

OLD_LINK = "cal-bd2.ahacommerce.net"
NEW_LINK = "th-bd2.ahacommerce.net"


def _update_link(from_link: str, to_link: str) -> None:
    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            "SELECT template, rules "
            "FROM scoring_rules "
            "WHERE marketplace = 'TH'"
        )
    ).fetchall()

    for row in rows:
        template = row[0]
        rules = json.loads(row[1]) if isinstance(row[1], str) else row[1]

        closing = rules.get("interpretation", {}).get("closing_messages", {})
        message = closing.get("✔️")
        if not isinstance(message, str):
            continue

        updated = message.replace(from_link, to_link)
        if updated == message:
            continue

        closing["✔️"] = updated

        conn.execute(
            sa.text(
                "UPDATE scoring_rules "
                "SET rules = CAST(:rules AS jsonb), "
                "    version = version + 1 "
                "WHERE template = :template AND marketplace = 'TH'"
            ),
            {"template": template, "rules": json.dumps(rules)},
        )


def upgrade() -> None:
    _update_link(OLD_LINK, NEW_LINK)


def downgrade() -> None:
    _update_link(NEW_LINK, OLD_LINK)
