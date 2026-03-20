"""Create email_history table for tracking sent evaluation emails.

Stores a record per email send (success or failure) with Brevo message ID,
so leaders/admins can audit what was dispatched and when.

Revision ID: 031
Revises: 030
Create Date: 2026-03-20
"""

import sqlalchemy as sa
from alembic import op

revision = "031"
down_revision = "030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text("""
            CREATE TABLE email_history (
                id SERIAL PRIMARY KEY,
                evaluation_id INTEGER NOT NULL REFERENCES evaluations(id) ON DELETE RESTRICT,
                sender_email VARCHAR(255) NOT NULL,
                recipient_email VARCHAR(255) NOT NULL,
                cc_emails TEXT[],
                bcc_emails TEXT[],
                subject VARCHAR(500) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'sent'
                    CHECK (status IN ('sent', 'failed')),
                message_id VARCHAR(255),
                error_detail TEXT,
                sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
    )
    op.execute(
        sa.text(
            "CREATE INDEX idx_email_history_evaluation_id ON email_history (evaluation_id)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX idx_email_history_sent_at ON email_history (sent_at DESC)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX idx_email_history_status ON email_history (status)"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS email_history"))
