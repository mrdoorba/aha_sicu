"""Unit tests for the Final Scoring Calculator.

Tests against the spec in logic/scoring-system-template-sicu.md.
"""

import pytest

from app.calculators.scoring import calculate_score
from app.calculators.scoring.categories import (
    _promo_verdict,
    _score_ads,
    _score_business,
    _score_campaign,
    _score_operational,
    _score_products,
    _score_promo_tools,
    _score_stock,
    _score_visitors,
)
from app.calculators.scoring.computations import (
    _compute_g68,
    _compute_g72,
    _compute_g73,
    _compute_g75,
    _parse_d73_percentages,
    _parse_g68_left,
)
from app.calculators.scoring.helpers import (
    _format_message_template,
    _generate_month_labels,
)
from app.calculators.scoring.models import ScoringResult
from app.calculators.scoring.rules import DEFAULT_RULES


# ---------------------------------------------------------------------------
# Fixtures: sample manual data
# ---------------------------------------------------------------------------

@pytest.fixture
def full_manual_data():
    """Complete manual data for a typical store evaluation."""
    return {
        "operational": {
            "unfulfilledOrderRate": 0.5,   # 0.5% — pass (<1%)
            "lateShipmentRate": 0.3,       # 0.3% — pass
            "preparationTime": 0.8,        # 0.8 days — pass (<1)
            "chatResponseRate": 98.0,      # 98% — pass (>95%)
            "overallRating": 4.9,          # pass (>4.7)
        },
        "business": {
            "salesMonth0": 200_000_000,    # 200M current
            "salesMonth1": 180_000_000,
            "salesMonth2": 190_000_000,
            "salesMonth3": 170_000_000,
            "salesMonth4": 160_000_000,
            "salesMonth5": 150_000_000,
        },
        "visitors": {
            "totalVisitors": 100_000,
            "returningVisitors": 30_000,   # 30% — pass (>23%)
            "totalFollowers": 60_000,      # pass (>50000)
        },
        "promoTools": {
            "promoToko": 20_000_000,
            "paketDiskon": 40_000_000,
            "komboHemat": 5_000_000,
            "flashSale": 5_000_000,
            "voucher": 180_000_000,
            "shopeeLive": 35_000_000,
            "gameToko": 3_000_000,
            "brandMembership": 4_000_000,
            "gratisOngkir": 10_000_000,
            "chatBroadcast": 3_000_000,
            "programAfiliasi": 40_000_000,
        },
        "products": {
            "productCount": 50,
            "storeStatus": "Shopee Mall",
        },
        "ads": {
            "adSales": 50_000_000,
            "adCost": 5_000_000,
        },
        "campaign": {
            "nominatedSessions": 18,
            "availableSessions": 20,
        },
        "competition": {
            "product1": {"keyword": "sepatu", "sellingPrice": 180_000, "marketPrice": 200_000, "productName": "Sepatu A"},
            "product2": {"keyword": "sandal", "sellingPrice": 140_000, "marketPrice": 150_000, "productName": "Sandal B"},
            "product3": {"keyword": "tas", "sellingPrice": 280_000, "marketPrice": 300_000, "productName": "Tas C"},
        },
    }


@pytest.fixture
def full_calculator_results():
    """Calculator results from Calculators 1-3."""
    return {
        "ads_keyword": {
            "details": {},
            "output_text": "Sheet 1 output\nSheet 2 output",
        },
        "top_sku": {
            "details": {
                "average_stock": 30,
                "output_1": [
                    {"kode_variasi": "A1", "product_name": "Sepatu A", "rata2_harga_jual": 180_000},
                    {"kode_variasi": "B1", "product_name": "Sandal B", "rata2_harga_jual": 140_000},
                    {"kode_variasi": "C1", "product_name": "Tas C", "rata2_harga_jual": 280_000},
                ],
            },
            "output_text": "",
        },
        "discount": {
            "details": {
                "fake_discount_flag": False,
                "discount_pct": "25.0%",
                "range_min": "15.0%",
                "range_max": "35.0%",
                "voucher_pct": "3.0%",
                "paket_pct": "1.0%",
            },
            "output_text": "% Diskon TOP SKU: 25.0%\nRange: 15.0% ~ 35.0%\nVoucher 3.0%\nPaket Diskon 1.0%",
        },
    }


# ---------------------------------------------------------------------------
# Month label generation tests
# ---------------------------------------------------------------------------


class TestGenerateMonthLabels:
    def test_valid_start_month(self):
        labels = _generate_month_labels("2026-01")
        assert labels == ["Jan 2026", "Dec 2025", "Nov 2025", "Oct 2025", "Sep 2025", "Aug 2025"]

    def test_mid_year(self):
        labels = _generate_month_labels("2026-06")
        assert labels == ["Jun 2026", "May 2026", "Apr 2026", "Mar 2026", "Feb 2026", "Jan 2026"]

    def test_none_returns_fallback(self):
        labels = _generate_month_labels(None)
        assert labels == ["Bulan Ini", "Bulan -1", "Bulan -2", "Bulan -3", "Bulan -4", "Bulan -5"]

    def test_empty_string_returns_fallback(self):
        labels = _generate_month_labels("")
        assert labels == ["Bulan Ini", "Bulan -1", "Bulan -2", "Bulan -3", "Bulan -4", "Bulan -5"]

    def test_invalid_format_returns_fallback(self):
        labels = _generate_month_labels("invalid")
        assert labels == ["Bulan Ini", "Bulan -1", "Bulan -2", "Bulan -3", "Bulan -4", "Bulan -5"]

    def test_invalid_month_13_returns_fallback(self):
        labels = _generate_month_labels("2026-13")
        assert labels == ["Bulan Ini", "Bulan -1", "Bulan -2", "Bulan -3", "Bulan -4", "Bulan -5"]


# ---------------------------------------------------------------------------
# Per-category scoring tests
# ---------------------------------------------------------------------------


class TestScoreOperational:
    def test_all_pass(self):
        data = {
            "operational": {
                "unfulfilledOrderRate": 0.5,
                "lateShipmentRate": 0.3,
                "preparationTime": 0.8,
                "chatResponseRate": 98.0,
                "overallRating": 4.9,
            }
        }
        cat = _score_operational(data)
        assert cat.score == 10.0  # 4 + 3 + 3
        assert cat.rows[0].verdict == "✔️"
        assert cat.rows[0].score == 4.0
        assert cat.rows[1].verdict == "✔️"
        assert cat.rows[1].score == 3.0
        assert cat.rows[2].verdict == "✔️"
        assert cat.rows[2].score == 3.0

    def test_unfulfilled_penalty(self):
        data = {"operational": {"unfulfilledOrderRate": 5.0}}  # 5%
        cat = _score_operational(data)
        assert cat.rows[0].verdict == "❌"
        assert cat.rows[0].score == -5.0  # -(5.0)

    def test_late_shipment_penalty(self):
        data = {"operational": {"lateShipmentRate": 3.0}}
        cat = _score_operational(data)
        assert cat.rows[1].verdict == "❌"
        assert cat.rows[1].score == -3.0

    def test_preparation_time_penalty(self):
        data = {"operational": {"preparationTime": 2.5}}
        cat = _score_operational(data)
        assert cat.rows[2].verdict == "❌"
        assert cat.rows[2].score == -((2.5 - 1) * 100)  # -150

    def test_preparation_time_exactly_1(self):
        data = {"operational": {"preparationTime": 1.0}}
        cat = _score_operational(data)
        assert cat.rows[2].verdict == "✔️"
        assert cat.rows[2].score == 3.0

    def test_chat_response_fail(self):
        data = {"operational": {"chatResponseRate": 90.0}}
        cat = _score_operational(data)
        assert cat.rows[3].verdict == "❌"
        assert cat.rows[3].score == 0.0  # No score, just verdict

    def test_rating_fail(self):
        data = {"operational": {"overallRating": 4.5}}
        cat = _score_operational(data)
        assert cat.rows[4].verdict == "❌"

    def test_empty_data(self):
        cat = _score_operational({})
        assert cat.rows[0].score == 4.0  # 0.0 <= 1.0, so pass
        assert cat.rows[1].score == 3.0
        assert cat.rows[2].score == 3.0


class TestScoreBusiness:
    def test_healthy_sales(self):
        data = {
            "business": {
                "salesMonth0": 200_000_000,
                "salesMonth1": 180_000_000,
                "salesMonth2": 190_000_000,
                "salesMonth3": 170_000_000,
                "salesMonth4": 160_000_000,
                "salesMonth5": 150_000_000,
            }
        }
        cat = _score_business(data)
        # avg = 175M, current = 200M, 175M < 200M * 1.10 = 220M → pass (H13=10)
        assert cat.rows[0].score == 10.0
        # avg = 175M > 100M → H19=15 (points_above)
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.score == 15.0
        assert cat.score == 25.0

    def test_declining_sales(self):
        data = {
            "business": {
                "salesMonth0": 50_000_000,   # 50M — current is low
                "salesMonth1": 200_000_000,
                "salesMonth2": 200_000_000,
                "salesMonth3": 200_000_000,
                "salesMonth4": 200_000_000,
                "salesMonth5": 200_000_000,
            }
        }
        cat = _score_business(data)
        # avg ~175M, 175M >= 50M * 1.10 = 55M → FAIL (H13=0)
        assert cat.rows[0].score == 0.0
        # avg = 175M > 100M → H19=15 (points_above)
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.score == 15.0

    def test_low_average(self):
        data = {
            "business": {
                "salesMonth0": 80_000_000,
                "salesMonth1": 70_000_000,
                "salesMonth2": 60_000_000,
                "salesMonth3": 50_000_000,
                "salesMonth4": 40_000_000,
                "salesMonth5": 30_000_000,
            }
        }
        cat = _score_business(data)
        # avg = 55M <= 100M → H19=10 (points_below)
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.score == 10.0

    def test_rata_penjualan_message_is_empty(self):
        from app.calculators.scoring.messages import _generate_business_messages
        from app.calculators.scoring.models import RowScore, CategoryScore
        data = {
            "business": {
                "salesMonth0": 120_000_000,
                "salesMonth1": 120_000_000,
                "salesMonth2": 120_000_000,
                "salesMonth3": 120_000_000,
                "salesMonth4": 120_000_000,
                "salesMonth5": 120_000_000,
            }
        }
        cat = CategoryScore(
            category="Bisnis Analisis",
            score=10.0, max_score=25.0,
            rows=[RowScore(row=19, metric="Rata² Penjualan 6 bulan terakhir", value=120_000_000, benchmark="-", verdict="-", message="", score=10.0)]
        )
        _generate_business_messages(cat, data)
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.message == "", f"Expected message to be empty, got: {h19_row.message}"



class TestScoreVisitors:
    def test_both_pass(self):
        data = {
            "visitors": {
                "totalVisitors": 100_000,
                "returningVisitors": 30_000,
                "totalFollowers": 60_000,
            }
        }
        cat = _score_visitors(data)
        assert cat.score == 5.0  # 3 + 2

    def test_low_returning(self):
        data = {
            "visitors": {
                "totalVisitors": 100_000,
                "returningVisitors": 20_000,  # 20% < 23%
                "totalFollowers": 60_000,
            }
        }
        cat = _score_visitors(data)
        h28_row = next(r for r in cat.rows if r.row == 28)
        assert h28_row.score == 0.0

    def test_low_followers(self):
        data = {
            "visitors": {
                "totalVisitors": 100_000,
                "returningVisitors": 30_000,
                "totalFollowers": 40_000,  # < 50000
            }
        }
        cat = _score_visitors(data)
        h29_row = next(r for r in cat.rows if r.row == 29)
        assert h29_row.score == 0.0


class TestPromoVerdict:
    def test_zero_value(self):
        assert _promo_verdict(0, 200_000_000, 0.08) == "❌"

    def test_too_dependent_promo_toko(self):
        # 60% of sales → ❌ (only applies to promoToko)
        assert _promo_verdict(120_000_000, 200_000_000, 0.08, key="promoToko") == "❌"

    def test_high_pct_non_promo_toko_passes_benchmark(self):
        # 60% of sales but NOT promoToko → 50% check skipped, meets 8% benchmark → ✔️
        assert _promo_verdict(120_000_000, 200_000_000, 0.08, key="paketDiskon") == "✔️"

    def test_meets_benchmark(self):
        # 10% of 200M = 20M, benchmark 8% → 16M. 20M >= 16M → ✔️
        assert _promo_verdict(20_000_000, 200_000_000, 0.08) == "✔️"

    def test_below_benchmark(self):
        # 5M / 200M = 2.5%, benchmark 8% → fails
        assert _promo_verdict(5_000_000, 200_000_000, 0.08) == "❌"

    def test_gratis_ongkir_any_value(self):
        assert _promo_verdict(1_000, 200_000_000, 0.0) == "✔️"

    def test_gratis_ongkir_zero(self):
        assert _promo_verdict(0, 200_000_000, 0.0) == "❌"


