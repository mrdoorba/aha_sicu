"""Unit tests for column drift detection."""

from app.modules.sync.column_drift import (
    EXPECTED_HEADERS_MEETING_ID,
    EXPECTED_HEADERS_VP_ID,
    EXPECTED_HEADERS_VP_TH,
    validate_headers,
)


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
    assert result.changed_columns == [
        {"position": 2, "expected": "Email", "actual": "Emails"},
    ]


def test_validate_headers_detects_reordered_columns():
    """Returns drift error when columns are in wrong order."""
    expected = ["Brand", "Email", "PIC"]
    actual = ["Email", "Brand", "PIC"]
    result = validate_headers(expected, actual, marketplace="TH", sheet="VP")
    assert result is not None
    assert result.changed_columns[:2] == [
        {"position": 1, "expected": "Brand", "actual": "Email"},
        {"position": 2, "expected": "Email", "actual": "Brand"},
    ]


def test_expected_headers_match_unified_schema():
    """Expected headers track the unified 'Brands Data' / '1st Meeting' schema."""
    # VP: brand key first, ID and TH share the same schema
    assert EXPECTED_HEADERS_VP_ID[0] == "Brand"
    assert "Category" in EXPECTED_HEADERS_VP_ID
    assert EXPECTED_HEADERS_VP_TH == EXPECTED_HEADERS_VP_ID
    # Meeting: new 1st Meeting tab layout
    assert EXPECTED_HEADERS_MEETING_ID == [
        "Logged At",
        "Brand",
        "BD",
        "Meeting Date",
        "Duration (min)",
        "Location",
        "Location Detail",
        "PIC",
        "Brand Emails",
        "Brand Phones",
        "Verified",
        "Meet Link",
        "Brand ID",
    ]
