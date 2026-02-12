"""Rules API endpoints."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.exceptions import AppException
from app.modules.rules.schemas import ScoringRuleResponse
from app.modules.rules.service import get_all_rules

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


def require_role(*allowed_roles: str):
    """Dependency that enforces role-based access control."""

    async def check(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise AppException(
                code="RULE_ACCESS_DENIED",
                detail="Only leaders and admins can access scoring rules",
                status_code=403,
            )
        return current_user

    return check


@router.get("", response_model=list[ScoringRuleResponse])
async def list_rules(
    current_user: dict = Depends(require_role("leader", "admin")),
) -> list[ScoringRuleResponse]:
    """Get all scoring rules for both templates.

    Requires leader or admin role.
    """
    return await get_all_rules()
