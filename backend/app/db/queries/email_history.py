"""Email history database queries."""

from datetime import date, datetime

from asyncpg import Connection

from app.db.queries.utils import FilterBuilder, escape_like, fetch_all, fetch_one, paginate

_VALID_STATUSES: frozenset[str] = frozenset({
    "sent", "failed", "delivered", "bounced", "deferred",
    "opened", "clicked", "spam", "blocked", "invalid",
})

_STATUS_PRIORITY: dict[str, int] = {
    "sent": 1,
    "deferred": 2,
    "delivered": 3,
    "opened": 4,
    "clicked": 5,
    "bounced": 10,
    "spam": 10,
    "blocked": 10,
    "invalid": 10,
    "failed": 10,
}

_VALID_SORT_COLUMNS: frozenset[str] = frozenset({"sent_at", "recipient_email", "subject", "status"})
_VALID_SORT_ORDERS: frozenset[str] = frozenset({"asc", "desc"})

_LIMIT_CAP = 100


async def insert_email_history(
    conn: Connection,
    *,
    evaluation_id: int,
    sender_email: str,
    recipient_email: str,
    cc_emails: list[str] | None,
    bcc_emails: list[str] | None,
    subject: str,
    status: str,
    message_id: str | None,
    error_detail: str | None,
) -> dict:
    """Insert an email history record and return the created row."""
    return await fetch_one(
        conn,
        """
        INSERT INTO email_history (
            evaluation_id, sender_email, recipient_email, cc_emails, bcc_emails,
            subject, status, message_id, error_detail
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id, evaluation_id, sender_email, recipient_email, cc_emails,
                  bcc_emails, subject, status, message_id, error_detail, sent_at, created_at
        """,
        evaluation_id,
        sender_email,
        recipient_email,
        cc_emails,
        bcc_emails,
        subject,
        status,
        message_id,
        error_detail,
    )


async def list_email_history(
    conn: Connection,
    *,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "sent_at",
    sort_order: str = "desc",
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    status_filter: str | None = None,
) -> dict:
    """List email history with pagination, filtering, and sorting.

    Returns dict with keys: items, total, page, limit, pages.
    """
    if sort_by not in _VALID_SORT_COLUMNS:
        raise ValueError(f"Invalid sort column: {sort_by}")
    if sort_order not in _VALID_SORT_ORDERS:
        raise ValueError(f"Invalid sort order: {sort_order}")

    limit = min(limit, _LIMIT_CAP)
    sql_limit, offset = paginate(page, limit)

    fb = FilterBuilder()
    if search:
        escaped = escape_like(search)
        fb.add(
            "(recipient_email ILIKE '%' || {p} || '%' ESCAPE '\\' "
            "OR subject ILIKE '%' || {p} || '%' ESCAPE '\\')",
            escaped,
        )
    if date_from:
        fb.add("sent_at >= {p}", date_from)
    if date_to:
        fb.add("sent_at < ({p} + interval '1 day')", date_to)
    if status_filter:
        fb.add("status = {p}", status_filter)

    where = fb.where_clause
    params = fb.params

    # Count query
    count_query = f"SELECT COUNT(*) FROM email_history {where}"
    total = await conn.fetchval(count_query, *params) or 0

    # Data query
    param_idx = fb.next_idx
    limit_param = f"${param_idx}"
    offset_param = f"${param_idx + 1}"
    params.extend([sql_limit, offset])

    data_query = f"""
        SELECT id, evaluation_id, sender_email, recipient_email, cc_emails,
               bcc_emails, subject, status, message_id, error_detail, sent_at
        FROM email_history
        {where}
        ORDER BY {sort_by} {sort_order}
        LIMIT {limit_param} OFFSET {offset_param}
    """
    rows = await fetch_all(conn, data_query, *params)

    pages = (total + limit - 1) // limit if limit > 0 else 0
    return {
        "items": rows,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }


async def update_email_status_by_message_id(
    conn: Connection,
    *,
    message_id: str,
    new_status: str,
    event_at: datetime,
    error_detail: str | None = None,
) -> bool:
    """Atomically update email status if the new status has higher priority.

    Uses a single UPDATE with a CASE-based priority comparison in the WHERE
    clause to prevent TOCTOU race conditions under concurrent webhooks.

    Returns True if a row was updated, False otherwise.
    """
    if new_status not in _VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}")

    new_priority = _STATUS_PRIORITY[new_status]

    result = await conn.execute(
        """
        UPDATE email_history
        SET status = $2,
            last_event_at = $3,
            error_detail = COALESCE($4, error_detail)
        WHERE message_id = $1
          AND (CASE status
                WHEN 'sent' THEN 1
                WHEN 'deferred' THEN 2
                WHEN 'delivered' THEN 3
                WHEN 'opened' THEN 4
                WHEN 'clicked' THEN 5
                WHEN 'bounced' THEN 10
                WHEN 'spam' THEN 10
                WHEN 'blocked' THEN 10
                WHEN 'invalid' THEN 10
                WHEN 'failed' THEN 10
                ELSE 0
              END) < $5
        """,
        message_id,
        new_status,
        event_at,
        error_detail,
        new_priority,
    )
    # asyncpg returns "UPDATE N" where N is rows affected
    return result == "UPDATE 1"


_DELETE_BATCH_CAP = 100


async def delete_email_history_by_ids(
    conn: Connection,
    *,
    ids: list[int],
) -> int:
    """Delete email history entries by IDs. Returns count deleted."""
    if not ids:
        return 0
    if len(ids) > _DELETE_BATCH_CAP:
        raise ValueError(f"Batch size {len(ids)} exceeds limit of {_DELETE_BATCH_CAP}")

    result = await conn.execute(
        "DELETE FROM email_history WHERE id = ANY($1::int[])",
        ids,
    )
    # asyncpg returns "DELETE N"
    return int(result.split()[-1])


async def list_email_history_by_evaluation(
    conn: Connection,
    evaluation_id: int,
) -> list[dict]:
    """List all email history entries for a specific evaluation."""
    return await fetch_all(
        conn,
        """
        SELECT id, evaluation_id, sender_email, recipient_email, cc_emails,
               bcc_emails, subject, status, message_id, error_detail, sent_at
        FROM email_history
        WHERE evaluation_id = $1
        ORDER BY sent_at DESC
        """,
        evaluation_id,
    )
