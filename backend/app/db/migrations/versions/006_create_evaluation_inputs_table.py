"""Create evaluation_inputs table

Stores per-user evaluation state for each brand: category type selection
and manual input data as JSONB.

Revision ID: 006
Revises: 005
Create Date: 2026-02-11
"""

from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE evaluation_inputs (
            id SERIAL PRIMARY KEY,
            brand_id INTEGER NOT NULL REFERENCES brand_vp_data(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            category_type VARCHAR(20),
            manual_data JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT uq_evaluation_inputs_brand_user UNIQUE (brand_id, user_id)
        );

        CREATE INDEX idx_evaluation_inputs_brand_id ON evaluation_inputs(brand_id);
        CREATE INDEX idx_evaluation_inputs_user_id ON evaluation_inputs(user_id);
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS idx_evaluation_inputs_user_id;
        DROP INDEX IF EXISTS idx_evaluation_inputs_brand_id;
        DROP TABLE IF EXISTS evaluation_inputs;
    """)
