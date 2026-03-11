"""Tests for i18n fields in scoring categories and messages."""

from app.calculators.scoring.categories import (
    _score_ads,
    _score_business,
    _score_campaign,
    _score_competition,
    _score_discount_row,
    _score_operational,
    _score_products,
    _score_promo_tools,
    _score_stock,
    _score_visitors,
)
from app.calculators.scoring.messages import (
    _generate_ads_messages,
    _generate_business_messages,
    _generate_campaign_messages,
    _generate_competition_messages,
    _generate_operational_messages,
    _generate_products_messages,
    _generate_promo_messages,
    _generate_visitors_messages,
)


# ---------------------------------------------------------------------------
# Task 2: Operational category
# ---------------------------------------------------------------------------

def test_operational_rows_have_metric_i18n():
    manual = {"operational": {
        "unfulfilledOrderRate": 0.5, "lateShipmentRate": 0.3,
        "preparationTime": 0.8, "chatResponseRate": 98.0, "overallRating": 4.9,
    }}
    cat = _score_operational(manual)

    expected_keys = {
        7: "scoring.unfulfilledOrderRate",
        8: "scoring.lateShipmentRate",
        9: "scoring.preparationTime",
        10: "scoring.chatResponseRate",
        11: "scoring.overallRating",
    }
    for row in cat.rows:
        if row.row in expected_keys:
            assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
            assert row.metric_i18n.key == expected_keys[row.row]

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.operational"


def test_operational_messages_have_i18n():
    manual = {"operational": {
        "unfulfilledOrderRate": 0.5, "lateShipmentRate": 0.3,
        "preparationTime": 0.8, "chatResponseRate": 98.0, "overallRating": 4.9,
    }}
    cat = _score_operational(manual)
    _generate_operational_messages(cat, manual)

    for row in cat.rows:
        if row.row in (7, 8, 9, 10, 11):
            assert row.message_i18n is not None, f"Row {row.row} missing message_i18n"
            assert "pass" in row.message_i18n.key or "fail" in row.message_i18n.key


def test_operational_fail_messages_have_i18n():
    manual = {"operational": {
        "unfulfilledOrderRate": 5.0, "lateShipmentRate": 5.0,
        "preparationTime": 3.0, "chatResponseRate": 80.0, "overallRating": 3.0,
    }}
    cat = _score_operational(manual)
    _generate_operational_messages(cat, manual)

    for row in cat.rows:
        if row.row in (7, 8, 9, 10, 11):
            assert row.message_i18n is not None
            assert "fail" in row.message_i18n.key


# ---------------------------------------------------------------------------
# Task 3: All remaining categories
# ---------------------------------------------------------------------------

def test_business_rows_have_i18n():
    manual = {"business": {
        "salesMonth0": 200_000_000, "salesMonth1": 180_000_000,
        "salesMonth2": 170_000_000, "salesMonth3": 160_000_000,
        "salesMonth4": 150_000_000, "salesMonth5": 140_000_000,
        "conversionRate": 4.0,
    }}
    cat = _score_business(manual)

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.business"

    expected_keys = {
        13: "scoring.monthlySales",
        14: "scoring.pastMonthlySales",
        15: "scoring.pastMonthlySales",
        16: "scoring.pastMonthlySales",
        17: "scoring.pastMonthlySales",
        18: "scoring.pastMonthlySales",
        19: "scoring.avgSales6mo",
        20: "scoring.conversionRate",
    }
    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
        assert row.metric_i18n.key == expected_keys[row.row]


def test_business_messages_have_i18n():
    manual = {"business": {
        "salesMonth0": 200_000_000, "salesMonth1": 180_000_000,
        "salesMonth2": 170_000_000, "salesMonth3": 160_000_000,
        "salesMonth4": 150_000_000, "salesMonth5": 140_000_000,
        "conversionRate": 4.0,
    }}
    cat = _score_business(manual)
    _generate_business_messages(cat, manual)

    # Row 13 always gets a message; row 20 only when verdict is not "-"
    row13 = next(r for r in cat.rows if r.row == 13)
    assert row13.message_i18n is not None, "Row 13 missing message_i18n"


