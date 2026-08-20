"""Column drift detection for Google Sheets sync."""

from dataclasses import dataclass, field
from itertools import zip_longest


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
    changed_columns: list[dict[str, str | int | None]] = field(default_factory=list)


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
    changed_columns = [
        {
            "position": index,
            "expected": expected_header,
            "actual": actual_header,
        }
        for index, (expected_header, actual_header) in enumerate(
            zip_longest(expected, actual),
            start=1,
        )
        if expected_header != actual_header
    ]

    return ColumnDriftError(
        marketplace=marketplace,
        sheet=sheet,
        expected=expected,
        actual=actual,
        missing=sorted(expected_set - actual_set),
        unexpected=sorted(actual_set - expected_set),
        changed_columns=changed_columns,
    )


# =============================================================================
# Expected headers per marketplace (defined in code, not config)
# =============================================================================

# VP "Brands Data" tab, columns A-Z. ID and TH share the same schema.
EXPECTED_HEADERS_VP_ID: list[str] = [
    "Brand",
    "Company",
    "Category",
    "Store Link",
    "VP",
    "LBS",
    "Can Approach",
    "Package",
    "GMV Tier",
    "SICU",
    "SICU Passed",
    "Stage",
    "Lock Owner",
    "Locked At",
    "Lock Expires",
    "Leader Approval",
    "Registered At",
    "Registered By",
    "Phones",
    "Emails",
    "PIC",
    "Address",
    "Notes",
    "Record Owner",
    "Updated At",
    "Brand ID",
]
EXPECTED_HEADERS_VP_TH: list[str] = EXPECTED_HEADERS_VP_ID

# Meeting "1st Meeting" tab, columns A-N. ID and TH share the same schema.
EXPECTED_HEADERS_MEETING_ID: list[str] = [
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
    "Meeting ID",
]
EXPECTED_HEADERS_MEETING_TH: list[str] = EXPECTED_HEADERS_MEETING_ID
