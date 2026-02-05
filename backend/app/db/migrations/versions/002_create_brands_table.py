"""Create brands table

Revision ID: 002
Revises: 001
Create Date: 2026-02-05
"""

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE brands (
            id SERIAL PRIMARY KEY,
            external_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            marketplace VARCHAR(100),
            raw_data JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX idx_brands_name ON brands(name);
        CREATE INDEX idx_brands_category ON brands(category);
        CREATE INDEX idx_brands_external_id ON brands(external_id);
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS idx_brands_external_id;
        DROP INDEX IF EXISTS idx_brands_category;
        DROP INDEX IF EXISTS idx_brands_name;
        DROP TABLE IF EXISTS brands;
    """)
