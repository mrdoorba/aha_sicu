"""OIDC token verification for Google Cloud service-to-service auth."""

import asyncio

from google.auth.transport import requests
from google.oauth2 import id_token

from app.config import settings
from app.core.exceptions import AuthException


async def verify_oidc_token(token: str) -> dict:
    """Verify a Google OIDC token from Cloud Scheduler.

    Args:
        token: The OIDC JWT token string.

    Returns:
        Dict with 'email' and 'issuer' from the verified token claims.

    Raises:
        AuthException: If the token is invalid, expired, or has wrong audience.
    """
    if not token:
        raise AuthException(
            code="AUTH_TOKEN_INVALID",
            detail="OIDC token is empty",
        )

    audience = settings.cloud_run_url or None

    try:
        claims = await asyncio.to_thread(
            id_token.verify_oauth2_token,
            token,
            requests.Request(),
            audience,
        )
    except ValueError as exc:
        raise AuthException(
            code="AUTH_TOKEN_INVALID",
            detail="OIDC token validation failed",
        ) from exc

    return {
        "email": claims.get("email", ""),
        "issuer": claims.get("iss", ""),
    }