class TestScorePromoTools:
    def test_all_tools_used_effectively(self, full_manual_data):
        cat = _score_promo_tools(full_manual_data)
        # H42 and H43 are opportunity scores (points when ❌)
        h42_row = next(r for r in cat.rows if r.row == 42)
        h43_row = next(r for r in cat.rows if r.row == 43)
        # All 11 tools used → usage > 80% → H42=0
        assert h42_row.score == 0.0
        # Check effectiveness score exists
        assert h43_row.row == 43

    def test_no_tools_used(self):
        data = {
            "promoTools": {
                "promoToko": 0, "paketDiskon": 0, "komboHemat": 0,
                "flashSale": 0, "voucher": 0, "shopeeLive": 0,
                "gameToko": 0, "brandMembership": 0, "gratisOngkir": 0,
                "chatBroadcast": 0, "programAfiliasi": 0,
            },
            "business": {"salesMonth0": 200_000_000},
        }
        cat = _score_promo_tools(data)
        h42_row = next(r for r in cat.rows if r.row == 42)
        h43_row = next(r for r in cat.rows if r.row == 43)
        assert h42_row.score == 5.0   # Opportunity: underused
        assert h43_row.score == 10.0  # Opportunity: ineffective
        assert cat.score == 15.0


class TestScoreProducts:
    def test_mall_with_enough_products(self):
        data = {"products": {"productCount": 50, "storeStatus": "Shopee Mall"}}
        cat = _score_products(data)
        assert cat.score == 15.0  # 5 + 10

    def test_star_plus(self):
        data = {"products": {"productCount": 50, "storeStatus": "Star+"}}
        cat = _score_products(data)
        assert cat.score == 10.0  # 5 + 5

    def test_regular_store(self):
        data = {"products": {"productCount": 50, "storeStatus": "Regular"}}
        cat = _score_products(data)
        assert cat.score == 5.0  # 5 + 0

    def test_few_products(self):
        data = {"products": {"productCount": 20, "storeStatus": "Shopee Mall"}}
        cat = _score_products(data)
        h45_row = next(r for r in cat.rows if r.row == 45)
        assert h45_row.score == 0.0

    def test_exactly_35_products(self):
        data = {"products": {"productCount": 35, "storeStatus": "Shopee Mall"}}
        cat = _score_products(data)
        h45_row = next(r for r in cat.rows if r.row == 45)
        assert h45_row.score == 5.0


class TestScoreAds:
    def test_roi_below_threshold(self):
        data = {
            "ads": {"adSales": 50_000_000, "adCost": 6_000_000},  # ROI ~8.3
            "business": {"salesMonth0": 200_000_000},
        }
        cat = _score_ads(data, "fashion")
        h50_row = next(r for r in cat.rows if r.row == 50)
        # ROI = 50M/6M = 8.33, unified threshold 9 → fail → H50=5 (opportunity)
        assert h50_row.score == 5.0
        assert h50_row.verdict == "❌"

    def test_roi_above_threshold(self):
        data = {
            "ads": {"adSales": 100_000_000, "adCost": 10_000_000},  # ROI = 10
            "business": {"salesMonth0": 200_000_000},
        }
        cat = _score_ads(data, "non_fashion")
        h50_row = next(r for r in cat.rows if r.row == 50)
        # ROI = 10, unified threshold 9 → pass → H50=0
        assert h50_row.score == 0.0
        assert h50_row.verdict == "✔️"

    def test_gmv_ratio_low(self):
        data = {
            "ads": {"adSales": 100_000_000, "adCost": 10_000_000},
            "business": {"salesMonth0": 200_000_000},
        }
        cat = _score_ads(data, "fashion")
        h51_row = next(r for r in cat.rows if r.row == 51)
        # GMV ratio = 100M/200M = 50% < 84% → pass → H51=5
        assert h51_row.score == 5.0

    def test_gmv_ratio_high(self):
        data = {
            "ads": {"adSales": 180_000_000, "adCost": 20_000_000},
            "business": {"salesMonth0": 200_000_000},
        }
        cat = _score_ads(data, "fashion")
        h51_row = next(r for r in cat.rows if r.row == 51)
        # GMV ratio = 180M/200M = 90% >= 84% → fail → H51=0
        assert h51_row.score == 0.0


class TestScoreCampaign:
    def test_high_participation(self):
        data = {"campaign": {"nominatedSessions": 19, "availableSessions": 20}}
        cat = _score_campaign(data)
        # 19/20 = 95% > 90% → pass → H57=0
        assert cat.score == 0.0

    def test_low_participation(self):
        data = {"campaign": {"nominatedSessions": 15, "availableSessions": 20}}
        cat = _score_campaign(data)
        # 15/20 = 75% <= 90% → fail → H57=10 (opportunity)
        assert cat.score == 10.0

    def test_no_sessions(self):
        data = {"campaign": {"nominatedSessions": 0, "availableSessions": 0}}
        cat = _score_campaign(data)
        # 0/0 → 0% → fail → H57=10
        assert cat.score == 10.0


class TestScoreStock:
    # -----------------------------------------------------------------------
    # BDD Scenarios:
    #   Scenario: High average stock with good availability
    #     Given TOP SKU data with average_stock=30 and 0% out of stock
    #     When scoring stock
    #     Then score = 10 (no penalty)
    #
    #   Scenario: High average stock but >10% out of stock
    #     Given TOP SKU data with average_stock=30 and 20% out of stock
    #     When scoring stock
    #     Then score = 10 + (-5) = 5
    #
    #   Scenario: Low average stock with >10% out of stock
    #     Given TOP SKU data with average_stock=8 and 50% out of stock
    #     When scoring stock
    #     Then score = -5 + (-5) = -10
    #
    #   Scenario: Stock availability exactly at threshold (10%)
    #     Given TOP SKU data with exactly 10% out of stock
    #     When scoring stock
    #     Then no penalty applied (<=10% is OK)
    # -----------------------------------------------------------------------

    def test_high_stock(self):
        results = {"top_sku": {"details": {"average_stock": 30, "out_of_stock_pct": 0.0}}}
        cat = _score_stock(results)
        assert cat.score == 10.0

    def test_medium_stock(self):
        results = {"top_sku": {"details": {"average_stock": 15, "out_of_stock_pct": 0.0}}}
        cat = _score_stock(results)
        assert cat.score == 5.0

    def test_low_stock(self):
        results = {"top_sku": {"details": {"average_stock": 8, "out_of_stock_pct": 0.0}}}
        cat = _score_stock(results)
        assert cat.score == -5.0

    def test_exactly_24(self):
        results = {"top_sku": {"details": {"average_stock": 24, "out_of_stock_pct": 0.0}}}
        cat = _score_stock(results)
        assert cat.score == 10.0

    def test_exactly_12(self):
        results = {"top_sku": {"details": {"average_stock": 12, "out_of_stock_pct": 0.0}}}
        cat = _score_stock(results)
        assert cat.score == 5.0

    def test_missing_data(self):
        cat = _score_stock({})
        assert cat.available is False
        assert cat.score == 0.0  # Missing calculator data → unavailable

    # --- Stock availability penalty tests ---

    def test_high_stock_with_penalty(self):
        """High avg stock but >10% out of stock → penalty applied."""
        # Arrange
        results = {"top_sku": {"details": {"average_stock": 30, "out_of_stock_pct": 0.20}}}

        # Act
        cat = _score_stock(results)

        # Assert — 10 (avg stock) + (-5) (penalty) = 5
        assert cat.score == 5.0
        assert len(cat.rows) == 2
        assert cat.rows[1].row == 71
        assert cat.rows[1].score == -5.0
        assert cat.rows[1].verdict == "❌"

    def test_low_stock_with_penalty_stacks(self):
        """Low avg stock + out of stock penalty stacks."""
        # Arrange
        results = {"top_sku": {"details": {"average_stock": 8, "out_of_stock_pct": 0.50}}}

        # Act
        cat = _score_stock(results)

        # Assert — (-5) + (-5) = -10
        assert cat.score == -10.0

    def test_at_threshold_no_penalty(self):
        """Exactly 10% out of stock → no penalty (<=10% is OK)."""
        # Arrange
        results = {"top_sku": {"details": {"average_stock": 30, "out_of_stock_pct": 0.10}}}

        # Act
        cat = _score_stock(results)

        # Assert — 10 (avg stock) + 0 (no penalty) = 10
        assert cat.score == 10.0
        assert len(cat.rows) == 2
        assert cat.rows[1].score == 0.0
        assert cat.rows[1].verdict == "✔️"

    def test_zero_out_of_stock_no_penalty(self):
        """0% out of stock → no penalty."""
        # Arrange
        results = {"top_sku": {"details": {"average_stock": 24, "out_of_stock_pct": 0.0}}}

        # Act
        cat = _score_stock(results)

        # Assert
        assert cat.score == 10.0
        assert len(cat.rows) == 2
        assert cat.rows[1].score == 0.0


class TestScoreH19Thresholds:
    """H19 uses points_above=15 (strict >) and points_below=10 (<=)."""

    def test_above_threshold_gets_15_points(self):
        """avg_6mo = 100_000_001 > 100_000_000 → 15 points."""
        data = {
            "business": {
                "salesMonth0": 100_000_001,
                "salesMonth1": 100_000_001,
                "salesMonth2": 100_000_001,
                "salesMonth3": 100_000_001,
                "salesMonth4": 100_000_001,
                "salesMonth5": 100_000_001,
            }
        }
        cat = _score_business(data)
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.score == 15.0

    def test_exactly_at_threshold_gets_10_points(self):
        """avg_6mo = 100_000_000 (not strictly >) → 10 points."""
        data = {
            "business": {
                "salesMonth0": 100_000_000,
                "salesMonth1": 100_000_000,
                "salesMonth2": 100_000_000,
                "salesMonth3": 100_000_000,
                "salesMonth4": 100_000_000,
                "salesMonth5": 100_000_000,
            }
        }
        cat = _score_business(data)
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.score == 10.0

    def test_below_threshold_gets_10_points(self):
        """avg_6mo = 50_000_000 < 100_000_000 → 10 points."""
        data = {
            "business": {
                "salesMonth0": 50_000_000,
                "salesMonth1": 50_000_000,
                "salesMonth2": 50_000_000,
                "salesMonth3": 50_000_000,
                "salesMonth4": 50_000_000,
                "salesMonth5": 50_000_000,
            }
        }
        cat = _score_business(data)
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.score == 10.0


# ---------------------------------------------------------------------------
# Fashion vs Non-Fashion threshold tests
# ---------------------------------------------------------------------------


class TestUnifiedThresholds:
    def test_roi_fails_at_8_for_both_templates(self):
        """ROI=8 fails for both fashion and non_fashion (unified threshold=9)."""
        data = {
            "ads": {"adSales": 80_000_000, "adCost": 10_000_000},  # ROI = 8
            "business": {"salesMonth0": 200_000_000},
        }
        for template in ("fashion", "non_fashion"):
            cat = _score_ads(data, template)
            h50 = next(r for r in cat.rows if r.row == 50)
            assert h50.verdict == "❌", f"Expected fail for {template}"

    def test_roi_passes_at_9_for_both_templates(self):
        """ROI=9 passes for both fashion and non_fashion (unified threshold=9)."""
        data = {
            "ads": {"adSales": 90_000_000, "adCost": 10_000_000},  # ROI = 9
            "business": {"salesMonth0": 200_000_000},
        }
        for template in ("fashion", "non_fashion"):
            cat = _score_ads(data, template)
            h50 = next(r for r in cat.rows if r.row == 50)
            assert h50.verdict == "✔️", f"Expected pass for {template}"


# ---------------------------------------------------------------------------
# G-column message tests
# ---------------------------------------------------------------------------


