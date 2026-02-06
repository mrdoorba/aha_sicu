"""Create sync_status table

Revision ID: 003
Revises: 002
Create Date: 2026-02-05
"""

from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE sync_status (
            id SERIAL PRIMARY KEY,
            started_at TIMESTAMPTZ NOT NULL,
            completed_at TIMESTAMPTZ,
            success BOOLEAN,
            brands_synced INTEGER DEFAULT 0,
            error_message TEXT,
            CONSTRAINT sync_status_completed_has_success CHECK (
                completed_at IS NULL OR success IS NOT NULL
            )
        );

        CREATE INDEX idx_sync_status_started_at ON sync_status(started_at DESC);
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS idx_sync_status_started_at;
        DROP TABLE IF EXISTS sync_status;
    """)
