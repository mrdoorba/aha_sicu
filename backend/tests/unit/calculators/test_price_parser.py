"""Unit tests for the shared price parser.

Covers IDR (default) and THB marketplace formats,
edge cases, and type passthrough.
"""

from app.calculators.price_parser import _parse_price


# ---------------------------------------------------------------------------
# IDR format (default marketplace)
# ---------------------------------------------------------------------------


class TestParsePrice_IDR:
    def test_removes_dots_thousands(self):
        assert _parse_price("125.000") == 125000.0

    def test_multiple_dots_thousands(self):
        assert _parse_price("1.250.000") == 1250000.0

    def test_zero_string(self):
        assert _parse_price("0") == 0.0

    def test_no_dots(self):
        assert _parse_price("5000") == 5000.0

    def test_explicit_id_marketplace(self):
        assert _parse_price("125.000", "ID") == 125000.0


# ---------------------------------------------------------------------------
# THB format
# ---------------------------------------------------------------------------


class TestParsePrice_THB:
    def test_comma_thousands_dot_decimal(self):
        assert _parse_price("1,250.50", "TH") == 1250.5

    def test_comma_thousands_no_decimal(self):
        assert _parse_price("12,500", "TH") == 12500.0

    def test_multiple_comma_thousands(self):
        assert _parse_price("1,250,000", "TH") == 1250000.0

    def test_decimal_only_no_comma(self):
        assert _parse_price("125.50", "TH") == 125.5

    def test_integer_string(self):
        assert _parse_price("500", "TH") == 500.0

    def test_comma_thousands_two_decimal(self):
        assert _parse_price("99,999.99", "TH") == 99999.99


# ---------------------------------------------------------------------------
# Edge cases (marketplace-independent)
# ---------------------------------------------------------------------------


class TestParsePrice_EdgeCases:
    def test_none_returns_zero(self):
        assert _parse_price(None) == 0.0

    def test_empty_string_returns_zero(self):
        assert _parse_price("") == 0.0

    def test_whitespace_string_returns_zero(self):
        assert _parse_price("   ") == 0.0

    def test_integer_passthrough(self):
        assert _parse_price(125000) == 125000.0

    def test_float_passthrough(self):
        assert _parse_price(125.5) == 125.5

    def test_non_numeric_string_returns_zero(self):
        assert _parse_price("abc") == 0.0

    def test_non_numeric_string_th_returns_zero(self):
        assert _parse_price("abc", "TH") == 0.0

    def test_default_marketplace_is_id(self):
        """No second argument = IDR behavior (strip dots)."""
        assert _parse_price("125.000") == 125000.0

    def test_zero_int(self):
        assert _parse_price(0) == 0.0

    def test_zero_float(self):
        assert _parse_price(0.0) == 0.0
