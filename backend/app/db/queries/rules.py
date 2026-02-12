"""Scoring rules database queries using parameterized SQL."""

from asyncpg import Connection


async def get_all_rules(conn: Connection) -> list[dict]:
    """Get all scoring rules ordered by template."""
    rows = await conn.fetch(
        """
        SELECT id, template, rules, version, updated_by, updated_at
        FROM scoring_rules
        ORDER BY template
        """
    )
    return [dict(row) for row in rows]


async def get_rules_by_template(conn: Connection, template: str) -> dict | None:
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
