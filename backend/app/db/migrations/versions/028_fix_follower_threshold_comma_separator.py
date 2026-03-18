"""Fix follower threshold comma separator in message templates

Updates the followers message_fail template from >50.000 (dot separator)
to >50,000 (comma separator) in the scoring_rules JSONB column.

Revision ID: 028
Revises: 027
Create Date: 2026-03-18
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "028"
down_revision = "027"
branch_labels = None
depends_on = None

# (json_path, old_value, new_value)
PATCHES: list[tuple[list[str], str, str]] = [
    (
        ["visitors", "followers", "message_fail"],
        "❌ Total Pengikut = {val_str} [Kurang Baik, nilai disarankan: >50.000]",
        "❌ Total Pengikut = {val_str} [Kurang Baik, nilai disarankan: >50,000]",
    ),
]


def _apply_patches(rules: dict, forward: bool = True) -> bool:
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
        sa.text("SELECT template, marketplace, rules FROM scoring_rules")
    ).fetchall()

    for template, marketplace, raw_rules in rows:
        rules = json.loads(raw_rules) if isinstance(raw_rules, str) else raw_rules

        if _apply_patches(rules, forward=True):
            conn.execute(
                sa.text(
                    "UPDATE scoring_rules "
                    "SET rules = CAST(:rules AS jsonb), "
                    "    version = version + 1 "
                    "WHERE template = :template AND marketplace = :marketplace"
                ),
                {"template": template, "marketplace": marketplace, "rules": json.dumps(rules)},
            )


def downgrade() -> None:
    conn = op.get_bind()

    rows = conn.execute(
        sa.text("SELECT template, marketplace, rules FROM scoring_rules")
    ).fetchall()

    for template, marketplace, raw_rules in rows:
        rules = json.loads(raw_rules) if isinstance(raw_rules, str) else raw_rules

        if _apply_patches(rules, forward=False):
            conn.execute(
                sa.text(
                    "UPDATE scoring_rules "
                    "SET rules = CAST(:rules AS jsonb), "
                    "    version = version - 1 "
                    "WHERE template = :template AND marketplace = :marketplace"
                ),
                {"template": template, "marketplace": marketplace, "rules": json.dumps(rules)},
            )
