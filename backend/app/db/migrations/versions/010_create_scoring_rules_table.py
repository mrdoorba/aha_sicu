"""Create scoring_rules table

Stores scoring thresholds and rules for fashion and non_fashion templates.
Seeded with default values extracted from scoring.py calculator.

Revision ID: 010
Revises: 009
Create Date: 2026-02-12
"""

import json

from alembic import op

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None

FASHION_RULES = {
    "operational": {
        "unfulfilled_order_rate": {"threshold": 1.0, "points": 4, "comparison": "lte"},
        "late_shipment_rate": {"threshold": 1.0, "points": 3, "comparison": "lte"},
        "preparation_time": {"threshold": 1.0, "points": 3, "comparison": "lte"},
        "chat_response_rate": {"threshold": 95.0, "comparison": "gte", "info_only": True},
        "overall_rating": {"threshold": 4.7, "comparison": "gte", "info_only": True},
    },
    "business": {
        "monthly_sales_trend": {"threshold_pct": 90.0, "points": 10, "comparison": "gte"},
        "six_month_avg_threshold": {"threshold": 100000000, "points": 10, "comparison": "gte"},
        "conversion_rate": {"threshold": 2.0, "comparison": "gte", "info_only": True},
    },
    "content": {
        "quality_ratio": {"threshold": 95.0, "comparison": "gte", "info_only": True},
    },
    "visitors": {
        "returning_visitors_pct": {"threshold": 23.0, "points": 3, "comparison": "gte"},
        "followers": {"threshold": 50000, "points": 2, "comparison": "gte"},
    },
    "promo_tools": {
        "usage_pct_threshold": {"threshold": 80.0, "opportunity_points": 5},
        "effectiveness_pct_threshold": {"threshold": 90.0, "opportunity_points": 10},
    },
    "products_status": {
        "product_count": {"threshold": 35, "points": 5, "comparison": "gte"},
        "store_status_points": {"mall": 10, "star_plus": 5, "star": 0, "regular": 0},
    },
    "ads": {
        "roi_threshold": {"threshold": 8.0, "opportunity_points": 5, "comparison": "gt"},
        "gmv_ratio_threshold": {"threshold": 84.0, "points": 5, "comparison": "lt"},
        "cost_ratio_range": {"min": 5.0, "max": 10.0, "info_only": True},
    },
    "campaign": {
        "participation_pct_threshold": {"threshold": 90.0, "opportunity_points": 10, "comparison": "gte"},
    },
    "stock": {
        "high_threshold": {"threshold": 24, "points": 10, "comparison": "gte"},
        "mid_threshold": {"threshold": 12, "points": 5, "comparison": "gte"},
        "low_penalty": {"threshold": 12, "points": -5, "comparison": "lt"},
    },
    "discount": {
        "fake_discount_flag": {"points_no_flag": 5, "points_flag": 0},
    },
    "interpretation": {
        "ranges": [
            {"min": 71, "max": None, "label": "Good Candidate", "verdict": "\u2714\ufe0f"},
            {"min": 41, "max": 70, "label": "Needs Review", "verdict": "\u2b55\ufe0f"},
            {"min": None, "max": 40, "label": "Not Recommended", "verdict": "\u274c"},
        ],
    },
}

NON_FASHION_RULES = {
    **FASHION_RULES,
    "business": {
        **FASHION_RULES["business"],
        "conversion_rate": {"threshold": 3.0, "comparison": "gte", "info_only": True},
    },
    "ads": {
        **FASHION_RULES["ads"],
        "roi_threshold": {"threshold": 9.0, "opportunity_points": 5, "comparison": "gt"},
    },
}


def upgrade() -> None:
    op.execute("""
        CREATE TABLE scoring_rules (
            id SERIAL PRIMARY KEY,
            template VARCHAR(20) UNIQUE NOT NULL,
            rules JSONB NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            updated_by INTEGER REFERENCES users(id),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_scoring_rules_template ON scoring_rules (template);
    """)

    fashion_json = json.dumps(FASHION_RULES)
    non_fashion_json = json.dumps(NON_FASHION_RULES)

    op.execute(
        f"""
        INSERT INTO scoring_rules (template, rules) VALUES
            ('fashion', '{fashion_json}'::jsonb),
            ('non_fashion', '{non_fashion_json}'::jsonb);
    """
    )


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS idx_scoring_rules_template;
        DROP TABLE IF EXISTS scoring_rules;
    """)
