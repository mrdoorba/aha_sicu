"""Replace hardcoded IDR with {currency} placeholder in message templates

Updates 4 message template strings in the scoring_rules JSONB to use
the {currency} placeholder instead of the hardcoded "IDR" prefix. This
allows the scoring engine to inject the correct currency code (IDR/THB)
at runtime based on the marketplace parameter.

Revision ID: 027
Revises: 026
Create Date: 2026-03-17
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "027"
down_revision = "026"
branch_labels = None
depends_on = None

# (json_path, old_value, new_value)
PATCHES: list[tuple[list[str], str, str]] = [
    (
        ["business", "monthly_sales_trend", "message_pass"],
        "✔️ Penjualan = IDR {idr_val} [Meningkat {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}]",
        "✔️ Penjualan = {currency} {idr_val} [Meningkat {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: {currency} {idr_avg}]",
    ),
    (
        ["business", "monthly_sales_trend", "message_fail"],
        "❌ Penjualan = IDR {idr_val} [Menurun {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: IDR {idr_avg}]",
        "❌ Penjualan = {currency} {idr_val} [Menurun {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: {currency} {idr_avg}]",
    ),
    (
        ["competition", "message_pass"],
        "{name} (IDR {selling_price}) = ✅[kompetitif]",
        "{name} ({currency} {selling_price}) = ✅[kompetitif]",
    ),
    (
        ["competition", "message_fail"],
        "{name} (IDR {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: IDR {market_price})]",
        "{name} ({currency} {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: {currency} {market_price})]",
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