def test_visitors_rows_have_i18n():
    manual = {"visitors": {
        "totalVisitors": 100_000, "returningVisitors": 30_000,
        "totalFollowers": 60_000,
    }}
    cat = _score_visitors(manual)

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.visitors"

    expected_keys = {
        26: "scoring.totalVisitors",
        27: "scoring.returningVisitors",
        28: "scoring.returningVisitorPct",
        29: "scoring.totalFollowers",
    }
    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
        assert row.metric_i18n.key == expected_keys[row.row]


def test_visitors_messages_have_i18n():
    manual = {"visitors": {
        "totalVisitors": 100_000, "returningVisitors": 30_000,
        "totalFollowers": 60_000,
    }}
    cat = _score_visitors(manual)
    _generate_visitors_messages(cat)

    for row in cat.rows:
        if row.row in (28, 29):
            assert row.message_i18n is not None, f"Row {row.row} missing message_i18n"


def test_promo_tools_rows_have_i18n():
    manual = {
        "business": {"salesMonth0": 100_000_000},
        "promoTools": {
            "promoToko": 5_000_000, "paketDiskon": 20_000_000,
            "komboHemat": 2_000_000, "flashSale": 3_000_000,
            "voucher": 90_000_000, "shopeeLive": 20_000_000,
            "gameToko": 1_500_000, "brandMembership": 2_000_000,
            "gratisOngkir": 1_000_000, "chatBroadcast": 1_500_000,
            "programAfiliasi": 25_000_000,
        },
    }
    cat = _score_promo_tools(manual)

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.promo"

    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"

    # Check specific promo tool keys
    promo_rows = [r for r in cat.rows if 31 <= r.row <= 41]
    expected_field_keys = [
        "promoToko", "paketDiskon", "komboHemat", "flashSale",
        "voucher", "shopeeLive", "gameToko", "brandMembership",
        "gratisOngkir", "chatBroadcast", "programAfiliasi",
    ]
    for row, field_key in zip(promo_rows, expected_field_keys):
        assert row.metric_i18n.key == f"scoring.promo.{field_key}"

    # Row 42-43
    usage_row = next(r for r in cat.rows if r.row == 42)
    assert usage_row.metric_i18n.key == "scoring.promoUsageRate"
    eff_row = next(r for r in cat.rows if r.row == 43)
    assert eff_row.metric_i18n.key == "scoring.promoEffectiveness"


def test_promo_messages_have_i18n():
    manual = {
        "business": {"salesMonth0": 100_000_000},
        "promoTools": {
            "promoToko": 5_000_000, "paketDiskon": 20_000_000,
            "komboHemat": 2_000_000, "flashSale": 3_000_000,
            "voucher": 90_000_000, "shopeeLive": 20_000_000,
            "gameToko": 1_500_000, "brandMembership": 2_000_000,
            "gratisOngkir": 1_000_000, "chatBroadcast": 1_500_000,
            "programAfiliasi": 25_000_000,
        },
    }
    cat = _score_promo_tools(manual)
    _generate_promo_messages(cat, manual)

    for row in cat.rows:
        if 31 <= row.row <= 43:
            assert row.message_i18n is not None, f"Row {row.row} missing message_i18n"


def test_products_rows_have_i18n():
    manual = {"products": {"productCount": 50, "storeStatus": "Shopee Mall"}}
    cat = _score_products(manual)

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.products"

    expected_keys = {45: "scoring.productCount", 46: "scoring.storeStatus"}
    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
        assert row.metric_i18n.key == expected_keys[row.row]


def test_products_messages_have_i18n():
    manual = {"products": {"productCount": 50, "storeStatus": "Shopee Mall"}}
    cat = _score_products(manual)
    _generate_products_messages(cat)

    for row in cat.rows:
        if row.row in (45, 46):
            assert row.message_i18n is not None, f"Row {row.row} missing message_i18n"


