"""Account management service layer."""

import asyncio
import logging

from firebase_admin import auth

from app.core.exceptions import AppException
from app.db.connection import db
from app.modules.accounts import queries as account_queries
from app.modules.accounts.schemas import UserListResponse

logger = logging.getLogger(__name__)


async def list_accounts() -> list[UserListResponse]:
    """List all user accounts."""
    async with db.connection() as conn:
        rows = await account_queries.get_all_users(conn)
    return [UserListResponse(**row) for row in rows]


async def create_account(email: str, password: str, role: str) -> UserListResponse:
    """Create a new account in Firebase and database.

    Creates Firebase account first, then DB row. If DB fails, rolls back Firebase.
    """
    try:
        firebase_user = await asyncio.to_thread(
            auth.create_user, email=email, password=password
        )
    except auth.EmailAlreadyExistsError:
        raise AppException(
            code="ACCOUNT_EMAIL_EXISTS",
            detail="An account with this email already exists",
            status_code=409,
        )
    except Exception as e:
        raise AppException(
            code="ACCOUNT_CREATE_FAILED",
            detail=f"Failed to create Firebase account: {e}",
            status_code=400,
        )

    try:
        async with db.connection() as conn:
            row = await account_queries.create_user(
                conn, firebase_user.uid, email, role
            )
    except Exception:
        # Rollback: delete Firebase account if DB insert fails
        try:
            await asyncio.to_thread(auth.delete_user, firebase_user.uid)
        except Exception:
            logger.error(
                "Failed to rollback Firebase account %s after DB failure",
                firebase_user.uid,
            )
        raise AppException(
            code="ACCOUNT_CREATE_FAILED",
            detail="Failed to create account in database",
            status_code=500,
        )

    return UserListResponse(**row)


async def update_role(user_id: int, role: str) -> UserListResponse:
    """Update a user's role."""
    async with db.connection() as conn:
        row = await account_queries.update_user_role(conn, user_id, role)

    if not row:
        raise AppException(
            code="ACCOUNT_NOT_FOUND",
            detail="User not found",
            status_code=404,
        )

    return UserListResponse(**row)


async def reset_password(user_id: int, new_password: str) -> None:
    """Reset a user's password via Firebase Admin SDK."""
    async with db.connection() as conn:
        user = await account_queries.get_user_by_id(conn, user_id)

    if not user:
        raise AppException(
            code="ACCOUNT_NOT_FOUND",
            detail="User not found",
            status_code=404,
        )

    try:
        await asyncio.to_thread(
            auth.update_user, user["firebase_uid"], password=new_password
        )
    except Exception as e:
        raise AppException(
            code="ACCOUNT_PASSWORD_RESET_FAILED",
            detail=f"Failed to reset password: {e}",
            status_code=400,
        )


async def delete_account(user_id: int) -> None:
    """Delete a user from database and Firebase atomically.

    Both deletions happen inside a DB transaction. If Firebase deletion
    fails, the DB deletion is rolled back — no orphaned state.
    """
    async with db.connection() as conn:
        user = await account_queries.get_user_by_id(conn, user_id)
        if not user:
            raise AppException(
                code="ACCOUNT_NOT_FOUND",
                detail="User not found",
                status_code=404,
            )

        async with conn.transaction():
            deleted = await account_queries.delete_user(conn, user_id)
            if not deleted:
                raise AppException(
                    code="ACCOUNT_NOT_FOUND",
                    detail="User not found",
                    status_code=404,
                )

            try:
                await asyncio.to_thread(auth.delete_user, user["firebase_uid"])
            except auth.UserNotFoundError:
                logger.info(
                    "Firebase user %s already absent — proceeding with DB deletion",
                    user["firebase_uid"],
                )
            except Exception as e:
                raise AppException(
                    code="FIREBASE_DELETE_FAILED",
                    detail=f"Failed to delete Firebase account: {e}",
                    status_code=502,
                )
