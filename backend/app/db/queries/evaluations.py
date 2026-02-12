"""Evaluation inputs database queries using parameterized SQL."""

import json
from typing import Any, Literal

from asyncpg import Connection


async def get_evaluation_inputs(
    conn: Connection,
    brand_id: int,
    user_id: int,
) -> dict | None:
    """Get evaluation inputs for a specific brand and user."""
    row = await conn.fetchrow(
        """
        SELECT id, brand_id, user_id, category_type, manual_data,
               created_at, updated_at
        FROM evaluation_inputs
        WHERE brand_id = $1 AND user_id = $2
        """,
        brand_id,
        user_id,
    )
    return dict(row) if row else None


async def upsert_evaluation_inputs(
    conn: Connection,
    brand_id: int,
    user_id: int,
    category_type: str | None,
    manual_data: dict[str, Any] | None,
) -> dict:
    """Insert or update evaluation inputs for a brand+user pair.

    Uses COALESCE to preserve existing values when new values are None.
    """
    row = await conn.fetchrow(
        """
        INSERT INTO evaluation_inputs (brand_id, user_id, category_type, manual_data, updated_at)
        VALUES ($1, $2, $3, $4, NOW())
        ON CONFLICT (brand_id, user_id) DO UPDATE SET
            category_type = COALESCE(EXCLUDED.category_type, evaluation_inputs.category_type),
            manual_data = COALESCE(EXCLUDED.manual_data, evaluation_inputs.manual_data),
            updated_at = NOW()
        RETURNING id, brand_id, user_id, category_type, manual_data, created_at, updated_at
        """,
        brand_id,
        user_id,
        category_type,
        json.dumps(manual_data) if manual_data is not None else None,
    )
    return dict(row)


async def insert_evaluation(
    conn: Connection,
    brand_id: int,
    user_id: int,
    template: str,
    final_score: float,
    verdict: str,
    score_breakdown: list[dict[str, Any]],
    calculator_results: dict[str, Any],
    manual_inputs: dict[str, Any],
    rule_version: int = 1,
    email_output: str | None = None,
) -> dict:
    """Insert a new evaluation record (immutable snapshot).

    Always creates a new record — never upserts.
    Returns the new record's id, brand_id, final_score, verdict, template, created_at.
    """
    row = await conn.fetchrow(
        """
        INSERT INTO evaluations (
            brand_id, user_id, template, final_score, verdict,
            score_breakdown, calculator_results, manual_inputs,
            rule_version, email_output
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id, brand_id, final_score, verdict, template, created_at
        """,
        brand_id,
        user_id,
        template,
        final_score,
        verdict,
        json.dumps(score_breakdown),
        json.dumps(calculator_results),
        json.dumps(manual_inputs),
        rule_version,
        email_output,
    )
    return dict(row)


async def list_evaluations(
    conn: Connection,
    *,
    limit: int,
    offset: int,
    sort_by: Literal["created_at", "final_score"],
    sort_order: Literal["asc", "desc"],
) -> list[dict]:
    """List evaluations with JOIN on brand_vp_data and users.

    Returns lightweight rows (no heavy JSONB columns).
    sort_by is validated via Literal type at router level — safe for f-string.
    """
    query = f"""
        SELECT e.id, b.brand_name, e.final_score, e.verdict, e.template,
               u.email AS evaluator_email, e.created_at
        FROM evaluations e
        JOIN brand_vp_data b ON e.brand_id = b.id
        JOIN users u ON e.user_id = u.id
        ORDER BY e.{sort_by} {sort_order}
        LIMIT $1 OFFSET $2
    """
    rows = await conn.fetch(query, limit, offset)
    return [dict(row) for row in rows]


async def count_evaluations(conn: Connection) -> int:
    """Return total number of evaluations."""
    row = await conn.fetchval("SELECT COUNT(*) FROM evaluations")
    return row or 0


async def get_any_evaluation_inputs(
    conn: Connection,
    brand_id: int,
) -> dict | None:
    """Get evaluation inputs for a brand (any user). Used for readiness checks."""
    row = await conn.fetchrow(
        """
        SELECT id, brand_id, user_id, category_type, manual_data,
               created_at, updated_at
        FROM evaluation_inputs
        WHERE brand_id = $1 AND manual_data IS NOT NULL
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        brand_id,
    )
    return dict(row) if row else None
