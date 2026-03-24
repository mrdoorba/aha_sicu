"""Add FK indexes and enforce NOT NULL on created_at columns.

Five foreign key columns lacked indexes, causing full table scans on
user-activity joins. Four created_at columns were nullable despite having
a now() default — tightened to NOT NULL since no NULL rows exist in prod.

Revision ID: 033
Revises: 032
Create Date: 2026-03-24
"""

import sqlalchemy as sa
from alembic import op

revision = "033"
down_revision = "032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- NOT NULL on created_at columns ---
    op.execute(sa.text("ALTER TABLE brand_vp_data ALTER COLUMN created_at SET NOT NULL"))
    op.execute(sa.text("ALTER TABLE brand_meeting_data ALTER COLUMN created_at SET NOT NULL"))
    op.execute(sa.text("ALTER TABLE evaluation_inputs ALTER COLUMN created_at SET NOT NULL"))
    op.execute(sa.text("ALTER TABLE users ALTER COLUMN created_at SET NOT NULL"))

    # --- Missing FK indexes ---
    op.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_brand_uploads_uploaded_by "
        "ON brand_uploads(uploaded_by)"
    ))
    op.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_evaluation_inputs_last_edited_by "
        "ON evaluation_inputs(last_edited_by)"
    ))
    op.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_evaluations_user_id "
        "ON evaluations(user_id)"
    ))
    op.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_scoring_rules_updated_by "
        "ON scoring_rules(updated_by)"
    ))
    op.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_pending_uploads_brand_id "
        "ON pending_uploads(brand_id)"
    ))


def downgrade() -> None:
    # --- Remove FK indexes ---
    op.execute(sa.text("DROP INDEX IF EXISTS idx_brand_uploads_uploaded_by"))
    op.execute(sa.text("DROP INDEX IF EXISTS idx_evaluation_inputs_last_edited_by"))
    op.execute(sa.text("DROP INDEX IF EXISTS idx_evaluations_user_id"))
    op.execute(sa.text("DROP INDEX IF EXISTS idx_scoring_rules_updated_by"))
    op.execute(sa.text("DROP INDEX IF EXISTS idx_pending_uploads_brand_id"))

    # --- Revert created_at to nullable ---
    op.execute(sa.text("ALTER TABLE brand_vp_data ALTER COLUMN created_at DROP NOT NULL"))
    op.execute(sa.text("ALTER TABLE brand_meeting_data ALTER COLUMN created_at DROP NOT NULL"))
    op.execute(sa.text("ALTER TABLE evaluation_inputs ALTER COLUMN created_at DROP NOT NULL"))
    op.execute(sa.text("ALTER TABLE users ALTER COLUMN created_at DROP NOT NULL"))