class TestGColumnMessages:
    def test_operational_messages_populated(self, full_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="Test Store",
            period="Jan 2026",
            brand_name="TEST",
        )
        ops_cat = result.category_scores[0]
        # All rows should have messages
        for row in ops_cat.rows:
            assert row.message, f"Row {row.row} has no message"

    def test_g7_pass_message(self):
        data = {"operational": {"unfulfilledOrderRate": 0.5}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        ops = result.category_scores[0]
        g7 = next(r for r in ops.rows if r.row == 7)
        assert "✔️" in g7.message
        assert "0.5%" in g7.message
        assert "[Sudah Baik]" in g7.message

    def test_g7_fail_message(self):
        data = {"operational": {"unfulfilledOrderRate": 2.0}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        ops = result.category_scores[0]
        g7 = next(r for r in ops.rows if r.row == 7)
        assert "❌" in g7.message
        assert "[Kurang Baik" in g7.message

    def test_g13_declining_sales_warning(self):
        data = {
            "business": {
                "salesMonth0": 50_000_000,
                "salesMonth1": 200_000_000,
                "salesMonth2": 200_000_000,
                "salesMonth3": 200_000_000,
                "salesMonth4": 200_000_000,
                "salesMonth5": 200_000_000,
            }
        }
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        biz = result.category_scores[1]
        g13 = next(r for r in biz.rows if r.row == 13)
        assert "[Menurun" in g13.message
        assert "❗️" in g13.message  # > 25% decline warning

    def test_g13_tolerated_decline_keeps_score_but_shows_fail_message_and_avg_benchmark(self):
        data = {
            "business": {
                "salesMonth0": 100,
                "salesMonth1": 110,
                "salesMonth2": 110,
                "salesMonth3": 110,
                "salesMonth4": 110,
                "salesMonth5": 110,
            }
        }
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        biz = result.category_scores[1]
        g13 = next(r for r in biz.rows if r.row == 13)
        assert g13.verdict == "❌"
        assert g13.score == 10.0
        assert "[Menurun" in g13.message
        assert "toleransi" not in g13.message
        assert g13.benchmark == ">108"


# ---------------------------------------------------------------------------
# G68 marketing estimation tests
# ---------------------------------------------------------------------------


class TestG68:
    def test_basic_computation(self):
        d73 = "% Diskon TOP SKU: 100.0%\nRange: 40.0% ~ 50.0%\nVoucher 3.0%\nPaket Diskon 1.0%"
        d52 = 0.05  # 5% ad cost
        result = _compute_g68(d73, d52)
        # t=1.0, ra=0.40, rb=0.50, v=0.03, p=0.01
        # low = (0.40*1.0) + 0.03 + 0.01 + 0.05 + 0.05 = 0.54 → 54.0%
        # high = (0.50*1.0) + 0.03 + 0.01 + 0.05 + 0.05 = 0.64 → 64.0%
        assert "54.0%" in result
        assert "64.0%" in result

    def test_fake_discount_flag_appended(self):
        d73 = "% Diskon TOP SKU: 100.0%\nRange: 40.0% ~ 50.0%\nVoucher 3.0%\nPaket Diskon 1.0%\n📌 Berpotensi menggunakan 'fake discount'"
        result = _compute_g68(d73, 0.05)
        assert "Berpotensi" in result

    def test_empty_text(self):
        assert _compute_g68("", 0.05) == ""


class TestG68WithDiscountDetails:
    """AC-3/AC-4: _compute_g68 reads from discount details when available."""

    D73 = "% Diskon TOP SKU: 100.0%\nRange: 40.0% ~ 50.0%\nVoucher 3.0%\nPaket Diskon 1.0%"

    def _make_details(
        self, *, t: float = 1.0, ra: float = 0.40, rb: float = 0.50,
        v: float = 0.03, p: float = 0.01, fake: bool = False,
    ) -> dict:
        return {
            "discount_pct_raw": t,
            "range_min_raw": ra,
            "range_max_raw": rb,
            "voucher_pct_raw": v,
            "paket_pct_raw": p,
            "fake_discount_flag": fake,
        }

    def test_produces_same_output_as_text_parsing(self):
        """G68 with discount_details produces identical output to regex parsing."""
        details = self._make_details()
        result_text = _compute_g68(self.D73, 0.05)
        result_details = _compute_g68(self.D73, 0.05, discount_details=details)
        assert result_details == result_text

    def test_falls_back_to_regex_when_details_none(self):
        """G68 falls back to regex when discount_details is None."""
        result = _compute_g68(self.D73, 0.05, discount_details=None)
        assert "54.0%" in result
        assert "64.0%" in result

    def test_falls_back_to_regex_when_details_lack_raw_fields(self):
        """G68 falls back to regex when discount_details lacks raw fields."""
        incomplete_details = {"fake_discount_flag": False}
        result = _compute_g68(self.D73, 0.05, discount_details=incomplete_details)
        assert "54.0%" in result

    def test_fake_discount_from_details(self):
        """G68 reads fake_discount_flag from details instead of text parsing."""
        details = self._make_details(fake=True)
        result = _compute_g68(self.D73, 0.05, discount_details=details)
        assert "Berpotensi" in result

    def test_no_fake_discount_from_details(self):
        """G68 with fake_discount_flag=False omits flag even if text has it."""
        d73_with_flag = self.D73 + "\n📌 Berpotensi menggunakan 'fake discount'"
        details = self._make_details(fake=False)
        result = _compute_g68(d73_with_flag, 0.05, discount_details=details)
        assert "Berpotensi" not in result

    def test_missing_fake_discount_flag_defaults_to_false(self):
        """G68 with discount_details missing fake_discount_flag defaults to no flag."""
        details = {
            "discount_pct_raw": 1.0,
            "range_min_raw": 0.40,
            "range_max_raw": 0.50,
            "voucher_pct_raw": 0.03,
            "paket_pct_raw": 0.01,
        }
        result = _compute_g68(self.D73, 0.05, discount_details=details)
        assert "Berpotensi" not in result

    @pytest.mark.parametrize("t,ra,rb,v,p", [
        (1.0, 0.40, 0.50, 0.03, 0.01),
        (0.5, 0.10, 0.20, 0.02, 0.005),
        (1.373, 0.595, 0.595, 0.114, 0.023),
    ])
    def test_parametrized_equivalence(self, t: float, ra: float, rb: float, v: float, p: float):
        """Both paths produce identical output for various inputs."""
        d73 = (
            f"% Diskon TOP SKU: {t * 100:.1f}%\n"
            f"Range: {ra * 100:.1f}% ~ {rb * 100:.1f}%\n"
            f"Voucher {v * 100:.1f}%\n"
            f"Paket Diskon {p * 100:.1f}%"
        )
        details = self._make_details(t=t, ra=ra, rb=rb, v=v, p=p)
        result_text = _compute_g68(d73, 0.05)
        result_details = _compute_g68(d73, 0.05, discount_details=details)
        assert result_details == result_text


class TestG72WithDiscountDetails:
    """_compute_g72 reads from discount details when available."""

    D73 = "% Diskon TOP SKU: 100.0%\nRange: 10.0% ~ 15.0%\nVoucher 1.0%\nPaket Diskon 0.5%"

    def _make_details(
        self, *, t: float = 1.0, ra: float = 0.10, rb: float = 0.15,
        v: float = 0.01, p: float = 0.005,
    ) -> dict:
        return {
            "discount_pct_raw": t,
            "range_min_raw": ra,
            "range_max_raw": rb,
            "voucher_pct_raw": v,
            "paket_pct_raw": p,
        }

    def test_produces_same_output_as_text_parsing(self):
        """G72 with discount_details produces identical output to regex parsing."""
        g68 = _compute_g68(self.D73, 0.03)
        details = self._make_details()
        result_text = _compute_g72(g68, 0.03, self.D73, is_fashion=False)
        result_details = _compute_g72(g68, 0.03, self.D73, is_fashion=False, discount_details=details)
        assert result_details == result_text

    def test_falls_back_to_regex_when_details_none(self):
        """G72 falls back to regex when discount_details is None."""
        g68 = _compute_g68(self.D73, 0.03)
        result = _compute_g72(g68, 0.03, self.D73, is_fashion=False, discount_details=None)
        assert result >= 0.12


class TestG72:
    def test_fashion_floor(self):
        d73 = "% Diskon TOP SKU: 100.0%\nRange: 10.0% ~ 15.0%\nVoucher 1.0%\nPaket Diskon 0.5%"
        g68 = _compute_g68(d73, 0.03)
        result = _compute_g72(g68, 0.03, d73, is_fashion=True)
        # Fashion floor is 15%
        assert result >= 0.15

    def test_non_fashion_floor(self):
        d73 = "% Diskon TOP SKU: 100.0%\nRange: 10.0% ~ 15.0%\nVoucher 1.0%\nPaket Diskon 0.5%"
        g68 = _compute_g68(d73, 0.03)
        result = _compute_g72(g68, 0.03, d73, is_fashion=False)
        # Non-fashion floor is 12%
        assert result >= 0.12

    def test_empty_d73_returns_default(self):
        result = _compute_g72("", 0.0, "", is_fashion=True)
        assert result == 0.15  # Fashion default


class TestG72Branching:
    """Test G72 two-branch comparison: capped_value vs ceiling_g68."""

    D73 = "% Diskon TOP SKU: 100.0%\nRange: 10.0% ~ 15.0%\nVoucher 1.0%\nPaket Diskon 0.5%"

    def test_true_branch_capped_exceeds_ceiling(self):
        """G72=TRUE: capped_value > ceiling_g68 returns capped_value."""
        # G68 "13.5% ~ 20.0%" → g68_left=0.135, ceiling_g68=0.14
        # Fashion floor=0.15 pushes capped above ceiling_g68
        result = _compute_g72("13.5% ~ 20.0%", 0.03, self.D73, is_fashion=True)
        assert result == 0.15

    def test_false_branch_ceiling_returned(self):
        """G72=FALSE: capped_value <= ceiling_g68 returns ceiling_g68."""
        # G68 "15.3% ~ 22.7%" → g68_left=0.153, ceiling_g68=0.16
        result = _compute_g72("15.3% ~ 22.7%", 0.03, self.D73, is_fashion=False)
        assert result == 0.16

    def test_non_fashion_high_g68_exceeds_20_percent(self):
        """Non-fashion store with high G68 can exceed the 20% upper limit."""
        # G68 "22.0% ~ 28.5%" → ceiling_g68=0.22, above non-fashion upper_limit
        result = _compute_g72("22.0% ~ 28.5%", 0.03, self.D73, is_fashion=False)
        assert result == 0.22

    def test_fashion_retains_capped_value(self):
        """Fashion store TRUE branch: high floor drives capped above ceiling_g68."""
        # floor_fashion=0.25 via rules, G68 "19.5% ~ 24.5%" → ceiling_g68=0.20
        # capped pushed to 0.25 by floor > ceiling_g68=0.20 → TRUE → return 0.25
        rules = {"marketing": {"floor_fashion": {"value": 0.25}}}
        result = _compute_g72(
            "19.5% ~ 24.5%", 0.03, self.D73, is_fashion=True, rules=rules,
        )
        assert result == 0.25

    def test_empty_g68_preserves_capped_behavior(self):
        """Empty G68 text returns capped value without G68 comparison."""
        result = _compute_g72("", 0.03, self.D73, is_fashion=False)
        assert result >= 0.12  # At least non-fashion floor
        assert result <= 0.20  # At most upper_limit

    def test_g68_without_tilde_uses_ceiling(self):
        """G68 without '~' defaults g68_left to 0.0, ceiling_g68 used as fallback."""
        # "15.3%" → g68_left=0.0, ceiling_g68=0.16
        result = _compute_g72("15.3%", 0.03, self.D73, is_fashion=False)
        assert result == 0.16


class TestParseG68Left:
    """Test _parse_g68_left helper extraction."""

    def test_standard_format(self):
        assert _parse_g68_left("15.3% ~ 22.7%") == pytest.approx(0.153)

    def test_no_tilde(self):
        assert _parse_g68_left("15.3%") == 0.0

    def test_empty(self):
        assert _parse_g68_left("") == 0.0


class TestG73:
    def test_normal_verdict(self):
        result = _compute_g73("✔️", 0.15, 200_000_000)
        assert "💡" in result
        assert "15%" in result
        assert "IDR" not in result  # budget amount removed

    def test_rejected_verdict_still_returns_budget(self):
        result = _compute_g73("❌", 0.15, 200_000_000)
        assert "💡" in result
        assert "15%" in result

    def test_rejected_non_mall_still_returns_budget(self):
        result = _compute_g73("❌ Non Mall", 0.15, 200_000_000)
        assert "💡" in result
        assert "15%" in result

    def test_rejected_no_brand_still_returns_budget(self):
        result = _compute_g73("❌ No Brand", 0.15, 200_000_000)
        assert "💡" in result
        assert "15%" in result

    def test_rejected_opex_still_returns_budget(self):
        result = _compute_g73("❌ Opex", 0.15, 200_000_000)
        assert "💡" in result
        assert "15%" in result

    def test_rejected_stock_still_returns_budget(self):
        result = _compute_g73("❌ Stock", 0.15, 200_000_000)
        assert "💡" in result
        assert "15%" in result


# ---------------------------------------------------------------------------
# G75 closing message tests
# ---------------------------------------------------------------------------


class TestG75:
    def test_approved(self):
        msg = _compute_g75("✔️")
        assert "potensi" in msg.lower()
        assert "cal-bd2" in msg

    def test_approved_th_marketplace_uses_th_link(self):
        msg = _compute_g75("✔️", marketplace="TH")
        assert "th-bd2" in msg
        assert "cal-bd2" not in msg

    def test_rejected(self):
        msg = _compute_g75("❌")
        assert "keuntungan" in msg.lower()

    def test_non_mall(self):
        msg = _compute_g75("❌ Non Mall")
        assert "Mall" in msg

    def test_no_brand(self):
        msg = _compute_g75("❌ No Brand")
        assert "brand" in msg.lower()

    def test_empty_verdict_returns_empty(self):
        msg = _compute_g75("")
        assert msg == ""

    def test_opex_verdict(self):
        msg = _compute_g75("❌ Opex")
        assert "keterlambatan" in msg.lower()

    def test_stock_verdict(self):
        msg = _compute_g75("❌ Stock")
        assert "stok per varian" in msg.lower()

    def test_stock_verdict_interpolates_store_name(self):
        msg = _compute_g75("❌ Stock", "BrandX")
        assert "BrandX" in msg
        assert msg.count("BrandX") == 2


# ---------------------------------------------------------------------------
# Email body assembly tests
# ---------------------------------------------------------------------------


class TestEmailAssembly:
    def test_email_has_all_sections(self, full_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="MOON DAE Official Store",
            period="Jan 2026",
            brand_name="MOON DAE",
        )
        body = result.email_body
        assert "Operasional" in body
        assert "Penjualan" in body
        assert "Pengunjung" in body
        assert "Promosi" in body
        assert "📦 Jumlah Produk & Status Toko:" in body
        assert "Iklan" in body
        assert "Campaign" in body
        assert "Kesimpulan" in body

    def test_jumlah_produk_section_has_both_rows(self, full_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="S",
            period="P",
            brand_name="B",
        )
        body = result.email_body
        # Extract the section between header and next section
        section_start = body.index("📦 Jumlah Produk & Status Toko:")
        section_end = body.index("📣 Performa Iklan:")
        section = body[section_start:section_end]
        assert "Jumlah Produk = 50" in section
        assert "Status Toko" in section

    def test_promo_section_does_not_contain_status_toko(self, full_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="S",
            period="P",
            brand_name="B",
        )
        body = result.email_body
        promo_start = body.index("🏷️ Tingkat Penggunaan Alat Promosi:")
        promo_end = body.index("📦 Jumlah Produk & Status Toko:")
        promo_section = body[promo_start:promo_end]
        assert "Status Toko" not in promo_section

    def test_section_ordering_promo_products_ads(self, full_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="S",
            period="P",
            brand_name="B",
        )
        body = result.email_body
        promo_pos = body.index("🏷️ Tingkat Penggunaan Alat Promosi:")
        products_pos = body.index("📦 Jumlah Produk & Status Toko:")
        ads_pos = body.index("📣 Performa Iklan:")
        assert promo_pos < products_pos < ads_pos

    def test_email_subject_format(self, full_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="MOON DAE Official Store",
            period="Jan 2026",
            brand_name="MOON DAE",
        )
        assert "🏥 AHA Store Internal Check Up" in result.email_subject
        assert "MOON DAE Official Store" in result.email_subject
        assert "Jan 2026" in result.email_subject


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_all_zeros(self):
        result = calculate_score(
            manual_data={}, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        assert isinstance(result, ScoringResult)
        assert isinstance(result.total_score, float)

    def test_missing_calculator_data(self):
        data = {
            "operational": {"unfulfilledOrderRate": 0.5},
            "business": {"salesMonth0": 100_000_000},
        }
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="non_fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        # Stock should be unavailable (no calculator data)
        stock_cat = next(c for c in result.category_scores if c.category == "Stok")
        assert stock_cat.available is False
        assert stock_cat.score == 0.0
        # Discount category is no longer part of scoring
        assert all(c.category != "Discount" for c in result.category_scores)

    def test_extreme_operational_values(self):
        data = {"operational": {"unfulfilledOrderRate": 50.0}}  # 50%
        cat = _score_operational(data)
        assert cat.rows[0].score == -50.0

    def test_negative_total_score_possible(self):
        data = {
            "operational": {
                "unfulfilledOrderRate": 10.0,  # -10
                "lateShipmentRate": 10.0,       # -10
                "preparationTime": 3.0,         # -200
            },
        }
        results = {"top_sku": {"details": {"average_stock": 5}}}  # -5
        result = calculate_score(
            manual_data=data, calculator_results=results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        assert result.total_score < 0


# ---------------------------------------------------------------------------
# D73 percentage parsing tests
# ---------------------------------------------------------------------------


class TestParseD73:
    def test_standard_format(self):
        text = "% Diskon TOP SKU: 102.9%\nRange: 42.2% ~ 50.4%\nVoucher 3.9%\nPaket Diskon 0.2%"
        t, ra, rb, v, p = _parse_d73_percentages(text)
        assert abs(t - 1.029) < 0.001
        assert abs(ra - 0.422) < 0.001
        assert abs(rb - 0.504) < 0.001
        assert abs(v - 0.039) < 0.001
        assert abs(p - 0.002) < 0.001

    def test_empty_text(self):
        t, ra, rb, v, p = _parse_d73_percentages("")
        assert t == 0.0
        assert ra == 0.0


# ---------------------------------------------------------------------------
# Full integration test
# ---------------------------------------------------------------------------


class TestCalculateScore:
    def test_full_calculation(self, full_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="MOON DAE Official Store",
            period="Jan 2026",
            brand_name="MOON DAE",
        )
        assert isinstance(result, ScoringResult)
        assert result.template == "fashion"
        assert result.verdict == "✔️"
        assert len(result.category_scores) == 9
        assert result.email_subject != ""
        assert result.email_body != ""
        assert result.total_score > 0

    def test_non_fashion_template(self, full_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="non_fashion",
            verdict="✔️",
            store_name="Test",
            period="Jan 2026",
            brand_name="T",
        )
        assert result.template == "non_fashion"
        # Conversion rate benchmark should be >3% for non-fashion
        biz_cat = result.category_scores[1]
        conv_row = next(r for r in biz_cat.rows if r.row == 20)
        assert conv_row.benchmark == ">3%"


# ---------------------------------------------------------------------------
# Task 4: Verify default rules produce identical results (AC #6)
# ---------------------------------------------------------------------------


class TestDefaultRulesIdentical:
    """Default rules from DB must produce identical scores to rules=None fallback."""

    def test_calculate_score_with_default_rules(self, full_manual_data, full_calculator_results):
        result_none = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        result_rules = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=DEFAULT_RULES,
        )
        assert result_none.total_score == result_rules.total_score
        for cat_none, cat_rules in zip(result_none.category_scores, result_rules.category_scores):
            assert cat_none.score == cat_rules.score

    def test_calculate_score_rules_none_fallback(self, full_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=None,
        )
        assert isinstance(result, ScoringResult)
        assert result.total_score > 0

    def test_non_fashion_default_rules_identical(self, full_manual_data, full_calculator_results):
        result_none = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="non_fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        result_rules = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="non_fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=DEFAULT_RULES,
        )
        assert result_none.total_score == result_rules.total_score

    def test_operational_with_default_rules(self):
        data = {
            "operational": {
                "unfulfilledOrderRate": 0.5,
                "lateShipmentRate": 0.3,
                "preparationTime": 0.8,
                "chatResponseRate": 98.0,
                "overallRating": 4.9,
            }
        }
        cat_none = _score_operational(data)
        cat_rules = _score_operational(data, DEFAULT_RULES)
        assert cat_none.score == cat_rules.score
        for r_none, r_rules in zip(cat_none.rows, cat_rules.rows):
            assert r_none.score == r_rules.score
            assert r_none.verdict == r_rules.verdict


# ---------------------------------------------------------------------------
# Task 5: New tests with modified rules (AC #7)
# ---------------------------------------------------------------------------


class TestCustomRulesOperational:
    """Custom operational thresholds change scores."""

    def test_custom_unfulfilled_threshold(self):
        data = {"operational": {"unfulfilledOrderRate": 1.5}}
        # Default: threshold=1.0 → 1.5 > 1.0 → fail
        cat_default = _score_operational(data)
        assert cat_default.rows[0].verdict == "❌"

        # Custom: threshold=2.0 → 1.5 <= 2.0 → pass
        custom_rules = {**DEFAULT_RULES, "operational": {
            **DEFAULT_RULES["operational"],
            "unfulfilled_order_rate": {"threshold": 2.0, "points": 6, "comparison": "lte"},
        }}
        cat_custom = _score_operational(data, custom_rules)
        assert cat_custom.rows[0].verdict == "✔️"
        assert cat_custom.rows[0].score == 6.0  # Custom points

    def test_custom_late_shipment_points(self):
        data = {"operational": {"lateShipmentRate": 0.5}}
        custom_rules = {**DEFAULT_RULES, "operational": {
            **DEFAULT_RULES["operational"],
            "late_shipment_rate": {"threshold": 1.0, "points": 8, "comparison": "lte"},
        }}
        cat = _score_operational(data, custom_rules)
        assert cat.rows[1].score == 8.0  # Custom points instead of default 3


class TestCustomRulesAds:
    """Custom ROI threshold changes verdict."""

    def test_custom_roi_threshold(self):
        data = {
            "ads": {"adSales": 30_000_000, "adCost": 5_000_000},  # ROI = 6
            "business": {"salesMonth0": 200_000_000},
        }
        # Default: threshold=9 → ROI 6 < 9 → fail
        cat_default = _score_ads(data, "fashion")
        h50 = next(r for r in cat_default.rows if r.row == 50)
        assert h50.verdict == "❌"
        assert h50.score == 5.0  # opportunity

        # Custom: threshold=5 → ROI 6 >= 5 → pass
        custom_rules = {**DEFAULT_RULES, "ads": {
            **DEFAULT_RULES["ads"],
            "roi_threshold": {"threshold": 5.0, "opportunity_points": 5, "comparison": "gt"},
        }}
        cat_custom = _score_ads(data, "fashion", custom_rules)
        h50 = next(r for r in cat_custom.rows if r.row == 50)
        assert h50.verdict == "✔️"
        assert h50.score == 0.0


class TestCustomRulesStock:
    """Custom stock thresholds change scoring tiers."""

    def test_custom_stock_thresholds(self):
        results = {"top_sku": {"details": {"average_stock": 20, "out_of_stock_pct": 0.0}}}
        # Default: >=24 → 10, >=12 → 5 → 20 falls in mid tier = 5
        cat_default = _score_stock(results)
        assert cat_default.score == 5.0

        # Custom: high=30, mid=15 → 20 >= 15 → mid = 5 (same tier but different thresholds)
        custom_rules = {**DEFAULT_RULES, "stock": {
            "high_threshold": {"threshold": 30, "points": 15, "comparison": "gte"},
            "mid_threshold": {"threshold": 15, "points": 7, "comparison": "gte"},
            "low_penalty": {"threshold": 15, "points": -10, "comparison": "lt"},
        }}
        cat_custom = _score_stock(results, custom_rules)
        assert cat_custom.score == 7.0  # custom mid points

    def test_stock_reclassified_by_threshold(self):
        results = {"top_sku": {"details": {"average_stock": 24, "out_of_stock_pct": 0.0}}}
        # Default: 24 >= 24 → high tier = 10
        cat_default = _score_stock(results)
        assert cat_default.score == 10.0

        # Custom: high=30 → 24 < 30, mid=20 → 24 >= 20 → mid = 5
        custom_rules = {**DEFAULT_RULES, "stock": {
            "high_threshold": {"threshold": 30, "points": 10, "comparison": "gte"},
            "mid_threshold": {"threshold": 20, "points": 5, "comparison": "gte"},
            "low_penalty": {"threshold": 20, "points": -5, "comparison": "lt"},
        }}
        cat_custom = _score_stock(results, custom_rules)
        assert cat_custom.score == 5.0  # Reclassified from high to mid

    def test_custom_out_of_stock_threshold(self):
        """Custom out_of_stock threshold overrides the default 10%."""
        # Arrange — 15% out of stock, default threshold 10% → penalty
        results = {"top_sku": {"details": {"average_stock": 30, "out_of_stock_pct": 0.15}}}

        # Act with default rules — 15% > 10% → penalty -5
        cat_default = _score_stock(results)
        assert cat_default.score == 5.0  # 10 + (-5)

        # Act with custom threshold 20% — 15% <= 20% → no penalty
        custom_rules = {**DEFAULT_RULES, "stock": {
            "out_of_stock": {"threshold": 0.20, "penalty": -5.0},
        }}
        cat_custom = _score_stock(results, custom_rules)
        assert cat_custom.score == 10.0  # 10 + 0


class TestCustomRulesVisitors:
    """Custom visitor thresholds change scores."""

    def test_custom_returning_visitors_threshold(self):
        data = {"visitors": {
            "totalVisitors": 100_000,
            "returningVisitors": 22_000,  # 22% - below default 23%
            "totalFollowers": 60_000,
        }}
        # Default: 22% < 23% → fail
        cat_default = _score_visitors(data)
        h28 = next(r for r in cat_default.rows if r.row == 28)
        assert h28.score == 0.0

        # Custom: threshold=20% → 22% > 20% → pass with 5 points
        custom_rules = {**DEFAULT_RULES, "visitors": {
            "returning_visitors_pct": {"threshold": 20.0, "points": 5, "comparison": "gte"},
            "followers": {"threshold": 50000, "points": 2, "comparison": "gte"},
        }}
        cat_custom = _score_visitors(data, custom_rules)
        h28 = next(r for r in cat_custom.rows if r.row == 28)
        assert h28.score == 5.0


class TestCustomRulesPromo:
    """Custom promo thresholds change opportunity points."""

    def test_custom_usage_opportunity_points(self):
        data = {
            "promoTools": {
                "promoToko": 0, "paketDiskon": 0, "komboHemat": 0,
                "flashSale": 0, "voucher": 0, "shopeeLive": 0,
                "gameToko": 0, "brandMembership": 0, "gratisOngkir": 0,
                "chatBroadcast": 0, "programAfiliasi": 0,
            },
            "business": {"salesMonth0": 200_000_000},
        }
        # Default: usage fails → opportunity_points = 5
        cat_default = _score_promo_tools(data)
        h42 = next(r for r in cat_default.rows if r.row == 42)
        assert h42.score == 5.0

        # Custom: opportunity_points = 8
        custom_rules = {**DEFAULT_RULES, "promo_tools": {
            "usage_pct_threshold": {"threshold": 80.0, "opportunity_points": 8},
            "effectiveness_pct_threshold": {"threshold": 90.0, "opportunity_points": 10},
        }}
        cat_custom = _score_promo_tools(data, custom_rules)
        h42 = next(r for r in cat_custom.rows if r.row == 42)
        assert h42.score == 8.0


class TestCustomRulesCampaign:
    """Custom campaign threshold changes score."""

    def test_custom_participation_threshold(self):
        data = {"campaign": {"nominatedSessions": 17, "availableSessions": 20}}
        # 17/20 = 85% — below default 90% → fail → opportunity 10
        cat_default = _score_campaign(data)
        assert cat_default.score == 10.0

        # Custom: threshold=80% → 85% > 80% → pass → 0
        custom_rules = {**DEFAULT_RULES, "campaign": {
            "participation_pct_threshold": {"threshold": 80.0, "opportunity_points": 10},
        }}
        cat_custom = _score_campaign(data, custom_rules)
        assert cat_custom.score == 0.0


class TestCustomRulesProducts:
    """Custom product count and status points."""

    def test_custom_product_threshold(self):
        data = {"products": {"productCount": 30, "storeStatus": "Shopee Mall"}}
        # Default: 30 < 35 → fail
        cat_default = _score_products(data)
        h45 = next(r for r in cat_default.rows if r.row == 45)
        assert h45.score == 0.0

        # Custom: threshold=25 → 30 >= 25 → pass with 8 points
        custom_rules = {**DEFAULT_RULES, "products_status": {
            "product_count": {"threshold": 25, "points": 8, "comparison": "gte"},
            "store_status_points": {"mall": 10, "star_plus": 5, "star": 0, "regular": 0},
        }}
        cat_custom = _score_products(data, custom_rules)
        h45 = next(r for r in cat_custom.rows if r.row == 45)
        assert h45.score == 8.0


class TestCustomRulesBusiness:
    """Custom business thresholds change scores."""

    def test_custom_sales_trend_threshold(self):
        data = {
            "business": {
                "salesMonth0": 100_000_000,
                "salesMonth1": 100_000_000,
                "salesMonth2": 100_000_000,
                "salesMonth3": 100_000_000,
                "salesMonth4": 100_000_000,
                "salesMonth5": 100_000_000,
            }
        }
        # Default: threshold_pct=90 → multiplier=1.10
        # avg=100M, current=100M → 100M < 100M*1.10=110M → pass (10pts)
        cat_default = _score_business(data)
        assert cat_default.rows[0].score == 10.0

        # Custom: threshold_pct=50 → multiplier=1.50
        # avg=100M, current=100M → 100M < 100M*1.50=150M → pass with 15pts
        custom_rules = {**DEFAULT_RULES, "business": {
            **DEFAULT_RULES["business"],
            "monthly_sales_trend": {"threshold_pct": 50.0, "points": 15, "comparison": "gte"},
        }}
        cat_custom = _score_business(data, custom_rules)
        assert cat_custom.rows[0].score == 15.0

    def test_custom_avg_threshold(self):
        data = {
            "business": {
                "salesMonth0": 80_000_000,
                "salesMonth1": 70_000_000,
                "salesMonth2": 60_000_000,
                "salesMonth3": 50_000_000,
                "salesMonth4": 40_000_000,
                "salesMonth5": 30_000_000,
            }
        }
        # avg = 55M, default threshold=100M → 55M <= 100M → points_below=10
        cat_default = _score_business(data)
        h19 = next(r for r in cat_default.rows if r.row == 19)
        assert h19.score == 10.0

        # Custom: threshold=50M, 55M > 50M → points_above=12
        custom_rules = {**DEFAULT_RULES, "business": {
            **DEFAULT_RULES["business"],
            "six_month_avg_threshold": {"threshold": 50_000_000, "points_above": 12, "points_below": 8, "comparison": "gt"},
        }}
        cat_custom = _score_business(data, custom_rules)
        h19 = next(r for r in cat_custom.rows if r.row == 19)
        assert h19.score == 12.0


class TestScoringResultRuleVersion:
    """ScoringResult dataclass has rule_version field."""

    def test_rule_version_default(self):
        result = calculate_score(
            manual_data={}, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        assert result.rule_version == 1

    def test_rule_version_custom(self):
        result = calculate_score(
            manual_data={}, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=DEFAULT_RULES, rule_version=3,
        )
        assert result.rule_version == 3


class TestEndToEndModifiedRules:
    """Modified rules produce different total_score."""

    def test_modified_rules_different_total(self, full_manual_data, full_calculator_results):
        result_default = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
        )
        # Modify: double operational points, change stock thresholds
        modified_rules = {
            **DEFAULT_RULES,
            "operational": {
                "unfulfilled_order_rate": {"threshold": 1.0, "points": 8, "comparison": "lte"},
                "late_shipment_rate": {"threshold": 1.0, "points": 6, "comparison": "lte"},
                "preparation_time": {"threshold": 1.0, "points": 6, "comparison": "lte"},
                "chat_response_rate": {"threshold": 95.0, "comparison": "gte", "info_only": True},
                "overall_rating": {"threshold": 4.7, "comparison": "gte", "info_only": True},
            },
        }
        result_modified = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=modified_rules, rule_version=2,
        )
        # Operational with default: 4+3+3=10. Modified: 8+6+6=20. Diff=10
        assert result_modified.total_score != result_default.total_score
        assert result_modified.total_score == result_default.total_score + 10
        assert result_modified.rule_version == 2


# ---------------------------------------------------------------------------
# Marketing rules tests (Story 5-4)
# ---------------------------------------------------------------------------


class TestG72WithRules:
    """Test _compute_g72 reads marketing constants from rules."""

    D73 = "% Diskon TOP SKU: 100.0%\nRange: 10.0% ~ 15.0%\nVoucher 1.0%\nPaket Diskon 0.5%"

    def _g68(self, d73=None, d52=0.03):
        return _compute_g68(d73 or self.D73, d52)

    def test_custom_floor_fashion(self):
        """Custom floor_fashion overrides default 0.15 for fashion."""
        rules = {"marketing": {"floor_fashion": {"value": 0.18}}}
        result = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=True, rules=rules)
        assert result >= 0.18

    def test_custom_floor_non_fashion(self):
        """Custom floor overrides default 0.12 for non-fashion."""
        rules = {"marketing": {"floor": {"value": 0.14}}}
        result = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=False, rules=rules)
        assert result >= 0.14

    def test_custom_base_subtraction(self):
        """Custom base_subtraction changes calculation."""
        rules_default = {"marketing": {
            "floor": {"value": 0.01},
            "base_subtraction": {"value": 0.03},
            "upper_limit_base": {"value": 0.50},
            "fashion_adjustment": {"value": 0.0},
            "minimum_threshold": {"value": 0.01},
        }}
        rules_custom = {**rules_default, "marketing": {
            **rules_default["marketing"],
            "base_subtraction": {"value": 0.10},
        }}
        result_default = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=False, rules=rules_default)
        result_custom = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=False, rules=rules_custom)
        # Higher subtraction → lower base → potentially lower result
        assert result_custom <= result_default

    def test_custom_upper_limit_base(self):
        """Custom upper_limit_base changes upper limit."""
        rules = {"marketing": {
            "floor": {"value": 0.01},
            "upper_limit_base": {"value": 0.30},
            "fashion_adjustment": {"value": 0.0},
            "base_subtraction": {"value": 0.03},
            "minimum_threshold": {"value": 0.01},
        }}
        result = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=False, rules=rules)
        # With higher upper_limit_base (0.30 vs 0.20), should still compute
        assert isinstance(result, float)

    def test_custom_fashion_adjustment(self):
        """Custom fashion_adjustment changes upper limit for fashion."""
        rules = {"marketing": {
            "floor_fashion": {"value": 0.01},
            "upper_limit_base": {"value": 0.20},
            "fashion_adjustment": {"value": 0.10},
            "base_subtraction": {"value": 0.03},
            "minimum_threshold": {"value": 0.01},
        }}
        result = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=True, rules=rules)
        assert isinstance(result, float)

    def test_custom_minimum_threshold(self):
        """Custom minimum_threshold changes minimum bound."""
        rules = {"marketing": {
            "floor": {"value": 0.01},
            "minimum_threshold": {"value": 0.15},
            "upper_limit_base": {"value": 0.20},
            "fashion_adjustment": {"value": 0.0},
            "base_subtraction": {"value": 0.03},
        }}
        result = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=False, rules=rules)
        assert result >= 0.15

    def test_rules_none_fallback(self):
        """rules=None falls back to hardcoded defaults."""
        result = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=True, rules=None)
        assert result >= 0.15  # Fashion floor default

    def test_rules_missing_marketing_category(self):
        """Rules dict without marketing key falls back to defaults."""
        rules = {"operational": {}}
        result = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=True, rules=rules)
        assert result >= 0.15  # Fallback to default fashion floor

    def test_empty_d73_returns_floor_from_rules(self):
        """Empty d73 returns floor_fashion from rules when is_fashion."""
        rules = {"marketing": {"floor_fashion": {"value": 0.20}}}
        result = _compute_g72("", 0.0, "", is_fashion=True, rules=rules)
        assert result == 0.20

    def test_all_constants_overridden(self):
        """All marketing constants overridden at once."""
        rules = {"marketing": {
            "floor_fashion": {"value": 0.18},
            "base_subtraction": {"value": 0.05},
            "upper_limit_base": {"value": 0.25},
            "fashion_adjustment": {"value": 0.08},
            "minimum_threshold": {"value": 0.12},
        }}
        result = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=True, rules=rules)
        assert result >= 0.18  # Must be at least the floor_fashion


