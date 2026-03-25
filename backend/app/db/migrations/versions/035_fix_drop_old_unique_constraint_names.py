"""Fix: drop old unique constraints that 034 missed

Migration 034 tried to drop {table}_brand_name_key but the actual
constraint names from migration 004 are uq_{table}_brand_name.
This drops those remaining constraints so the new composite unique
on (brand_name, marketplace) is the only one.

Revision ID: 035
Revises: 034
Create Date: 2026-03-25
"""

from alembic import op

revision = "035"
down_revision = "034"
branch_labels = None
depends_on = None

_TABLES = ["brand_vp_data", "brand_meeting_data"]


def upgrade() -> None:
    for table in _TABLES:
        op.execute(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS uq_{table}_brand_name"
        )


def downgrade() -> None:
    for table in reversed(_TABLES):
        # Cannot safely restore the old single-column unique if TH rows exist,
        # but this is best-effort for rollback
        op.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT uq_{table}_brand_name "
            f"UNIQUE (brand_name)"
        )
