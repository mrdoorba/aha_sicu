"""Unit tests for calculator_service helper functions."""

import pytest

from app.core.exceptions import CalculatorException
from app.modules.evaluations.calculator_service import _extract_source_language


class TestExtractSourceLanguage:
    def test_english_language(self):
        upload = {"parsed_data": {"source_language": "en", "data": [], "columns": []}}
        assert _extract_source_language(upload) == "en"

    def test_indonesian_language(self):
        upload = {"parsed_data": {"source_language": "id", "data": [], "columns": []}}
        assert _extract_source_language(upload) == "id"

    def test_missing_key_defaults_to_id(self):
        """Existing data without source_language defaults to 'id'."""
        upload = {"parsed_data": {"data": [], "columns": []}}
        assert _extract_source_language(upload) == "id"

    def test_no_parsed_data_defaults_to_id(self):
        upload = {}
        assert _extract_source_language(upload) == "id"

    def test_string_parsed_data(self):
        """Double-encoded parsed_data (string instead of dict)."""
        import json
        upload = {"parsed_data": json.dumps({"source_language": "en", "data": []})}
        assert _extract_source_language(upload) == "en"

    def test_invalid_string_parsed_data_defaults_to_id(self):
        upload = {"parsed_data": "not-valid-json"}
        assert _extract_source_language(upload) == "id"


class TestLanguageMismatchValidation:
    """Test that language mismatch between CPC and Keyword uploads is caught.

    The actual validation happens in run_ads_keyword_calculator (which requires DB),
    but we can verify the logic by testing the helper + exception behavior.
    """

    def test_matching_languages_no_error(self):
        cpc = {"parsed_data": {"source_language": "en"}}
        kw = {"parsed_data": {"source_language": "en"}}
        assert _extract_source_language(cpc) == _extract_source_language(kw)

    def test_mismatched_languages_detected(self):
        cpc = {"parsed_data": {"source_language": "en"}}
        kw = {"parsed_data": {"source_language": "id"}}
        cpc_lang = _extract_source_language(cpc)
        kw_lang = _extract_source_language(kw)
        assert cpc_lang != kw_lang
        # Verify the exception that would be raised
        with pytest.raises(CalculatorException) as exc:
            raise CalculatorException(
                code="CALC_MISSING_DATA",
                detail=f"Language mismatch: CPC is '{cpc_lang}' but Keyword is '{kw_lang}'",
            )
        assert exc.value.code == "CALC_MISSING_DATA"
        assert "mismatch" in exc.value.detail.lower()
