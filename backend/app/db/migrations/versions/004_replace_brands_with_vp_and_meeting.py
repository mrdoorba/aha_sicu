"""Replace brands table with brand_vp_data and brand_meeting_data

Revision ID: 004
Revises: 003
Create Date: 2026-02-05
"""

from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the generic brands table (replaced by specific tables)
    op.execute("""
        DROP INDEX IF EXISTS idx_brands_external_id;
        DROP INDEX IF EXISTS idx_brands_category;
        DROP INDEX IF EXISTS idx_brands_name;
        DROP TABLE IF EXISTS brands;
    """)

    # Create brand_vp_data table (from VP sheet)
    op.execute("""
        CREATE TABLE brand_vp_data (
            id SERIAL PRIMARY KEY,
            brand_name VARCHAR(255) NOT NULL,
            raw_data JSONB NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT uq_brand_vp_data_brand_name UNIQUE (brand_name)
        );

        CREATE INDEX idx_brand_vp_data_brand_name ON brand_vp_data(brand_name);
        CREATE INDEX idx_brand_vp_data_updated_at ON brand_vp_data(updated_at DESC);
    """)

    # Create brand_meeting_data table (from 1st Meeting sheet)
    op.execute("""
        CREATE TABLE brand_meeting_data (
            id SERIAL PRIMARY KEY,
            brand_name VARCHAR(255) NOT NULL,
            raw_data JSONB NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT uq_brand_meeting_data_brand_name UNIQUE (brand_name)
        );

        CREATE INDEX idx_brand_meeting_data_brand_name ON brand_meeting_data(brand_name);
        CREATE INDEX idx_brand_meeting_data_updated_at ON brand_meeting_data(updated_at DESC);
    """)


def downgrade() -> None:
    # Drop new tables
    op.execute("""
        DROP INDEX IF EXISTS idx_brand_meeting_data_updated_at;
        DROP INDEX IF EXISTS idx_brand_meeting_data_brand_name;
        DROP TABLE IF EXISTS brand_meeting_data;

        DROP INDEX IF EXISTS idx_brand_vp_data_updated_at;
        DROP INDEX IF EXISTS idx_brand_vp_data_brand_name;
        DROP TABLE IF EXISTS brand_vp_data;
    """)

    # Recreate original brands table
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
