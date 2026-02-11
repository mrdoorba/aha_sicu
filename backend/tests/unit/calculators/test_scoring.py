"""Unit tests for the Final Scoring Calculator.

Tests against the spec in logic/scoring-system-template-sicu.md.
"""

import pytest

from app.calculators.scoring import (
    CategoryScore,
    RowScore,
    ScoringResult,
    _compute_g68,
    _compute_g72,
    _compute_g73,
    _compute_g75,
    _extract_pct,
    _fmt_idr,
    _parse_d73_percentages,
    _promo_verdict,
    _safe_num,
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
        avg = sum([200, 180, 190, 170, 160, 150]) * 1_000_000 / 6
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
        avg = (50 + 200 * 5) * 1_000_000 / 6  # ~175M
        # 175M >= 50M * 1.10 = 55M → FAIL (H13=0)
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
        avg = (80 + 70 + 60 + 50 + 40 + 30) * 1_000_000 / 6  # 55M
        h19_row = next(r for r in cat.rows if r.row == 19)
        assert h19_row.score == 0.0  # 55M < 100M


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
        assert cat.score == -5.0  # 0 < 12 → -5


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
        assert cat.score == 5.0  # No flag → default False → 5


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
        result = _compute_g73("✔️", 0.15, 200_000_000, is_fashion=True)
        assert "💡" in result
        assert "15%" in result
        assert "30.000.000" in result  # 200M * 15%

    def test_rejected_verdict_suppressed(self):
        result = _compute_g73("❌", 0.15, 200_000_000, is_fashion=True)
        assert result == ""

    def test_circle_verdict_suppressed(self):
        result = _compute_g73("⭕️", 0.15, 200_000_000, is_fashion=True)
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
        # Stock should be -5 (missing data → 0 < 12)
        stock_cat = next(c for c in result.category_scores if c.category == "Stok")
        assert stock_cat.score == -5.0
        # Discount should be 5 (no flag → pass)
        disc_cat = next(c for c in result.category_scores if c.category == "Discount")
        assert disc_cat.score == 5.0

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
