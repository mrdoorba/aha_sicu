"""Account management database queries."""

from datetime import datetime
from typing import TypedDict

from asyncpg import Connection

from app.db.queries.utils import fetch_all, fetch_one


class AccountUserRow(TypedDict):
    id: int
    email: str
    role: str
    created_at: datetime
    last_login: datetime | None


class AccountUserDetailRow(TypedDict):
    id: int
    firebase_uid: str
    email: str
    role: str
    created_at: datetime
    last_login: datetime | None


async def get_all_users(conn: Connection) -> list[AccountUserRow]:
    """Get all users ordered by creation date."""
    return await fetch_all(
        conn,
        "SELECT id, email, role, created_at, last_login FROM users ORDER BY created_at",
    )


async def create_user(
    conn: Connection, firebase_uid: str, email: str, role: str
) -> AccountUserRow:
    """Create a new user with specified role."""
    return await fetch_one(
        conn,
        """
        INSERT INTO users (firebase_uid, email, role)
        VALUES ($1, $2, $3)
        RETURNING id, email, role, created_at, last_login
        """,
        firebase_uid,
        email,
        role,
    )


async def update_user_role(conn: Connection, user_id: int, role: str) -> AccountUserRow | None:
    """Update a user's role. Returns updated user or None if not found."""
    return await fetch_one(
        conn,
        """
        UPDATE users SET role = $2
        WHERE id = $1
        RETURNING id, email, role, created_at, last_login
        """,
        user_id,
        role,
    )


async def get_user_by_id(conn: Connection, user_id: int) -> AccountUserDetailRow | None:
    """Get a user by ID."""
    return await fetch_one(
        conn,
        "SELECT id, firebase_uid, email, role, created_at, last_login FROM users WHERE id = $1",
        user_id,
    )


async def delete_user(conn: Connection, user_id: int) -> bool:
    """Delete a user by ID. Returns True if deleted."""
    result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)
    return result == "DELETE 1"
