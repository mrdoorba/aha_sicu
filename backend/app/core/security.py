"""Security: Firebase Auth validation."""

import asyncio
import json

import firebase_admin
from firebase_admin import auth, credentials

from app.config import Settings
from app.core.exceptions import AuthException


def init_firebase(settings: Settings) -> None:
    """Initialize Firebase Admin SDK."""
    if firebase_admin._apps:
        return  # Already initialized

    if settings.firebase_credentials_json:
        # Production: credentials from Secret Manager
        cred_dict = json.loads(settings.firebase_credentials_json)
        cred = credentials.Certificate(cred_dict)
    elif settings.firebase_credentials_path:
        # Development: credentials from file
        cred = credentials.Certificate(settings.firebase_credentials_path)
    else:
        raise ValueError("Firebase credentials not configured")

    firebase_admin.initialize_app(cred)


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
