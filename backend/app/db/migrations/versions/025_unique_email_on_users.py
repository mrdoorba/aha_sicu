"""Add unique constraint on users.email

Prevents duplicate user rows when Firebase emulator UIDs change
across container rebuilds. The create_user query now uses
ON CONFLICT (email) DO UPDATE to update the firebase_uid.

Revision ID: 025
Revises: 024
Create Date: 2026-03-16
"""

from alembic import op

revision = "025"
down_revision = "024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Clean up any existing duplicates — keep the most recent (highest id)
    op.execute("""
        DELETE FROM users a USING users b
        WHERE a.email = b.email AND a.id < b.id;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'users_email_key'
            ) THEN
                ALTER TABLE users ADD CONSTRAINT users_email_key UNIQUE (email);
            END IF;
        END$$;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE users
            DROP CONSTRAINT IF EXISTS users_email_key;
    """)
