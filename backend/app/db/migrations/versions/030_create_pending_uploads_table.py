"""Create pending_uploads table for cross-instance upload state.

Replaces in-memory _pending_uploads dict with database-backed state
so the two-step upload flow works across multiple Cloud Run instances.
Addresses AEGIS finding F-08-001.

Revision ID: 030
Revises: 029
Create Date: 2026-03-19
"""

import sqlalchemy as sa
from alembic import op

revision = "030"
down_revision = "029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text("""
            CREATE TABLE pending_uploads (
                upload_id TEXT PRIMARY KEY,
                brand_id INTEGER NOT NULL REFERENCES brand_vp_data(id) ON DELETE CASCADE,
                file_type TEXT NOT NULL,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                object_name TEXT NOT NULL,
                expires_at TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
    )
    op.execute(
        sa.text(
            "CREATE INDEX idx_pending_uploads_expires_at ON pending_uploads (expires_at)"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS pending_uploads"))
