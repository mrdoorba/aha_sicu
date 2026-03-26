"""Tests for _extract_parsed_data backward compatibility."""

import pytest

from app.core.exceptions import CalculatorException
from app.modules.evaluations.calculator_service import ColumnarRows, _extract_parsed_data


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
        assert isinstance(result, ColumnarRows)
        assert list(result) == [{"A": 1, "B": "x"}, {"A": 2, "B": "y"}]

    def test_reads_old_data_format(self):
        upload = {
            "parsed_data": {
                "columns": ["A", "B"],
                "data": [{"A": 1, "B": "x"}, {"A": 2, "B": "y"}],
                "row_count": 2,
            }
        }
        result = _extract_parsed_data(upload, "order_export")
        assert isinstance(result, list)
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
        assert list(result) == [{"A": 1}]

    def test_empty_rows(self):
        upload = {
            "parsed_data": {
                "columns": ["A", "B"],
                "rows": [],
                "row_count": 0,
            }
        }
        result = _extract_parsed_data(upload, "order_export")
        assert isinstance(result, ColumnarRows)
        assert len(result) == 0
        assert list(result) == []

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
        assert list(result) == [{"A": 1}, {"A": 2}]


class TestColumnarRows:
    """ColumnarRows lazily converts rows and supports re-iteration."""

    def test_iteration_yields_dicts(self):
        cr = ColumnarRows(["a", "b"], [[1, 2], [3, 4]])
        assert list(cr) == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]

    def test_len(self):
        cr = ColumnarRows(["a"], [[1], [2], [3]])
        assert len(cr) == 3

    def test_bool_true(self):
        cr = ColumnarRows(["a"], [[1]])
        assert bool(cr) is True

    def test_bool_false(self):
        cr = ColumnarRows(["a"], [])
        assert bool(cr) is False

    def test_re_iteration(self):
        """Can iterate multiple times (important for calculators)."""
        cr = ColumnarRows(["x"], [[1], [2]])
        first = list(cr)
        second = list(cr)
        assert first == second == [{"x": 1}, {"x": 2}]