class TestG73WithRules:
    """Test _compute_g73 reads display bounds from rules."""

    def test_custom_display_max(self):
        """Custom display_max clamps high values."""
        rules = {"marketing": {"display_max": {"value": 0.20}, "display_min": {"value": 0.10}}}
        result = _compute_g73("✔️", 0.30, 200_000_000, rules=rules)
        assert "20%" in result  # Clamped to 20% not 30%

    def test_custom_display_min(self):
        """Custom display_min clamps low values."""
        rules = {"marketing": {"display_max": {"value": 0.25}, "display_min": {"value": 0.15}}}
        result = _compute_g73("✔️", 0.05, 200_000_000, rules=rules)
        assert "15%" in result  # Clamped to 15% not 5%

    def test_rules_none_fallback(self):
        """rules=None uses default display bounds (0.10 - 0.25)."""
        result = _compute_g73("✔️", 0.15, 200_000_000, rules=None)
        assert "15%" in result
        assert "💡" in result

    def test_rules_missing_marketing_category(self):
        """Rules without marketing key falls back to defaults."""
        rules = {"operational": {}}
        result = _compute_g73("✔️", 0.15, 200_000_000, rules=rules)
        assert "15%" in result

    def test_rejected_verdicts_still_return_budget_with_rules(self):
        """Custom marketing rules still apply for rejected verdicts."""
        rules = {"marketing": {"display_max": {"value": 0.30}, "display_min": {"value": 0.05}}}
        result = _compute_g73("❌", 0.15, 200_000_000, rules=rules)
        assert "💡" in result
        assert "15%" in result


