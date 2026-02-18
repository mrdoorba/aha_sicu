"""Shared utility helpers."""

import json
from typing import Any


def ensure_dict(value: Any) -> dict:
    """Ensure a value is a dict, parsing JSON string if needed.

    Handles legacy double-encoded JSONB data where asyncpg returns a
    string instead of a dict due to prior json.dumps() before insert.
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
    return {}
