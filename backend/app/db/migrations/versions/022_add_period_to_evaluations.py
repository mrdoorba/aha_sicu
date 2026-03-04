"""Add period column to evaluations table

Stores the evaluation period (e.g., "Jan 2026") selected during scoring.

Revision ID: 022
Revises: 021
Create Date: 2026-03-04
"""

import sqlalchemy as sa
from alembic import op

revision = "022"
down_revision = "021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "evaluations",
        sa.Column("period", sa.String(50), server_default="", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("evaluations", "period")
