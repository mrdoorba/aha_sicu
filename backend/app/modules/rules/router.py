"""Rules API endpoints."""

from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import require_role
from app.modules.rules.schemas import ScoringRuleResponse, ScoringRuleUpdateRequest
from app.modules.rules.service import get_all_rules, update_rules

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


@router.get("", response_model=list[ScoringRuleResponse])
async def list_rules(
    marketplace: str = Query("ID", description="Marketplace code (ID or TH)"),
    current_user: dict = Depends(require_role("leader", "admin", "scheduler")),
) -> list[ScoringRuleResponse]:
    """Get all scoring rules for a marketplace.

    Requires leader or admin role. Also open to ``scheduler`` — the role an
    allowlisted service account authenticates as — so a downstream consumer
    scoring against our thresholds reads them here rather than pinning its own
    copy. Read-only; updating rules stays leader/admin.
    """
    return await get_all_rules(marketplace=marketplace)


@router.put("/{template}", response_model=ScoringRuleResponse)
async def update_rules_endpoint(
    template: Literal["fashion", "non_fashion", "default"],
    body: ScoringRuleUpdateRequest,
    marketplace: str = Query("ID", description="Marketplace code (ID or TH)"),
    current_user: dict = Depends(require_role("leader", "admin")),
) -> ScoringRuleResponse:
    """Update scoring rules for a template and marketplace.

    Requires leader or admin role.
    Password re-confirmation handled by frontend (Firebase reauthentication).
    """
    return await update_rules(template, body.rules, current_user["id"], marketplace=marketplace)
