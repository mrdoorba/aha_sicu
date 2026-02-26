"""Remove content category from scoring_rules

The content category (goodQuality/needsImprovement) was removed from the
application but the seed data from migration 010 persists in the database.
This migration strips the "content" key from the rules JSONB column.

Revision ID: 018
Revises: 017
Create Date: 2026-02-26
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None

CONTENT_RULES = {
    "quality_ratio": {"threshold": 95.0, "comparison": "gte", "info_only": True},
}


def upgrade() -> None:
    conn = op.get_bind()

    rows = conn.execute(
        sa.text("SELECT template, rules FROM scoring_rules")
    ).fetchall()

    for template, raw_rules in rows:
        rules = json.loads(raw_rules) if isinstance(raw_rules, str) else raw_rules

        if "content" not in rules:
            continue

        del rules["content"]

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

        if "content" in rules:
            continue

        rules["content"] = CONTENT_RULES

        conn.execute(
            sa.text(
                "UPDATE scoring_rules "
                "SET rules = CAST(:rules AS jsonb), "
                "    version = version - 1 "
                "WHERE template = :template"
            ),
            {"template": template, "rules": json.dumps(rules)},
        )
