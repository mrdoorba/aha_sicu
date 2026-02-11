"""Create evaluations table

Stores completed evaluation snapshots as permanent, immutable records.
Each save creates a new record (INSERT-only, no upsert).

Revision ID: 009
Revises: 008
Create Date: 2026-02-11
"""

from alembic import op

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE evaluations (
            id SERIAL PRIMARY KEY,
            brand_id INTEGER NOT NULL REFERENCES brand_vp_data(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            template VARCHAR(20) NOT NULL,
            final_score DECIMAL(5,2) NOT NULL,
            verdict VARCHAR(20) NOT NULL,
            score_breakdown JSONB NOT NULL,
            calculator_results JSONB NOT NULL,
            manual_inputs JSONB NOT NULL,
            rule_version INTEGER NOT NULL DEFAULT 1,
            email_output TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_evaluations_brand_id ON evaluations(brand_id);
        CREATE INDEX idx_evaluations_created_at ON evaluations(created_at DESC);
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS idx_evaluations_created_at;
        DROP INDEX IF EXISTS idx_evaluations_brand_id;
        DROP TABLE IF EXISTS evaluations;
    """)
