"""Unit tests for Firebase token verification."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import AuthException
from app.core.security import verify_firebase_token


@pytest.mark.asyncio
async def test_verify_token_valid():
    """Test successful token verification."""
    with patch("app.core.security.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        result = await verify_firebase_token("valid-token")
        assert result["uid"] == "test-uid"
        assert result["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_verify_token_invalid():
    """Test token verification with invalid token."""
    with patch("app.core.security.auth.verify_id_token") as mock_verify:
        from firebase_admin.auth import InvalidIdTokenError

        mock_verify.side_effect = InvalidIdTokenError("Invalid token")
        with pytest.raises(AuthException) as exc_info:
            await verify_firebase_token("invalid-token")
        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
        assert exc_info.value.detail == "Token validation failed"


@pytest.mark.asyncio
async def test_verify_token_expired():
    """Test token verification with expired token."""
    with patch("app.core.security.auth.verify_id_token") as mock_verify:
        from firebase_admin.auth import ExpiredIdTokenError

        mock_verify.side_effect = ExpiredIdTokenError("Token expired", cause=None)
        with pytest.raises(AuthException) as exc_info:
            await verify_firebase_token("expired-token")
        assert exc_info.value.code == "AUTH_TOKEN_EXPIRED"
        assert exc_info.value.detail == "Token has expired"


@pytest.mark.asyncio
async def test_verify_token_generic_exception():
    """Test token verification with generic exception."""
    with patch("app.core.security.auth.verify_id_token") as mock_verify:
        mock_verify.side_effect = Exception("Unknown error")
        with pytest.raises(AuthException) as exc_info:
            await verify_firebase_token("bad-token")
        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
