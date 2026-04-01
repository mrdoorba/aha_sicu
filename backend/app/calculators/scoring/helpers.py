"""Scoring helper utilities — formatting, parsing, rules access."""

from __future__ import annotations

import math
import re
from typing import Any


MONTH_ABBRS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _generate_month_labels(start_month: str | None) -> list[str]:
    """Given '2026-01', returns ['Jan 2026', 'Dec 2025', ...] for 6 months.

    If None or invalid, returns ['Bulan Ini', 'Bulan -1', ..., 'Bulan -5'].
    """
    fallback = ["Bulan Ini", "Bulan -1", "Bulan -2", "Bulan -3", "Bulan -4", "Bulan -5"]
    if not start_month:
        return fallback
    if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", start_month):
        return fallback
    year_str, month_str = start_month.split("-")
    year = int(year_str)
    month = int(month_str)
    labels: list[str] = []
    for i in range(6):
        month_index = ((month - 1 - i) % 12 + 12) % 12
        year_offset = (month - 1 - i) // 12
        labels.append(f"{MONTH_ABBRS[month_index]} {year + year_offset}")
    return labels


def _safe_num(value: Any, default: float = 0.0) -> float:
    """Coerce a value to float, treating None/empty as default."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if value in ("", "-"):
            return default
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _safe_str(value: Any, default: str = "") -> str:
    """Coerce value to string."""
    if value is None:
        return default
    return str(value).strip()


def _get_nested(data: dict, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dict keys."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def _fmt_pct_1dp(value: float) -> str:
    """Format fraction as percentage with 1 decimal: 0.235 -> '23.5%'."""
    return f"{value * 100:.1f}%"


def _fmt_pct_0dp(value: float) -> str:
    """Format fraction as percentage with no decimal: 0.95 -> '95%'."""
    return f"{value * 100:.0f}%"


def _fmt_num_1dp(value: float) -> str:
    """Format as number with 1 decimal: 0.005 -> '0.5%' (percentage number)."""
    return f"{value:.1f}%"


def _fmt_num_2dp(value: float) -> str:
    """Format as number with 2 decimals."""
    return f"{value:.2f}"


def _fmt_idr(value: float) -> str:
    """Format IDR value with comma thousands separator."""
    rounded = round(value)
    if rounded < 0:
        return f"-{abs(rounded):,}"
    return f"{rounded:,}"


def _fmt_currency(value: float, marketplace: str = "ID") -> str:
    """Format a currency value with comma thousands separator.

    Returns the formatted number only (no currency prefix).
    The currency code is injected via message template placeholders.
    """
    return _fmt_idr(value)


def _rounddown(value: float, decimals: int) -> float:
    """Round DOWN to specified decimal places."""
    factor = 10 ** decimals
    return math.floor(value * factor) / factor


def _extract_pct(pattern: str, text: str) -> float:
    """Extract a percentage value from text using regex, return as fraction."""
    match = re.search(pattern, text)
    if match:
        try:
            return float(match.group(1)) / 100
        except (ValueError, IndexError):
            return 0.0
    return 0.0


# ---------------------------------------------------------------------------
# Rules helpers — extract configurable thresholds with fallback defaults
#
# NOTE: The rules JSONB contains a `comparison` field per rule entry (e.g.,
# "lte", "gte", "gt") as descriptive metadata. These are NOT dynamically
# applied — each scoring function hardcodes its comparison operator because
# the comparison semantics are structural to the scoring logic, not a
# business-configurable parameter. Only thresholds and points are dynamic.
# ---------------------------------------------------------------------------

def _get_rule_category(rules: dict | None, category: str) -> dict:
    """Get a category dict from rules, or empty dict if missing."""
    if rules is None:
        return {}
    return rules.get(category, {})


def _get_rule_value(category_rules: dict, key: str, field: str, default: Any) -> Any:
    """Get a specific value from category rules, with default fallback."""
    return category_rules.get(key, {}).get(field, default)


class _SafeDict(dict):
    """Dict subclass that returns the placeholder markup for missing keys."""

    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


def _format_message_template(template: str, **kwargs: Any) -> str:
    """Format a message template safely — missing placeholders stay as-is.

    Resilient to both missing keys AND malformed format strings (unmatched
    braces from user-edited templates).
    """
    try:
        return template.format_map(_SafeDict(**kwargs))
    except (ValueError, KeyError):
        return template
