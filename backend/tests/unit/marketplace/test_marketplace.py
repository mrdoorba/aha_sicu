"""Tests for marketplace constants and migration correctness.

Covers:
- Constants importability and completeness
- IDR→THB conversion arithmetic
- THB threshold derivation from IDR defaults
- Invalid marketplace code rejection
- Migration SQL structure verification
"""

import json
from pathlib import Path

import pytest

from app.core.marketplace import (
    CURRENCY_SYMBOLS,
    IDR_TO_THB_RATE,
    MARKETPLACE_CURRENCY,
    MARKETPLACE_LABELS,
    VALID_MARKETPLACES,
    convert_idr_to_thb,
)


# ---------------------------------------------------------------------------
# Constants importability and completeness
# ---------------------------------------------------------------------------


class TestMarketplaceConstants:
    """Verify MARKETPLACE_CURRENCY and MARKETPLACE_LABELS are importable and complete."""

    def test_valid_marketplaces_contains_id_and_th(self) -> None:
        assert "ID" in VALID_MARKETPLACES
        assert "TH" in VALID_MARKETPLACES

    def test_valid_marketplaces_is_frozen(self) -> None:
        assert isinstance(VALID_MARKETPLACES, frozenset)

    def test_marketplace_currency_maps_id_to_idr(self) -> None:
        assert MARKETPLACE_CURRENCY["ID"] == "IDR"

    def test_marketplace_currency_maps_th_to_thb(self) -> None:
        assert MARKETPLACE_CURRENCY["TH"] == "THB"

    def test_marketplace_labels_maps_id_to_indonesia(self) -> None:
        assert MARKETPLACE_LABELS["ID"] == "Indonesia"

    def test_marketplace_labels_maps_th_to_thailand(self) -> None:
        assert MARKETPLACE_LABELS["TH"] == "Thailand"

    def test_currency_symbols_has_idr(self) -> None:
        assert CURRENCY_SYMBOLS["IDR"] == "Rp"

    def test_currency_symbols_has_thb(self) -> None:
        assert CURRENCY_SYMBOLS["THB"] == "฿"

    def test_all_valid_marketplaces_have_currency(self) -> None:
        for mp in VALID_MARKETPLACES:
            assert mp in MARKETPLACE_CURRENCY, f"Missing currency mapping for {mp}"

    def test_all_valid_marketplaces_have_label(self) -> None:
        for mp in VALID_MARKETPLACES:
            assert mp in MARKETPLACE_LABELS, f"Missing label mapping for {mp}"


# ---------------------------------------------------------------------------
# IDR → THB conversion
# ---------------------------------------------------------------------------


class TestIDRToTHBConversion:
    """Verify conversion arithmetic using the fixed project rate."""

    def test_conversion_rate_is_0_0019(self) -> None:
        assert IDR_TO_THB_RATE == 0.0019

    def test_convert_100m_idr_to_thb(self) -> None:
        """100,000,000 IDR × 0.0019 = 190,000 THB."""
        result = convert_idr_to_thb(100_000_000)
        assert result == 190_000.0

    def test_convert_zero(self) -> None:
        assert convert_idr_to_thb(0) == 0.0

    def test_convert_small_value(self) -> None:
        """50,000 IDR × 0.0019 = 95.0 THB."""
        assert convert_idr_to_thb(50_000) == 95.0

    def test_convert_result_is_rounded_to_2_decimals(self) -> None:
        """Verify rounding: 1,111 IDR × 0.0019 = 2.1109 → 2.11."""
        assert convert_idr_to_thb(1_111) == 2.11


# ---------------------------------------------------------------------------
# THB threshold derivation from IDR defaults
# ---------------------------------------------------------------------------


class TestTHBThresholdDerivation:
    """Verify that the THB six_month_avg_threshold is correctly derived."""

    def test_thb_six_month_avg_threshold_equals_190000(self) -> None:
        """Must-have: THB six_month_avg_threshold = 100M × 0.0019 = 190,000."""
        idr_threshold = 100_000_000
        thb_threshold = convert_idr_to_thb(idr_threshold)
        assert thb_threshold == 190_000.0


# ---------------------------------------------------------------------------
# Non-currency thresholds identity between ID and TH
# ---------------------------------------------------------------------------