# ---------------------------------------------------------------------------
# End-to-end marketing rules propagation (moved from integration — Story 5-4)
# ---------------------------------------------------------------------------


class TestMarketingRulesPropagation:
    """Test calculate_score with custom marketing rules affects G72, G73, and email."""

    CALC_RESULTS = {
        "discount": {
            "details": {"fake_discount_flag": False},
            "output_text": "% Diskon TOP SKU: 25.0%\nRange: 15.0% ~ 35.0%\nVoucher 3.0%\nPaket Diskon 1.0%",
        },
        "top_sku": {
            "details": {
                "average_stock": 30,
                "output_1": [
                    {"rata2_harga_jual": 180_000},
                    {"rata2_harga_jual": 140_000},
                ],
            },
            "output_text": "",
        },
        "ads_keyword": {"details": {}, "output_text": ""},
    }

    def test_custom_marketing_rules_change_g72_g73(self, full_manual_data):
        """Custom marketing rules with higher floor change marketing percentage and budget."""
        calculate_score(
            manual_data=full_manual_data,
            calculator_results=self.CALC_RESULTS,
            template="fashion",
            verdict="✔️",
            store_name="Test Store",
            period="Jan 2026",
            brand_name="TestBrand",
            rules=DEFAULT_RULES,
            rule_version=1,
        )

        custom_rules = {
            **DEFAULT_RULES,
            "marketing": {
                "floor": {"value": 0.12},
                "floor_fashion": {"value": 0.20},
                "base_subtraction": {"value": 0.03},
                "upper_limit_base": {"value": 0.20},
                "fashion_adjustment": {"value": 0.05},
                "minimum_threshold": {"value": 0.10},
                "display_max": {"value": 0.30},
                "display_min": {"value": 0.05},
            },
        }
        result_custom = calculate_score(
            manual_data=full_manual_data,
            calculator_results=self.CALC_RESULTS,
            template="fashion",
            verdict="✔️",
            store_name="Test Store",
            period="Jan 2026",
            brand_name="TestBrand",
            rules=custom_rules,
            rule_version=2,
        )

        assert result_custom.marketing_percentage == "20%"
        assert "20%" in result_custom.marketing_budget

    def test_marketing_changes_propagate_to_email_body(self, full_manual_data):
        """Custom marketing rules propagate to email body."""
        calc_results = {
            **self.CALC_RESULTS,
            "top_sku": {
                "details": {
                    "average_stock": 30,
                    "output_1": [{"rata2_harga_jual": 180_000}],
                },
                "output_text": "",
            },
        }

        custom_rules = {
            **DEFAULT_RULES,
            "marketing": {
                "floor": {"value": 0.12},
                "floor_fashion": {"value": 0.22},
                "base_subtraction": {"value": 0.03},
                "upper_limit_base": {"value": 0.30},
                "fashion_adjustment": {"value": 0.05},
                "minimum_threshold": {"value": 0.10},
                "display_max": {"value": 0.30},
                "display_min": {"value": 0.10},
            },
        }

        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=calc_results,
            template="fashion",
            verdict="✔️",
            store_name="Test Store",
            period="Jan 2026",
            brand_name="TestBrand",
            rules=custom_rules,
            rule_version=2,
        )

        assert result.marketing_budget != ""
        assert "22%" in result.marketing_budget
        assert "22%" in result.email_body


