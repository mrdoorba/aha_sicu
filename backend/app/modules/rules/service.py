"""Rules service for querying and updating scoring rules."""

from app.core.exceptions import AppException
from app.db.connection import db
from app.db.queries import rules as rules_queries
from app.modules.rules.schemas import ScoringRuleResponse


async def get_all_rules(*, marketplace: str = "ID") -> list[ScoringRuleResponse]:
    """Get all scoring rules for a marketplace.

    Returns:
        List of ScoringRuleResponse for all templates in the given marketplace.
    """
    async with db.connection() as conn:
        rows = await rules_queries.get_all_rules(conn, marketplace=marketplace)

    return [ScoringRuleResponse(**row) for row in rows]


async def update_rules(template: str, rules_jsonb: dict, user_id: int, *, marketplace: str = "ID") -> ScoringRuleResponse:
    """Update scoring rules for a template and marketplace.

    Args:
        template: Template name (fashion or non_fashion).
        rules_jsonb: The full JSONB rules object to replace.
        user_id: ID of the user making the update.
        marketplace: Marketplace code ('ID' or 'TH').

    Returns:
        Updated ScoringRuleResponse.

    Raises:
        AppException: If template not found in database.
    """
    async with db.connection() as conn:
        row = await rules_queries.update_rules(conn, template, rules_jsonb, user_id, marketplace=marketplace)

    if not row:
        raise AppException(
            code="RULE_NOT_FOUND",
            detail="Scoring rules not found for template",
            status_code=404,
        )

    return ScoringRuleResponse(**row)
