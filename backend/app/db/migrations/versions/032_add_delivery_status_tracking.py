"""Expand email_history status to delivery lifecycle values, add last_event_at.

Adds webhook-driven delivery statuses (delivered, bounced, opened, etc.)
and a last_event_at column for tracking the most recent Brevo event.
Also indexes message_id for fast webhook lookups.

Revision ID: 032
Revises: 031
Create Date: 2026-03-20
"""

import sqlalchemy as sa
from alembic import op

revision = "032"
down_revision = "031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing CHECK constraint (PostgreSQL auto-names it {table}_{column}_check)
    op.execute(
        sa.text(
            "ALTER TABLE email_history DROP CONSTRAINT IF EXISTS email_history_status_check"
        )
    )
    # Add expanded CHECK constraint with delivery lifecycle statuses
    op.execute(
        sa.text(
            "ALTER TABLE email_history ADD CONSTRAINT email_history_status_check "
            "CHECK (status IN ('sent', 'failed', 'delivered', 'bounced', 'deferred', "
            "'opened', 'clicked', 'spam', 'blocked', 'invalid'))"
        )
    )
    # Add last_event_at column (nullable — NULL until first webhook event)
    op.execute(
        sa.text(
            "ALTER TABLE email_history ADD COLUMN last_event_at TIMESTAMPTZ"
        )
    )
    # Index message_id for fast webhook lookups (partial — only non-NULL)
    op.execute(
        sa.text(
            "CREATE INDEX idx_email_history_message_id "
            "ON email_history (message_id) WHERE message_id IS NOT NULL"
        )
    )


def downgrade() -> None:
    # Drop message_id index
    op.execute(sa.text("DROP INDEX IF EXISTS idx_email_history_message_id"))
    # Drop last_event_at column
    op.execute(
        sa.text("ALTER TABLE email_history DROP COLUMN IF EXISTS last_event_at")
    )
    # Restore original CHECK constraint (will fail if rows have new status values — intentional)
    op.execute(
        sa.text(
            "ALTER TABLE email_history DROP CONSTRAINT IF EXISTS email_history_status_check"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE email_history ADD CONSTRAINT email_history_status_check "
            "CHECK (status IN ('sent', 'failed'))"
        )
    )
