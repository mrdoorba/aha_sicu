"""Shared evaluation inputs — one row per brand

Consolidates duplicate evaluation_inputs rows (keep most recent updated_at),
renames user_id → last_edited_by, replaces UNIQUE (brand_id, user_id) with
UNIQUE (brand_id), and drops idx_evaluation_inputs_user_id.

Revision ID: 015
Revises: 014
Create Date: 2026-02-24
"""

from alembic import op

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Consolidate duplicates: keep the row with MAX(updated_at) per brand
    op.execute("""
        DELETE FROM evaluation_inputs
        WHERE id NOT IN (
            SELECT DISTINCT ON (brand_id) id
            FROM evaluation_inputs
            ORDER BY brand_id, updated_at DESC NULLS LAST, id DESC
        );
    """)

    # 2. Rename user_id → last_edited_by
    op.execute("""
        ALTER TABLE evaluation_inputs
            RENAME COLUMN user_id TO last_edited_by;
    """)

    # 3. Drop old unique constraint and user_id index
    op.execute("""
        ALTER TABLE evaluation_inputs
            DROP CONSTRAINT IF EXISTS uq_evaluation_inputs_brand_user;
        DROP INDEX IF EXISTS idx_evaluation_inputs_user_id;
    """)

    # 4. Update FK constraint name to match new column name
    op.execute("""
        ALTER TABLE evaluation_inputs
            DROP CONSTRAINT IF EXISTS evaluation_inputs_user_id_fkey,
            ADD CONSTRAINT evaluation_inputs_last_edited_by_fkey
                FOREIGN KEY (last_edited_by) REFERENCES users(id) ON DELETE SET NULL;
    """)

    # 5. Add new unique constraint on brand_id only
    op.execute("""
        ALTER TABLE evaluation_inputs
            ADD CONSTRAINT uq_evaluation_inputs_brand UNIQUE (brand_id);
    """)


def downgrade() -> None:
    # Reverse: rename back, restore old constraint
    op.execute("""
        ALTER TABLE evaluation_inputs
            DROP CONSTRAINT IF EXISTS uq_evaluation_inputs_brand;
    """)

    op.execute("""
        ALTER TABLE evaluation_inputs
            DROP CONSTRAINT IF EXISTS evaluation_inputs_last_edited_by_fkey,
            ADD CONSTRAINT evaluation_inputs_user_id_fkey
                FOREIGN KEY (last_edited_by) REFERENCES users(id) ON DELETE SET NULL;
    """)

    op.execute("""
        ALTER TABLE evaluation_inputs
            RENAME COLUMN last_edited_by TO user_id;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_evaluation_inputs_user_id
            ON evaluation_inputs(user_id);
        ALTER TABLE evaluation_inputs
            ADD CONSTRAINT uq_evaluation_inputs_brand_user UNIQUE (brand_id, user_id);
    """)
