"""Lower the ads GMV ratio threshold from 84% to 74%

Tightens ads.gmv_ratio_threshold.threshold in the scoring_rules JSONB column
for every template and marketplace (ID and TH). A store whose ad GMV sits
between 74% and 84% of store GMV now fails row 51 and loses its 5 points.

Only rows still holding the old 84.0 are touched, so a threshold someone
edited by hand from the Rules page is left alone.

Revision ID: 039
Revises: 038
Create Date: 2026-07-29
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "039"
down_revision = "038"
branch_labels = None
depends_on = None

# (json_path, old_value, new_value)
PATCHES: list[tuple[list[str], float, float]] = [
    (["ads", "gmv_ratio_threshold", "threshold"], 84.0, 74.0),
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


def _patch_all_rows(forward: bool) -> None:
    conn = op.get_bind()

    rows = conn.execute(
        sa.text("SELECT template, marketplace, rules FROM scoring_rules")
    ).fetchall()

    version_step = "version + 1" if forward else "version - 1"

    for template, marketplace, raw_rules in rows:
        rules = json.loads(raw_rules) if isinstance(raw_rules, str) else raw_rules

        if _apply_patches(rules, forward=forward):
            conn.execute(
                sa.text(
                    "UPDATE scoring_rules "
                    "SET rules = CAST(:rules AS jsonb), "
                    f"    version = {version_step} "
                    "WHERE template = :template AND marketplace = :marketplace"
                ),
                {"template": template, "marketplace": marketplace, "rules": json.dumps(rules)},
            )


def upgrade() -> None:
    _patch_all_rows(forward=True)


def downgrade() -> None:
    _patch_all_rows(forward=False)
