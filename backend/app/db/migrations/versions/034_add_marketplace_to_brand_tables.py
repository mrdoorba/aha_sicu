"""Add marketplace column to brand_vp_data and brand_meeting_data

Extends multi-marketplace support to brand data tables. Follows the
same pattern as migration 026 (scoring_rules, evaluations).

Revision ID: 034
Revises: 033
Create Date: 2026-03-25
"""

import sqlalchemy as sa
from alembic import op

revision = "034"
down_revision = "033"
branch_labels = None
depends_on = None

_TABLES = ["brand_vp_data", "brand_meeting_data"]


def upgrade() -> None:
    for table in _TABLES:
        # 1. Add marketplace column (backfills existing rows with 'ID')
        op.add_column(
            table,
            sa.Column("marketplace", sa.String(2), server_default="ID", nullable=False),
        )

        # 2. Add CHECK constraint
        op.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT chk_{table}_marketplace "
            f"CHECK (marketplace IN ('ID', 'TH'))"
        )

        # 3. Drop old UNIQUE on brand_name, create new on (brand_name, marketplace)
        op.execute(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {table}_brand_name_key"
        )
        op.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT uq_{table}_brand_name_marketplace "
            f"UNIQUE (brand_name, marketplace)"
        )

        # 4. Add index on marketplace for filtering
        op.execute(
            f"CREATE INDEX idx_{table}_marketplace ON {table} (marketplace)"
        )


def downgrade() -> None:
    for table in reversed(_TABLES):
        # Drop marketplace index
        op.execute(f"DROP INDEX IF EXISTS idx_{table}_marketplace")

        # Restore original UNIQUE on brand_name
        op.execute(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS uq_{table}_brand_name_marketplace"
        )
        # Delete TH rows first to avoid unique violation
        op.execute(f"DELETE FROM {table} WHERE marketplace = 'TH'")
        op.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT {table}_brand_name_key UNIQUE (brand_name)"
        )

        # Drop CHECK and column
        op.execute(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS chk_{table}_marketplace"
        )
        op.drop_column(table, "marketplace")
