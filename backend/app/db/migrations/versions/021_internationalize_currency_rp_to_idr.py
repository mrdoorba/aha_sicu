"""Internationalize currency: Rp. → IDR in competition message templates

Replaces Indonesian "Rp." prefix with international "IDR" in competition
scoring message templates stored in the database.

Revision ID: 021
Revises: 020
Create Date: 2026-03-04
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "021"
down_revision = "020"
branch_labels = None
depends_on = None

# (json_path, old_value, new_value)
PATCHES: list[tuple[list[str], str, str]] = [
    (
        ["competition", "message_pass"],
        "{name} (Rp. {selling_price}) = ✅[kompetitif]",
        "{name} (IDR {selling_price}) = ✅[kompetitif]",
    ),
    (
        ["competition", "message_fail"],
        "{name} (Rp. {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: Rp. {market_price})]",
        "{name} (IDR {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: IDR {market_price})]",
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