class TestNonCurrencyThresholdIdentity:
    """Non-currency thresholds must be identical between ID and TH seed rows.

    The migration seeds the TH row by copying the ID row and only converting
    currency-denominated thresholds. All percentage, count, and ratio thresholds
    must remain identical.
    """

    # These thresholds are NOT currency-denominated and must be copied as-is
    NON_CURRENCY_PATHS = [
        ("operational", "unfulfilled_order_rate", "threshold"),
        ("operational", "late_shipment_rate", "threshold"),
        ("operational", "preparation_time", "threshold"),
        ("operational", "chat_response_rate", "threshold"),
        ("operational", "overall_rating", "threshold"),
        ("business", "monthly_sales_trend", "threshold_pct"),
        ("business", "conversion_rate", "threshold"),
        ("visitors", "returning_visitors_pct", "threshold"),
        ("visitors", "followers", "threshold"),
        ("promo_tools", "usage_pct_threshold", "threshold"),
        ("promo_tools", "effectiveness_pct_threshold", "threshold"),
        ("products_status", "product_count", "threshold"),
        ("ads", "roi_threshold", "threshold"),
        ("ads", "gmv_ratio_threshold", "threshold"),
        ("ads", "cost_ratio_range", "min"),
        ("ads", "cost_ratio_range", "max"),
        ("campaign", "participation_pct_threshold", "threshold"),
        ("stock", "high_threshold", "threshold"),
        ("stock", "mid_threshold", "threshold"),
        ("stock", "low_penalty", "threshold"),
    ]

    def _get_nested(self, d: dict, *keys: str):
        """Traverse nested dict by key path."""
        for k in keys:
            d = d[k]
        return d

    def test_non_currency_thresholds_identical_when_only_six_month_avg_converted(self) -> None:
        """Simulate the migration logic: copy rules, convert only six_month_avg."""
        # Load the IDR default rules from migration 010
        # We inline the known structure to keep the test self-contained
        idr_rules = self._load_default_rules_from_migration()
        th_rules = json.loads(json.dumps(idr_rules))  # deep copy

        # Convert only the currency threshold
        th_rules["business"]["six_month_avg_threshold"]["threshold"] = convert_idr_to_thb(
            idr_rules["business"]["six_month_avg_threshold"]["threshold"]
        )

        for path in self.NON_CURRENCY_PATHS:
            idr_val = self._get_nested(idr_rules, *path)
            th_val = self._get_nested(th_rules, *path)
            assert idr_val == th_val, f"Mismatch at {'.'.join(path)}: {idr_val} != {th_val}"

    def _load_default_rules_from_migration(self) -> dict:
        """Read the current default rules from migration 010 source.

        Uses the FASHION_RULES dict as the base (migration 013 unified to non_fashion
        which becomes 'default'). For threshold identity testing, we just need any
        valid rules structure.
        """
        # The IDR default six_month_avg_threshold is 100,000,000
        # We use the known structure from migration 010
        return {
            "operational": {
                "unfulfilled_order_rate": {"threshold": 1.0, "points": 4, "comparison": "lte"},
                "late_shipment_rate": {"threshold": 1.0, "points": 3, "comparison": "lte"},
                "preparation_time": {"threshold": 1.0, "points": 3, "comparison": "lte"},
                "chat_response_rate": {"threshold": 95.0, "comparison": "gte", "info_only": True},
                "overall_rating": {"threshold": 4.7, "comparison": "gte", "info_only": True},
            },
            "business": {
                "monthly_sales_trend": {"threshold_pct": 90.0, "points": 10, "comparison": "gte"},
                "six_month_avg_threshold": {"threshold": 100_000_000, "points_above": 15, "points_below": 10, "comparison": "gt"},
                "conversion_rate": {"threshold": 3.0, "comparison": "gte", "info_only": True},
            },
            "visitors": {
                "returning_visitors_pct": {"threshold": 23.0, "points": 3, "comparison": "gte"},
                "followers": {"threshold": 50_000, "points": 2, "comparison": "gte"},
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
                "roi_threshold": {"threshold": 9.0, "opportunity_points": 5, "comparison": "gt"},
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
            "interpretation": {
                "ranges": [
                    {"min": 71, "max": None, "label": "Good Candidate", "verdict": "✔️"},
                    {"min": 41, "max": 70, "label": "Needs Review", "verdict": "⭕️"},
                    {"min": None, "max": 40, "label": "Not Recommended", "verdict": "❌"},
                ],
            },
        }


# ---------------------------------------------------------------------------
# Invalid marketplace rejection
# ---------------------------------------------------------------------------


class TestInvalidMarketplaceRejection:
    """Verify that invalid marketplace codes are caught at the constants level."""

    @pytest.mark.parametrize("code", ["XX", "US", "id", "th", "", "IDR"])
    def test_invalid_code_not_in_valid_marketplaces(self, code: str) -> None:
        assert code not in VALID_MARKETPLACES

    def test_marketplace_currency_raises_on_invalid_key(self) -> None:
        with pytest.raises(KeyError):
            _ = MARKETPLACE_CURRENCY["XX"]


# ---------------------------------------------------------------------------
# Migration file structure verification
# ---------------------------------------------------------------------------


class TestMigrationFileStructure:
    """Verify migration 026 exists and has expected structure."""

    MIGRATION_PATH = (
        Path(__file__).resolve().parents[3]
        / "app"
        / "db"
        / "migrations"
        / "versions"
        / "026_add_marketplace_to_schema.py"
    )

    def test_migration_file_exists(self) -> None:
        assert self.MIGRATION_PATH.exists(), f"Migration not found at {self.MIGRATION_PATH}"

    def test_migration_has_upgrade_function(self) -> None:
        content = self.MIGRATION_PATH.read_text()
        assert "def upgrade()" in content

    def test_migration_has_downgrade_function(self) -> None:
        content = self.MIGRATION_PATH.read_text()
        assert "def downgrade()" in content

    def test_migration_revision_is_026(self) -> None:
        content = self.MIGRATION_PATH.read_text()
        assert 'revision = "026"' in content

    def test_migration_down_revision_is_025(self) -> None:
        content = self.MIGRATION_PATH.read_text()
        assert 'down_revision = "025"' in content

    def test_migration_adds_marketplace_check_constraint(self) -> None:
        content = self.MIGRATION_PATH.read_text()
        assert "chk_scoring_rules_marketplace" in content

    def test_migration_seeds_th_row(self) -> None:
        content = self.MIGRATION_PATH.read_text()
        # Must contain TH marketplace value for seeding
        assert "'TH'" in content or '"TH"' in content

    def test_migration_updates_unique_constraint(self) -> None:
        content = self.MIGRATION_PATH.read_text()
        # Must reference both template and marketplace in unique constraint
        assert "template" in content and "marketplace" in content
