"""Dependency injection: auth, db connections."""

import logging

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.core.exceptions import AppException, AuthException
from app.core.oidc import verify_oidc_token
from app.core.security import verify_firebase_token
from app.db.connection import db
from app.db.queries import users as user_queries

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Validate token and return current user context.

    Supports two auth paths:
    1. Firebase tokens (human users via Firebase Auth SDK)
    2. Google OIDC tokens (service accounts like Cloud Scheduler)

    Firebase is tried first. On failure, OIDC is attempted.
    """
    # Check for Authorization header
    if not credentials:
        raise AuthException(code="AUTH_TOKEN_MISSING", detail="Authorization header required")

    token = credentials.credentials

    # Try Firebase token first (existing path — handles user requests)
    try:
        token_data = await verify_firebase_token(token)
    except AuthException:
        # Firebase failed — try OIDC (handles scheduler requests)
        logger.debug("Firebase auth failed, attempting OIDC fallback")
        try:
            oidc_claims = await verify_oidc_token(token)
        except AuthException as oidc_exc:
            # Both failed — reject
            raise AuthException(
                code="AUTH_TOKEN_INVALID",
                detail="Token validation failed",
            ) from oidc_exc

        # Validate service account is in allowlist (when configured)
        if settings.allowed_scheduler_emails:
            allowed = [e.strip() for e in settings.allowed_scheduler_emails.split(",")]
            if oidc_claims["email"] not in allowed:
                logger.warning("OIDC auth rejected: %s not in allowlist", oidc_claims["email"])
                raise AuthException(
                    code="AUTH_TOKEN_INVALID",
                    detail="Service account not authorized",
                )

        logger.info("OIDC service account authenticated: %s", oidc_claims["email"])

        # Return synthetic scheduler user (no DB write needed)
        return {
            "id": None,
            "email": oidc_claims["email"],
            "role": "scheduler",
            "firebase_uid": None,
        }

    # Firebase succeeded — get or create user in database
    async with db.connection() as conn:
        user = await user_queries.get_user_by_firebase_uid(conn, token_data["uid"])

        if not user:
            # First login - create user
            user = await user_queries.create_user(conn, token_data["uid"], token_data["email"])
        else:
            # Update last login and re-fetch to get fresh data
            await user_queries.update_last_login(conn, user["id"])
            user = await user_queries.get_user_by_firebase_uid(conn, token_data["uid"])

    return user


async def get_db_connection():
    """Yield a database connection from the pool.

    Usage in routers:
        conn: Connection = Depends(get_db_connection)
    """
    async with db.connection() as conn:
        yield conn


def require_role(*allowed_roles: str):
    """Dependency factory that enforces role-based access control.

    Usage in routers:
        @router.get("", dependencies=[Depends(require_role("leader", "admin"))])
    Or:
        current_user: dict = Depends(require_role("leader", "admin"))
    """

    async def check(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise AppException(
                code="RULE_ACCESS_DENIED",
                detail="Only leaders and admins can access scoring rules",
                status_code=403,
            )
        return current_user

    return check
