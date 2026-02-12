"""Rules service for querying and updating scoring rules."""

from app.core.exceptions import AppException
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


async def update_rules(template: str, rules_jsonb: dict, user_id: int) -> ScoringRuleResponse:
    """Update scoring rules for a template.

    Args:
        template: Template name (fashion or non_fashion).
        rules_jsonb: The full JSONB rules object to replace.
        user_id: ID of the user making the update.

    Returns:
        Updated ScoringRuleResponse.

    Raises:
        AppException: If template not found in database.
    """
    async with db.connection() as conn:
        row = await rules_queries.update_rules(conn, template, rules_jsonb, user_id)

    if not row:
        raise AppException(
            code="RULE_NOT_FOUND",
            detail="Scoring rules not found for template",
            status_code=404,
        )

    return ScoringRuleResponse(**row)