# ---------------------------------------------------------------------------
# _format_message_template helper tests (Story 5-5, Task 3)
# ---------------------------------------------------------------------------


class TestFormatMessageTemplate:
    def test_basic_substitution(self):
        result = _format_message_template("Hello {name}", name="World")
        assert result == "Hello World"

    def test_multiple_placeholders(self):
        result = _format_message_template("{a} and {b}", a="X", b="Y")
        assert result == "X and Y"

    def test_missing_placeholder_stays(self):
        result = _format_message_template("Value is {missing}")
        assert result == "Value is {missing}"

    def test_partial_placeholders(self):
        result = _format_message_template("{present} and {absent}", present="OK")
        assert result == "OK and {absent}"

    def test_extra_kwargs_ignored(self):
        result = _format_message_template("{a}", a="1", b="2", c="3")
        assert result == "1"

    def test_empty_template(self):
        result = _format_message_template("")
        assert result == ""

    def test_no_placeholders(self):
        result = _format_message_template("Static text")
        assert result == "Static text"

    def test_unicode_in_template(self):
        result = _format_message_template("✔️ {val_str} [Sudah Baik]", val_str="0.5%")
        assert result == "✔️ 0.5% [Sudah Baik]"

    def test_unmatched_opening_brace(self):
        result = _format_message_template("Value is {broken", val_str="0.5%")
        assert result == "Value is {broken"

    def test_unmatched_closing_brace(self):
        result = _format_message_template("50% discount}", val_str="0.5%")
        assert result == "50% discount}"

    def test_mixed_valid_and_malformed(self):
        result = _format_message_template("{val_str} and {broken", val_str="0.5%")
        assert result == "{val_str} and {broken"  # returns raw on error


# ---------------------------------------------------------------------------
# Message template tests — each generator with custom templates (Story 5-5, Task 8)
# ---------------------------------------------------------------------------


