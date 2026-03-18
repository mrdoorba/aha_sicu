"""Unit tests for THB marketplace scoring — currency formatting, messages,
benchmarks, conclusion text, and backward compatibility.

Verifies that the marketplace parameter threads correctly through the
scoring engine, producing THB-labelled output for Thailand and
IDR-labelled output (unchanged) for Indonesia.
"""

import pytest

from app.calculators.scoring import calculate_score, DEFAULT_RULES
from app.calculators.scoring.helpers import _fmt_currency, _fmt_idr
from app.calculators.scoring.computations import _compute_g66, _compute_g66_i18n
from app.calculators.scoring.messages import (
    _generate_business_messages,
    _generate_competition_messages,
)
from app.calculators.scoring.categories import _score_competition
from app.calculators.scoring.models import CategoryScore, RowScore, ScoringResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def thb_manual_data():
    """Manual data with THB-scale values (IDR / ~500)."""
    return {
        "operational": {
            "unfulfilledOrderRate": 0.5,
            "lateShipmentRate": 0.3,
            "preparationTime": 0.8,
            "chatResponseRate": 98.0,
            "overallRating": 4.9,
        },
        "business": {
            "salesMonth0": 400_000,    # ~200M IDR / 500
            "salesMonth1": 360_000,
            "salesMonth2": 380_000,
            "salesMonth3": 340_000,
            "salesMonth4": 320_000,
            "salesMonth5": 300_000,
        },
        "visitors": {
            "totalVisitors": 100_000,
            "returningVisitors": 30_000,
            "totalFollowers": 60_000,
        },
        "promoTools": {
            "promoToko": 40_000,
            "paketDiskon": 80_000,
            "komboHemat": 10_000,
            "flashSale": 10_000,
            "voucher": 360_000,
            "shopeeLive": 70_000,
            "gameToko": 6_000,
            "brandMembership": 8_000,
            "gratisOngkir": 20_000,
            "chatBroadcast": 6_000,
            "programAfiliasi": 80_000,
        },
        "products": {
            "productCount": 50,
            "storeStatus": "Shopee Mall",
        },
        "ads": {
            "adSales": 100_000,
            "adCost": 10_000,
        },
        "campaign": {
            "nominatedSessions": 18,
            "availableSessions": 20,
        },
        "competition": {
            "product1": {"keyword": "shoes", "sellingPrice": 500, "marketPrice": 600, "productName": "Shoe A"},
            "product2": {"keyword": "sandal", "sellingPrice": 300, "marketPrice": 350, "productName": "Sandal B"},
            "product3": {"keyword": "bag", "sellingPrice": 800, "marketPrice": 700, "productName": "Bag C"},
        },
    }


