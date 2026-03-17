"""Marketplace constants and currency helpers.

Each supported marketplace has:
- A two-letter code ('ID', 'TH') used as the DB discriminator
- A currency code ('IDR', 'THB')
- A display label ('Indonesia', 'Thailand')

The IDR→THB conversion rate is fixed at project initialization time (0.0019).
This is NOT a live exchange rate — it is used solely for seeding initial THB
thresholds from known IDR values. Admins adjust thresholds after migration.
"""

from typing import Final

# -- Valid marketplace codes ------------------------------------------------

VALID_MARKETPLACES: Final[frozenset[str]] = frozenset({"ID", "TH"})

# -- Marketplace → currency mapping ----------------------------------------

MARKETPLACE_CURRENCY: Final[dict[str, str]] = {
    "ID": "IDR",
    "TH": "THB",
}

# -- Marketplace → display label -------------------------------------------

MARKETPLACE_LABELS: Final[dict[str, str]] = {
    "ID": "Indonesia",
    "TH": "Thailand",
}

# -- Currency symbols (for scoring message formatting) ----------------------

CURRENCY_SYMBOLS: Final[dict[str, str]] = {
    "IDR": "Rp",
    "THB": "฿",
}

# -- IDR → THB conversion rate (fixed at project init) ---------------------
# Source: PROJECT.md — "IDR 100M ≈ THB 190,000 at 0.0019"

IDR_TO_THB_RATE: Final[float] = 0.0019


def convert_idr_to_thb(value_idr: float) -> float:
    """Convert an IDR amount to THB using the fixed project rate.

    This is for seeding initial thresholds only — not for runtime
    currency conversion of live data.

    >>> convert_idr_to_thb(100_000_000)
    190000.0
    """
    return round(value_idr * IDR_TO_THB_RATE, 2)
