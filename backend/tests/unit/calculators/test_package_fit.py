"""Tests for package fit — VP against the bar its package sets."""

import pytest

from app.calculators.package_fit import PACKAGE_BARS, has_scored_vp, read_package_fit


def _row(package: str = "New Star", vp: str = "80") -> dict:
    return {"Brand": "Test Brand", "Package": package, "VP": vp}


class TestBars:
    """Each package's bar, and the boundary between met and short."""

    def test_bars_match_the_agreed_thresholds(self):
        assert PACKAGE_BARS == {
            "New Star": 65.0,
            "Rising Star": 80.0,
            "Superstar": 80.0,
        }

    @pytest.mark.parametrize(
        "package,vp",
        [("New Star", "65"), ("Rising Star", "80"), ("Superstar", "80")],
    )
    def test_vp_exactly_on_the_bar_is_not_penalised(self, package, vp):
        fit = read_package_fit(_row(package, vp))
        assert fit.adjustment == 0.0
        assert fit.met is True

    @pytest.mark.parametrize(
        "package,vp",
        [("New Star", "64"), ("Rising Star", "79"), ("Superstar", "79")],
    )
    def test_vp_one_below_the_bar_loses_ten(self, package, vp):
        fit = read_package_fit(_row(package, vp))
        assert fit.adjustment == -10.0
        assert fit.met is False

    def test_new_star_bar_is_lower_than_rising_star(self):
        # VP 70 clears New Star but falls short of Rising Star.
        assert read_package_fit(_row("New Star", "70")).adjustment == 0.0
        assert read_package_fit(_row("Rising Star", "70")).adjustment == -10.0

    def test_reports_the_bar_it_judged_against(self):
        fit = read_package_fit(_row("Superstar", "50"))
        assert (fit.package, fit.vp, fit.bar) == ("Superstar", 50.0, 80.0)


class TestUnjudgeable:
    """Sheet bookkeeping never costs a brand points."""

    @pytest.mark.parametrize("vp", ["0", "", "   ", "n/a", None])
    def test_vp_without_a_real_number_is_not_penalised(self, vp):
        # 0 marks a duplicate row whose real data sits on the brand's other row.
        fit = read_package_fit({"Package": "Superstar", "VP": vp})
        assert fit.adjustment == 0.0
        assert fit.vp is None
        assert fit.met is None
        assert fit.judged is False

    @pytest.mark.parametrize("package", ["Super Star", "Platinum", "", None])
    def test_unrecognised_package_has_no_bar_and_no_penalty(self, package):
        fit = read_package_fit({"Package": package, "VP": "10"})
        assert fit.adjustment == 0.0
        assert fit.bar is None
        assert fit.met is None

    def test_empty_row(self):
        fit = read_package_fit({})
        assert (fit.package, fit.vp, fit.bar, fit.adjustment) == (None, None, None, 0.0)

    def test_missing_raw_data(self):
        assert read_package_fit(None).adjustment == 0.0


class TestSheetFormats:
    """The VP column is text from a spreadsheet, not a number."""

    @pytest.mark.parametrize("vp,expected", [("80", 80.0), (80, 80.0), ("80.0", 80.0), (" 85 ", 85.0), ("1,100", 1100.0)])
    def test_parses_the_cell_as_written(self, vp, expected):
        assert read_package_fit(_row("Superstar", vp)).vp == expected

    def test_package_name_is_trimmed(self):
        assert read_package_fit(_row(" Rising Star ", "50")).adjustment == -10.0


class TestRealSheetRows:
    """Rows read from the live BD sheets on 2026-09-10."""

    @pytest.mark.parametrize(
        "brand,package,vp,expected",
        [
            ("Lem Castol", "New Star", "65", 0.0),        # exactly on its bar
            ("151.store", "New Star", "45", -10.0),
            ("11/10 Studios", "Rising Star", "65", -10.0),
            ("24 Bottles", "Rising Star", "95", 0.0),
            ("ACCA by Dr.DSP", "Superstar", "50", -10.0),  # TH
            ("109 Pillow", "Superstar", "85", 0.0),
            ("Your Glasses", "New Star", "0", 0.0),        # duplicate row
        ],
    )
    def test_matches_the_agreed_outcome(self, brand, package, vp, expected):
        fit = read_package_fit({"Brand": brand, "Package": package, "VP": vp})
        assert fit.adjustment == expected


class TestHasScoredVp:
    """The predicate sync uses to pick a duplicate brand's real row."""

    def test_a_real_number_counts_as_scored(self):
        assert has_scored_vp({"VP": "72"}) is True

    def test_zero_does_not_count_as_scored(self):
        assert has_scored_vp({"VP": "0"}) is False

    def test_blank_does_not_count_as_scored(self):
        assert has_scored_vp({"VP": ""}) is False

    def test_a_missing_column_does_not_count_as_scored(self):
        assert has_scored_vp({"Package": "New Star"}) is False

    def test_none_does_not_count_as_scored(self):
        assert has_scored_vp(None) is False

    def test_it_agrees_with_the_vp_the_penalty_reads(self):
        """One fact, one source: both readers must never disagree."""
        for cell in ["72", "0", "", "  ", "n/a", "1,05", "110"]:
            row = {"VP": cell}
            assert has_scored_vp(row) is (read_package_fit(row).vp is not None)
