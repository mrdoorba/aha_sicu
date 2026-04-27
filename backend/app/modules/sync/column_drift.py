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

# Indonesia VP sheet columns A-Y (column X is empty)
EXPECTED_HEADERS_VP_ID: list[str] = [
    "Nama Brand",
    "BD",
    "Timestamp",
    "Link Shopee Mall / LazMall",
    "Kategori",
    ">= 25 Produk in stock",
    "Shopee Mall",
    "Umur brand >5 tahun",
    "No OPEX Issue",
    "Lokasi Jabodetabek / Email Domain Perusahaan",
    "Terdaftar DJKI",
    "Omset >100jt",
    "LBS",
    "Leader Approval",
    "Score\nVP",
    "Approach",
    "Nama Perusahaan/Perorangan*",
    "Nama PIC/ Jabatan*",
    "No WA*",
    "Email",
    "Alamat*",
    "Kirim surat fisik",
    "SICU",
    "",
    "Signed up",
]

# Thailand VP sheet columns A-W
EXPECTED_HEADERS_VP_TH: list[str] = [
    "Brand",
    "BD",
    "Timestamp",
    "Shopee Link",
    "Product\nCategory",
    "\u2265 25 Product Live",
    "ShopeeMall",
    "Store \u2265 5 Years",
    "No OPEX Issue",
    "GMV (THB) >200K",
    "LBS",
    "Leader Approval",
    "VP",
    "Approach",
    "Company",
    "Instagram",
    "PIC",
    "Contact Number",
    "Email",
    "Address",
    "Printed Letter",
    "SICU",
    "Signed Up",
]

# Indonesia Meeting sheet columns A-D
EXPECTED_HEADERS_MEETING_ID: list[str] = [
    "Brand",
    "Title",
    "Duration (mins)",
    "Timestamp",
]
