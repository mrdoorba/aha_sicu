"""Make user FK columns nullable with ON DELETE SET NULL

Allows user deletion while retaining evaluation, upload, and rule data.
Columns evaluation_inputs.user_id, evaluations.user_id, brand_uploads.uploaded_by
change from NOT NULL to NULLABLE. All four FK constraints changed to ON DELETE SET NULL.

Revision ID: 014
Revises: 013
Create Date: 2026-02-20
"""

from alembic import op

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        -- evaluation_inputs.user_id: drop NOT NULL, change FK to SET NULL
        ALTER TABLE evaluation_inputs
            ALTER COLUMN user_id DROP NOT NULL;
        ALTER TABLE evaluation_inputs
            DROP CONSTRAINT IF EXISTS evaluation_inputs_user_id_fkey,
            ADD CONSTRAINT evaluation_inputs_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

        -- evaluations.user_id: drop NOT NULL, change FK to SET NULL
        ALTER TABLE evaluations
            ALTER COLUMN user_id DROP NOT NULL;
        ALTER TABLE evaluations
            DROP CONSTRAINT IF EXISTS evaluations_user_id_fkey,
            ADD CONSTRAINT evaluations_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

        -- brand_uploads.uploaded_by: drop NOT NULL, change FK to SET NULL
        ALTER TABLE brand_uploads
            ALTER COLUMN uploaded_by DROP NOT NULL;
        ALTER TABLE brand_uploads
            DROP CONSTRAINT IF EXISTS brand_uploads_uploaded_by_fkey,
            ADD CONSTRAINT brand_uploads_uploaded_by_fkey
                FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL;

        -- scoring_rules.updated_by: already nullable, just change FK to SET NULL
        ALTER TABLE scoring_rules
            DROP CONSTRAINT IF EXISTS scoring_rules_updated_by_fkey,
            ADD CONSTRAINT scoring_rules_updated_by_fkey
                FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL;
    """)


def downgrade() -> None:
    op.execute("""
        -- scoring_rules.updated_by: revert to RESTRICT
        ALTER TABLE scoring_rules
            DROP CONSTRAINT IF EXISTS scoring_rules_updated_by_fkey,
            ADD CONSTRAINT scoring_rules_updated_by_fkey
                FOREIGN KEY (updated_by) REFERENCES users(id);

        -- brand_uploads.uploaded_by: restore NOT NULL, revert to RESTRICT
        UPDATE brand_uploads SET uploaded_by = 0 WHERE uploaded_by IS NULL;
        ALTER TABLE brand_uploads
            ALTER COLUMN uploaded_by SET NOT NULL;
        ALTER TABLE brand_uploads
            DROP CONSTRAINT IF EXISTS brand_uploads_uploaded_by_fkey,
            ADD CONSTRAINT brand_uploads_uploaded_by_fkey
                FOREIGN KEY (uploaded_by) REFERENCES users(id);

        -- evaluations.user_id: restore NOT NULL, revert to RESTRICT
        UPDATE evaluations SET user_id = 0 WHERE user_id IS NULL;
        ALTER TABLE evaluations
            ALTER COLUMN user_id SET NOT NULL;
        ALTER TABLE evaluations
            DROP CONSTRAINT IF EXISTS evaluations_user_id_fkey,
            ADD CONSTRAINT evaluations_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES users(id);

        -- evaluation_inputs.user_id: restore NOT NULL, revert to RESTRICT
        UPDATE evaluation_inputs SET user_id = 0 WHERE user_id IS NULL;
        ALTER TABLE evaluation_inputs
            ALTER COLUMN user_id SET NOT NULL;
        ALTER TABLE evaluation_inputs
            DROP CONSTRAINT IF EXISTS evaluation_inputs_user_id_fkey,
            ADD CONSTRAINT evaluation_inputs_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES users(id);
    """)
