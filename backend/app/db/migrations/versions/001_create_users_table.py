"""Create users table

Revision ID: 001
Revises:
Create Date: 2026-02-05
"""

from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            firebase_uid VARCHAR(128) UNIQUE NOT NULL,
            email VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'member' CHECK (role IN ('member', 'leader', 'admin')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            last_login TIMESTAMPTZ
        );

        CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS idx_users_firebase_uid;
        DROP TABLE IF EXISTS users;
    """)
