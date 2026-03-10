"""User database queries using parameterized SQL."""

from datetime import datetime
from typing import TypedDict

from asyncpg import Connection


class UserRow(TypedDict):
    id: int
    firebase_uid: str
    email: str
    role: str
    language: str | None
    created_at: datetime
    last_login: datetime | None


async def get_user_by_firebase_uid(conn: Connection, firebase_uid: str) -> UserRow | None:
    """Get user by Firebase UID."""
    row = await conn.fetchrow(
        "SELECT id, firebase_uid, email, role, language, created_at, last_login FROM users WHERE firebase_uid = $1",
        firebase_uid,
    )
    return dict(row) if row else None


async def create_user(conn: Connection, firebase_uid: str, email: str) -> UserRow:
    """Create new user with default role."""
    row = await conn.fetchrow(
        """
        INSERT INTO users (firebase_uid, email, role, language, last_login)
        VALUES ($1, $2, 'member', 'id', NOW())
        RETURNING id, firebase_uid, email, role, language, created_at, last_login
        """,
        firebase_uid,
        email,
    )
    return dict(row)


async def update_language(conn: Connection, user_id: int, language: str) -> UserRow | None:
    """Update user's language preference."""
    row = await conn.fetchrow(
        "UPDATE users SET language = $1 WHERE id = $2 RETURNING id, firebase_uid, email, role, language, created_at, last_login",
        language,
        user_id,
    )
    return dict(row) if row else None


async def update_last_login(conn: Connection, user_id: int) -> None:
    """Update user's last login timestamp."""
    await conn.execute("UPDATE users SET last_login = NOW() WHERE id = $1", user_id)