def test_ads_rows_have_i18n():
    manual = {
        "business": {"salesMonth0": 100_000_000},
        "ads": {"adSales": 50_000_000, "adCost": 5_000_000},
    }
    cat = _score_ads(manual, "non_fashion")

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.ads"

    expected_keys = {
        48: "scoring.adSales",
        49: "scoring.adCost",
        50: "scoring.adsROI",
        51: "scoring.adsGMVPct",
        52: "scoring.adsCostPct",
        53: "scoring.adsCheckup",
    }
    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
        assert row.metric_i18n.key == expected_keys[row.row]


def test_ads_messages_have_i18n():
    manual = {
        "business": {"salesMonth0": 100_000_000},
        "ads": {"adSales": 50_000_000, "adCost": 5_000_000},
    }
    cat = _score_ads(manual, "non_fashion")
    _generate_ads_messages(cat, manual, {})

    for row in cat.rows:
        if row.row in (50, 51, 52):
            assert row.message_i18n is not None, f"Row {row.row} missing message_i18n"


def test_campaign_rows_have_i18n():
    manual = {"campaign": {"nominatedSessions": 18, "availableSessions": 20}}
    cat = _score_campaign(manual)

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.campaign"

    expected_keys = {
        55: "scoring.nominatedSessions",
        56: "scoring.availableSessions",
        57: "scoring.campaignParticipation",
    }
    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
        assert row.metric_i18n.key == expected_keys[row.row]


def test_campaign_messages_have_i18n():
    manual = {"campaign": {"nominatedSessions": 18, "availableSessions": 20}}
    cat = _score_campaign(manual)
    _generate_campaign_messages(cat)

    for row in cat.rows:
        if row.row == 57:
            assert row.message_i18n is not None, f"Row {row.row} missing message_i18n"


def test_competition_rows_have_i18n():
    manual = {"competition": {
        "product1": {"sellingPrice": 100_000, "marketPrice": 120_000, "productName": "A"},
        "product2": {"sellingPrice": 200_000, "marketPrice": 180_000, "productName": "B"},
        "product3": {"sellingPrice": 150_000, "marketPrice": 160_000, "productName": "C"},
    }}
    cat = _score_competition(manual, {})

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.competition"

    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
        assert row.metric_i18n.key == "scoring.competitionProduct"


def test_competition_messages_have_i18n():
    manual = {"competition": {
        "product1": {"sellingPrice": 100_000, "marketPrice": 120_000, "productName": "A"},
        "product2": {"sellingPrice": 200_000, "marketPrice": 180_000, "productName": "B"},
        "product3": {"sellingPrice": 150_000, "marketPrice": 160_000, "productName": "C"},
    }}
    cat = _score_competition(manual, {})
    _generate_competition_messages(cat, manual)

    for row in cat.rows:
        if row.verdict != "-":
            assert row.message_i18n is not None, f"Row {row.row} missing message_i18n"


def test_stock_rows_have_i18n():
    calculator_results = {
        "top_sku": {"details": {"average_stock": 30, "out_of_stock_pct": 0.05}},
    }
    cat = _score_stock(calculator_results)

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.stock"

    expected_keys = {70: "scoring.avgStockTop20", 71: "scoring.stockAvailability"}
    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
        assert row.metric_i18n.key == expected_keys[row.row]


def test_stock_no_data_has_i18n():
    cat = _score_stock({})

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.stock"

    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"


def test_discount_rows_have_i18n():
    calculator_results = {
        "discount": {"details": {"fake_discount_flag": False}, "output_text": "OK"},
    }
    cat = _score_discount_row(calculator_results)

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.discount"

    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
        assert row.metric_i18n.key == "scoring.discountCheckup"


def test_discount_no_data_has_i18n():
    cat = _score_discount_row({})

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.discount"

    for row in cat.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
