"""Scoring rules database queries using parameterized SQL."""

from datetime import datetime
from typing import Any, TypedDict

from asyncpg import Connection

from app.db.queries.utils import fetch_all, fetch_one


class RuleRow(TypedDict):
    id: int
    template: str
    marketplace: str
    rules: dict[str, Any]
    version: int
    updated_by: int | None
    updated_at: datetime


async def get_all_rules(conn: Connection, *, marketplace: str = "ID") -> list[RuleRow]:
    """Get all scoring rules for a marketplace, ordered by template."""
    return await fetch_all(
        conn,
        """
        SELECT id, template, marketplace, rules, version, updated_by, updated_at
        FROM scoring_rules
        WHERE marketplace = $1
        ORDER BY template
        """,
        marketplace,
    )


async def get_rules_by_template(conn: Connection, template: str) -> RuleRow | None:
    """Get scoring rules for a specific template (defaults to marketplace='ID').

    Kept for backward compatibility — prefer get_rules_by_template_and_marketplace.
    """
    return await get_rules_by_template_and_marketplace(conn, template, marketplace="ID")


async def get_rules_by_template_and_marketplace(
    conn: Connection,
    template: str,
    *,
    marketplace: str = "ID",
) -> RuleRow | None:
    """Get scoring rules for a specific template and marketplace."""
    return await fetch_one(
        conn,
        """
        SELECT id, template, marketplace, rules, version, updated_by, updated_at
        FROM scoring_rules
        WHERE template = $1 AND marketplace = $2
        """,
        template,
        marketplace,
    )


async def update_rules(
    conn: Connection,
    template: str,
    rules: dict,
    user_id: int,
    *,
    marketplace: str = "ID",
) -> RuleRow | None:
    """Update scoring rules for a template and marketplace, incrementing version."""
    return await fetch_one(
        conn,
        """
        UPDATE scoring_rules
        SET rules = $1, version = version + 1, updated_by = $2, updated_at = NOW()
        WHERE template = $3 AND marketplace = $4
        RETURNING id, template, marketplace, rules, version, updated_by, updated_at
        """,
        rules,
        user_id,
        template,
        marketplace,
    )
