"""The VP adjustment where it meets the scoring calculator."""

from app.calculators.package_fit import read_package_fit
from app.calculators.scoring import calculate_score

MANUAL_DATA = {
    "operational": {
        "unfulfilledOrderRate": 0.1,
        "lateShipmentRate": 0.1,
        "preparationTime": 0.5,
        "chatResponseRate": 95.0,
    },
    "business": {"salesMonth0": 100_000_000},
}


def _score(raw_data: dict | None):
    return calculate_score(
        manual_data=MANUAL_DATA,
        calculator_results={},
        template="fashion",
        verdict="✔️",
        store_name="S",
        period="P",
        brand_name="B",
        package_fit=read_package_fit(raw_data) if raw_data is not None else None,
    )


def test_no_package_fit_leaves_the_total_untouched():
    result = _score(None)
    assert result.vp_adjustment == 0.0
    assert result.total_score == result.category_total


def test_vp_below_its_bar_costs_ten_points():
    short = _score({"Package": "Rising Star", "VP": "65"})
    clean = _score({"Package": "Rising Star", "VP": "80"})

    assert short.vp_adjustment == -10.0
    assert short.category_total == clean.category_total
    assert short.total_score == clean.category_total - 10.0


def test_category_total_still_reports_the_sum_of_the_categories():
    result = _score({"Package": "Superstar", "VP": "50"})

    assert result.category_total == sum(c.score for c in result.category_scores)
    assert result.total_score == result.category_total - 10.0


def test_unjudgeable_vp_leaves_the_total_untouched():
    result = _score({"Package": "Superstar", "VP": "0"})

    assert result.vp_adjustment == 0.0
    assert result.total_score == result.category_total


def test_adjustment_does_not_disturb_the_email_or_conclusion():
    short = _score({"Package": "Superstar", "VP": "50"})
    clean = _score({"Package": "Superstar", "VP": "90"})

    # Q14: the shortfall is an internal judgement — it never reaches the partner.
    assert short.email_body == clean.email_body
    assert short.conclusion == clean.conclusion
