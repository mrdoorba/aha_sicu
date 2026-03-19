"""Accounts API endpoints — admin only."""

import logging

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.core.audit import record_audit_event
from app.core.dependencies import require_role
from app.core.exceptions import AppException
from app.db.connection import db
from app.modules.accounts import queries as account_queries
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


async def _audit(
    action: str,
    actor: dict,
    target_type: str,
    target_id: str,
    details: dict | None = None,
) -> None:
    """Record an audit event, logging errors without failing the request."""
    try:
        async with db.connection() as conn:
            await record_audit_event(
                conn,
                action=action,
                actor_id=actor["id"],
                actor_email=actor["email"],
                target_type=target_type,
                target_id=target_id,
                details=details,
            )
    except Exception:
        logger.error(
            "Audit failed for action=%s target=%s/%s actor=%s",
            action,
            target_type,
            target_id,
            actor["email"],
        )


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
    result = await create_account(
        email=body.email, password=body.password, role=body.role
    )
    await _audit(
        "account.create",
        current_user,
        "user",
        str(result.id),
        details={"email": body.email, "role": body.role},
    )
    return result


@router.patch("/{user_id}/role", response_model=UserListResponse)
async def update_role_endpoint(
    user_id: int,
    body: UpdateRoleRequest,
    current_user: dict = Depends(require_role("admin")),
) -> UserListResponse:
    """Update a user's role. Requires admin role."""
    _guard_self_action(user_id, current_user)

    # Capture old role for audit details
    async with db.connection() as conn:
        old_user = await account_queries.get_user_by_id(conn, user_id)
    old_role = old_user["role"] if old_user else "unknown"

    result = await update_role(user_id, body.role)
    await _audit(
        "account.role_change",
        current_user,
        "user",
        str(user_id),
        details={"old_role": old_role, "new_role": body.role},
    )
    return result


@router.post("/{user_id}/reset-password", status_code=204, response_class=Response)
async def reset_password_endpoint(
    user_id: int,
    body: ResetPasswordRequest,
    current_user: dict = Depends(require_role("admin")),
) -> Response:
    """Reset a user's password. Requires admin role."""
    _guard_self_action(user_id, current_user)
    await reset_password(user_id, body.password)
    await _audit(
        "account.password_reset",
        current_user,
        "user",
        str(user_id),
    )
    return Response(status_code=204)


@router.delete("/{user_id}", status_code=204, response_class=Response)
async def delete_account_endpoint(
    user_id: int,
    current_user: dict = Depends(require_role("admin")),
) -> Response:
    """Delete a user account. Requires admin role."""
    _guard_self_action(user_id, current_user)

    # Capture state before deletion for audit details
    async with db.connection() as conn:
        user_before = await account_queries.get_user_by_id(conn, user_id)
    deleted_email = user_before["email"] if user_before else "unknown"
    deleted_role = user_before["role"] if user_before else "unknown"

    await delete_account(user_id)
    await _audit(
        "account.delete",
        current_user,
        "user",
        str(user_id),
        details={"email": deleted_email, "role": deleted_role},
    )
    return Response(status_code=204)
