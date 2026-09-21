"""Tests for OIDC fail-closed allowlist behavior in dependencies."""

from unittest.mock import AsyncMock, patch

import pytest

from app.core.dependencies import get_current_user
from app.core.exceptions import AuthException


def _make_credentials(token: str = "test-oidc-token"):
    """Create a mock HTTPAuthorizationCredentials."""
    from unittest.mock import MagicMock

    creds = MagicMock()
    creds.credentials = token
    return creds



async def test_oidc_rejected_when_allowlist_empty():
    """OIDC auth must be rejected when ALLOWED_SCHEDULER_EMAILS is empty."""
    credentials = _make_credentials()

    with (
        patch(
            "app.core.dependencies.verify_firebase_token",
            new_callable=AsyncMock,
            side_effect=AuthException(code="AUTH_TOKEN_INVALID", detail="Firebase failed"),
        ),
        patch(
            "app.core.dependencies.verify_oidc_token",
            new_callable=AsyncMock,
            return_value={"email": "scheduler@project.iam.gserviceaccount.com", "issuer": "accounts.google.com"},
        ),
        patch("app.core.dependencies.settings") as mock_settings,
    ):
        mock_settings.allowed_scheduler_emails = ""

        with pytest.raises(AuthException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
        assert "authorization not configured" in exc_info.value.detail.lower()



async def test_oidc_rejected_when_email_not_in_allowlist():
    """OIDC auth must be rejected when service account email is not in allowlist."""
    credentials = _make_credentials()

    with (
        patch(
            "app.core.dependencies.verify_firebase_token",
            new_callable=AsyncMock,
            side_effect=AuthException(code="AUTH_TOKEN_INVALID", detail="Firebase failed"),
        ),
        patch(
            "app.core.dependencies.verify_oidc_token",
            new_callable=AsyncMock,
            return_value={"email": "attacker@evil-project.iam.gserviceaccount.com", "issuer": "accounts.google.com"},
        ),
        patch("app.core.dependencies.settings") as mock_settings,
    ):
        mock_settings.allowed_scheduler_emails = "scheduler@project.iam.gserviceaccount.com"

        with pytest.raises(AuthException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
        assert "not authorized" in exc_info.value.detail.lower()



async def test_oidc_accepted_when_email_in_allowlist():
    """OIDC auth must succeed when service account email matches allowlist."""
    credentials = _make_credentials()
    scheduler_email = "scheduler@project.iam.gserviceaccount.com"

    with (
        patch(
            "app.core.dependencies.verify_firebase_token",
            new_callable=AsyncMock,
            side_effect=AuthException(code="AUTH_TOKEN_INVALID", detail="Firebase failed"),
        ),
        patch(
            "app.core.dependencies.verify_oidc_token",
            new_callable=AsyncMock,
            return_value={"email": scheduler_email, "issuer": "accounts.google.com"},
        ),
        patch("app.core.dependencies.settings") as mock_settings,
    ):
        mock_settings.allowed_scheduler_emails = scheduler_email

        user = await get_current_user(credentials)

        assert user["email"] == scheduler_email
        assert user["role"] == "scheduler"
        assert user["id"] is None


async def test_oidc_rejected_when_allowlist_has_blank_entry():
    """A blank allowlist entry must not admit a token with no email claim.

    ALLOWED_SCHEDULER_EMAILS is assembled from a list, so a disabled scheduler
    or a stray comma can leave an empty element. verify_oidc_token reports a
    missing email claim as "", so keeping that element would match it and admit
    the caller. Two separate defects have to line up for this to bite, which is
    exactly why the guard belongs here and not only in the config that builds
    the value.
    """
    credentials = _make_credentials()

    with (
        patch(
            "app.core.dependencies.verify_firebase_token",
            new_callable=AsyncMock,
            side_effect=AuthException(code="AUTH_TOKEN_INVALID", detail="Firebase failed"),
        ),
        patch(
            "app.core.dependencies.verify_oidc_token",
            new_callable=AsyncMock,
            return_value={"email": "", "issuer": "accounts.google.com"},
        ),
        patch("app.core.dependencies.settings") as mock_settings,
    ):
        # Leading comma — what join() produces when the scheduler SA is absent.
        mock_settings.allowed_scheduler_emails = ",scheduler@project.iam.gserviceaccount.com"

        with pytest.raises(AuthException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
        assert "not authorized" in exc_info.value.detail.lower()


async def test_oidc_allowlist_tolerates_surrounding_blanks():
    """A real entry still matches when the allowlist carries blank elements."""
    credentials = _make_credentials()
    scheduler_email = "scheduler@project.iam.gserviceaccount.com"

    with (
        patch(
            "app.core.dependencies.verify_firebase_token",
            new_callable=AsyncMock,
            side_effect=AuthException(code="AUTH_TOKEN_INVALID", detail="Firebase failed"),
        ),
        patch(
            "app.core.dependencies.verify_oidc_token",
            new_callable=AsyncMock,
            return_value={"email": scheduler_email, "issuer": "accounts.google.com"},
        ),
        patch("app.core.dependencies.settings") as mock_settings,
    ):
        mock_settings.allowed_scheduler_emails = f", {scheduler_email} ,"

        user = await get_current_user(credentials)

        assert user["email"] == scheduler_email
        assert user["role"] == "scheduler"
