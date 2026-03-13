"""Tests for email HTML template rendering."""

from __future__ import annotations

import pytest

from app.modules.email.template import (
    CATEGORY_MAP,
    STRINGS,
    render_email_html,
    _compute_verdict_counts,
    _score_color,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_categories() -> list[dict]:
    """Minimal score_breakdown list for testing."""
    return [
        {
            "category": "Kesehatan Operasional Toko",
            "score": 8.0,
            "max_score": 10.0,
            "available": True,
            "rows": [
                {
                    "row": 1,
                    "metric": "Tingkat Chat Dibalas",
                    "value": 95,
                    "benchmark": ">= 80%",
                    "verdict": "\u2714\ufe0f",
                    "message": "Baik",
                    "score": 4.0,
                },
                {
                    "row": 2,
                    "metric": "Waktu Chat Dibalas",
                    "value": 120,
                    "benchmark": "<= 300 detik",
                    "verdict": "\u2714\ufe0f",
                    "message": "Baik",
                    "score": 4.0,
                },
            ],
        },
        {
            "category": "Bisnis Analisis",
            "score": 3.0,
            "max_score": 10.0,
            "available": True,
            "rows": [
                {
                    "row": 1,
                    "metric": "Konversi",
                    "value": 1.2,
                    "benchmark": ">= 3%",
                    "verdict": "\u274c",
                    "message": "Perlu ditingkatkan",
                    "score": 0.0,
                },
                {
                    "row": 2,
                    "metric": "Rasio Penjualan",
                    "value": 0.5,
                    "benchmark": ">= 1%",
                    "verdict": "\u274c",
                    "message": "Perlu ditingkatkan",
                    "score": 0.0,
                },
                {
                    "row": 3,
                    "metric": "Bounce Rate",
                    "value": 30,
                    "benchmark": "<= 50%",
                    "verdict": "\u2714\ufe0f",
                    "message": "Baik",
                    "score": 3.0,
                },
            ],
        },
    ]


@pytest.fixture()
def sample_calculator_results() -> dict:
    """Minimal calculator_results for testing with correct output_1/output_2 keys."""
    return {
        "ads_keyword": {
            "output_text": "Keyword 'sepatu' memiliki CTR 2.5%\nKeyword 'tas' memiliki CTR 1.8%",
            "details": {},
        },
        "top_sku": {
            "output_text": "Top SKU analysis",
            "details": {
                "average_stock": 325,
                "output_1": [
                    {"kode_variasi": "SKU-001", "product_name": "Sepatu Running", "total_omzet": 15_000_000, "rata2_harga_jual": 500_000},
                    {"kode_variasi": "SKU-002", "product_name": "Tas Ransel", "total_omzet": 12_000_000, "rata2_harga_jual": 400_000},
                    {"kode_variasi": "SKU-003", "product_name": "Jaket Outdoor", "total_omzet": 9_000_000, "rata2_harga_jual": 350_000},
                    {"kode_variasi": "SKU-004", "product_name": "Topi Baseball", "total_omzet": 5_000_000, "rata2_harga_jual": 150_000},
                    {"kode_variasi": "SKU-005", "product_name": "Kaos Polos", "total_omzet": 3_000_000, "rata2_harga_jual": 100_000},
                    {"kode_variasi": "SKU-006", "product_name": "Celana Jeans", "total_omzet": 2_000_000, "rata2_harga_jual": 200_000},
                ],
                "output_2": [
                    {"kode_variasi": "SKU-001", "nama_produk": "Sepatu Running", "varian": "42 Black", "stok": 500},
                    {"kode_variasi": "SKU-002", "nama_produk": "Tas Ransel", "varian": "Large Grey", "stok": 350},
                    {"kode_variasi": "SKU-003", "nama_produk": "Jaket Outdoor", "varian": "M Navy", "stok": 200},
                    {"kode_variasi": "SKU-004", "nama_produk": "Topi Baseball", "varian": "One Size", "stok": 100},
                    {"kode_variasi": "SKU-005", "nama_produk": "Kaos Polos", "varian": "L White", "stok": 80},
                    {"kode_variasi": "SKU-006", "nama_produk": "Celana Jeans", "varian": "32 Blue", "stok": 50},
                ],
                "product_count": 6,
                "total_unique_products": 6,
            },
        },
        "scoring_summary": {
            "conclusion": "- Performa toko sangat baik\n- Chat response rate tinggi\n- Konversi perlu ditingkatkan",
            "marketing_estimation": "22.4% ~ 26.2%",
            "marketing_budget": "IDR 5,000,000",
            "closing_message": "Secara keseluruhan, brand ini menunjukkan performa yang baik.\nFokus pada peningkatan konversi untuk hasil optimal.",
        },
    }


@pytest.fixture()
def evaluation_data(
    sample_categories: list[dict],
    sample_calculator_results: dict,
) -> dict:
    """Full evaluation data dict matching EvaluationDetailResponse shape."""
    return {
        "id": 42,
        "brand_id": 7,
        "brand_name": "Toko Sejahtera",
        "final_score": 72.5,
        "verdict": "\u2714\ufe0f",
        "template": "fashion",
        "score_breakdown": sample_categories,
        "calculator_results": sample_calculator_results,
        "period": "Januari 2026",
    }


# ===================================================================
# Task 1 Tests: Score overview, header/footer, structure
# ===================================================================


class TestHTMLStructure:
    """HTML output structure tests."""

    def test_returns_doctype_html(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        assert "<!DOCTYPE html" in html.upper() or "<!doctype html" in html.lower()

    def test_no_style_blocks(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        # No <style> blocks in the <body>. A single <style> in <head> for
        # progressive-enhancement media queries is acceptable (Task 2 adds it).
        body_start = html.lower().find("<body")
        body_html = html[body_start:] if body_start != -1 else html
        assert "<style" not in body_html.lower()

    def test_table_layout(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        assert 'role="presentation"' in html
        assert "<table" in html.lower()


class TestHeaderFooter:
    """Header and footer CID image tests."""

    def test_header_cid_image(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        assert "cid:header123@domain" in html

    def test_footer_cid_image(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        assert "cid:footer123@domain" in html

    def test_brand_name_and_period(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        assert "Toko Sejahtera" in html
        assert "Januari 2026" in html


class TestScoreOverview:
    """Score overview section tests."""

    def test_final_score_displayed(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        assert "72.5" in html

    def test_score_color_green(self) -> None:
        assert _score_color(80.0) == "#4CAF50"
        assert _score_color(95.0) == "#4CAF50"

    def test_score_color_blue(self) -> None:
        assert _score_color(50.0) == "#1976D2"
        assert _score_color(79.9) == "#1976D2"

    def test_score_color_orange(self) -> None:
        assert _score_color(49.9) == "#FF9800"
        assert _score_color(0.0) == "#FF9800"

    def test_progress_bar_present(self, evaluation_data: dict) -> None:
        """Score overview should contain a progress bar (nested table pattern)."""
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        # Progress bar uses background-color for the filled portion
        assert "background-color:" in html

    def test_verdict_counts_displayed(
        self, evaluation_data: dict, sample_categories: list[dict],
    ) -> None:
        counts = _compute_verdict_counts(sample_categories)
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        assert str(counts["checks"]) in html
        assert str(counts["xs"]) in html

    def test_template_type_displayed(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        assert "fashion" in html.lower()

    def test_verdict_text_displayed(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        assert "\u2714\ufe0f" in html

    def test_section_number_01(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        assert "01" in html


class TestVerdictCounting:
    """Verdict counting logic tests."""

    def test_compute_verdict_counts(self, sample_categories: list[dict]) -> None:
        counts = _compute_verdict_counts(sample_categories)
        assert counts["checks"] == 3
        assert counts["xs"] == 2
        assert counts["total"] == 5

    def test_compute_verdict_counts_empty(self) -> None:
        counts = _compute_verdict_counts([])
        assert counts["checks"] == 0
        assert counts["xs"] == 0
        assert counts["total"] == 0


class TestStringsAndCategoryMap:
    """STRINGS dict and CATEGORY_MAP tests."""

    def test_strings_has_id_key(self) -> None:
        assert "id" in STRINGS

    def test_strings_has_section_headers(self) -> None:
        id_strings = STRINGS["id"]
        required_keys = [
            "score_overview",
            "detailed_evaluation",
            "score_breakdown",
            "data_intelligence",
            "ads_analysis",
            "top_sku",
            "kesimpulan",
            "marketing_budget",
        ]
        for key in required_keys:
            assert key in id_strings, f"Missing STRINGS key: {key}"

    def test_strings_has_new_keys(self) -> None:
        for lang in ("id", "en", "th"):
            s = STRINGS[lang]
            for key in ("average_stock", "product_code", "product_name", "kesimpulan", "marketing_budget"):
                assert key in s, f"Missing STRINGS[{lang}] key: {key}"

    def test_category_map_entries(self) -> None:
        expected_keys = [
            "Kesehatan Operasional Toko",
            "Bisnis Analisis",
            "Tinjauan Pengunjung",
            "Promo Toko",
            "Jumlah Produk & Status Toko",
            "Data Iklan",
            "Partisipasi Campaign",
            "Kompetisi TOP Produk",
            "Stok",
            "Discount",
        ]
        for key in expected_keys:
            assert key in CATEGORY_MAP["id"], f"Missing CATEGORY_MAP key: {key}"


# ===================================================================
# Task 2 Tests: Detailed evaluation, score breakdown, data intelligence
# ===================================================================


def _render_full(evaluation_data: dict) -> str:
    """Helper to render full email HTML with standard CIDs."""
    return render_email_html(
        evaluation_data=evaluation_data,
        chart_src="cid:chart123@domain",
        header_src="cid:header123@domain",
        footer_src="cid:footer123@domain",
    )


class TestDetailedEvaluation:
    """Detailed evaluation section tests."""

    def test_renders_all_categories(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        # Should contain short display names from CATEGORY_MAP
        assert "Operasional" in html
        assert "Bisnis" in html

    def test_metric_card_content(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        # Metric names from the fixture
        assert "Tingkat Chat Dibalas" in html
        assert "Konversi" in html

    def test_metric_card_fields(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        # Check that benchmark and message values appear
        assert "&gt;= 80%" in html or ">= 80%" in html
        assert "Baik" in html
        assert "Perlu ditingkatkan" in html

    def test_two_column_grid(self, evaluation_data: dict) -> None:
        """Metric cards should be in a 2-column table grid."""
        html = _render_full(evaluation_data)
        # 2-column layout means td elements with width ~50%
        assert "width:50%" in html.replace(" ", "") or 'width="50%"' in html

    def test_section_number_02(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "02" in html

    def test_skips_category_with_no_rows_in_detailed(self, sample_calculator_results: dict) -> None:
        """Category with empty rows should not render metric cards in detailed section."""
        data = {
            "id": 1,
            "brand_id": 1,
            "brand_name": "Test",
            "final_score": 50.0,
            "verdict": "\u2714\ufe0f",
            "template": "fashion",
            "score_breakdown": [
                {"category": "Bisnis Analisis", "score": 5.0, "max_score": 10.0, "rows": []},
            ],
            "calculator_results": sample_calculator_results,
            "period": "Maret 2026",
        }
        html = _render_full(data)
        # Detailed Evaluation section header should not appear (no categories with rows)
        assert STRINGS["id"]["detailed_evaluation"] not in html


class TestScoreBreakdown:
    """Score breakdown section tests."""

    def test_chart_cid_image(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "cid:chart123@domain" in html

    def test_category_bars(self, evaluation_data: dict) -> None:
        """Score breakdown should show category summary bars."""
        html = _render_full(evaluation_data)
        # Category short names in the breakdown section
        assert "Operasional" in html
        # Score values (8.0 / 10.0 for first category)
        assert "8" in html
        assert "10" in html

    def test_section_number_03(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "03" in html


class TestDataIntelligence:
    """Data intelligence section tests."""

    def test_ads_keyword_preformatted(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        # ads_keyword output_text should appear
        assert "Keyword &#x27;sepatu&#x27;" in html or "Keyword 'sepatu'" in html or "sepatu" in html

    def test_top_sku_revenue_table(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        # Top 5 revenue SKUs should appear (output_1)
        assert "Sepatu Running" in html
        assert "Tas Ransel" in html
        assert "Jaket Outdoor" in html
        assert "Topi Baseball" in html
        assert "Kaos Polos" in html

    def test_top_sku_stock_table(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        # Stock values for top 5 (output_2)
        assert "500" in html
        assert "350" in html
        assert "200" in html

    def test_top_sku_limits_to_five(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        # 6th item should NOT appear
        assert "Celana Jeans" not in html

    def test_top_sku_kode_variasi(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "SKU-001" in html
        assert "SKU-002" in html

    def test_average_stock_displayed(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "325" in html

    def test_missing_calculator_results(self, sample_categories: list[dict]) -> None:
        """Should not crash with empty calculator_results."""
        data = {
            "id": 1,
            "brand_id": 1,
            "brand_name": "Test Brand",
            "final_score": 50.0,
            "verdict": "\u2714\ufe0f",
            "template": "non_fashion",
            "score_breakdown": sample_categories,
            "calculator_results": {},
            "period": "Februari 2026",
        }
        html = _render_full(data)
        # Should produce valid HTML without crashing
        assert "<!DOCTYPE html" in html.upper() or "<!doctype html" in html.lower()

    def test_section_header_present(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert STRINGS["id"]["data_intelligence"] in html

    def test_section_number_04(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "04" in html

    def test_skips_when_no_data(self, sample_categories: list[dict]) -> None:
        """Data intelligence section should be omitted when calculator_results is empty."""
        data = {
            "id": 1,
            "brand_id": 1,
            "brand_name": "Test",
            "final_score": 50.0,
            "verdict": "\u2714\ufe0f",
            "template": "fashion",
            "score_breakdown": sample_categories,
            "calculator_results": {},
            "period": "Maret 2026",
        }
        html = _render_full(data)
        assert STRINGS["id"]["data_intelligence"] not in html


# ===================================================================
# Kesimpulan (Conclusion) section tests
# ===================================================================


class TestKesimpulan:
    """Kesimpulan (conclusion) section tests."""

    def test_conclusion_bullets_rendered(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "Performa toko sangat baik" in html
        assert "Chat response rate tinggi" in html
        assert "Konversi perlu ditingkatkan" in html

    def test_marketing_budget_rendered(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "IDR 5,000,000" in html
        assert STRINGS["id"]["marketing_budget"] in html

    def test_closing_message_rendered(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "brand ini menunjukkan performa yang baik" in html

    def test_closing_message_preserves_line_breaks(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "<br>" in html

    def test_section_header_present(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert STRINGS["id"]["kesimpulan"] in html

    def test_section_number_05(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "05" in html

    def test_skips_when_no_scoring_summary(self, sample_categories: list[dict]) -> None:
        data = {
            "id": 1,
            "brand_id": 1,
            "brand_name": "Test",
            "final_score": 50.0,
            "verdict": "\u2714\ufe0f",
            "template": "fashion",
            "score_breakdown": sample_categories,
            "calculator_results": {"ads_keyword": {"output_text": "test", "details": {}}},
            "period": "Maret 2026",
        }
        html = _render_full(data)
        assert STRINGS["id"]["kesimpulan"] not in html

    def test_skips_when_summary_has_no_content(self, sample_categories: list[dict]) -> None:
        data = {
            "id": 1,
            "brand_id": 1,
            "brand_name": "Test",
            "final_score": 50.0,
            "verdict": "\u2714\ufe0f",
            "template": "fashion",
            "score_breakdown": sample_categories,
            "calculator_results": {
                "scoring_summary": {
                    "conclusion": "",
                    "marketing_budget": "",
                    "closing_message": "",
                },
            },
            "period": "Maret 2026",
        }
        html = _render_full(data)
        assert STRINGS["id"]["kesimpulan"] not in html

    def test_renders_only_conclusion_when_budget_missing(self, sample_categories: list[dict]) -> None:
        data = {
            "id": 1,
            "brand_id": 1,
            "brand_name": "Test",
            "final_score": 50.0,
            "verdict": "\u2714\ufe0f",
            "template": "fashion",
            "score_breakdown": sample_categories,
            "calculator_results": {
                "scoring_summary": {
                    "conclusion": "- Good performance",
                    "marketing_budget": "",
                    "closing_message": "",
                },
            },
            "period": "Maret 2026",
        }
        html = _render_full(data)
        assert STRINGS["id"]["kesimpulan"] in html
        assert "Good performance" in html
        assert STRINGS["id"]["marketing_budget"] not in html

    def test_html_escaped(self, sample_categories: list[dict]) -> None:
        data = {
            "id": 1,
            "brand_id": 1,
            "brand_name": "Test",
            "final_score": 50.0,
            "verdict": "\u2714\ufe0f",
            "template": "fashion",
            "score_breakdown": sample_categories,
            "calculator_results": {
                "scoring_summary": {
                    "conclusion": "- <script>alert('xss')</script>",
                    "marketing_budget": "",
                    "closing_message": "",
                },
            },
            "period": "Maret 2026",
        }
        html = _render_full(data)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


class TestResponsive:
    """Responsive email structure tests."""

    def test_media_query_present(self, evaluation_data: dict) -> None:
        """Progressive enhancement media query should be in <head>."""
        html = _render_full(evaluation_data)
        head_end = html.lower().find("</head>")
        head_html = html[:head_end] if head_end != -1 else ""
        assert "@media" in head_html

    def test_max_width_pattern(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "max-width:600px" in html.replace(" ", "")


class TestFullRender:
    """Full HTML output completeness tests."""

    def test_all_sections_present(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        s = STRINGS["id"]
        assert s["score_overview"] in html
        assert s["detailed_evaluation"] in html
        assert s["score_breakdown"] in html
        assert s["data_intelligence"] in html
        assert s["kesimpulan"] in html

    def test_complete_html_structure(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        lower = html.lower()
        assert "<html" in lower
        assert "</html>" in lower
        assert "<head" in lower
        assert "</head>" in lower
        assert "<body" in lower
        assert "</body>" in lower

    def test_section_ordering(self, evaluation_data: dict) -> None:
        """Sections should appear in order: 01-05."""
        html = _render_full(evaluation_data)
        s = STRINGS["id"]
        pos_overview = html.find(s["score_overview"])
        pos_detailed = html.find(s["detailed_evaluation"])
        pos_breakdown = html.find(s["score_breakdown"])
        pos_intelligence = html.find(s["data_intelligence"])
        pos_kesimpulan = html.find(s["kesimpulan"])
        assert pos_overview < pos_detailed < pos_breakdown < pos_intelligence < pos_kesimpulan


# ===================================================================
# Phase 3 Tests: Custom Note
# ===================================================================


class TestCustomNote:
    """Custom note rendering tests."""

    def test_note_rendered_when_provided(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
            note="Catatan penting untuk brand ini",
        )
        assert "Catatan penting untuk brand ini" in html

    def test_note_preserves_line_breaks(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
            note="Baris pertama\nBaris kedua",
        )
        assert "<br>" in html
        assert "Baris pertama" in html
        assert "Baris kedua" in html

    def test_note_html_escaped(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
            note="<script>alert('xss')</script>",
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_no_note_section_when_none(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
            note=None,
        )
        assert "Custom Note" not in html

    def test_no_note_section_when_empty_string(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
            note="",
        )
        assert "Custom Note" not in html

    def test_note_positioned_before_score_overview(self, evaluation_data: dict) -> None:
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
            note="Test note positioning",
        )
        note_pos = html.find("Test note positioning")
        score_pos = html.find(STRINGS["id"]["score_overview"])
        assert note_pos < score_pos, "Note should appear before Score Overview"
