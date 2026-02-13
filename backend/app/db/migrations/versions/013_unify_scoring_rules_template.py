"""Unify scoring rules: merge fashion/non_fashion into single 'default' template

The BD team confirmed there's no need for separate fashion and non-fashion scoring
rule templates. Unified thresholds:
  - Conversion rate: 3.0% (was 2.0% fashion, 3.0% non-fashion)
  - ROI: 9.0 (was 8.0 fashion, 9.0 non-fashion)
  - Marketing floor: 0.12 (non-fashion value), with floor_fashion: 0.15
  - Fashion adjustment: 0.05 (kept for marketing calc)

The fashion/non-fashion radio button is kept ONLY for the marketing budget
calculation (floor 12% vs 15%, adjustment 0% vs 5%).

Revision ID: 013
Revises: 012
Create Date: 2026-02-13
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Read the non_fashion row as the base (it already has conv=3.0, ROI=9.0,
    # floor=0.12, fashion_adjustment=0.0)
    row = conn.execute(
        sa.text("SELECT rules, version FROM scoring_rules WHERE template = :t"),
        {"t": "non_fashion"},
    ).fetchone()
    if row is None:
        return

    rules = json.loads(row[0]) if isinstance(row[0], str) else row[0]
    version = row[1]

    # Add floor_fashion so both floor values are configurable from one template
    if "marketing" in rules:
        rules["marketing"]["floor_fashion"] = {"value": 0.15}
        # Ensure fashion_adjustment is 0.05 (for when is_fashion is True)
        rules["marketing"]["fashion_adjustment"] = {"value": 0.05}

    # Insert the unified "default" row
    conn.execute(
        sa.text(
            "INSERT INTO scoring_rules (template, rules, version, updated_at) "
            "VALUES (:template, CAST(:rules AS jsonb), :version, NOW())"
        ),
        {"template": "default", "rules": json.dumps(rules), "version": version + 1},
    )

    # Delete the old rows
    conn.execute(
        sa.text("DELETE FROM scoring_rules WHERE template IN ('fashion', 'non_fashion')")
    )


def downgrade() -> None:
    conn = op.get_bind()

    # Read the default row
    row = conn.execute(
        sa.text("SELECT rules, version FROM scoring_rules WHERE template = :t"),
        {"t": "default"},
    ).fetchone()
    if row is None:
        return

    rules = json.loads(row[0]) if isinstance(row[0], str) else row[0]
    version = row[1]

    # Build fashion rules: conv=2.0, ROI=8.0, floor=0.15, adj=0.05
    fashion_rules = json.loads(json.dumps(rules))
    if "business" in fashion_rules and "conversion_rate" in fashion_rules["business"]:
        fashion_rules["business"]["conversion_rate"]["threshold"] = 2.0
    if "ads" in fashion_rules and "roi_threshold" in fashion_rules["ads"]:
        fashion_rules["ads"]["roi_threshold"]["threshold"] = 8.0
    if "marketing" in fashion_rules:
        fashion_rules["marketing"]["floor"] = {"value": 0.15}
        fashion_rules["marketing"]["fashion_adjustment"] = {"value": 0.05}
        fashion_rules["marketing"].pop("floor_fashion", None)

    # Build non_fashion rules: conv=3.0, ROI=9.0, floor=0.12, adj=0.0
    non_fashion_rules = json.loads(json.dumps(rules))
    if "marketing" in non_fashion_rules:
        non_fashion_rules["marketing"]["floor"] = {"value": 0.12}
        non_fashion_rules["marketing"]["fashion_adjustment"] = {"value": 0.0}
        non_fashion_rules["marketing"].pop("floor_fashion", None)

    # Insert the old rows back
    for template, tmpl_rules in [("fashion", fashion_rules), ("non_fashion", non_fashion_rules)]:
        conn.execute(
            sa.text(
                "INSERT INTO scoring_rules (template, rules, version, updated_at) "
                "VALUES (:template, CAST(:rules AS jsonb), :version, NOW())"
            ),
            {"template": template, "rules": json.dumps(tmpl_rules), "version": version},
        )

    # Delete the default row
    conn.execute(
        sa.text("DELETE FROM scoring_rules WHERE template = 'default'")
    )
