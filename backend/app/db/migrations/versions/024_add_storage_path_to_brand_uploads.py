"""Add storage_path column to brand_uploads

Stores the GCS/local object path so files can be downloaded later.

Revision ID: 024
Revises: 023
Create Date: 2026-03-10
"""

import sqlalchemy as sa
from alembic import op

revision = "024"
down_revision = "023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "brand_uploads",
        sa.Column("storage_path", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("brand_uploads", "storage_path")
