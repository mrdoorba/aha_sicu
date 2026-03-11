"""Tests for TranslatableText and i18n-aware model serialization."""

from dataclasses import asdict

from app.calculators.scoring.models import (
    CategoryScore,
    RowScore,
    ScoringResult,
    TranslatableText,
)


def test_translatable_text_serializes_to_dict():
    t = TranslatableText(key="scoring.preparationTime.pass", vars={"value": "0.56"})
    result = asdict(t)
    assert result == {"key": "scoring.preparationTime.pass", "vars": {"value": "0.56"}}


def test_translatable_text_empty_vars():
    t = TranslatableText(key="verdict.good", vars={})
    result = asdict(t)
    assert result == {"key": "verdict.good", "vars": {}}


def test_row_score_i18n_fields_default_to_none():
    row = RowScore(
        row=7, metric="Tingkat Pesanan Tidak Terselesaikan",
        value=0.5, benchmark="<1%", verdict="✔️", message="pass", score=4.0,
    )
    assert row.metric_i18n is None
    assert row.message_i18n is None
    assert row.benchmark_i18n is None


def test_row_score_i18n_fields_set():
    row = RowScore(
        row=7, metric="Tingkat Pesanan Tidak Terselesaikan",
        value=0.5, benchmark="<1%", verdict="✔️", message="pass", score=4.0,
        metric_i18n=TranslatableText(key="scoring.unfulfilledOrderRate", vars={}),
        message_i18n=TranslatableText(key="scoring.unfulfilledOrderRate.pass", vars={"value": "0.5%"}),
    )
    assert row.metric_i18n.key == "scoring.unfulfilledOrderRate"
    assert row.message_i18n.vars == {"value": "0.5%"}


def test_row_score_i18n_serializes_in_asdict():
    row = RowScore(
        row=7, metric="test", value=0, benchmark="", verdict="", message="", score=0,
        metric_i18n=TranslatableText(key="k", vars={"a": "b"}),
    )
    d = asdict(row)
    assert d["metric_i18n"] == {"key": "k", "vars": {"a": "b"}}
    assert d["message_i18n"] is None


def test_category_score_i18n_field():
    cat = CategoryScore(category="Kesehatan Operasional Toko", score=10, max_score=10)
    assert cat.category_i18n is None

    cat2 = CategoryScore(
        category="Kesehatan Operasional Toko", score=10, max_score=10,
        category_i18n=TranslatableText(key="category.operational", vars={}),
    )
    assert cat2.category_i18n.key == "category.operational"


def test_scoring_result_i18n_fields():
    result = ScoringResult(
        total_score=50, category_scores=[], verdict="✔️",
        conclusion="test", marketing_estimation="test",
        marketing_percentage="10%", marketing_budget="test",
        closing_message="test", email_subject="test",
        email_body="test", template="fashion",
    )
    assert result.conclusion_i18n is None
    assert result.marketing_budget_i18n is None
    assert result.closing_message_i18n is None
    assert result.email_subject_i18n is None
