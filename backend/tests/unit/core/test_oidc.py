"""Unit tests for OIDC token verification."""

from unittest.mock import patch

import pytest

from app.core.exceptions import AuthException
from app.core.oidc import verify_oidc_token



async def test_verify_oidc_token_valid():
    """Test successful OIDC token verification."""
    mock_claims = {
        "email": "aha-coms-sicu-dev-sched-sa@project.iam.gserviceaccount.com",
        "iss": "https://accounts.google.com",
        "aud": "https://api.example.com",
    }
    with patch("app.core.oidc.id_token.verify_oauth2_token", return_value=mock_claims):
        result = await verify_oidc_token("valid-oidc-token")
        assert result["email"] == "aha-coms-sicu-dev-sched-sa@project.iam.gserviceaccount.com"
        assert result["issuer"] == "https://accounts.google.com"



async def test_verify_oidc_token_expired():
    """Test OIDC token verification with expired token."""
    with patch(
        "app.core.oidc.id_token.verify_oauth2_token",
        side_effect=ValueError("Token expired"),
    ):
        with pytest.raises(AuthException) as exc_info:
            await verify_oidc_token("expired-oidc-token")
        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
        assert exc_info.value.detail == "OIDC token validation failed"



async def test_verify_oidc_token_invalid():
    """Test OIDC token verification with invalid token."""
    with patch(
        "app.core.oidc.id_token.verify_oauth2_token",
        side_effect=ValueError("Could not verify token signature"),
    ):
        with pytest.raises(AuthException) as exc_info:
            await verify_oidc_token("invalid-oidc-token")
        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
        assert exc_info.value.detail == "OIDC token validation failed"



async def test_verify_oidc_token_wrong_audience():
    """Test OIDC token verification with wrong audience."""
    with patch(
        "app.core.oidc.id_token.verify_oauth2_token",
        side_effect=ValueError("Token has wrong audience"),
    ):
        with pytest.raises(AuthException) as exc_info:
            await verify_oidc_token("wrong-audience-token")
        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
        assert exc_info.value.detail == "OIDC token validation failed"



async def test_verify_oidc_token_empty():
    """Test OIDC token verification rejects empty token."""
    with pytest.raises(AuthException) as exc_info:
        await verify_oidc_token("")
    assert exc_info.value.code == "AUTH_TOKEN_INVALID"
    assert exc_info.value.detail == "OIDC token is empty"



async def test_verify_oidc_token_passes_audience():
    """Test that verify_oidc_token passes cloud_run_url as audience."""
    mock_claims = {
        "email": "sa@project.iam.gserviceaccount.com",
        "iss": "https://accounts.google.com",
    }
    with (
        patch("app.core.oidc.settings") as mock_settings,
        patch("app.core.oidc.id_token.verify_oauth2_token", return_value=mock_claims) as mock_verify,
    ):
        mock_settings.cloud_run_url = "https://api.example.com"
        await verify_oidc_token("valid-token")
        mock_verify.assert_called_once()
        call_args = mock_verify.call_args
        assert call_args[0][0] == "valid-token"
        assert call_args[0][2] == "https://api.example.com"



async def test_verify_oidc_token_no_audience_when_empty_url():
    """Test that audience is None when cloud_run_url is empty."""
    mock_claims = {
        "email": "sa@project.iam.gserviceaccount.com",
        "iss": "https://accounts.google.com",
    }
    with (
        patch("app.core.oidc.settings") as mock_settings,
        patch("app.core.oidc.id_token.verify_oauth2_token", return_value=mock_claims) as mock_verify,
    ):
        mock_settings.cloud_run_url = ""
        await verify_oidc_token("valid-token")
        mock_verify.assert_called_once()
        call_args = mock_verify.call_args
        assert call_args[0][2] is None



async def test_verify_oidc_token_transport_error():
    """Test OIDC token verification handles network/transport errors gracefully."""
    with patch(
        "app.core.oidc.id_token.verify_oauth2_token",
        side_effect=ConnectionError("Connection refused"),
    ):
        with pytest.raises(AuthException) as exc_info:
            await verify_oidc_token("valid-oidc-token")
        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
        assert exc_info.value.detail == "OIDC token verification error"
