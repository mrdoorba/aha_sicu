"""Tests for email HTML template rendering."""

from __future__ import annotations

import pytest

from app.modules.email.template import (
    _closing_with_cta_buttons,
    _get_category_map,
    _get_strings,
    _load_locale,
    _render_detailed_evaluation,
    _render_metric_card,
    _resolve_ads_output_text,
    _resolve_translatable_text,
    _translate,
    render_email_html,
    _compute_verdict_counts,
    _format_display_value,
    _resolve_metric_name,
    _score_color,
)


class TestMetricCardLink:
    """Competition rows carry a product link in message_i18n.vars.link."""

    def _row(self) -> dict:
        return {
            "verdict": "❌",
            "metric": "Kompetisi TOP Produk",
            "value": "Produk A",
            "message": "Kompetitor unggul di harga",
            "message_i18n": {"key": "x.missing", "vars": {"link": "https://shopee.co.id/product/1/2"}},
        }

    def test_link_rendered_as_anchor(self) -> None:
        html = _render_metric_card(self._row(), _get_strings("id"), "id", "ID")
        assert 'href="https://shopee.co.id/product/1/2"' in html

    def test_link_localized_for_th_marketplace(self) -> None:
        html = _render_metric_card(self._row(), _get_strings("id"), "th", "TH")
        assert "shopee.co.th/product/1/2" in html
        assert "shopee.co.id" not in html

    def test_link_is_labelled_pill_button(self) -> None:
        html = _render_metric_card(self._row(), _get_strings("id"), "id", "ID")
        # Link renders as a labelled pill, not the raw URL as visible text.
        assert "Lihat di Shopee" in html
        assert "border-radius:20px" in html
        assert ">↪ https://shopee.co.id/product/1/2<" not in html


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
        """Score overview displays the partner score (pass ratio) not internal final_score."""
        html = render_email_html(
            evaluation_data=evaluation_data,
            chart_src="cid:chart123@domain",
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        # Partner score = round(3 checks / 5 total * 100) = 60
        assert ">60<" in html or ">60 " in html.replace("&nbsp;", " ")
        # AHA Compatibility Score pill carries the internal final_score (72.5 -> 72)
        assert ">AHA Compatibility<" in html
        assert ">72<" in html

    def test_score_color_green(self) -> None:
        assert _score_color(80.0) == "#22C55E"
        assert _score_color(95.0) == "#22C55E"

    def test_score_color_blue(self) -> None:
        assert _score_color(50.0) == "#325FEC"
        assert _score_color(79.9) == "#325FEC"

    def test_score_color_orange(self) -> None:
        assert _score_color(49.9) == "#F97316"
        assert _score_color(0.0) == "#F97316"

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

    def test_verdict_counts_not_in_overview(self, evaluation_data: dict) -> None:
        """The ✔️/❌ tally row was removed from the score overview."""
        html = render_email_html(
            evaluation_data=evaluation_data,
            header_src="cid:header123@domain",
            footer_src="cid:footer123@domain",
        )
        # The dedicated green-check tally cell no longer exists.
        assert "font-size:16px;font-weight:bold;color:#22C55E;" not in html

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


class TestDetailedEvaluationTrim:
    """Email detailed section drops per-month Bisnis rows and the ✔️/❌ counter+bar."""

    def _bisnis(self) -> list[dict]:
        return [{
            "category": "Bisnis Analisis",
            "score": 3.0, "max_score": 25.0, "available": True,
            "rows": [
                {"row": 13, "metric": "Penjualan Bulan ZZMONTH", "value": 1, "benchmark": "-",
                 "verdict": "❌", "message": "",
                 "metric_i18n": {"key": "scoring.monthlySales", "vars": {"month": "ZZMONTH"}}},
                {"row": 14, "metric": "Penjualan Bulan YYMONTH", "value": 2, "benchmark": "-",
                 "verdict": "-", "message": "",
                 "metric_i18n": {"key": "scoring.pastMonthlySales", "vars": {"month": "YYMONTH"}}},
                {"row": 19, "metric": "Rata² Penjualan 6 bulan terakhir", "value": 3, "benchmark": "-",
                 "verdict": "-", "message": "",
                 "metric_i18n": {"key": "scoring.avgSales6mo", "vars": {}}},
                {"row": 20, "metric": "Tingkat Konversi", "value": 2.5, "benchmark": ">3%",
                 "verdict": "❌", "message": "",
                 "metric_i18n": {"key": "scoring.conversionRate", "vars": {}}},
            ],
        }]

    def _render(self) -> str:
        return _render_detailed_evaluation(
            self._bisnis(), _get_strings("id"), _get_category_map("id"),
        )

    def test_monthly_rows_dropped(self) -> None:
        html = self._render()
        assert "ZZMONTH" not in html
        assert "YYMONTH" not in html

    def test_avg_and_conversion_kept(self) -> None:
        html = self._render()
        assert "Rata-rata Penjualan 6 Bulan" in html
        assert "Conversion Rate" in html

    def test_no_counter_or_bar(self) -> None:
        html = self._render()
        # Per-category ✔️/❌ counter cell and progress bar are gone from detail cards.
        assert "text-align:right;font-size:13px;font-weight:bold" not in html
        assert 'class="bar-bg"' not in html

    def _promo(self) -> list[dict]:
        tools = [{
            "row": 31 + i, "metric": f"ZZTOOL{i}", "value": i, "benchmark": ">1%",
            "verdict": "❌", "message": "",
            "metric_i18n": {"key": f"scoring.promo.tool{i}", "vars": {}},
        } for i in range(11)]
        summary = [
            {"row": 42, "metric": "% Penggunaan alat promosi", "value": 0.55,
             "benchmark": ">80%", "verdict": "❌", "message": "",
             "metric_i18n": {"key": "scoring.promoUsageRate", "vars": {}}},
            {"row": 43, "metric": "% Efektifitas alat promosi", "value": 0.27,
             "benchmark": ">90%", "verdict": "❌", "message": "",
             "metric_i18n": {"key": "scoring.promoEffectiveness", "vars": {}}},
        ]
        return [{"category": "Promo Toko", "score": 15.0, "max_score": 15.0,
                 "available": True, "rows": tools + summary}]

    def test_promo_tool_rows_dropped(self) -> None:
        html = _render_detailed_evaluation(
            self._promo(), _get_strings("id"), _get_category_map("id"),
        )
        assert all(f"ZZTOOL{i}" not in html for i in range(11))

    def test_promo_percent_summaries_kept(self) -> None:
        html = _render_detailed_evaluation(
            self._promo(), _get_strings("id"), _get_category_map("id"),
        )
        # The two percent cards survive (usage % + effectiveness %).
        assert "Penggunaan" in html
        assert "Efekti" in html or "Effect" in html


class TestVerdictCounting:
    """Verdict counting logic tests."""

    def test_compute_verdict_counts(self, sample_categories: list[dict]) -> None:
        counts = _compute_verdict_counts(sample_categories)
        assert counts["checks"] == 3
        assert counts["xs"] == 2
        assert counts["total"] == 5
        assert counts["score"] == 60  # round(3/5 * 100)

    def test_compute_verdict_counts_empty(self) -> None:
        counts = _compute_verdict_counts([])
        assert counts["checks"] == 0
        assert counts["xs"] == 0
        assert counts["total"] == 0
        assert counts["score"] == 0


class TestDisplayValueFormatting:
    """_format_display_value matches dashboard's CategoryMetricCard logic."""

    def test_pct_prefix_metric_converts_ratio(self) -> None:
        assert _format_display_value("% Pengunjung Lama", 0.15) == "15.0%"

    def test_pct_prefix_metric_zero(self) -> None:
        assert _format_display_value("% Ketersediaan Stok", 0.0) == "0.0%"

    def test_tingkat_appends_pct(self) -> None:
        assert _format_display_value("Tingkat Pesanan Tidak Terselesaikan", 20) == "20%"

    def test_persentase_appends_pct(self) -> None:
        assert _format_display_value("Persentase Chat Dibalas", 14) == "14%"

    def test_plain_int_gets_thousands_sep(self) -> None:
        assert _format_display_value("Penjualan Bulan Feb 2026", 12490428) == "12,490,428"

    def test_plain_float_trimmed(self) -> None:
        assert _format_display_value("Keseluruhan Penilaian", 4.88) == "4.88"

    def test_none_returns_dash(self) -> None:
        assert _format_display_value("Anything", None) == "-"

    def test_string_value_passthrough(self) -> None:
        assert _format_display_value("Anything", "custom") == "custom"


class TestMetricNameTranslation:
    """_resolve_metric_name uses metric_i18n to translate metric names."""

    def test_translates_ad_cost_to_biaya_iklan(self) -> None:
        row = {"metric": "Biaya (iklan)", "metric_i18n": {"key": "scoring.adCost", "vars": {}}}
        assert _resolve_metric_name(row, "id") == "Biaya Iklan"

    def test_translates_ad_sales_to_penjualan_iklan(self) -> None:
        row = {"metric": "Penjualan (iklan)", "metric_i18n": {"key": "scoring.adSales", "vars": {}}}
        assert _resolve_metric_name(row, "id") == "Penjualan Iklan"

    def test_interpolates_month_var(self) -> None:
        row = {"metric": "Penjualan Bulan Feb 2026", "metric_i18n": {"key": "scoring.monthlySales", "vars": {"month": "Feb 2026"}}}
        assert _resolve_metric_name(row, "id") == "Penjualan Bulan Feb 2026"

    def test_falls_back_to_raw_metric_when_no_i18n(self) -> None:
        row = {"metric": "Some Custom Metric", "metric_i18n": None}
        assert _resolve_metric_name(row, "id") == "Some Custom Metric"

    def test_falls_back_when_key_missing_from_locale(self) -> None:
        row = {"metric": "Fallback Name", "metric_i18n": {"key": "nonexistent.key", "vars": {}}}
        assert _resolve_metric_name(row, "id") == "Fallback Name"


class TestStringsAndCategoryMap:
    """_get_strings() and _get_category_map() tests."""

    def test_strings_returns_dict_for_id(self) -> None:
        s = _get_strings("id")
        assert isinstance(s, dict)
        assert len(s) > 0

    def test_strings_has_section_headers(self) -> None:
        id_strings = _get_strings("id")
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
            s = _get_strings(lang)
            for key in ("average_stock", "product_code", "product_name", "kesimpulan", "marketing_budget"):
                assert key in s, f"Missing _get_strings({lang}) key: {key}"

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
        cat_map = _get_category_map("id")
        for key in expected_keys:
            assert key in cat_map, f"Missing CATEGORY_MAP key: {key}"

    def test_migrated_email_strings_fidelity(self) -> None:
        """Spot-check that migrated locale values match original hardcoded values."""
        id_s = _get_strings("id")
        assert id_s["score_overview"] == "Laporan Evaluasi Brand"
        assert id_s["marketing_budget"] == "Est. Biaya Marketing"
        en_s = _get_strings("en")
        assert en_s["score_overview"] == "Brand Evaluation Report"
        assert en_s["marketing_budget"] == "Est. Marketing Budget"
        th_s = _get_strings("th")
        assert th_s["score_overview"] is not None  # Thai chars, just verify present

    def test_get_strings_returns_key_name_when_locale_missing(self, tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> None:
        """_get_strings falls back to key name when locale file unavailable."""
        import app.modules.email.layout as layout
        monkeypatch.setattr(layout, "_LOCALES_DIR", tmp_path)
        _load_locale.cache_clear()
        s = _get_strings("id")
        assert s["score_overview"] == "score_overview"  # key name as fallback
        _load_locale.cache_clear()  # restore for other tests


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

    def test_metric_card_no_score_line(self, evaluation_data: dict) -> None:
        """Metric cards should NOT render a per-metric score line."""
        html = _render_full(evaluation_data)
        # The Indonesian label "Skor:" should not appear as a metric-card field.
        # The word "Skor" may appear in section headers (e.g. "Ringkasan Skor"),
        # so we check specifically for the pattern used in metric cards.
        assert "Skor: <strong" not in html
        assert "Score: <strong" not in html

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
        assert _get_strings("id")["detailed_evaluation"] not in html


class TestBenchmarkVisibility:
    """Benchmark line hidden when value is '-' or empty, matching dashboard behavior."""

    def test_hides_benchmark_when_dash(self, evaluation_data: dict) -> None:
        """Metrics with benchmark='-' should not render 'Benchmark: -'."""
        # Inject a row with benchmark='-'
        evaluation_data["score_breakdown"][0]["rows"].append(
            {"metric": "Sales Info", "value": 100, "benchmark": "-", "message": "", "verdict": "-", "score": 0}
        )
        html = _render_full(evaluation_data)
        assert "Benchmark: -" not in html

    def test_hides_benchmark_for_biaya_iklan(self, evaluation_data: dict) -> None:
        """Biaya (iklan) benchmark is overridden to '-' like the dashboard."""
        evaluation_data["score_breakdown"].append(
            {"category": "Data Iklan", "score": 0, "max_score": 10, "rows": [
                {"metric": "Biaya (iklan)", "value": 3500000, "benchmark": "28.0%", "message": "", "verdict": "-", "score": 0}
            ]}
        )
        html = _render_full(evaluation_data)
        assert "Benchmark: 28.0%" not in html

    def test_shows_benchmark_when_present(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "Benchmark:" in html

    def test_hides_separator_when_no_detail(self, evaluation_data: dict) -> None:
        """No separator or benchmark row for metrics with benchmark='-' and no message."""
        evaluation_data["score_breakdown"] = [
            {"category": "Bisnis Analisis", "score": 5, "max_score": 10, "rows": [
                {"metric": "Revenue Only", "value": 1000, "benchmark": "-", "message": "", "verdict": "-", "score": 0}
            ]}
        ]
        html = _render_full(evaluation_data)
        # The card should just be name + value, no separator border
        assert "Revenue Only" in html
        assert "Benchmark:" not in html


class TestMessageFormatting:
    """Metric card messages and multiline values render correctly in email."""

    def test_multiline_message_renders_br_tags(self, evaluation_data: dict) -> None:
        """Messages with newlines should use <br> in email HTML."""
        evaluation_data["score_breakdown"][0]["rows"][0]["message"] = (
            "Line one\nLine two\nLine three"
        )
        html = _render_full(evaluation_data)
        assert "Line one<br>Line two<br>Line three" in html

    def test_single_line_message_no_br(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        # "Baik" should appear without any <br>
        assert "Baik" in html

    def test_multiline_value_renders_br_and_left_aligned(self, evaluation_data: dict) -> None:
        """Multiline string values (e.g. Discount Check Up) use <br> and left align."""
        evaluation_data["score_breakdown"][0]["rows"][0]["value"] = (
            "% Diskon TOP SKU: 84.0%\nRange: 30.0% ~ 50.0%"
        )
        html = _render_full(evaluation_data)
        assert "% Diskon TOP SKU: 84.0%<br>Range: 30.0% ~ 50.0%" in html
        assert "text-align:left" in html

    def test_single_value_right_aligned(self, evaluation_data: dict) -> None:
        """Normal numeric values stay right-aligned."""
        html = _render_full(evaluation_data)
        assert "text-align:right" in html


class TestCategoryDividers:
    """Divider lines appear between metric sub-groups matching the dashboard."""

    def _make_eval_data(self, rows: list[dict]) -> dict:
        """Build minimal evaluation_data dict matching EvaluationDetailResponse shape."""
        return {
            "id": 1,
            "brand_id": 1,
            "brand_name": "Test",
            "final_score": 50.0,
            "verdict": "✔️",
            "template": "non_fashion",
            "score_breakdown": [
                {
                    "category": "Bisnis Analisis",
                    "score": 5,
                    "max_score": 10,
                    "rows": rows,
                }
            ],
            "calculator_results": {},
            "period": "Jan 2026",
        }

    def _row(self, metric: str) -> dict:
        return {
            "metric": metric,
            "value": 100,
            "benchmark": "-",
            "verdict": "✔️",
            "message": "",
            "score": 5,
        }

    def test_no_divider_after_rata_penjualan(self) -> None:
        # The Rata² divider was dropped: monthly sales rows are hidden in the
        # email, so the average pairs side-by-side with Conversion Rate.
        data = self._make_eval_data([
            self._row("Rata² Penjualan 6 bulan terakhir"),
            self._row("Tingkat Konversi"),
        ])
        html = _render_full(data)
        assert "border-top:1px solid #325FEC4D" not in html

    def test_divider_after_program_afiliasi(self) -> None:
        data = self._make_eval_data([
            self._row("Program Afiliasi"),
            self._row("% Penggunaan alat promosi"),
        ])
        html = _render_full(data)
        assert "border-top:1px solid #325FEC4D" in html

    def test_divider_after_roi(self) -> None:
        data = self._make_eval_data([
            self._row("Penjualan (iklan)"),
            self._row("Biaya (iklan)"),
            self._row("ROI"),
            self._row("% GMV Iklan / GMV Toko"),
        ])
        html = _render_full(data)
        assert "border-top:1px solid #325FEC4D" in html

    def test_no_divider_for_normal_metrics(self) -> None:
        data = self._make_eval_data([
            self._row("Penjualan Bulan Feb 2026"),
            self._row("Penjualan Bulan Jan 2026"),
        ])
        html = _render_full(data)
        assert "border-top:1px solid #325FEC4D" not in html

    def test_iklan_check_up_excluded(self) -> None:
        """'Iklan check up' metric is hidden in email, matching dashboard filter."""
        data = self._make_eval_data([
            self._row("Penjualan (iklan)"),
            self._row("ROI"),
            self._row("Iklan check up"),
        ])
        html = _render_full(data)
        assert "Iklan check up" not in html
        # Other metrics still present
        assert "ROI" in html


class TestDroppedSections:
    """Data Intelligence (03) + Score Breakdown radar (04) are dropped from the email."""

    def test_data_intelligence_absent(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert _get_strings("id")["data_intelligence"] not in html
        # Top-SKU / ads content that lived only in that section is gone.
        assert "Sepatu Running" not in html

    def test_score_breakdown_absent(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert _get_strings("id")["score_breakdown"] not in html
        assert "cid:chart123@domain" not in html

    def test_still_valid_html(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "<!doctype html" in html.lower()


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
        assert _get_strings("id")["marketing_budget"] in html

    def test_closing_message_rendered(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "brand ini menunjukkan performa yang baik" in html

    def test_closing_message_preserves_line_breaks(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert "<br>" in html

    def test_section_header_present(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        assert _get_strings("id")["kesimpulan"] in html

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
        assert _get_strings("id")["kesimpulan"] not in html

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
        assert _get_strings("id")["kesimpulan"] not in html

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
        assert _get_strings("id")["kesimpulan"] in html
        assert "Good performance" in html
        assert _get_strings("id")["marketing_budget"] not in html

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

    def test_no_max_width_on_wrapper(self, evaluation_data: dict) -> None:
        """Email wrapper table should be fully fluid — no max-width cap."""
        html = _render_full(evaluation_data)
        # The outer wrapper table should NOT have a max-width constraint.
        # (Inner elements like table cells and media queries may still use max-width.)
        assert "max-width:600px" not in html.replace(" ", "")
        assert "max-width:900px" not in html.replace(" ", "")


class TestFullRender:
    """Full HTML output completeness tests."""

    def test_all_sections_present(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        s = _get_strings("id")
        assert s["score_overview"] in html
        assert s["detailed_evaluation"] in html
        assert s["kesimpulan"] in html

    def test_dropped_sections_absent(self, evaluation_data: dict) -> None:
        # Data Intelligence (03) + Score Breakdown radar (04) are dropped.
        html = _render_full(evaluation_data)
        s = _get_strings("id")
        assert s["data_intelligence"] not in html
        assert s["score_breakdown"] not in html
        assert "cid:chart123@domain" not in html

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
        """Remaining sections in order: overview, detailed, kesimpulan."""
        html = _render_full(evaluation_data)
        s = _get_strings("id")
        pos_overview = html.find(s["score_overview"])
        pos_detailed = html.find(s["detailed_evaluation"])
        pos_kesimpulan = html.find(s["kesimpulan"])
        assert pos_overview < pos_detailed < pos_kesimpulan


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
        # The score-overview section title now matches the email's main title
        # ("Laporan Evaluasi Brand") too, so the section is the *last* occurrence.
        score_pos = html.rfind(_get_strings("id")["score_overview"])
        assert note_pos < score_pos, "Note should appear before Score Overview"


# ===================================================================
# Phase: Email i18n — translate _i18n companion fields
# ===================================================================


def _render_full_th(evaluation_data: dict) -> str:
    """Helper to render full email HTML in Thai."""
    return render_email_html(
        evaluation_data=evaluation_data,
        chart_src="cid:chart123@domain",
        header_src="cid:header123@domain",
        footer_src="cid:footer123@domain",
        language="th",
    )


class TestResolveTranslatableText:
    """Unit tests for _resolve_translatable_text helper."""

    def test_resolves_valid_i18n_dict(self) -> None:
        i18n = {"key": "scoring.adCost", "vars": {}}
        result = _resolve_translatable_text(i18n, "Biaya (iklan)", "th")
        assert result == "ค่าใช้จ่ายโฆษณา"

    def test_falls_back_when_i18n_is_none(self) -> None:
        result = _resolve_translatable_text(None, "fallback text", "th")
        assert result == "fallback text"

    def test_falls_back_when_i18n_has_no_key(self) -> None:
        result = _resolve_translatable_text({"key": "", "vars": {}}, "fallback", "th")
        assert result == "fallback"

    def test_falls_back_when_key_missing_from_locale(self) -> None:
        i18n = {"key": "nonexistent.key.xyz", "vars": {}}
        result = _resolve_translatable_text(i18n, "raw text", "th")
        assert result == "raw text"

    def test_interpolates_vars(self) -> None:
        i18n = {"key": "scoring.monthlySales", "vars": {"month": "Feb 2026"}}
        result = _resolve_translatable_text(i18n, "Penjualan Bulan Feb 2026", "th")
        assert "Feb 2026" in result
        # Should be Thai, not Indonesian
        assert "ยอดขาย" in result

    def test_falls_back_when_i18n_is_not_dict(self) -> None:
        result = _resolve_translatable_text("not a dict", "fallback", "th")
        assert result == "fallback"


class TestBenchmarkLabelI18n:
    """Benchmark label uses S['benchmark'] instead of hardcoded 'Benchmark:'."""

    def test_thai_benchmark_label_translated(self, evaluation_data: dict) -> None:
        html = _render_full_th(evaluation_data)
        th_strings = _get_strings("th")
        # TH emails append an English copy below a divider; check the TH portion only.
        th_portion = html.split("English version", 1)[0]
        # Should contain the Thai benchmark label
        assert f"{th_strings['benchmark']}:" in th_portion
        # Should NOT contain hardcoded English/Indonesian "Benchmark:"
        assert "Benchmark:" not in th_portion

    def test_indonesian_benchmark_label_still_works(self, evaluation_data: dict) -> None:
        html = _render_full(evaluation_data)
        id_strings = _get_strings("id")
        assert f"{id_strings['benchmark']}:" in html


class TestRowMessageI18n:
    """Row-level message_i18n resolution in metric cards."""

    def test_thai_row_message_resolved_from_i18n(self, evaluation_data: dict) -> None:
        """When message_i18n is present, Thai email should use translated message."""
        evaluation_data["score_breakdown"][0]["rows"][0]["message_i18n"] = {
            "key": "scoring.chatResponseRate.pass",
            "vars": {"value": "95"},
        }
        html = _render_full_th(evaluation_data)
        # Thai translation should appear
        assert "อัตราการตอบแชท" in html

    def test_falls_back_to_raw_message_when_no_i18n(self, evaluation_data: dict) -> None:
        """Without message_i18n, raw Indonesian message is used (backward compat)."""
        # Ensure no message_i18n key
        for cat in evaluation_data["score_breakdown"]:
            for row in cat["rows"]:
                row.pop("message_i18n", None)
        html = _render_full_th(evaluation_data)
        assert "Baik" in html  # raw Indonesian text

    def test_falls_back_when_i18n_key_missing(self, evaluation_data: dict) -> None:
        """If the i18n key doesn't exist in locale, fall back to raw message."""
        evaluation_data["score_breakdown"][0]["rows"][0]["message_i18n"] = {
            "key": "nonexistent.key",
            "vars": {},
        }
        html = _render_full_th(evaluation_data)
        assert "Baik" in html  # fallback to raw "message"


class TestValueI18n:
    """Row-level value_i18n resolution (e.g. discount checkup multiline value)."""

    def test_thai_value_resolved_from_value_i18n(self, evaluation_data: dict) -> None:
        """Discount checkup multiline value should use value_i18n when present."""
        evaluation_data["score_breakdown"].append({
            "category": "Discount",
            "score": 0, "max_score": 10, "available": True,
            "rows": [{
                "row": 73, "metric": "Discount Check Up",
                "value": "% Diskon TOP SKU: 26.9%\nRange: 0.0% ~ 69.6%\nVoucher 0.0%\nPaket Diskon 0.0%\n📌 Berpotensi menggunakan 'fake discount'",
                "value_i18n": {
                    "key": "scoring.discountCheckup.fail",
                    "vars": {"discountPct": "26.9%", "rangeMin": "0.0%", "rangeMax": "69.6%", "voucherPct": "0.0%", "paketPct": "0.0%"},
                },
                "benchmark": "-", "verdict": "❌", "message": "", "score": 0,
                "metric_i18n": {"key": "scoring.discountCheckup", "vars": {}},
                "message_i18n": None,
            }],
        })
        html = _render_full_th(evaluation_data)
        # Thai translation should appear
        assert "ส่วนลด TOP SKU" in html
        # Indonesian raw should NOT appear
        assert "Diskon TOP SKU" not in html

    def test_falls_back_to_raw_value_when_no_value_i18n(self, evaluation_data: dict) -> None:
        """Without value_i18n, raw value is used."""
        evaluation_data["score_breakdown"].append({
            "category": "Discount",
            "score": 0, "max_score": 10, "available": True,
            "rows": [{
                "row": 73, "metric": "Discount Check Up",
                "value": "% Diskon TOP SKU: 26.9%",
                "benchmark": "-", "verdict": "❌", "message": "", "score": 0,
            }],
        })
        html = _render_full_th(evaluation_data)
        assert "Diskon TOP SKU" in html  # raw Indonesian preserved


class TestConclusionI18n:
    """conclusion_i18n bullet points resolved in kesimpulan section."""

    def _make_th_eval(self, sample_categories: list[dict]) -> dict:
        return {
            "id": 1,
            "brand_id": 1,
            "brand_name": "Test TH",
            "final_score": 50.0,
            "verdict": "✔️",
            "template": "fashion",
            "score_breakdown": sample_categories,
            "calculator_results": {
                "scoring_summary": {
                    "conclusion": "- Performa toko sangat baik",
                    "conclusion_i18n": [
                        {"key": "conclusion.operationalGood", "vars": {}},
                    ],
                    "marketing_budget": "IDR 5,000,000",
                    "marketing_budget_i18n": {
                        "key": "marketing.budgetRecommendation",
                        "vars": {"pct": "22.4% ~ 26.2%"},
                    },
                    "closing_message": "Kami melihat potensi toko",
                    "closing_message_i18n": {
                        "key": "closing.potentialTh",
                        "vars": {"store_name": "Test TH"},
                    },
                },
            },
            "period": "Maret 2026",
            "marketplace": "TH",
        }

    def test_thai_conclusion_bullets_translated(self, sample_categories: list[dict]) -> None:
        data = self._make_th_eval(sample_categories)
        html = render_email_html(
            evaluation_data=data,
            chart_src="cid:chart",
            header_src="cid:header",
            footer_src="cid:footer",
            language="th",
        )
        # Thai translation of conclusion.operationalGood
        assert "คุณภาพการดำเนินงานของร้านค้าอยู่ในเกณฑ์ค่อนข้างดี" in html
        # Raw Indonesian should NOT appear
        assert "Performa toko sangat baik" not in html

    def test_inline_store_url_is_not_turned_into_cta_button(self) -> None:
        # Regression: a brand whose store_name is itself a URL (e.g. redcarpet.id)
        # used to render a second, bogus "Jadwalkan Konsultasi Gratis" button
        # pointing at the store. Only the standalone consultation link is a CTA.
        S = _get_strings("id")
        closing = (
            "Kami melihat bahwa potensi dari Toko https://redcarpet.id/ masih belum maksimal. "
            "Silahkan klik di link berikut ini untuk menjadwalkan sesi konsultasi.\n\n"
            "cal-bd2.ahacommerce.net\n\n"
            "Semoga apa yang kami bagikan dapat bermanfaat."
        )
        html = _closing_with_cta_buttons(closing, S)
        assert html.count(S["schedule_consultation"]) == 1
        assert "cal-bd2.ahacommerce.net" in html
        # The store URL survives as inline text, never as an <a href> button.
        assert "redcarpet.id" in html
        assert 'href="https://redcarpet.id/"' not in html

    def test_thai_closing_message_translated(self, sample_categories: list[dict]) -> None:
        data = self._make_th_eval(sample_categories)
        html = render_email_html(
            evaluation_data=data,
            chart_src="cid:chart",
            header_src="cid:header",
            footer_src="cid:footer",
            language="th",
        )
        # Thai closing.potential contains this
        assert "ศักยภาพ" in html
        assert "th-bd2.ahacommerce.net" in html
        assert "cal-bd2.ahacommerce.net" not in html
        # Raw Indonesian should NOT appear
        assert "Kami melihat potensi toko" not in html

    def test_english_th_closing_message_uses_th_link(self, sample_categories: list[dict]) -> None:
        data = self._make_th_eval(sample_categories)
        html = render_email_html(
            evaluation_data=data,
            chart_src="cid:chart",
            header_src="cid:header",
            footer_src="cid:footer",
            language="en",
        )
        assert "th-bd2.ahacommerce.net" in html
        assert "cal-bd2.ahacommerce.net" not in html

    def test_thai_marketing_budget_translated(self, sample_categories: list[dict]) -> None:
        data = self._make_th_eval(sample_categories)
        html = render_email_html(
            evaluation_data=data,
            chart_src="cid:chart",
            header_src="cid:header",
            footer_src="cid:footer",
            language="th",
        )
        # Thai marketing.budgetRecommendation contains this
        assert "งบการตลาด" in html

    def test_conclusion_atomic_fallback(self, sample_categories: list[dict]) -> None:
        """If ANY bullet in conclusion_i18n fails, use entire raw conclusion."""
        data = self._make_th_eval(sample_categories)
        data["calculator_results"]["scoring_summary"]["conclusion_i18n"] = [
            {"key": "conclusion.operationalGood", "vars": {}},
            {"key": "nonexistent.key.xyz", "vars": {}},  # will fail
        ]
        html = render_email_html(
            evaluation_data=data,
            chart_src="cid:chart",
            header_src="cid:header",
            footer_src="cid:footer",
            language="th",
        )
        # Falls back to raw Indonesian
        assert "Performa toko sangat baik" in html


class TestBackwardCompatibility:
    """Indonesian emails without _i18n fields render identically."""

    def test_indonesian_without_i18n_fields_unchanged(self, evaluation_data: dict) -> None:
        """Evaluation data without any _i18n fields should render the same as before."""
        # Ensure no _i18n fields
        for cat in evaluation_data["score_breakdown"]:
            for row in cat["rows"]:
                row.pop("message_i18n", None)
        summary = evaluation_data["calculator_results"]["scoring_summary"]
        summary.pop("conclusion_i18n", None)
        summary.pop("closing_message_i18n", None)
        summary.pop("marketing_budget_i18n", None)

        html = _render_full(evaluation_data)
        # Indonesian text preserved
        assert "Baik" in html
        assert "Performa toko sangat baik" in html
        assert "IDR 5,000,000" in html
        assert "brand ini menunjukkan performa yang baik" in html

    def test_fallback_missing_translation_key(self, evaluation_data: dict) -> None:
        """When _i18n key doesn't exist in locale, fall back to raw text."""
        evaluation_data["calculator_results"]["scoring_summary"]["conclusion_i18n"] = [
            {"key": "totally.fake.key", "vars": {}},
        ]
        html = _render_full(evaluation_data)
        # Falls back to raw Indonesian conclusion
        assert "Performa toko sangat baik" in html


# ===================================================================
# Phase: Ads keyword i18n — translate ads output_text sections
# ===================================================================


class TestTranslateNestedRefs:
    """_translate resolves $t(key) nested references."""

    def test_resolves_dollar_t_refs(self) -> None:
        # ads.topAd template contains $t({{biddingKey}}) etc.
        result = _translate(
            "ads.topAd",
            {
                "name": "Test Ad",
                "gmv": "THB 1,000",
                "roas": "5.00",
                "biddingKey": "ads.value.biddingOtomatis",
                "jenisKey": "ads.value.iklanProduk",
                "penempatanKey": "ads.value.semuaPenempatan",
                "keyword": "shoes",
            },
            "th",
        )
        assert result is not None
        # $t(ads.value.biddingOtomatis) should resolve to Thai "บิดอัตโนมัติ"
        assert "บิดอัตโนมัติ" in result
        assert "$t(" not in result  # no unresolved refs
        assert "Test Ad" in result

    def test_dollar_t_with_missing_key_leaves_key_name(self) -> None:
        """When a $t() ref key is missing from locale, leave the key name."""
        result = _translate(
            "ads.topRecommendation.manual",
            {},
            "th",
        )
        assert result is not None
        # This key has no $t() refs, should just work
        assert "$t(" not in result


class TestResolveAdsOutputText:
    """_resolve_ads_output_text assembles translated ads sections."""

    def _sample_details(self) -> dict:
        return {
            "ak2_i18n": {"key": "ads.summary", "vars": {
                "active": "25", "paused": "0", "ended": "0",
                "unique_count": "24", "product_pct": "68.6%",
                "total_products": "35",
            }},
            "ak3_i18n": {"key": "ads.typeBreakdown", "vars": {
                "semua_total": "23", "toko_total": "1",
                "toko_auto": "1", "toko_manual": "0",
            }},
            "ak4_i18n": [
                {"key": "ads.flag.productGood", "vars": {}},
                {"key": "ads.flag.activeGood", "vars": {}},
            ],
            "al2_i18n": {
                "header": {"key": "ads.topHeader", "vars": {}},
                "ads": [
                    {"key": "ads.topAd", "vars": {
                        "name": "SALT Cameron",
                        "gmv": "THB 42,609",
                        "roas": "8.82",
                        "biddingKey": "ads.value.gmvMaxRoas",
                        "jenisKey": "ads.value.iklanProduk",
                        "penempatanKey": "ads.value.semuaPenempatan",
                        "keyword": "Auto Selected",
                    }},
                ],
            },
            "al3_i18n": {"key": "ads.topRecommendation.auto", "vars": {}},
            "al5_i18n": None,
            "al6_i18n": {"key": "ads.flag.autoUncontrolled", "vars": {}},
            "al7_i18n": None,
            "al8_i18n": None,
            "al9_i18n": None,
        }

    def test_resolves_all_sections_to_thai(self) -> None:
        details = self._sample_details()
        result = _resolve_ads_output_text(details, "th")
        assert result is not None
        # ak2: Thai ads.summary
        assert "โฆษณาทั้งหมด" in result
        # ak3: Thai ads.typeBreakdown
        assert "ประเภทโฆษณา" in result
        # ak4: Thai flags
        assert "จำนวนสินค้าที่เข้าร่วมโฆษณาอยู่ในระดับดี" in result
        # al2: Thai top ads header
        assert "โฆษณา TOP" in result
        # al3: Thai recommendation
        assert "การตั้งค่าอัตโนมัติ" in result
        # al6: Thai flag
        assert "ค่าใช้จ่ายไม่สามารถควบคุมได้" in result

    def test_returns_none_when_no_i18n_details(self) -> None:
        result = _resolve_ads_output_text({}, "th")
        assert result is None

    def test_returns_none_when_all_i18n_none(self) -> None:
        details = {
            "ak2_i18n": None, "ak3_i18n": None, "ak4_i18n": None,
            "al2_i18n": None, "al3_i18n": None, "al5_i18n": None,
            "al6_i18n": None, "al7_i18n": None, "al8_i18n": None,
            "al9_i18n": None,
        }
        result = _resolve_ads_output_text(details, "th")
        assert result is None

    def test_falls_back_to_none_on_missing_key(self) -> None:
        details = self._sample_details()
        details["ak2_i18n"] = {"key": "nonexistent.key", "vars": {}}
        result = _resolve_ads_output_text(details, "th")
        # Atomic fallback — if any section fails, return None
        assert result is None
