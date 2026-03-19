"""Tests for core audit module — record_audit_event."""

import json
from unittest.mock import AsyncMock

from app.core.audit import record_audit_event


async def test_inserts_row_with_correct_parameters() -> None:
    conn = AsyncMock()

    await record_audit_event(
        conn,
        action="account.create",
        actor_id=1,
        actor_email="admin@company.com",
        target_type="user",
        target_id="42",
        details={"email": "new@company.com", "role": "member"},
    )

    conn.execute.assert_called_once()
    args = conn.execute.call_args
    assert args[0][0].strip().startswith("INSERT INTO audit_log")
    assert args[0][1] == "account.create"
    assert args[0][2] == 1
    assert args[0][3] == "admin@company.com"
    assert args[0][4] == "user"
    assert args[0][5] == "42"
    parsed = json.loads(args[0][6])
    assert parsed == {"email": "new@company.com", "role": "member"}


async def test_details_none_passes_null() -> None:
    conn = AsyncMock()

    await record_audit_event(
        conn,
        action="account.password_reset",
        actor_id=1,
        actor_email="admin@company.com",
        target_type="user",
        target_id="5",
        details=None,
    )

    args = conn.execute.call_args
    assert args[0][6] is None


async def test_details_default_is_none() -> None:
    conn = AsyncMock()

    await record_audit_event(
        conn,
        action="account.delete",
        actor_id=1,
        actor_email="admin@company.com",
        target_type="user",
        target_id="3",
    )

    args = conn.execute.call_args
    assert args[0][6] is None


async def test_details_dict_serialized_to_json_string() -> None:
    conn = AsyncMock()

    await record_audit_event(
        conn,
        action="account.role_change",
        actor_id=1,
        actor_email="admin@company.com",
        target_type="user",
        target_id="7",
        details={"old_role": "member", "new_role": "leader"},
    )

    args = conn.execute.call_args
    assert isinstance(args[0][6], str)
    assert json.loads(args[0][6]) == {"old_role": "member", "new_role": "leader"}
