"""Audit trail for administrative actions (F-05-001)."""

import json
import logging

from asyncpg import Connection

logger = logging.getLogger(__name__)


async def record_audit_event(
    conn: Connection,
    *,
    action: str,
    actor_id: int,
    actor_email: str,
    target_type: str,
    target_id: str,
    details: dict | None = None,
) -> None:
    """Insert an audit log entry.

    Args:
        conn: asyncpg connection.
        action: Action identifier (e.g. "account.create", "account.delete").
        actor_id: Database ID of the user performing the action.
        actor_email: Email of the user performing the action.
        target_type: Type of entity acted upon (e.g. "user").
        target_id: ID of the target entity (as string).
        details: Optional JSONB payload (before/after state, metadata).
    """
    await conn.execute(
        """
        INSERT INTO audit_log (action, actor_id, actor_email, target_type, target_id, details)
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        action,
        actor_id,
        actor_email,
        target_type,
        target_id,
        json.dumps(details) if details is not None else None,
    )
