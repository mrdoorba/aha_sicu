"""Scoring rules database queries using parameterized SQL."""

from datetime import datetime
from typing import Any, TypedDict

from asyncpg import Connection


class RuleRow(TypedDict):
    id: int
    template: str
    rules: dict[str, Any]
    version: int
    updated_by: int | None
    updated_at: datetime


async def get_all_rules(conn: Connection) -> list[RuleRow]:
    """Get all scoring rules ordered by template."""
    rows = await conn.fetch(
        """
        SELECT id, template, rules, version, updated_by, updated_at
        FROM scoring_rules
        ORDER BY template
        """
    )
    return [dict(row) for row in rows]


async def get_rules_by_template(conn: Connection, template: str) -> RuleRow | None:
    """Get scoring rules for a specific template."""
    row = await conn.fetchrow(
        """
        SELECT id, template, rules, version, updated_by, updated_at
        FROM scoring_rules
        WHERE template = $1
        """,
        template,
    )
    return dict(row) if row else None


async def update_rules(conn: Connection, template: str, rules: dict, user_id: int) -> RuleRow | None:
    """Update scoring rules for a template, incrementing version."""
    row = await conn.fetchrow(
        """
        UPDATE scoring_rules
        SET rules = $1, version = version + 1, updated_by = $2, updated_at = NOW()
        WHERE template = $3
        RETURNING id, template, rules, version, updated_by, updated_at
        """,
        rules,
        user_id,
        template,
    )
    return dict(row) if row else None
