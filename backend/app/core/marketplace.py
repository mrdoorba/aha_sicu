"""Marketplace constants and currency helpers.

Each supported marketplace has:
- A two-letter code ('ID', 'TH') used as the DB discriminator
- A currency code ('IDR', 'THB')
"""

from typing import Final

# -- Marketplace → currency mapping ----------------------------------------

MARKETPLACE_CURRENCY: Final[dict[str, str]] = {
    "ID": "IDR",
    "TH": "THB",
}
