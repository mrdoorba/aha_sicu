"""Tests for multi-language email template rendering."""

import pytest

from app.modules.email.template import render_email_html


@pytest.fixture
def minimal_eval_data() -> dict:
    """Minimal evaluation data for template rendering tests."""
    return {
        "brand_name": "TestBrand",
        "period": "Jan 2026",
        "final_score": 85.0,
        "verdict": "Good",
        "template": "standard",
        "score_breakdown": [],
        "calculator_results": {},
    }


def test_indonesian_labels_when_language_id(minimal_eval_data):
    html = render_email_html(
        evaluation_data=minimal_eval_data,
        chart_src="chart.png",
        header_src="header.png",
        footer_src="footer.png",
        language="id",
    )
    assert "Laporan Evaluasi Brand" in html


def test_english_labels_when_language_en(minimal_eval_data):
    html = render_email_html(
        evaluation_data=minimal_eval_data,
        chart_src="chart.png",
        header_src="header.png",
        footer_src="footer.png",
        language="en",
    )
    assert "Brand Evaluation Report" in html


def test_thai_labels_when_language_th(minimal_eval_data):
    html = render_email_html(
        evaluation_data=minimal_eval_data,
        chart_src="chart.png",
        header_src="header.png",
        footer_src="footer.png",
        language="th",
    )
    assert "\u0e23\u0e32\u0e22\u0e07\u0e32\u0e19\u0e01\u0e32\u0e23\u0e1b\u0e23\u0e30\u0e40\u0e21\u0e34\u0e19\u0e41\u0e1a\u0e23\u0e19\u0e14\u0e4c" in html


def test_html_lang_matches_language(minimal_eval_data):
    html = render_email_html(
        evaluation_data=minimal_eval_data,
        chart_src="chart.png",
        header_src="header.png",
        footer_src="footer.png",
        language="en",
    )
    assert '<html lang="en">' in html


def test_fallback_to_indonesian_when_unknown_language(minimal_eval_data):
    html = render_email_html(
        evaluation_data=minimal_eval_data,
        chart_src="chart.png",
        header_src="header.png",
        footer_src="footer.png",
        language="fr",
    )
    assert "Laporan Evaluasi Brand" in html