class TestMessageTemplatesOperational:
    """Test operational message generators read templates from rules."""

    def test_custom_pass_template(self):
        rules = {**DEFAULT_RULES, "operational": {
            **DEFAULT_RULES["operational"],
            "unfulfilled_order_rate": {
                **DEFAULT_RULES["operational"]["unfulfilled_order_rate"],
                "message_pass": "CUSTOM PASS: {val_str}",
            },
        }}
        data = {"operational": {"unfulfilledOrderRate": 0.5}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        ops = result.category_scores[0]
        g7 = next(r for r in ops.rows if r.row == 7)
        assert g7.message == "CUSTOM PASS: 0.5%"

    def test_custom_fail_template(self):
        rules = {**DEFAULT_RULES, "operational": {
            **DEFAULT_RULES["operational"],
            "unfulfilled_order_rate": {
                **DEFAULT_RULES["operational"]["unfulfilled_order_rate"],
                "message_fail": "BAD: {val_str} needs <{threshold}%",
            },
        }}
        data = {"operational": {"unfulfilledOrderRate": 2.0}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        ops = result.category_scores[0]
        g7 = next(r for r in ops.rows if r.row == 7)
        assert g7.message == "BAD: 2.0% needs <1%"

    def test_all_operational_rows_customizable(self):
        """All 5 operational rows read from rules."""
        rules = {**DEFAULT_RULES, "operational": {
            "unfulfilled_order_rate": {**DEFAULT_RULES["operational"]["unfulfilled_order_rate"],
                "message_pass": "R7 PASS {val_str}"},
            "late_shipment_rate": {**DEFAULT_RULES["operational"]["late_shipment_rate"],
                "message_pass": "R8 PASS {val_str}"},
            "preparation_time": {**DEFAULT_RULES["operational"]["preparation_time"],
                "message_pass": "R9 PASS {val_str}"},
            "chat_response_rate": {**DEFAULT_RULES["operational"]["chat_response_rate"],
                "message_pass": "R10 PASS {val_str}"},
            "overall_rating": {**DEFAULT_RULES["operational"]["overall_rating"],
                "message_pass": "R11 PASS {val_str}"},
        }}
        data = {"operational": {
            "unfulfilledOrderRate": 0.5, "lateShipmentRate": 0.3,
            "preparationTime": 0.8, "chatResponseRate": 98.0, "overallRating": 4.9,
        }}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        ops = result.category_scores[0]
        for row in ops.rows:
            assert row.message.startswith(f"R{row.row} PASS"), f"Row {row.row}: {row.message}"

    def test_fallback_when_rules_none(self):
        """rules=None still produces correct default messages."""
        data = {"operational": {"unfulfilledOrderRate": 0.5}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=None,
        )
        ops = result.category_scores[0]
        g7 = next(r for r in ops.rows if r.row == 7)
        assert "[Sudah Baik]" in g7.message

    def test_fallback_when_template_missing(self):
        """Rules without message fields still produce correct messages."""
        rules = {**DEFAULT_RULES, "operational": {
            "unfulfilled_order_rate": {"threshold": 1.0, "points": 4, "comparison": "lte"},
            "late_shipment_rate": {"threshold": 1.0, "points": 3, "comparison": "lte"},
            "preparation_time": {"threshold": 1.0, "points": 3, "comparison": "lte"},
            "chat_response_rate": {"threshold": 95.0, "comparison": "gte", "info_only": True},
            "overall_rating": {"threshold": 4.7, "comparison": "gte", "info_only": True},
        }}
        data = {"operational": {"unfulfilledOrderRate": 0.5}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        ops = result.category_scores[0]
        g7 = next(r for r in ops.rows if r.row == 7)
        assert g7.message != ""  # Fallback should produce a message


class TestMessageTemplatesBusiness:
    """Test business message generators read templates from rules."""

    def test_custom_sales_trend_pass(self):
        rules = {**DEFAULT_RULES, "business": {
            **DEFAULT_RULES["business"],
            "monthly_sales_trend": {
                **DEFAULT_RULES["business"]["monthly_sales_trend"],
                "message_pass": "SALES UP: {idr_val} by {change_pct}%",
            },
        }}
        data = {"business": {
            "salesMonth0": 200_000_000, "salesMonth1": 180_000_000,
            "salesMonth2": 190_000_000, "salesMonth3": 170_000_000,
            "salesMonth4": 160_000_000, "salesMonth5": 150_000_000,
        }}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        biz = result.category_scores[1]
        g13 = next(r for r in biz.rows if r.row == 13)
        assert "SALES UP:" in g13.message

    def test_custom_severe_drop_addendum(self):
        rules = {**DEFAULT_RULES, "business": {
            **DEFAULT_RULES["business"],
            "monthly_sales_trend": {
                **DEFAULT_RULES["business"]["monthly_sales_trend"],
                "message_fail_severe": "\nCRITICAL: Sales dropped severely!",
            },
        }}
        data = {"business": {
            "salesMonth0": 50_000_000, "salesMonth1": 200_000_000,
            "salesMonth2": 200_000_000, "salesMonth3": 200_000_000,
            "salesMonth4": 200_000_000, "salesMonth5": 200_000_000,
        }}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        biz = result.category_scores[1]
        g13 = next(r for r in biz.rows if r.row == 13)
        assert "CRITICAL: Sales dropped severely!" in g13.message

    def test_custom_conversion_template(self):
        rules = {**DEFAULT_RULES, "business": {
            **DEFAULT_RULES["business"],
            "conversion_rate": {
                **DEFAULT_RULES["business"]["conversion_rate"],
                "message_pass": "CONV OK: {val_str}",
                "message_fail": "CONV BAD: {val_str}, need {benchmark}",
            },
        }}
        data = {"business": {"salesMonth0": 200_000_000},
                "visitors": {"totalVisitors": 100_000}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        biz = result.category_scores[1]
        g20 = next(r for r in biz.rows if r.row == 20)
        assert "CONV" in g20.message


class TestMessageTemplatesVisitors:
    """Test visitor message generators read templates from rules."""

    def test_custom_returning_visitors(self):
        rules = {**DEFAULT_RULES, "visitors": {
            **DEFAULT_RULES["visitors"],
            "returning_visitors_pct": {
                **DEFAULT_RULES["visitors"]["returning_visitors_pct"],
                "message_pass": "VISITORS OK: {val_str}",
            },
        }}
        data = {"visitors": {"totalVisitors": 100_000, "returningVisitors": 30_000, "totalFollowers": 60_000}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        vis = result.category_scores[2]
        g28 = next(r for r in vis.rows if r.row == 28)
        assert "VISITORS OK:" in g28.message

    def test_custom_followers(self):
        rules = {**DEFAULT_RULES, "visitors": {
            **DEFAULT_RULES["visitors"],
            "followers": {
                **DEFAULT_RULES["visitors"]["followers"],
                "message_pass": "FOLLOWERS GREAT: {val_str}",
            },
        }}
        data = {"visitors": {"totalVisitors": 100_000, "returningVisitors": 30_000, "totalFollowers": 60_000}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        vis = result.category_scores[2]
        g29 = next(r for r in vis.rows if r.row == 29)
        assert "FOLLOWERS GREAT:" in g29.message


class TestMessageTemplatesPromo:
    """Test promo message generators read templates from rules."""

    def test_custom_individual_messages(self):
        rules = {**DEFAULT_RULES, "promo_tools": {
            **DEFAULT_RULES["promo_tools"],
            "individual_messages": {
                "message_zero": "ZERO: {metric}",
                "message_dependent": "DEP: {metric} = {pct_str}",
                "message_fail": "FAIL: {metric} = {pct_str}",
                "message_pass": "PASS: {metric} ({pct_str})",
                "message_pass_afiliasi": "AFIL: {metric} ({pct_str})",
            },
        }}
        data = {
            "promoTools": {
                "promoToko": 0, "paketDiskon": 40_000_000, "komboHemat": 5_000_000,
                "flashSale": 5_000_000, "voucher": 180_000_000, "shopeeLive": 35_000_000,
                "gameToko": 3_000_000, "brandMembership": 4_000_000, "gratisOngkir": 10_000_000,
                "chatBroadcast": 3_000_000, "programAfiliasi": 40_000_000,
            },
            "business": {"salesMonth0": 200_000_000},
        }
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        promo = result.category_scores[3]
        # First row (promoToko=0) should use message_zero
        first_promo = next(r for r in promo.rows if r.row == 31)
        assert "ZERO:" in first_promo.message

    def test_custom_summary_messages(self):
        rules = {**DEFAULT_RULES, "promo_tools": {
            **DEFAULT_RULES["promo_tools"],
            "usage_pct_threshold": {
                **DEFAULT_RULES["promo_tools"]["usage_pct_threshold"],
                "message_pass": "USAGE OK: {val_str}",
                "message_fail": "USAGE BAD: {val_str}",
            },
            "effectiveness_pct_threshold": {
                **DEFAULT_RULES["promo_tools"]["effectiveness_pct_threshold"],
                "message_pass": "EFF OK: {val_str}",
                "message_fail": "EFF BAD: {val_str}",
            },
        }}
        data = {
            "promoTools": {
                "promoToko": 20_000_000, "paketDiskon": 40_000_000, "komboHemat": 5_000_000,
                "flashSale": 5_000_000, "voucher": 180_000_000, "shopeeLive": 35_000_000,
                "gameToko": 3_000_000, "brandMembership": 4_000_000, "gratisOngkir": 10_000_000,
                "chatBroadcast": 3_000_000, "programAfiliasi": 40_000_000,
            },
            "business": {"salesMonth0": 200_000_000},
        }
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        promo = result.category_scores[3]
        g42 = next(r for r in promo.rows if r.row == 42)
        assert "USAGE" in g42.message


class TestMessageTemplatesProducts:
    """Test products message generators read templates from rules."""

    def test_custom_product_count_template(self):
        rules = {**DEFAULT_RULES, "products_status": {
            **DEFAULT_RULES["products_status"],
            "product_count": {
                **DEFAULT_RULES["products_status"]["product_count"],
                "message_pass": "PROD OK: {value_int} items",
            },
        }}
        data = {"products": {"productCount": 50, "storeStatus": "Shopee Mall"}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        prod = result.category_scores[4]
        g45 = next(r for r in prod.rows if r.row == 45)
        assert g45.message == "PROD OK: 50 items"

    def test_custom_store_status_template(self):
        rules = {**DEFAULT_RULES, "products_status": {
            **DEFAULT_RULES["products_status"],
            "store_status_points": {
                **DEFAULT_RULES["products_status"]["store_status_points"],
                "message_pass": "STATUS: {store_status} approved",
            },
        }}
        data = {"products": {"productCount": 50, "storeStatus": "Shopee Mall"}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        prod = result.category_scores[4]
        g46 = next(r for r in prod.rows if r.row == 46)
        assert g46.message == "STATUS: Shopee Mall approved"


class TestMessageTemplatesAds:
    """Test ads message generators read templates from rules."""

    def test_custom_roi_template(self):
        rules = {**DEFAULT_RULES, "ads": {
            **DEFAULT_RULES["ads"],
            "roi_threshold": {
                **DEFAULT_RULES["ads"]["roi_threshold"],
                "message_pass": "ROI GOOD: {val_str}",
            },
        }}
        data = {
            "ads": {"adSales": 50_000_000, "adCost": 5_000_000},
            "business": {"salesMonth0": 200_000_000},
        }
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        ads = result.category_scores[5]
        g50 = next(r for r in ads.rows if r.row == 50)
        assert "ROI GOOD:" in g50.message

    def test_custom_gmv_no_ads_template(self):
        rules = {**DEFAULT_RULES, "ads": {
            **DEFAULT_RULES["ads"],
            "gmv_ratio_threshold": {
                **DEFAULT_RULES["ads"]["gmv_ratio_threshold"],
                "message_no_ads": "NO ADS ACTIVE",
            },
        }}
        data = {
            "ads": {"adSales": 0, "adCost": 0},
            "business": {"salesMonth0": 200_000_000},
        }
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        ads = result.category_scores[5]
        g51 = next(r for r in ads.rows if r.row == 51)
        assert g51.message == "NO ADS ACTIVE"

    def test_custom_cost_ratio_too_minimal(self):
        rules = {**DEFAULT_RULES, "ads": {
            **DEFAULT_RULES["ads"],
            "cost_ratio_range": {
                **DEFAULT_RULES["ads"]["cost_ratio_range"],
                "message_too_minimal": "TOO LOW: {pct_str}, need {min}%-{max}%",
            },
        }}
        data = {
            "ads": {"adSales": 50_000_000, "adCost": 1_000_000},
            "business": {"salesMonth0": 200_000_000},
        }
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        ads = result.category_scores[5]
        g52 = next(r for r in ads.rows if r.row == 52)
        assert "TOO LOW:" in g52.message
        assert "5%" in g52.message
        assert "10%" in g52.message


class TestMessageTemplatesCampaign:
    """Test campaign message generators read templates from rules."""

    def test_custom_campaign_pass(self):
        rules = {**DEFAULT_RULES, "campaign": {
            "participation_pct_threshold": {
                **DEFAULT_RULES["campaign"]["participation_pct_threshold"],
                "message_pass": "CAMP OK: {pct_str}",
            },
        }}
        data = {"campaign": {"nominatedSessions": 19, "availableSessions": 20}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        camp = result.category_scores[6]
        g57 = next(r for r in camp.rows if r.row == 57)
        assert "CAMP OK:" in g57.message

    def test_custom_campaign_no_data(self):
        rules = {**DEFAULT_RULES, "campaign": {
            "participation_pct_threshold": {
                **DEFAULT_RULES["campaign"]["participation_pct_threshold"],
                "message_no_data": "NO CAMPAIGNS",
            },
        }}
        data = {"campaign": {"nominatedSessions": 0, "availableSessions": 0}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        camp = result.category_scores[6]
        g57 = next(r for r in camp.rows if r.row == 57)
        assert g57.message == "NO CAMPAIGNS"


class TestMessageTemplatesCompetition:
    """Test competition message generators read templates from rules."""

    def test_custom_competition_pass(self):
        rules = {**DEFAULT_RULES, "competition": {
            "message_pass": "COMPETITIVE",
            "message_fail": "NOT COMPETITIVE: IDR {market_price}",
        }}
        data = {
            "competition": {
                "product1": {"keyword": "sepatu", "sellingPrice": 180_000, "marketPrice": 200_000, "productName": "Sepatu A"},
            },
        }
        calc = {"top_sku": {"details": {
            "average_stock": 30,
            "output_1": [{"kode_variasi": "A1", "product_name": "Sepatu A", "rata2_harga_jual": 180_000}],
        }}}
        result = calculate_score(
            manual_data=data, calculator_results=calc,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        comp = result.category_scores[7]
        g61 = next(r for r in comp.rows if r.row == 61)
        assert "COMPETITIVE" in g61.message

    def test_custom_competition_fail(self):
        rules = {**DEFAULT_RULES, "competition": {
            "message_pass": "COMPETITIVE",
            "message_fail": "OVERPRICED: IDR {market_price}",
        }}
        data = {
            "competition": {
                "product1": {"keyword": "sepatu", "sellingPrice": 200_000, "marketPrice": 100_000, "productName": "Sepatu A"},
            },
        }
        calc = {"top_sku": {"details": {
            "average_stock": 30,
            "output_1": [{"kode_variasi": "A1", "product_name": "Sepatu A", "rata2_harga_jual": 200_000}],
        }}}
        result = calculate_score(
            manual_data=data, calculator_results=calc,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        comp = result.category_scores[7]
        g61 = next(r for r in comp.rows if r.row == 61)
        assert "OVERPRICED:" in g61.message


class TestMessageTemplatesG75:
    """Test G75 closing messages read from rules."""

    def test_custom_closing_messages(self):
        rules = {**DEFAULT_RULES, "interpretation": {
            **DEFAULT_RULES["interpretation"],
            "closing_messages": {
                "✔️": "CUSTOM APPROVED MESSAGE",
                "❌": "CUSTOM REJECTED MESSAGE",
                "❌ Non Mall": "CUSTOM NON MALL",
                "❌ No Brand": "CUSTOM NO BRAND",
                "❌ Opex": "CUSTOM OPEX",
                "❌ Stock": "CUSTOM STOCK",
            },
        }}
        assert _compute_g75("✔️", "TestStore", rules) == "CUSTOM APPROVED MESSAGE"
        assert _compute_g75("❌", "TestStore", rules) == "CUSTOM REJECTED MESSAGE"
        assert _compute_g75("❌ Non Mall", "TestStore", rules) == "CUSTOM NON MALL"
        assert _compute_g75("❌ No Brand", "TestStore", rules) == "CUSTOM NO BRAND"
        assert _compute_g75("❌ Opex", "TestStore", rules) == "CUSTOM OPEX"
        assert _compute_g75("❌ Stock", "TestStore", rules) == "CUSTOM STOCK"

    def test_custom_closing_with_store_name_placeholder(self):
        rules = {**DEFAULT_RULES, "interpretation": {
            **DEFAULT_RULES["interpretation"],
            "closing_messages": {
                **DEFAULT_RULES["interpretation"]["closing_messages"],
                "✔️": "Hello {store_name}, welcome!",
            },
        }}
        assert _compute_g75("✔️", "BrandX", rules) == "Hello BrandX, welcome!"

    def test_g75_rules_none_fallback(self):
        msg = _compute_g75("✔️", "TestStore", rules=None)
        assert "potensi" in msg.lower()
        assert "cal-bd2" in msg
        assert "TestStore" in msg

    def test_g75_th_marketplace_rewrites_default_link_from_rules(self):
        rules = {**DEFAULT_RULES, "interpretation": {
            **DEFAULT_RULES["interpretation"],
            "closing_messages": {
                **DEFAULT_RULES["interpretation"]["closing_messages"],
                "✔️": "Meet us at cal-bd2.ahacommerce.net",
            },
        }}
        msg = _compute_g75("✔️", "TestStore", rules=rules, marketplace="TH")
        assert "th-bd2.ahacommerce.net" in msg
        assert "cal-bd2.ahacommerce.net" not in msg

    def test_g75_rules_missing_closing(self):
        rules = {"interpretation": {}}
        msg = _compute_g75("✔️", "TestStore", rules=rules)
        assert "potensi" in msg.lower()  # Falls back to hardcoded
        assert "TestStore" in msg

    def test_g75_custom_closing_propagates_to_email(self, full_manual_data, full_calculator_results):
        rules = {**DEFAULT_RULES, "interpretation": {
            **DEFAULT_RULES["interpretation"],
            "closing_messages": {
                "✔️": "CUSTOM CLOSING IN EMAIL",
                "❌": "", "❌ Non Mall": "", "❌ No Brand": "",
                "❌ Opex": "", "❌ Stock": "",
            },
        }}
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        # The custom closing template still drives the raw G75 field.
        assert result.closing_message == "CUSTOM CLOSING IN EMAIL"
        # email_body is now produced by the unified renderer, which prefers the
        # i18n companion (closing_message_i18n) over the raw custom template —
        # matching what every send/preview surface already displayed.
        assert result.closing_message_i18n is not None
        assert result.closing_message_i18n.key == "closing.potential"


class TestMessageTemplateEndToEnd:
    """End-to-end: custom messages propagate to email body."""

    def test_custom_messages_in_email_body(self, full_manual_data, full_calculator_results):
        rules = {**DEFAULT_RULES, "operational": {
            **DEFAULT_RULES["operational"],
            "unfulfilled_order_rate": {
                **DEFAULT_RULES["operational"]["unfulfilled_order_rate"],
                "message_pass": "E2E TEST PASS: {val_str}",
            },
        }}
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        # The custom message template still drives the raw G-column message.
        op_cat = next(c for c in result.category_scores if c.category == "Kesehatan Operasional Toko")
        assert any("E2E TEST PASS:" in r.message for r in op_cat.rows)
        # email_body is now produced by the unified renderer, which prefers a
        # row's i18n companion over the raw custom template when one exists —
        # matching what every send/preview surface already displayed.
        assert result.email_body != ""

    def test_default_rules_produce_identical_messages(self, full_manual_data, full_calculator_results):
        """Default rules with message templates produce identical output to rules=None."""
        result_none = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=None,
        )
        result_default = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=DEFAULT_RULES,
        )
        # All messages should be identical
        for cat_none, cat_default in zip(result_none.category_scores, result_default.category_scores):
            for row_none, row_default in zip(cat_none.rows, cat_default.rows):
                assert row_none.message == row_default.message, (
                    f"Row {row_none.row}: '{row_none.message}' != '{row_default.message}'"
                )
        # Email body should be identical
        assert result_none.email_body == result_default.email_body
        # Closing message should be identical
        assert result_none.closing_message == result_default.closing_message


class TestMigrationTemplatesDrift:
    """Catch drift between DB migration templates and DEFAULT_RULES.

    Migration 012 seeds message templates into the DB. If DEFAULT_RULES is
    updated but the DB templates are not patched via a new migration, the DB
    values silently override the code defaults. This test extracts the
    effective DB state (012 + subsequent patches) and compares against
    DEFAULT_RULES to ensure they stay in sync.
    """

    @staticmethod
    def _build_effective_db_templates() -> dict:
        """Replay migration 012 + 019 + 020 + 021 + 027 + 028 patches to get the effective DB state."""
        import importlib

        m012 = importlib.import_module(
            "app.db.migrations.versions.012_add_message_templates"
        )
        m019 = importlib.import_module(
            "app.db.migrations.versions.019_sync_db_message_templates_with_code"
        )
        m020 = importlib.import_module(
            "app.db.migrations.versions.020_add_brackets_to_all_scoring_messages"
        )
        m021 = importlib.import_module(
            "app.db.migrations.versions.021_internationalize_currency_rp_to_idr"
        )
        m027 = importlib.import_module(
            "app.db.migrations.versions.027_update_message_templates_currency_placeholder"
        )
        m028 = importlib.import_module(
            "app.db.migrations.versions.028_fix_follower_threshold_comma_separator"
        )

        db: dict = {}
        # Merge shared messages from 012
        for category, rule_messages in m012.SHARED_MESSAGES.items():
            db[category] = {}
            for rule_key, msg_fields in rule_messages.items():
                db[category][rule_key] = dict(msg_fields)

        # Merge competition from 012
        db["competition"] = dict(m012.COMPETITION_MESSAGES)

        # Apply 019 patches
        m019._apply_patches(db, forward=True)

        # Apply 020 patches
        m020._apply_patches(db, forward=True)

        # Apply 021 patches
        m021._apply_patches(db, forward=True)

        # Apply 027 patches
        m027._apply_patches(db, forward=True)

        # Apply 028 patches
        m028._apply_patches(db, forward=True)

        return db

    @staticmethod
    def _extract_message_keys(d: dict) -> dict[str, str]:
        """Flatten a nested dict into {dotted_path: value} for message_* keys."""
        result = {}

        def _walk(obj: dict, prefix: str) -> None:
            for k, v in obj.items():
                path = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    _walk(v, path)
                elif isinstance(v, str) and k.startswith("message_"):
                    result[path] = v

        _walk(d, "")
        return result

    def test_db_templates_match_default_rules(self):
        """Every message template in the DB must match DEFAULT_RULES."""
        db_templates = self._build_effective_db_templates()
        db_msgs = self._extract_message_keys(db_templates)
        code_msgs = self._extract_message_keys(DEFAULT_RULES)

        mismatches = []
        for path, db_val in db_msgs.items():
            code_val = code_msgs.get(path)
            if code_val is None:
                continue  # DB has templates not in code defaults (extra is OK)
            if db_val != code_val:
                mismatches.append(
                    f"  {path}:\n"
                    f"    DB:   {db_val!r}\n"
                    f"    Code: {code_val!r}"
                )

        assert not mismatches, (
            "DB migration templates have drifted from DEFAULT_RULES.\n"
            "Create a new migration to sync them, or update DEFAULT_RULES.\n"
            + "\n".join(mismatches)
        )


class TestFollowerFormattingR023R024:
    """Verify follower val_str uses comma separator and fail message threshold uses >50,000."""

    def test_follower_val_str_uses_comma_when_value_is_40000(self):
        """R024: val_str for 40000 followers renders as '40,000' not '40.000'."""
        from app.calculators.scoring.messages import _generate_visitors_messages
        from app.calculators.scoring.models import CategoryScore, RowScore

        cat = CategoryScore(
            category="Analisis Pengunjung",
            score=0.0,
            max_score=5.0,
            rows=[
                RowScore(row=29, metric="Total Pengikut", value=40000,
                         benchmark=">50,000", verdict="❌", message="", score=0.0),
            ],
        )
        _generate_visitors_messages(cat)
        msg = cat.rows[0].message
        assert "40,000" in msg, f"Expected comma-separated '40,000' in message, got: {msg}"
        assert "40.000" not in msg, f"Dot-separated '40.000' must not appear in message, got: {msg}"

    def test_follower_fail_message_contains_comma_threshold(self):
        """R023: Follower fail message contains '>50,000' not '>50.000'."""
        from app.calculators.scoring.messages import _generate_visitors_messages
        from app.calculators.scoring.models import CategoryScore, RowScore

        cat = CategoryScore(
            category="Analisis Pengunjung",
            score=0.0,
            max_score=5.0,
            rows=[
                RowScore(row=29, metric="Total Pengikut", value=40000,
                         benchmark=">50,000", verdict="❌", message="", score=0.0),
            ],
        )
        _generate_visitors_messages(cat)
        msg = cat.rows[0].message
        assert ">50,000" in msg, f"Expected '>50,000' in fail message, got: {msg}"
        assert ">50.000" not in msg, f"'>50.000' must not appear in fail message, got: {msg}"

    def test_default_rules_followers_message_fail_uses_comma(self):
        """R023: DEFAULT_RULES followers message_fail contains '>50,000'."""
        msg = DEFAULT_RULES["visitors"]["followers"]["message_fail"]
        assert ">50,000" in msg, f"Expected '>50,000' in DEFAULT_RULES, got: {msg}"
        assert ">50.000" not in msg, f"'>50.000' must not appear in DEFAULT_RULES, got: {msg}"


class TestComputeG66JutaR026:
    """Verify _compute_g66 uses juta for ID marketplace and raw numbers for TH."""

    def test_compute_g66_uses_juta_when_marketplace_is_id(self):
        """R026: ID marketplace sales range displays in juta."""
        from app.calculators.scoring.computations import _compute_g66

        manual_data = {
            "business": {
                "salesMonth0": 50_000_000,
                "salesMonth1": 80_000_000,
                "salesMonth2": 60_000_000,
                "salesMonth3": 70_000_000,
                "salesMonth4": 90_000_000,
                "salesMonth5": 100_000_000,
            }
        }
        result = _compute_g66([], manual_data, "", marketplace="ID")
        assert "juta" in result, f"Expected 'juta' in ID marketplace g66, got: {result}"



    def test_compute_g66_uses_updated_indonesian_conclusion_copy(self):
        from app.calculators.scoring.computations import _compute_g66
        from app.calculators.scoring.models import CategoryScore, RowScore

        categories = [
            CategoryScore(
                category="Kesehatan Operasional Toko",
                score=0,
                max_score=10,
                rows=[RowScore(row=10, metric="Persentase Chat Dibalas", value=90, benchmark=">95%", verdict="❌", message="", score=0)],
            ),
            CategoryScore(
                category="Promo Toko",
                score=0,
                max_score=15,
                rows=[RowScore(row=43, metric="% Efektifitas", value=0.5, benchmark=">80%", verdict="❌", message="", score=0)],
            ),
            CategoryScore(
                category="Partisipasi Campaign",
                score=0,
                max_score=10,
                rows=[RowScore(row=57, metric="Partisipasi", value=0.5, benchmark=">80%", verdict="❌", message="", score=0)],
            ),
        ]
        manual_data = {
            "business": {
                "salesMonth0": 50_000_000,
                "salesMonth1": 80_000_000,
                "salesMonth2": 60_000_000,
                "salesMonth3": 70_000_000,
                "salesMonth4": 90_000_000,
                "salesMonth5": 100_000_000,
            }
        }

        result = _compute_g66(categories, manual_data, "12.0% ~ 18.0%", marketplace="ID")

        assert "Kualitas operasional toko sudah cukup baik, hanya tingkat response chat masih dapat ditingkatkan." in result
        assert "Nama produk disarankan untuk dimulai dengan nama brand dan mencantumkan FAB produk (Feature, Advantage, & Benefit)." in result
        assert "Gambar produk utama sebaiknya menampilkan logo brand termasuk FAB (Features, Advantage, Benefit)." in result
        assert "Beberapa fitur promosi masih belum optimal." in result
        assert "Partisipasi Campaign Shopee belum maksimal." in result
        assert "Pastikan produk yang stoknya habis diarsipkan" in result
        assert "Range diskon: 12.0% ~ 18.0%" in result

    def test_compute_g66_uses_raw_numbers_when_marketplace_is_th(self):
        """R026: TH marketplace sales range displays raw comma-formatted numbers, not juta."""
        from app.calculators.scoring.computations import _compute_g66

        manual_data = {
            "business": {
                "salesMonth0": 50_000_000,
                "salesMonth1": 80_000_000,
                "salesMonth2": 60_000_000,
                "salesMonth3": 70_000_000,
                "salesMonth4": 90_000_000,
                "salesMonth5": 100_000_000,
            }
        }
        result = _compute_g66([], manual_data, "", marketplace="TH")
        assert "juta" not in result, f"'juta' must not appear in TH marketplace g66, got: {result}"
        assert "50,000,000" in result, f"Expected comma-formatted number in TH g66, got: {result}"
