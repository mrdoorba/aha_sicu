"""Add marketplace column to scoring_rules, evaluation_inputs, and evaluations

Establishes the data foundation for multi-marketplace support (IDR + THB).
- Adds marketplace VARCHAR(2) NOT NULL DEFAULT 'ID' with CHECK constraint to all three tables
- Changes scoring_rules UNIQUE constraint from (template) to (template, marketplace)
- Seeds a TH scoring_rules row with THB-converted six_month_avg_threshold

The fixed IDR→THB conversion rate (0.0019) is used solely for initial threshold
seeding. Admins may adjust the THB thresholds after migration.

Revision ID: 026
Revises: 025
Create Date: 2026-03-17
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "026"
down_revision = "025"
branch_labels = None
depends_on = None

# Fixed conversion rate for initial THB threshold seeding (not a live rate)
IDR_TO_THB_RATE = 0.0019


def upgrade() -> None:
    conn = op.get_bind()

    # -----------------------------------------------------------------------
    # 1. scoring_rules: add marketplace column, update constraints, seed TH
    # -----------------------------------------------------------------------

    # 1a. Add marketplace column with default 'ID' (backfills all existing rows)
    op.add_column(
        "scoring_rules",
        sa.Column("marketplace", sa.String(2), server_default="ID", nullable=False),
    )

    # 1b. Add CHECK constraint
    op.execute(
        "ALTER TABLE scoring_rules ADD CONSTRAINT chk_scoring_rules_marketplace "
        "CHECK (marketplace IN ('ID', 'TH'))"
    )

    # 1c. Drop old UNIQUE constraint on template (from migration 010)
    #     and create new UNIQUE on (template, marketplace)
    op.execute(
        "ALTER TABLE scoring_rules DROP CONSTRAINT IF EXISTS scoring_rules_template_key"
    )
    op.execute(
        "ALTER TABLE scoring_rules ADD CONSTRAINT uq_scoring_rules_template_marketplace "
        "UNIQUE (template, marketplace)"
    )

    # 1d. Seed the TH row by copying the existing 'default' ID row
    row = conn.execute(
        sa.text("SELECT rules, version FROM scoring_rules WHERE template = 'default' AND marketplace = 'ID'")
    ).fetchone()

    if row is not None:
        rules = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        version = row[1]

        # Convert only currency-denominated thresholds
        if "business" in rules and "six_month_avg_threshold" in rules["business"]:
            idr_val = rules["business"]["six_month_avg_threshold"]["threshold"]
            rules["business"]["six_month_avg_threshold"]["threshold"] = round(
                idr_val * IDR_TO_THB_RATE, 2
            )

        conn.execute(
            sa.text(
                "INSERT INTO scoring_rules (template, marketplace, rules, version, updated_at) "
                "VALUES (:template, :marketplace, CAST(:rules AS jsonb), :version, NOW())"
            ),
            {
                "template": "default",
                "marketplace": "TH",
                "rules": json.dumps(rules),
                "version": version,
            },
        )

    # -----------------------------------------------------------------------
    # 2. evaluation_inputs: add marketplace column
    # -----------------------------------------------------------------------

    op.add_column(
        "evaluation_inputs",
        sa.Column("marketplace", sa.String(2), server_default="ID", nullable=False),
    )
    op.execute(
        "ALTER TABLE evaluation_inputs ADD CONSTRAINT chk_evaluation_inputs_marketplace "
        "CHECK (marketplace IN ('ID', 'TH'))"
    )

    # -----------------------------------------------------------------------
    # 3. evaluations: add marketplace column
    # -----------------------------------------------------------------------

    op.add_column(
        "evaluations",
        sa.Column("marketplace", sa.String(2), server_default="ID", nullable=False),
    )
    op.execute(
        "ALTER TABLE evaluations ADD CONSTRAINT chk_evaluations_marketplace "
        "CHECK (marketplace IN ('ID', 'TH'))"
    )


def downgrade() -> None:
    # -----------------------------------------------------------------------
    # 3. evaluations: remove marketplace
    # -----------------------------------------------------------------------
    op.execute("ALTER TABLE evaluations DROP CONSTRAINT IF EXISTS chk_evaluations_marketplace")
    op.drop_column("evaluations", "marketplace")

    # -----------------------------------------------------------------------
    # 2. evaluation_inputs: remove marketplace
    # -----------------------------------------------------------------------
    op.execute(
        "ALTER TABLE evaluation_inputs DROP CONSTRAINT IF EXISTS chk_evaluation_inputs_marketplace"
    )
    op.drop_column("evaluation_inputs", "marketplace")

    # -----------------------------------------------------------------------
    # 1. scoring_rules: remove TH row, restore original UNIQUE, drop marketplace
    # -----------------------------------------------------------------------

    # 1a. Delete TH rows
    op.execute("DELETE FROM scoring_rules WHERE marketplace = 'TH'")

    # 1b. Drop new UNIQUE, restore original
    op.execute(
        "ALTER TABLE scoring_rules DROP CONSTRAINT IF EXISTS uq_scoring_rules_template_marketplace"
    )
    op.execute(
        "ALTER TABLE scoring_rules ADD CONSTRAINT scoring_rules_template_key UNIQUE (template)"
    )

    # 1c. Drop CHECK and column
    op.execute(
        "ALTER TABLE scoring_rules DROP CONSTRAINT IF EXISTS chk_scoring_rules_marketplace"
    )
    op.drop_column("scoring_rules", "marketplace")
