"""Unit tests for Firebase token verification and initialization."""

from unittest.mock import patch

import pytest

from app.config import Settings
from app.core.exceptions import AuthException
from app.core.security import init_firebase, verify_firebase_token


# --- init_firebase tests ---


def test_init_firebase_uses_adc_when_no_credentials():
    """ADC fallback when credentials_path is not set."""
    settings = Settings(firebase_credentials_path=None)
    with patch("app.core.security.firebase_admin._apps", {}), \
         patch("app.core.security.firebase_admin.initialize_app") as mock_init:
        init_firebase(settings)
        mock_init.assert_called_once_with()


def test_init_firebase_uses_file_path_when_provided():
    """File path credentials used when set."""
    settings = Settings(firebase_credentials_path="/path/to/creds.json")
    with patch("app.core.security.firebase_admin._apps", {}), \
         patch("app.core.security.firebase_admin.initialize_app") as mock_init, \
         patch("app.core.security.credentials.Certificate") as mock_cert:
        init_firebase(settings)
        mock_cert.assert_called_once_with("/path/to/creds.json")
        mock_init.assert_called_once_with(mock_cert.return_value)


def test_init_firebase_skips_when_already_initialized():
    """No-op when Firebase is already initialized."""
    settings = Settings(firebase_credentials_path=None)
    with patch("app.core.security.firebase_admin._apps", {"default": "app"}), \
         patch("app.core.security.firebase_admin.initialize_app") as mock_init:
        init_firebase(settings)
        mock_init.assert_not_called()


# --- verify_firebase_token tests ---


async def test_verify_token_valid():
    """Test successful token verification."""
    with patch("app.core.security.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        result = await verify_firebase_token("valid-token")
        assert result["uid"] == "test-uid"
        assert result["email"] == "test@example.com"


async def test_verify_token_invalid():
    """Test token verification with invalid token."""
    with patch("app.core.security.auth.verify_id_token") as mock_verify:
        from firebase_admin.auth import InvalidIdTokenError

        mock_verify.side_effect = InvalidIdTokenError("Invalid token")
        with pytest.raises(AuthException) as exc_info:
            await verify_firebase_token("invalid-token")
        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
        assert exc_info.value.detail == "Token validation failed"


async def test_verify_token_expired():
    """Test token verification with expired token."""
    with patch("app.core.security.auth.verify_id_token") as mock_verify:
        from firebase_admin.auth import ExpiredIdTokenError

        mock_verify.side_effect = ExpiredIdTokenError("Token expired", cause=None)
        with pytest.raises(AuthException) as exc_info:
            await verify_firebase_token("expired-token")
        assert exc_info.value.code == "AUTH_TOKEN_EXPIRED"
        assert exc_info.value.detail == "Token has expired"


async def test_verify_token_generic_exception():
    """Test token verification with generic exception."""
    with patch("app.core.security.auth.verify_id_token") as mock_verify:
        mock_verify.side_effect = Exception("Unknown error")
        with pytest.raises(AuthException) as exc_info:
            await verify_firebase_token("bad-token")
        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
