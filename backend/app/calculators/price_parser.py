"""Shared price-parsing utility for marketplace-aware number conversion.

Handles Indonesian (IDR) and Thai (THB) price formats:
- IDR: '.' is thousands separator → '125.000' = 125000
- THB: ',' is thousands separator, '.' is decimal → '1,250.50' = 1250.5
"""

from __future__ import annotations

from typing import Any


def _parse_price(value: Any, marketplace: str = "ID") -> float:
    """Parse a price value with marketplace-aware thousands-separator handling.

    Args:
        value: Raw price value (None, int, float, or string).
        marketplace: ``"ID"`` for Indonesian format (strip ``'.'``),
            ``"TH"`` for Thai format (strip ``','``, keep ``'.'`` as decimal).
            Defaults to ``"ID"`` for backward compatibility.

    Returns:
        Parsed float, or ``0.0`` on any conversion failure.
    """
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip()
    if not s:
        return 0.0

    if marketplace == "TH":
        # Thai format: ',' is thousands separator, '.' is decimal
        s = s.replace(",", "")
    else:
        # Indonesian format (default): '.' is thousands separator
        s = s.replace(".", "")

    try:
        return float(s)
    except ValueError:
        return 0.0
