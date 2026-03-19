"""Create audit_log table for administrative action tracking.

Append-only table — no foreign keys to users (must survive user deletions).
Addresses AEGIS finding F-05-001.

Revision ID: 029
Revises: 028
Create Date: 2026-03-19
"""

import sqlalchemy as sa
from alembic import op

revision = "029"
down_revision = "028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text("""
            CREATE TABLE audit_log (
                id BIGSERIAL PRIMARY KEY,
                action VARCHAR(100) NOT NULL,
                actor_id INTEGER NOT NULL,
                actor_email VARCHAR(255) NOT NULL,
                target_type VARCHAR(50) NOT NULL,
                target_id VARCHAR(255) NOT NULL,
                details JSONB,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
    )
    op.execute(sa.text("CREATE INDEX idx_audit_log_action ON audit_log(action)"))
    op.execute(sa.text("CREATE INDEX idx_audit_log_actor ON audit_log(actor_id)"))
    op.execute(
        sa.text("CREATE INDEX idx_audit_log_target ON audit_log(target_type, target_id)")
    )
    op.execute(sa.text("CREATE INDEX idx_audit_log_created ON audit_log(created_at)"))


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS audit_log"))
