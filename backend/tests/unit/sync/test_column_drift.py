"""Unit tests for column drift detection."""

from app.modules.sync.column_drift import validate_headers


def test_validate_headers_passes_when_exact_match():
    """No error when actual headers match expected exactly."""
    expected = ["Brand", "Email", "PIC"]
    actual = ["Brand", "Email", "PIC"]
    result = validate_headers(expected, actual, marketplace="TH", sheet="VP")
    assert result is None


def test_validate_headers_detects_missing_column():
    """Returns drift error when expected column is missing."""
    expected = ["Brand", "Email", "PIC"]
    actual = ["Brand", "Email"]
    result = validate_headers(expected, actual, marketplace="TH", sheet="VP")
    assert result is not None
    assert result.marketplace == "TH"
    assert "PIC" in result.missing


def test_validate_headers_detects_unexpected_column():
    """Returns drift error when actual has extra/renamed column."""
    expected = ["Brand", "Email"]
    actual = ["Brand", "Emails"]
    result = validate_headers(expected, actual, marketplace="TH", sheet="VP")
    assert result is not None
    assert "Email" in result.missing
    assert "Emails" in result.unexpected


def test_validate_headers_detects_reordered_columns():
    """Returns drift error when columns are in wrong order."""
    expected = ["Brand", "Email", "PIC"]
    actual = ["Email", "Brand", "PIC"]
    result = validate_headers(expected, actual, marketplace="TH", sheet="VP")
    assert result is not None
