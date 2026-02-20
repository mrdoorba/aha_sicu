"""Accounts API endpoints — admin only."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.core.dependencies import require_role
from app.core.exceptions import AppException
from app.modules.accounts.schemas import (
    CreateAccountRequest,
    ResetPasswordRequest,
    UpdateRoleRequest,
    UserListResponse,
)
from app.modules.accounts.service import (
    create_account,
    delete_account,
    list_accounts,
    reset_password,
    update_role,
)

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


def _guard_self_action(target_id: int, current_user: dict) -> None:
    """Reject requests where the admin targets their own account."""
    if target_id == current_user["id"]:
        raise AppException(
            code="ACCOUNT_SELF_ACTION",
            detail="Cannot modify or delete your own account",
            status_code=409,
        )


@router.get("", response_model=list[UserListResponse])
async def list_accounts_endpoint(
    current_user: dict = Depends(require_role("admin")),
) -> list[UserListResponse]:
    """List all user accounts. Requires admin role."""
    return await list_accounts()


@router.post("", response_model=UserListResponse, status_code=201)
async def create_account_endpoint(
    body: CreateAccountRequest,
    current_user: dict = Depends(require_role("admin")),
) -> UserListResponse:
    """Create a new user account. Requires admin role."""
    return await create_account(
        email=body.email, password=body.password, role=body.role
    )


@router.patch("/{user_id}/role", response_model=UserListResponse)
async def update_role_endpoint(
    user_id: int,
    body: UpdateRoleRequest,
    current_user: dict = Depends(require_role("admin")),
) -> UserListResponse:
    """Update a user's role. Requires admin role."""
    _guard_self_action(user_id, current_user)
    return await update_role(user_id, body.role)


@router.post("/{user_id}/reset-password", status_code=204, response_class=Response)
async def reset_password_endpoint(
    user_id: int,
    body: ResetPasswordRequest,
    current_user: dict = Depends(require_role("admin")),
) -> Response:
    """Reset a user's password. Requires admin role."""
    _guard_self_action(user_id, current_user)
    await reset_password(user_id, body.password)
    return Response(status_code=204)


@router.delete("/{user_id}", status_code=204, response_class=Response)
async def delete_account_endpoint(
    user_id: int,
    current_user: dict = Depends(require_role("admin")),
) -> Response:
    """Delete a user account. Requires admin role."""
    _guard_self_action(user_id, current_user)
    await delete_account(user_id)
    return Response(status_code=204)
