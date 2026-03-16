"""Security: Firebase Auth validation."""

import asyncio
import os

import firebase_admin
from firebase_admin import auth, credentials

from app.config import Settings
from app.core.exceptions import AuthException


def init_firebase(settings: Settings) -> None:
    """Initialize Firebase Admin SDK.

    Priority: emulator (Docker local dev) → file path → ADC (Cloud Run).
    """
    if firebase_admin._apps:
        return  # Already initialized

    if os.environ.get("FIREBASE_AUTH_EMULATOR_HOST"):
        # Emulator mode — no real credentials needed
        firebase_admin.initialize_app(options={"projectId": "fbi-dev-484410"})
    elif settings.firebase_credentials_path:
        cred = credentials.Certificate(settings.firebase_credentials_path)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()


async def verify_firebase_token(token: str) -> dict:
    """Verify Firebase ID token and return decoded claims."""
    try:
        # Run synchronous Firebase SDK call in thread pool to avoid blocking event loop
        decoded = await asyncio.to_thread(auth.verify_id_token, token)
        return {
            "uid": decoded["uid"],
            "email": decoded.get("email"),
        }
    except auth.ExpiredIdTokenError:
        raise AuthException(code="AUTH_TOKEN_EXPIRED", detail="Token has expired")
    except auth.InvalidIdTokenError:
        raise AuthException(code="AUTH_TOKEN_INVALID", detail="Token validation failed")
    except Exception:
        raise AuthException(code="AUTH_TOKEN_INVALID", detail="Token validation failed")
