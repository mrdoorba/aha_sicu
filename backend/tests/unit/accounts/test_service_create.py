"""Unit tests for create_account — the shared-Firebase-project adopt path."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from asyncpg import UniqueViolationError
from firebase_admin import auth

from app.core.exceptions import AppException
from app.modules.accounts.service import create_account

ROW = {
    "id": 7,
    "email": "iffat.kartiwa@ahacommerce.net",
    "role": "member",
    "created_at": datetime(2026, 7, 28, tzinfo=timezone.utc),
    "last_login": None,
}


def _mock_db(mock_conn):
    mock_db = MagicMock()
    mock_db.connection = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_conn),
            __aexit__=AsyncMock(return_value=False),
        )
    )
    return mock_db


async def test_adopts_existing_firebase_identity():
    """Email taken in the shared project → reuse the UID, set the password, insert the row."""
    existing = MagicMock(uid="3ctqmF7jF5gHABYvT8FUXEhnRN42")
    mock_conn = AsyncMock()

    with (
        patch("app.modules.accounts.service.db", _mock_db(mock_conn)),
        patch("app.modules.accounts.service.auth") as mock_auth,
        patch(
            "app.modules.accounts.service.account_queries.create_user",
            AsyncMock(return_value=ROW),
        ) as mock_create_user,
    ):
        mock_auth.EmailAlreadyExistsError = auth.EmailAlreadyExistsError
        mock_auth.create_user.side_effect = auth.EmailAlreadyExistsError(
            "taken", None, None
        )
        mock_auth.get_user_by_email.return_value = existing

        result = await create_account(ROW["email"], "s3cret1", "member")

    assert result.id == 7
    mock_auth.update_user.assert_called_once_with(existing.uid, password="s3cret1")
    assert mock_create_user.await_args.args[1] == existing.uid


async def test_adopted_identity_is_never_deleted_on_db_failure():
    """Rollback must not delete an identity we did not create."""
    mock_conn = AsyncMock()

    with (
        patch("app.modules.accounts.service.db", _mock_db(mock_conn)),
        patch("app.modules.accounts.service.auth") as mock_auth,
        patch(
            "app.modules.accounts.service.account_queries.create_user",
            AsyncMock(side_effect=OSError("db down")),
        ),
    ):
        mock_auth.EmailAlreadyExistsError = auth.EmailAlreadyExistsError
        mock_auth.create_user.side_effect = auth.EmailAlreadyExistsError(
            "taken", None, None
        )
        mock_auth.get_user_by_email.return_value = MagicMock(uid="uid-existing")

        with pytest.raises(AppException) as exc:
            await create_account(ROW["email"], "s3cret1", "member")

    assert exc.value.status_code == 500
    mock_auth.delete_user.assert_not_called()


async def test_duplicate_db_row_is_409():
    """Already provisioned in SICU → 409, and the Firebase identity survives."""
    mock_conn = AsyncMock()

    with (
        patch("app.modules.accounts.service.db", _mock_db(mock_conn)),
        patch("app.modules.accounts.service.auth") as mock_auth,
        patch(
            "app.modules.accounts.service.account_queries.create_user",
            AsyncMock(side_effect=UniqueViolationError("dup")),
        ),
    ):
        mock_auth.EmailAlreadyExistsError = auth.EmailAlreadyExistsError
        mock_auth.create_user.return_value = MagicMock(uid="uid-new")

        with pytest.raises(AppException) as exc:
            await create_account(ROW["email"], "s3cret1", "member")

    assert (exc.value.status_code, exc.value.code) == (409, "ACCOUNT_EMAIL_EXISTS")
    mock_auth.delete_user.assert_not_called()
