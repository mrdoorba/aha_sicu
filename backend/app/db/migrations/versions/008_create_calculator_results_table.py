"""Create calculator_results table

Stores calculator output per brand for the scoring system.
Each brand has at most one result per calculator type (upsert on recalculation).

Revision ID: 008
Revises: 007
Create Date: 2026-02-11
"""

from alembic import op

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE calculator_results (
            id SERIAL PRIMARY KEY,
            brand_id INTEGER NOT NULL REFERENCES brand_vp_data(id),
            calculator_type VARCHAR(50) NOT NULL,
            details JSONB NOT NULL,
            output_text TEXT NOT NULL,
            calculated_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT uq_calculator_results_brand_type UNIQUE (brand_id, calculator_type)
        );

        CREATE INDEX idx_calculator_results_brand_id ON calculator_results(brand_id);
        CREATE INDEX idx_calculator_results_type ON calculator_results(calculator_type);
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS idx_calculator_results_type;
        DROP INDEX IF EXISTS idx_calculator_results_brand_id;
        DROP TABLE IF EXISTS calculator_results;
    """)
