"""Account management database queries."""

from asyncpg import Connection


async def get_all_users(conn: Connection) -> list[dict]:
    """Get all users ordered by creation date."""
    rows = await conn.fetch(
        "SELECT id, email, role, created_at, last_login FROM users ORDER BY created_at"
    )
    return [dict(row) for row in rows]


async def create_user(
    conn: Connection, firebase_uid: str, email: str, role: str
) -> dict:
    """Create a new user with specified role."""
    row = await conn.fetchrow(
        """
        INSERT INTO users (firebase_uid, email, role)
        VALUES ($1, $2, $3)
        RETURNING id, email, role, created_at, last_login
        """,
        firebase_uid,
        email,
        role,
    )
    return dict(row)


async def update_user_role(conn: Connection, user_id: int, role: str) -> dict | None:
    """Update a user's role. Returns updated user or None if not found."""
    row = await conn.fetchrow(
        """
        UPDATE users SET role = $2
        WHERE id = $1
        RETURNING id, email, role, created_at, last_login
        """,
        user_id,
        role,
    )
    return dict(row) if row else None


async def get_user_by_id(conn: Connection, user_id: int) -> dict | None:
    """Get a user by ID."""
    row = await conn.fetchrow(
        "SELECT id, firebase_uid, email, role, created_at, last_login FROM users WHERE id = $1",
        user_id,
    )
    return dict(row) if row else None


async def delete_user(conn: Connection, user_id: int) -> bool:
    """Delete a user by ID. Returns True if deleted."""
    result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)
    return result == "DELETE 1"
