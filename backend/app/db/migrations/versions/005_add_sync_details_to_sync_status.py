"""Add sync_details JSONB column to sync_status table

Stores per-sheet breakdown (VP/Meeting results) so that granular sync
information is not lost when persisting to the database.

Revision ID: 005
Revises: 004
Create Date: 2026-02-06
"""

from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE sync_status
        ADD COLUMN sync_details JSONB;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE sync_status
        DROP COLUMN IF EXISTS sync_details;
    """)
