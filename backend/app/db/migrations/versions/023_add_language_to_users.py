"""Add language preference column to users table

Stores the user's preferred UI/email language (id, en, th).

Revision ID: 023
Revises: 022
Create Date: 2026-03-09
"""

import sqlalchemy as sa
from alembic import op

revision = "023"
down_revision = "022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "language",
            sa.String(5),
            server_default="id",
            nullable=False,
        ),
    )
    op.execute(
        "ALTER TABLE users ADD CONSTRAINT chk_users_language "
        "CHECK (language IN ('id', 'en', 'th'))"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP CONSTRAINT chk_users_language")
    op.drop_column("users", "language")
