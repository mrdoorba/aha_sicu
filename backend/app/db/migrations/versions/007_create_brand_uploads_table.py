"""Create brand_uploads table

Stores parsed file upload data per brand for calculator consumption.
Each brand has at most one file per type (upsert by brand_id + file_type).

Revision ID: 007
Revises: 006
Create Date: 2026-02-11
"""

from alembic import op

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE brand_uploads (
            id SERIAL PRIMARY KEY,
            brand_id INTEGER NOT NULL REFERENCES brand_vp_data(id),
            file_type VARCHAR(50) NOT NULL,
            calculator_target VARCHAR(100) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_size INTEGER NOT NULL,
            row_count INTEGER,
            parsed_data JSONB NOT NULL,
            uploaded_by INTEGER NOT NULL REFERENCES users(id),
            uploaded_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT uq_brand_uploads_brand_file_type UNIQUE (brand_id, file_type)
        );

        CREATE INDEX idx_brand_uploads_brand_id ON brand_uploads(brand_id);
        CREATE INDEX idx_brand_uploads_file_type ON brand_uploads(file_type);
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS idx_brand_uploads_file_type;
        DROP INDEX IF EXISTS idx_brand_uploads_brand_id;
        DROP TABLE IF EXISTS brand_uploads;
    """)
