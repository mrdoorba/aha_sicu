"""Tests for _extract_parsed_data backward compatibility."""

import pytest

from app.core.exceptions import CalculatorException
from app.modules.evaluations.calculator_service import _extract_parsed_data


class TestExtractParsedData:
    """_extract_parsed_data reads both old and new formats."""

    def test_reads_new_rows_format(self):
        upload = {
            "parsed_data": {
                "columns": ["A", "B"],
                "rows": [[1, "x"], [2, "y"]],
                "row_count": 2,
            }
        }
        result = _extract_parsed_data(upload, "order_export")
        assert result == [{"A": 1, "B": "x"}, {"A": 2, "B": "y"}]

    def test_reads_old_data_format(self):
        upload = {
            "parsed_data": {
                "columns": ["A", "B"],
                "data": [{"A": 1, "B": "x"}, {"A": 2, "B": "y"}],
                "row_count": 2,
            }
        }
        result = _extract_parsed_data(upload, "order_export")
        assert result == [{"A": 1, "B": "x"}, {"A": 2, "B": "y"}]

    def test_prefers_rows_over_data(self):
        """If both keys exist (shouldn't happen), prefer rows."""
        upload = {
            "parsed_data": {
                "columns": ["A"],
                "rows": [[1]],
                "data": [{"A": 999}],
                "row_count": 1,
            }
        }
        result = _extract_parsed_data(upload, "order_export")
        assert result == [{"A": 1}]

    def test_empty_rows(self):
        upload = {
            "parsed_data": {
                "columns": ["A", "B"],
                "rows": [],
                "row_count": 0,
            }
        }
        result = _extract_parsed_data(upload, "order_export")
        assert result == []

    def test_invalid_parsed_data_raises(self):
        upload = {"parsed_data": None}
        with pytest.raises(CalculatorException) as exc:
            _extract_parsed_data(upload, "order_export")
        assert exc.value.code == "CALC_MISSING_DATA"

    def test_missing_both_keys_raises(self):
        upload = {
            "parsed_data": {
                "columns": ["A"],
                "row_count": 0,
            }
        }
        with pytest.raises(CalculatorException) as exc:
            _extract_parsed_data(upload, "order_export")
        assert exc.value.code == "CALC_MISSING_DATA"

    def test_json_string_with_rows_format(self):
        """Handle double-encoded JSON string (rows format)."""
        import json
        upload = {
            "parsed_data": json.dumps({
                "columns": ["A"],
                "rows": [[1], [2]],
                "row_count": 2,
            })
        }
        result = _extract_parsed_data(upload, "order_export")
        assert result == [{"A": 1}, {"A": 2}]