@pytest.fixture
def idr_manual_data():
    """Manual data with standard IDR-scale values."""
    return {
        "operational": {
            "unfulfilledOrderRate": 0.5,
            "lateShipmentRate": 0.3,
            "preparationTime": 0.8,
            "chatResponseRate": 98.0,
            "overallRating": 4.9,
        },
        "business": {
            "salesMonth0": 200_000_000,
            "salesMonth1": 180_000_000,
            "salesMonth2": 190_000_000,
            "salesMonth3": 170_000_000,
            "salesMonth4": 160_000_000,
            "salesMonth5": 150_000_000,
        },
        "visitors": {
            "totalVisitors": 100_000,
            "returningVisitors": 30_000,
            "totalFollowers": 60_000,
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
                    {"kode_variasi": "A1", "product_name": "Product A", "rata2_harga_jual": 500},
                    {"kode_variasi": "B1", "product_name": "Product B", "rata2_harga_jual": 300},
                    {"kode_variasi": "C1", "product_name": "Product C", "rata2_harga_jual": 800},
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
# a. TestFmtCurrency — currency formatting helper
# ---------------------------------------------------------------------------


class TestFmtCurrency:
    def test_fmt_currency_id_marketplace(self):
        assert _fmt_currency(100_000_000, "ID") == "100,000,000"

    def test_fmt_currency_th_marketplace(self):
        assert _fmt_currency(190_000, "TH") == "190,000"

    def test_fmt_currency_defaults_to_id(self):
        assert _fmt_currency(100_000_000) == "100,000,000"

    def test_fmt_currency_matches_fmt_idr(self):
        """_fmt_currency with ID marketplace produces identical output to _fmt_idr."""
        test_values = [0, 1, 999, 1_000, 50_000, 1_234_567, 100_000_000, 999_999_999]
        for val in test_values:
            assert _fmt_currency(val, "ID") == _fmt_idr(val), f"Mismatch for value {val}"

    def test_fmt_currency_zero(self):
        assert _fmt_currency(0, "TH") == "0"

    def test_fmt_currency_negative(self):
        assert _fmt_currency(-50_000, "TH") == "-50,000"


# ---------------------------------------------------------------------------
# b. TestTHBBusinessMessages — business message output with THB
# ---------------------------------------------------------------------------


class TestTHBBusinessMessages:
    def _make_business_cat(self, verdict: str) -> CategoryScore:
        """Create a CategoryScore with a row 13 (monthly sales) and given verdict."""
        return CategoryScore(
            category="Bisnis Analisis",
            score=5.0,
            max_score=5.0,
            rows=[
                RowScore(
                    row=13, metric="Tren Penjualan Bulanan",
                    value=400_000, benchmark="-", verdict=verdict,
                    message="", score=5.0,
                ),
            ],
        )

    def test_thb_business_pass_message_contains_thb(self):
        cat = self._make_business_cat("✔️")
        manual_data = {
            "business": {
                "salesMonth0": 400_000,
                "salesMonth1": 360_000,
                "salesMonth2": 380_000,
                "salesMonth3": 340_000,
                "salesMonth4": 320_000,
                "salesMonth5": 300_000,
            },
        }
        _generate_business_messages(cat, manual_data, rules=DEFAULT_RULES, marketplace="TH")
        row13 = next(r for r in cat.rows if r.row == 13)
        assert "THB" in row13.message
        assert "IDR" not in row13.message

    def test_thb_business_fail_message_contains_thb(self):
        cat = self._make_business_cat("❌")
        manual_data = {
            "business": {
                "salesMonth0": 200_000,   # lower than avg → fail
                "salesMonth1": 360_000,
                "salesMonth2": 380_000,
                "salesMonth3": 340_000,
                "salesMonth4": 320_000,
                "salesMonth5": 300_000,
            },
        }
        _generate_business_messages(cat, manual_data, rules=DEFAULT_RULES, marketplace="TH")
        row13 = next(r for r in cat.rows if r.row == 13)
        assert "THB" in row13.message
        assert "IDR" not in row13.message

    def test_id_business_message_contains_idr(self):
        cat = self._make_business_cat("✔️")
        manual_data = {
            "business": {
                "salesMonth0": 200_000_000,
                "salesMonth1": 180_000_000,
                "salesMonth2": 190_000_000,
                "salesMonth3": 170_000_000,
                "salesMonth4": 160_000_000,
                "salesMonth5": 150_000_000,
            },
        }
        _generate_business_messages(cat, manual_data, rules=DEFAULT_RULES, marketplace="ID")
        row13 = next(r for r in cat.rows if r.row == 13)
        assert "IDR" in row13.message
        assert "THB" not in row13.message


# ---------------------------------------------------------------------------
# c. TestTHBCompetitionMessages — competition message output with THB
# ---------------------------------------------------------------------------


class TestTHBCompetitionMessages:
    def _make_competition_cat(self, verdicts: list[str]) -> CategoryScore:
        """Create competition CategoryScore with rows 61-63."""
        rows = []
        for i, v in enumerate(verdicts):
            rows.append(RowScore(
                row=61 + i, metric=f"Produk {i + 1}",
                value=500 + i * 100, benchmark="-", verdict=v,
                message="", score=0.0,
            ))
        return CategoryScore(
            category="Kompetisi TOP Produk",
            score=0.0, max_score=0.0, rows=rows,
        )

    def test_thb_competition_fail_message_contains_thb(self):
        cat = self._make_competition_cat(["❌", "❌", "❌"])
        manual_data = {
            "competition": {
                "product1": {"sellingPrice": 800, "marketPrice": 600, "productName": "Shoe A"},
                "product2": {"sellingPrice": 500, "marketPrice": 350, "productName": "Sandal B"},
                "product3": {"sellingPrice": 1000, "marketPrice": 700, "productName": "Bag C"},
            },
        }
        _generate_competition_messages(cat, manual_data, rules=DEFAULT_RULES, marketplace="TH")
        for row in cat.rows:
            assert "THB" in row.message, f"Row {row.row} message missing THB: {row.message}"
            assert "IDR" not in row.message, f"Row {row.row} still has IDR: {row.message}"

    def test_thb_competition_pass_message_contains_thb(self):
        cat = self._make_competition_cat(["✔️", "✔️", "✔️"])
        manual_data = {
            "competition": {
                "product1": {"sellingPrice": 500, "marketPrice": 600, "productName": "Shoe A"},
                "product2": {"sellingPrice": 300, "marketPrice": 350, "productName": "Sandal B"},
                "product3": {"sellingPrice": 600, "marketPrice": 700, "productName": "Bag C"},
            },
        }
        _generate_competition_messages(cat, manual_data, rules=DEFAULT_RULES, marketplace="TH")
        for row in cat.rows:
            assert "THB" in row.message, f"Row {row.row} message missing THB: {row.message}"
            assert "IDR" not in row.message, f"Row {row.row} still has IDR: {row.message}"

    def test_id_competition_message_contains_idr(self):
        cat = self._make_competition_cat(["❌", "✔️", "❌"])
        manual_data = {
            "competition": {
                "product1": {"sellingPrice": 250_000, "marketPrice": 200_000, "productName": "Sepatu A"},
                "product2": {"sellingPrice": 140_000, "marketPrice": 150_000, "productName": "Sandal B"},
                "product3": {"sellingPrice": 350_000, "marketPrice": 300_000, "productName": "Tas C"},
            },
        }
        _generate_competition_messages(cat, manual_data, rules=DEFAULT_RULES, marketplace="ID")
        for row in cat.rows:
            if row.verdict in ("❌", "✔️"):
                assert "IDR" in row.message, f"Row {row.row} message missing IDR: {row.message}"
                assert "THB" not in row.message, f"Row {row.row} has unexpected THB: {row.message}"


# ---------------------------------------------------------------------------
# d. TestTHBCompetitionBenchmark — benchmark string in _score_competition
# ---------------------------------------------------------------------------


class TestTHBCompetitionBenchmark:
    def test_thb_benchmark_starts_with_thb(self):
        manual_data = {
            "competition": {
                "product1": {"sellingPrice": 500, "marketPrice": 600, "productName": "Shoe A"},
                "product2": {"sellingPrice": 300, "marketPrice": 350, "productName": "Sandal B"},
                "product3": {"sellingPrice": 800, "marketPrice": 700, "productName": "Bag C"},
            },
        }
        cat = _score_competition(manual_data, {}, marketplace="TH")
        for row in cat.rows:
            assert row.benchmark.startswith("THB "), f"Row {row.row} benchmark does not start with 'THB ': {row.benchmark}"

    def test_id_benchmark_starts_with_idr(self):
        manual_data = {
            "competition": {
                "product1": {"sellingPrice": 180_000, "marketPrice": 200_000, "productName": "Sepatu A"},
                "product2": {"sellingPrice": 140_000, "marketPrice": 150_000, "productName": "Sandal B"},
                "product3": {"sellingPrice": 280_000, "marketPrice": 300_000, "productName": "Tas C"},
            },
        }
        cat = _score_competition(manual_data, {}, marketplace="ID")
        for row in cat.rows:
            assert row.benchmark.startswith("IDR "), f"Row {row.row} benchmark does not start with 'IDR ': {row.benchmark}"


# ---------------------------------------------------------------------------
# e. TestTHBConclusionText — _compute_g66 scaling
# ---------------------------------------------------------------------------


class TestTHBConclusionText:
    def _make_minimal_categories(self) -> list[CategoryScore]:
        """Create minimal categories for _compute_g66."""
        return [
            CategoryScore(
                category="Kesehatan Operasional Toko", score=10.0, max_score=10.0,
                rows=[RowScore(row=10, metric="Chat", value=98.0, benchmark=">95%",
                               verdict="✔️", message="", score=0.0)],
            ),
            CategoryScore(
                category="Promo Toko", score=5.0, max_score=10.0,
                rows=[RowScore(row=43, metric="Efektifitas", value=0.85, benchmark=">90%",
                               verdict="❌", message="", score=0.0)],
            ),
            CategoryScore(
                category="Partisipasi Campaign", score=5.0, max_score=5.0,
                rows=[RowScore(row=57, metric="% Partisipasi", value=0.90, benchmark=">90%",
                               verdict="✔️", message="", score=5.0)],
            ),
        ]

    def test_thb_conclusion_no_juta(self):
        categories = self._make_minimal_categories()
        manual_data = {
            "business": {
                "salesMonth0": 400_000,
                "salesMonth1": 360_000,
                "salesMonth2": 380_000,
                "salesMonth3": 340_000,
                "salesMonth4": 320_000,
                "salesMonth5": 300_000,
            },
        }
        g66 = _compute_g66(categories, manual_data, "", marketplace="TH")
        assert "juta" not in g66, f"THB conclusion should not contain 'juta': {g66}"
        # Should contain comma-formatted values
        assert "300,000" in g66, f"THB conclusion missing formatted min: {g66}"
        assert "400,000" in g66, f"THB conclusion missing formatted max: {g66}"

    def test_id_conclusion_has_juta(self):
        categories = self._make_minimal_categories()
        manual_data = {
            "business": {
                "salesMonth0": 200_000_000,
                "salesMonth1": 180_000_000,
                "salesMonth2": 190_000_000,
                "salesMonth3": 170_000_000,
                "salesMonth4": 160_000_000,
                "salesMonth5": 150_000_000,
            },
        }
        g66 = _compute_g66(categories, manual_data, "", marketplace="ID")
        assert "juta" in g66, f"IDR conclusion should contain 'juta': {g66}"
        assert "150 juta" in g66
        assert "200 juta" in g66

    def test_thb_g66_i18n_vars_raw_numbers(self):
        categories = self._make_minimal_categories()
        manual_data = {
            "business": {
                "salesMonth0": 400_000,
                "salesMonth1": 360_000,
                "salesMonth2": 380_000,
                "salesMonth3": 340_000,
                "salesMonth4": 320_000,
                "salesMonth5": 300_000,
            },
        }
        items = _compute_g66_i18n(categories, manual_data, "", marketplace="TH")
        sales_item = next(i for i in items if i.key == "conclusion.salesRange")
        # THB: raw formatted numbers, not /1M scaled
        assert sales_item.vars["min"] == "300,000"
        assert sales_item.vars["max"] == "400,000"

    def test_id_g66_i18n_vars_scaled_numbers(self):
        categories = self._make_minimal_categories()
        manual_data = {
            "business": {
                "salesMonth0": 200_000_000,
                "salesMonth1": 180_000_000,
                "salesMonth2": 190_000_000,
                "salesMonth3": 170_000_000,
                "salesMonth4": 160_000_000,
                "salesMonth5": 150_000_000,
            },
        }
        items = _compute_g66_i18n(categories, manual_data, "", marketplace="ID")
        sales_item = next(i for i in items if i.key == "conclusion.salesRange")
        # IDR: divided by 1M
        assert sales_item.vars["min"] == "150"
        assert sales_item.vars["max"] == "200"


# ---------------------------------------------------------------------------
# f. TestFullScoringTHB — end-to-end calculate_score with THB
# ---------------------------------------------------------------------------


class TestFullScoringTHB:
    def test_calculate_score_thb_produces_valid_result(self, thb_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=thb_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="TestStore",
            period="Jan 2026",
            brand_name="TestBrand",
            marketplace="TH",
        )
        assert isinstance(result, ScoringResult)
        assert result.closing_message != ""

    def test_calculate_score_thb_business_messages_have_thb(self, thb_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=thb_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="TestStore",
            period="Jan 2026",
            brand_name="TestBrand",
            marketplace="TH",
        )
        biz_cat = next(c for c in result.category_scores if c.category == "Bisnis Analisis")
        row13 = next(r for r in biz_cat.rows if r.row == 13)
        assert "THB" in row13.message, f"Business row 13 missing THB: {row13.message}"
        assert "IDR" not in row13.message

    def test_calculate_score_thb_competition_benchmarks_have_thb(self, thb_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=thb_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="TestStore",
            period="Jan 2026",
            brand_name="TestBrand",
            marketplace="TH",
        )
        comp_cat = next(c for c in result.category_scores if c.category == "Kompetisi TOP Produk")
        for row in comp_cat.rows:
            if row.benchmark != "-":
                assert "THB" in row.benchmark, f"Competition row {row.row} benchmark missing THB: {row.benchmark}"

    def test_calculate_score_thb_conclusion_no_juta(self, thb_manual_data, full_calculator_results):
        result = calculate_score(
            manual_data=thb_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="TestStore",
            period="Jan 2026",
            brand_name="TestBrand",
            marketplace="TH",
        )
        assert "juta" not in result.conclusion, f"THB conclusion should not have 'juta': {result.conclusion}"


# ---------------------------------------------------------------------------
# g. TestBackwardCompatibility — default marketplace produces same as 'ID'
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    def test_default_marketplace_equals_explicit_id(self, idr_manual_data, full_calculator_results):
        result_default = calculate_score(
            manual_data=idr_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="TestStore",
            period="Jan 2026",
            brand_name="TestBrand",
            # No marketplace param — should default to "ID"
        )
        result_explicit = calculate_score(
            manual_data=idr_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="TestStore",
            period="Jan 2026",
            brand_name="TestBrand",
            marketplace="ID",
        )
        # Total score must be identical
        assert result_default.total_score == result_explicit.total_score
        # Email body must be identical
        assert result_default.email_body == result_explicit.email_body
        # Conclusion must be identical
        assert result_default.conclusion == result_explicit.conclusion

    def test_unknown_marketplace_falls_back_to_idr(self, idr_manual_data, full_calculator_results):
        """Unknown marketplace code should fall back to IDR via MARKETPLACE_CURRENCY.get()."""
        result = calculate_score(
            manual_data=idr_manual_data,
            calculator_results=full_calculator_results,
            template="fashion",
            verdict="✔️",
            store_name="TestStore",
            period="Jan 2026",
            brand_name="TestBrand",
            marketplace="XX",  # unknown
        )
        biz_cat = next(c for c in result.category_scores if c.category == "Bisnis Analisis")
        row13 = next(r for r in biz_cat.rows if r.row == 13)
        assert "IDR" in row13.message, f"Unknown marketplace should fall back to IDR: {row13.message}"
