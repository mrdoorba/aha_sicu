"""Rules API endpoints."""

from typing import Literal

from fastapi import APIRouter, Depends

from app.core.dependencies import require_role
from app.modules.rules.schemas import ScoringRuleResponse, ScoringRuleUpdateRequest
from app.modules.rules.service import get_all_rules, update_rules

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


@router.get("", response_model=list[ScoringRuleResponse])
async def list_rules(
    current_user: dict = Depends(require_role("leader", "admin")),
) -> list[ScoringRuleResponse]:
    """Get all scoring rules for both templates.

    Requires leader or admin role.
    """
    return await get_all_rules()


@router.put("/{template}", response_model=ScoringRuleResponse)
async def update_rules_endpoint(
    template: Literal["fashion", "non_fashion"],
    body: ScoringRuleUpdateRequest,
    current_user: dict = Depends(require_role("leader", "admin")),
) -> ScoringRuleResponse:
    """Update scoring rules for a template.

    Requires leader or admin role.
    Password re-confirmation handled by frontend (Firebase reauthentication).
    """
    return await update_rules(template, body.rules, current_user["id"])
