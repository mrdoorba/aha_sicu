"""Dependency injection: auth, db connections."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AuthException
from app.core.security import verify_firebase_token
from app.db.connection import db
from app.db.queries import users as user_queries

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Validate token and return current user context."""
    # Check for Authorization header
    if not credentials:
        raise AuthException(code="AUTH_TOKEN_MISSING", detail="Authorization header required")

    # Verify Firebase token
    token_data = await verify_firebase_token(credentials.credentials)

    # Get or create user in database
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
