"""Column drift detection for Google Sheets sync."""

from dataclasses import dataclass, field


@dataclass
class ColumnDriftError:
    """Structured error when sheet headers don't match expected."""

    marketplace: str
    sheet: str
    status: str = "column_drift"
    expected: list[str] = field(default_factory=list)
    actual: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    unexpected: list[str] = field(default_factory=list)


def validate_headers(
    expected: list[str],
    actual: list[str],
    marketplace: str,
    sheet: str,
) -> ColumnDriftError | None:
    """Compare actual sheet headers against expected.

    Returns None if headers match exactly (including order).
    Returns ColumnDriftError with details if any mismatch is found.
    """
    if expected == actual:
        return None

    expected_set = set(expected)
    actual_set = set(actual)

    return ColumnDriftError(
        marketplace=marketplace,
        sheet=sheet,
        expected=expected,
        actual=actual,
        missing=sorted(expected_set - actual_set),
        unexpected=sorted(actual_set - expected_set),
    )


# =============================================================================
# Expected headers per marketplace (defined in code, not config)
# =============================================================================

# Indonesia VP sheet columns A-Y
# TODO: Fill in the complete list during Task 13 by reading the actual sheet
EXPECTED_HEADERS_VP_ID: list[str] = []

# Thailand VP sheet columns A-W
# TODO: Fill in the complete list during Task 13 by reading the actual sheet
EXPECTED_HEADERS_VP_TH: list[str] = []

# Indonesia Meeting sheet columns A-D
EXPECTED_HEADERS_MEETING_ID: list[str] = []
