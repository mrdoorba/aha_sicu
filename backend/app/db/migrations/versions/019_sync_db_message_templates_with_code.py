"""Sync DB message templates with code defaults

Migration 012 stored older/simplified message templates that diverge from the
code defaults in scoring.py.  Specifically:

- competition: missing {name} and {selling_price} placeholders
- promo_tools individual_messages.message_fail: missing [brackets]
- products_status product_count: missing [brackets]

This migration patches the DB to match the current code defaults.

Revision ID: 019
Revises: 018
Create Date: 2026-02-26
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "019"
down_revision = "018"
branch_labels = None
depends_on = None

# (json_path, old_value, new_value)
# json_path is a list of keys to traverse into the rules dict.
PATCHES: list[tuple[list[str], str, str]] = [
    # Competition: add product name and selling price
    (
        ["competition", "message_pass"],
        "✅kompetitif",
        "{name} (Rp. {selling_price}) = ✅kompetitif",
    ),
    (
        ["competition", "message_fail"],
        "❌tidak kompetitif (harga kisaran pasaran: Rp. {market_price})",
        "{name} (Rp. {selling_price}) = ❌tidak kompetitif (harga kisaran pasaran: Rp. {market_price})",
    ),
    # Promo tools individual: add brackets
    (
        ["promo_tools", "individual_messages", "message_fail"],
        "❌ {metric} = {pct_str} Kurang Efektif, nilai disarankan: {benchmark}",
        "❌ {metric} = {pct_str} [Kurang Efektif, nilai disarankan: {benchmark}]",
    ),
    # Product count: add brackets
    (
        ["products_status", "product_count", "message_pass"],
        "✔️ Jumlah Produk = {value_int} OK",
        "✔️ Jumlah Produk = {value_int} [OK]",
    ),
    (
        ["products_status", "product_count", "message_fail"],
        "❌ Jumlah Produk = {value_int} NOT OK, nilai disarankan: >={threshold}",
        "❌ Jumlah Produk = {value_int} [NOT OK, nilai disarankan: >={threshold}]",
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
