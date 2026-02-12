"""Rules service for querying scoring rules."""

from app.db.connection import db
from app.db.queries import rules as rules_queries
from app.modules.rules.schemas import ScoringRuleResponse


async def get_all_rules() -> list[ScoringRuleResponse]:
    """Get all scoring rules.

    Returns:
        List of ScoringRuleResponse for all templates.
    """
    async with db.connection() as conn:
        rows = await rules_queries.get_all_rules(conn)

    return [ScoringRuleResponse(**row) for row in rows]
