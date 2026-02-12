"""Rules API endpoints."""

from fastapi import APIRouter, Depends

from app.core.dependencies import require_role
from app.modules.rules.schemas import ScoringRuleResponse
from app.modules.rules.service import get_all_rules

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


@router.get("", response_model=list[ScoringRuleResponse])
async def list_rules(
    current_user: dict = Depends(require_role("leader", "admin")),
) -> list[ScoringRuleResponse]:
    """Get all scoring rules for both templates.

    Requires leader or admin role.
    """
    return await get_all_rules()
