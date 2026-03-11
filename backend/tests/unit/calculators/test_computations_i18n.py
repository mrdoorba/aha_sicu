"""Tests for i18n functions in computations.py."""

from app.calculators.scoring.computations import (
    _compute_g66_i18n,
    _compute_g73_i18n,
    _compute_g75_i18n,
)
from app.calculators.scoring.models import CategoryScore, RowScore, TranslatableText


def test_g66_i18n_returns_translatable_list():
    ops = CategoryScore(
        category="Kesehatan Operasional Toko", score=10, max_score=10,
        rows=[RowScore(row=10, metric="Persentase Chat Dibalas",
                       value=98, benchmark=">95%", verdict="✔️", message="", score=0)],
    )
    promo = CategoryScore(
        category="Promo Toko", score=0, max_score=15,
        rows=[RowScore(row=43, metric="", value=0.5, benchmark="", verdict="❌", message="", score=10)],
    )
    campaign = CategoryScore(
        category="Partisipasi Campaign", score=10, max_score=10,
        rows=[RowScore(row=57, metric="", value=0.5, benchmark="", verdict="❌", message="", score=10)],
    )
    manual = {"business": {
        "salesMonth0": 200_000_000, "salesMonth1": 180_000_000,
        "salesMonth2": 190_000_000, "salesMonth3": 170_000_000,
        "salesMonth4": 160_000_000, "salesMonth5": 150_000_000,
    }}
    items = _compute_g66_i18n([ops, promo, campaign], manual, "15.3% ~ 22.7%")
    assert len(items) > 0
    assert all(isinstance(i, TranslatableText) for i in items)
    assert items[0].key == "conclusion.salesRange"
    assert "min" in items[0].vars
    assert "max" in items[0].vars


def test_g73_i18n_returns_translatable_text():
    result = _compute_g73_i18n("✔️", 0.15, 200_000_000)
    assert result is not None
    assert result.key == "marketing.budgetRecommendation"
    assert "pct" in result.vars


def test_g73_i18n_returns_none_for_rejected():
    result = _compute_g73_i18n("❌", 0.15, 200_000_000)
    assert result is None


def test_g75_i18n_returns_translatable_text():
    result = _compute_g75_i18n("✔️", "Toko Salt")
    assert result is not None
    assert result.key == "closing.potential"
    assert result.vars["store_name"] == "Toko Salt"


def test_g75_i18n_rejected():
    result = _compute_g75_i18n("❌", "Toko Salt")
    assert result is not None
    assert result.key == "closing.valueAdd"


def test_g75_i18n_non_mall():
    result = _compute_g75_i18n("❌ Non Mall", "Test")
    assert result is not None
    assert result.key == "closing.directAnalysis"


def test_g75_i18n_unknown_verdict():
    result = _compute_g75_i18n("UNKNOWN", "Test")
    assert result is None
