"""Add marketing category to scoring_rules JSONB

Adds configurable marketing constants (floor, base_subtraction, upper_limit_base,
fashion_adjustment, minimum_threshold, display_max, display_min) to the rules
JSONB for both Fashion and Non-Fashion templates.

Revision ID: 011
Revises: 010
Create Date: 2026-02-12
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None

FASHION_MARKETING = {
    "floor": {"value": 0.15},
    "base_subtraction": {"value": 0.03},
    "upper_limit_base": {"value": 0.20},
    "fashion_adjustment": {"value": 0.05},
    "minimum_threshold": {"value": 0.10},
    "display_max": {"value": 0.25},
    "display_min": {"value": 0.10},
}

NON_FASHION_MARKETING = {
    "floor": {"value": 0.12},
    "base_subtraction": {"value": 0.03},
    "upper_limit_base": {"value": 0.20},
    "fashion_adjustment": {"value": 0.0},
    "minimum_threshold": {"value": 0.10},
    "display_max": {"value": 0.25},
    "display_min": {"value": 0.10},
}


def upgrade() -> None:
    conn = op.get_bind()

    # Add marketing category to Fashion template
    conn.execute(
        sa.text(
            "UPDATE scoring_rules "
            "SET rules = jsonb_set(rules, '{marketing}', CAST(:marketing AS jsonb)), "
            "    version = version + 1 "
            "WHERE template = :template"
        ),
        {"template": "fashion", "marketing": json.dumps(FASHION_MARKETING)},
    )

    # Add marketing category to Non-Fashion template
    conn.execute(
        sa.text(
            "UPDATE scoring_rules "
            "SET rules = jsonb_set(rules, '{marketing}', CAST(:marketing AS jsonb)), "
            "    version = version + 1 "
            "WHERE template = :template"
        ),
        {"template": "non_fashion", "marketing": json.dumps(NON_FASHION_MARKETING)},
    )


def downgrade() -> None:
    conn = op.get_bind()

    # Remove marketing category from both templates
    conn.execute(
        sa.text(
            "UPDATE scoring_rules "
            "SET rules = rules - 'marketing', "
            "    version = version - 1 "
            "WHERE template IN (:t1, :t2)"
        ),
        {"t1": "fashion", "t2": "non_fashion"},
    )
