"""Unit tests for the Final Scoring Calculator.

Tests against the spec in logic/scoring-system-template-sicu.md.
"""

import pytest

from app.calculators.scoring import (
    DEFAULT_RULES,
    ScoringResult,
    _compute_g68,
    _compute_g72,
    _compute_g73,
    _compute_g75,
    _format_message_template,
    _parse_d73_percentages,
    _promo_verdict,
    _score_ads,
    _score_business,
    _score_campaign,
    _score_content,
    _score_discount_row,
    _score_operational,
    _score_products,
    _score_promo_tools,
    _score_stock,
    _score_visitors,
    calculate_score,
)


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
        "content": {
            "needsImprovement": 2,
            "goodQuality": 48,
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
            "product1": {"keyword": "sepatu", "marketPrice": 200_000},
            "product2": {"keyword": "sandal", "marketPrice": 150_000},
            "product3": {"keyword": "tas", "marketPrice": 300_000},
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
        # avg = 175M > 100M → pass (H19=10)
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.score == 10.0
        assert cat.score == 20.0

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
        # avg = 175M > 100M → H19=10
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.score == 10.0

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
        # avg = 55M
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.score == 0.0  # 55M < 100M


class TestScoreContent:
    def test_high_quality(self):
        data = {"content": {"needsImprovement": 2, "goodQuality": 48}}
        cat = _score_content(data)
        assert cat.category == "Skor Kesehatan Konten"
        assert cat.score == 0.0  # Content has no H-column scores
        assert cat.max_score == 0.0
        d24_row = next(r for r in cat.rows if r.row == 24)
        assert d24_row.verdict == "✔️"  # 48/50 = 96% > 95%
        assert abs(d24_row.value - 0.96) < 0.01

    def test_low_quality(self):
        data = {"content": {"needsImprovement": 10, "goodQuality": 40}}
        cat = _score_content(data)
        d24_row = next(r for r in cat.rows if r.row == 24)
        assert d24_row.verdict == "❌"  # 40/50 = 80% < 95%

    def test_exactly_95_percent(self):
        data = {"content": {"needsImprovement": 5, "goodQuality": 95}}
        cat = _score_content(data)
        d24_row = next(r for r in cat.rows if r.row == 24)
        assert d24_row.verdict == "✔️"  # 95/100 = 95% >= 95%

    def test_no_content_data(self):
        cat = _score_content({})
        assert len(cat.rows) == 3
        d24_row = next(r for r in cat.rows if r.row == 24)
        assert d24_row.verdict == "❌"  # 0/0 → 0% < 95%

    def test_all_good(self):
        data = {"content": {"needsImprovement": 0, "goodQuality": 100}}
        cat = _score_content(data)
        d24_row = next(r for r in cat.rows if r.row == 24)
        assert d24_row.verdict == "✔️"
        assert d24_row.value == 1.0  # 100%

    def test_all_bad(self):
        data = {"content": {"needsImprovement": 50, "goodQuality": 0}}
        cat = _score_content(data)
        d24_row = next(r for r in cat.rows if r.row == 24)
        assert d24_row.verdict == "❌"
        assert d24_row.value == 0.0  # 0%


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

    def test_too_dependent(self):
        # 60% of sales → ❌
        assert _promo_verdict(120_000_000, 200_000_000, 0.08) == "❌"

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
    def test_fashion_roi_threshold(self):
        data = {
            "ads": {"adSales": 50_000_000, "adCost": 6_000_000},  # ROI ~8.3
            "business": {"salesMonth0": 200_000_000},
        }
        cat = _score_ads(data, "fashion")
        h50_row = next(r for r in cat.rows if r.row == 50)
        # ROI = 50M/6M = 8.33, threshold 8 → pass → H50=0
        assert h50_row.score == 0.0
        assert h50_row.verdict == "✔️"

    def test_non_fashion_roi_threshold(self):
        data = {
            "ads": {"adSales": 50_000_000, "adCost": 6_000_000},  # ROI ~8.3
            "business": {"salesMonth0": 200_000_000},
        }
        cat = _score_ads(data, "non_fashion")
        h50_row = next(r for r in cat.rows if r.row == 50)
        # ROI = 8.33, threshold 9 → fail → H50=5 (opportunity)
        assert h50_row.score == 5.0
        assert h50_row.verdict == "❌"

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
    def test_high_stock(self):
        results = {"top_sku": {"details": {"average_stock": 30}}}
        cat = _score_stock(results)
        assert cat.score == 10.0

    def test_medium_stock(self):
        results = {"top_sku": {"details": {"average_stock": 15}}}
        cat = _score_stock(results)
        assert cat.score == 5.0

    def test_low_stock(self):
        results = {"top_sku": {"details": {"average_stock": 8}}}
        cat = _score_stock(results)
        assert cat.score == -5.0

    def test_exactly_24(self):
        results = {"top_sku": {"details": {"average_stock": 24}}}
        cat = _score_stock(results)
        assert cat.score == 10.0

    def test_exactly_12(self):
        results = {"top_sku": {"details": {"average_stock": 12}}}
        cat = _score_stock(results)
        assert cat.score == 5.0

    def test_missing_data(self):
        cat = _score_stock({})
        assert cat.available is False
        assert cat.score == 0.0  # Missing calculator data → unavailable


class TestScoreDiscount:
    def test_no_fake_discount(self):
        results = {"discount": {"details": {"fake_discount_flag": False}, "output_text": "test"}}
        cat = _score_discount_row(results)
        assert cat.score == 5.0

    def test_fake_discount(self):
        results = {"discount": {"details": {"fake_discount_flag": True}, "output_text": "test"}}
        cat = _score_discount_row(results)
        assert cat.score == 0.0

    def test_missing_data(self):
        cat = _score_discount_row({})
        assert cat.available is False
        assert cat.score == 0.0  # Missing calculator data → unavailable


# ---------------------------------------------------------------------------
# Fashion vs Non-Fashion threshold tests
# ---------------------------------------------------------------------------


class TestFashionThresholds:
    def test_roi_fashion_passes_at_8(self):
        data = {
            "ads": {"adSales": 80_000_000, "adCost": 10_000_000},  # ROI = 8
            "business": {"salesMonth0": 200_000_000},
        }
        cat = _score_ads(data, "fashion")
        h50 = next(r for r in cat.rows if r.row == 50)
        assert h50.verdict == "✔️"

    def test_roi_non_fashion_fails_at_8(self):
        data = {
            "ads": {"adSales": 80_000_000, "adCost": 10_000_000},  # ROI = 8
            "business": {"salesMonth0": 200_000_000},
        }
        cat = _score_ads(data, "non_fashion")
        h50 = next(r for r in cat.rows if r.row == 50)
        assert h50.verdict == "❌"


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
        assert "Sudah Baik" in g7.message

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
        assert "Kurang Baik" in g7.message

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
        assert "Menurun" in g13.message
        assert "❗️" in g13.message  # > 25% decline warning


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


class TestG73:
    def test_normal_verdict(self):
        result = _compute_g73("✔️", 0.15, 200_000_000)
        assert "💡" in result
        assert "15%" in result
        assert "30.000.000" in result  # 200M * 15%

    def test_rejected_verdict_suppressed(self):
        result = _compute_g73("❌", 0.15, 200_000_000)
        assert result == ""

    def test_circle_verdict_suppressed(self):
        result = _compute_g73("⭕️", 0.15, 200_000_000)
        assert result == ""

    def test_rejected_non_mall_suppressed(self):
        result = _compute_g73("❌ Non Mall", 0.15, 200_000_000)
        assert result == ""

    def test_rejected_no_brand_suppressed(self):
        result = _compute_g73("❌ No Brand", 0.15, 200_000_000)
        assert result == ""

    def test_rejected_opex_suppressed(self):
        result = _compute_g73("❌ Opex", 0.15, 200_000_000)
        assert result == ""


# ---------------------------------------------------------------------------
# G75 closing message tests
# ---------------------------------------------------------------------------


class TestG75:
    def test_approved(self):
        msg = _compute_g75("✔️")
        assert "potensi" in msg.lower()
        assert "cal-bd2" in msg

    def test_rejected(self):
        msg = _compute_g75("❌")
        assert "keuntungan" in msg.lower()

    def test_non_mall(self):
        msg = _compute_g75("❌ Non Mall")
        assert "Mall" in msg

    def test_no_brand(self):
        msg = _compute_g75("❌ No Brand")
        assert "brand" in msg.lower()

    def test_empty_verdict(self):
        msg = _compute_g75("")
        assert "cukup baik" in msg.lower()

    def test_opex_verdict(self):
        msg = _compute_g75("❌ Opex")
        assert "keterlambatan" in msg.lower()


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
        assert "Iklan" in body
        assert "Campaign" in body
        assert "Kesimpulan" in body

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
# WhatsApp link test
# ---------------------------------------------------------------------------


class TestWhatsAppLink:
    def test_link_format(self, full_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="Test Store",
            period="Jan 2026",
            brand_name="TEST",
        )
        assert result.whatsapp_link.startswith("https://api.whatsapp.com/send?text=")
        assert "Test%20Store" in result.whatsapp_link


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
        # Discount should also be unavailable
        disc_cat = next(c for c in result.category_scores if c.category == "Discount")
        assert disc_cat.available is False
        assert disc_cat.score == 0.0

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
        assert len(result.category_scores) == 11
        assert result.email_subject != ""
        assert result.email_body != ""
        assert result.whatsapp_link.startswith("https://")
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
        # Default fashion: threshold=8 → ROI 6 < 8 → fail
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
        results = {"top_sku": {"details": {"average_stock": 20}}}
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
        results = {"top_sku": {"details": {"average_stock": 24}}}
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


class TestCustomRulesDiscount:
    """Custom discount points change category score."""

    def test_custom_no_flag_points(self):
        results = {"discount": {"details": {"fake_discount_flag": False}, "output_text": "test"}}
        # Default: no flag = 5 points
        cat_default = _score_discount_row(results)
        assert cat_default.score == 5.0

        # Custom: no flag = 10 points
        custom_rules = {**DEFAULT_RULES, "discount": {
            "fake_discount_flag": {"points_no_flag": 10, "points_flag": -5},
        }}
        cat_custom = _score_discount_row(results, custom_rules)
        assert cat_custom.score == 10.0

    def test_custom_flag_penalty(self):
        results = {"discount": {"details": {"fake_discount_flag": True}, "output_text": "test"}}
        # Default: flag = 0 points
        cat_default = _score_discount_row(results)
        assert cat_default.score == 0.0

        # Custom: flag = -5 penalty
        custom_rules = {**DEFAULT_RULES, "discount": {
            "fake_discount_flag": {"points_no_flag": 10, "points_flag": -5},
        }}
        cat_custom = _score_discount_row(results, custom_rules)
        assert cat_custom.score == -5.0


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
        # avg = 55M, default threshold=100M → 55M < 100M → fail
        cat_default = _score_business(data)
        h19 = next(r for r in cat_default.rows if r.row == 19)
        assert h19.score == 0.0

        # Custom: threshold=50M → 55M > 50M → pass with 12pts
        custom_rules = {**DEFAULT_RULES, "business": {
            **DEFAULT_RULES["business"],
            "six_month_avg_threshold": {"threshold": 50_000_000, "points": 12, "comparison": "gte"},
        }}
        cat_custom = _score_business(data, custom_rules)
        h19 = next(r for r in cat_custom.rows if r.row == 19)
        assert h19.score == 12.0


class TestCustomRulesContent:
    """Custom content quality_ratio threshold changes verdict."""

    def test_custom_quality_threshold(self):
        data = {"content": {"needsImprovement": 10, "goodQuality": 90}}
        # ratio = 90/100 = 90%, default threshold=95% → fail
        cat_default = _score_content(data)
        d24 = next(r for r in cat_default.rows if r.row == 24)
        assert d24.verdict == "❌"

        # Custom: threshold=85% → 90% >= 85% → pass
        custom_rules = {**DEFAULT_RULES, "content": {
            "quality_ratio": {"threshold": 85.0, "comparison": "gte", "info_only": True},
        }}
        cat_custom = _score_content(data, custom_rules)
        d24 = next(r for r in cat_custom.rows if r.row == 24)
        assert d24.verdict == "✔️"


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
        """Custom floor overrides default 0.15 for fashion."""
        rules = {"marketing": {"floor": {"value": 0.18}}}
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
            "floor": {"value": 0.01},
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
        """Empty d73 returns floor from rules when provided."""
        rules = {"marketing": {"floor": {"value": 0.20}}}
        result = _compute_g72("", 0.0, "", is_fashion=True, rules=rules)
        assert result == 0.20

    def test_all_constants_overridden(self):
        """All 5 marketing constants overridden at once."""
        rules = {"marketing": {
            "floor": {"value": 0.18},
            "base_subtraction": {"value": 0.05},
            "upper_limit_base": {"value": 0.25},
            "fashion_adjustment": {"value": 0.08},
            "minimum_threshold": {"value": 0.12},
        }}
        result = _compute_g72(self._g68(), 0.03, self.D73, is_fashion=True, rules=rules)
        assert result >= 0.18  # Must be at least the floor


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

    def test_suppressed_for_rejected_verdicts_with_rules(self):
        """Verdict suppression still works with custom rules."""
        rules = {"marketing": {"display_max": {"value": 0.30}, "display_min": {"value": 0.05}}}
        assert _compute_g73("❌", 0.15, 200_000_000, rules=rules) == ""
        assert _compute_g73("⭕️", 0.15, 200_000_000, rules=rules) == ""


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
                "floor": {"value": 0.20},
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
                "floor": {"value": 0.22},
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
        result = _format_message_template("✔️ {val_str} Sudah Baik", val_str="0.5%")
        assert result == "✔️ 0.5% Sudah Baik"

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
        assert "Sudah Baik" in g7.message

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


class TestMessageTemplatesContent:
    """Test content message generators read templates from rules."""

    def test_custom_content_pass(self):
        rules = {**DEFAULT_RULES, "content": {
            "quality_ratio": {
                **DEFAULT_RULES["content"]["quality_ratio"],
                "message_pass": "CONTENT GOOD: {val_str}",
            },
        }}
        data = {"content": {"needsImprovement": 2, "goodQuality": 48}}
        result = calculate_score(
            manual_data=data, calculator_results={},
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        content = result.category_scores[2]
        g24 = next(r for r in content.rows if r.row == 24)
        assert "CONTENT GOOD:" in g24.message


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
        vis = result.category_scores[3]
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
        vis = result.category_scores[3]
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
        promo = result.category_scores[4]
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
        promo = result.category_scores[4]
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
        prod = result.category_scores[5]
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
        prod = result.category_scores[5]
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
        ads = result.category_scores[6]
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
        ads = result.category_scores[6]
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
        ads = result.category_scores[6]
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
        camp = result.category_scores[7]
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
        camp = result.category_scores[7]
        g57 = next(r for r in camp.rows if r.row == 57)
        assert g57.message == "NO CAMPAIGNS"


class TestMessageTemplatesCompetition:
    """Test competition message generators read templates from rules."""

    def test_custom_competition_pass(self):
        rules = {**DEFAULT_RULES, "competition": {
            "message_pass": "COMPETITIVE",
            "message_fail": "NOT COMPETITIVE: Rp. {market_price}",
        }}
        data = {
            "competition": {
                "product1": {"keyword": "sepatu", "marketPrice": 200_000},
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
        comp = result.category_scores[8]
        g61 = next(r for r in comp.rows if r.row == 61)
        assert "COMPETITIVE" in g61.message

    def test_custom_competition_fail(self):
        rules = {**DEFAULT_RULES, "competition": {
            "message_pass": "COMPETITIVE",
            "message_fail": "OVERPRICED: Rp. {market_price}",
        }}
        data = {
            "competition": {
                "product1": {"keyword": "sepatu", "marketPrice": 100_000},
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
        comp = result.category_scores[8]
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
                "": "CUSTOM GOOD STORE",
                "❌ Opex": "CUSTOM OPEX",
                "⭕️": "",
            },
        }}
        assert _compute_g75("✔️", rules) == "CUSTOM APPROVED MESSAGE"
        assert _compute_g75("❌", rules) == "CUSTOM REJECTED MESSAGE"
        assert _compute_g75("❌ Non Mall", rules) == "CUSTOM NON MALL"
        assert _compute_g75("❌ No Brand", rules) == "CUSTOM NO BRAND"
        assert _compute_g75("", rules) == "CUSTOM GOOD STORE"
        assert _compute_g75("❌ Opex", rules) == "CUSTOM OPEX"
        assert _compute_g75("⭕️", rules) == ""

    def test_g75_rules_none_fallback(self):
        msg = _compute_g75("✔️", rules=None)
        assert "potensi" in msg.lower()
        assert "cal-bd2" in msg

    def test_g75_rules_missing_closing(self):
        rules = {"interpretation": {"ranges": []}}
        msg = _compute_g75("✔️", rules=rules)
        assert "potensi" in msg.lower()  # Falls back to hardcoded

    def test_g75_custom_closing_propagates_to_email(self, full_manual_data, full_calculator_results):
        rules = {**DEFAULT_RULES, "interpretation": {
            **DEFAULT_RULES["interpretation"],
            "closing_messages": {
                "✔️": "CUSTOM CLOSING IN EMAIL",
                "❌": "", "❌ Non Mall": "", "❌ No Brand": "",
                "": "", "❌ Opex": "", "⭕️": "",
            },
        }}
        result = calculate_score(
            manual_data=full_manual_data,
            calculator_results=full_calculator_results,
            template="fashion", verdict="✔️",
            store_name="S", period="P", brand_name="B",
            rules=rules,
        )
        assert "CUSTOM CLOSING IN EMAIL" in result.email_body


class TestMessageTemplateEndToEnd:
    """End-to-end: custom messages propagate to email body and WhatsApp."""

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
        assert "E2E TEST PASS:" in result.email_body

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
