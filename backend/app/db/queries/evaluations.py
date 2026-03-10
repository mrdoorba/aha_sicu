"""Evaluation inputs database queries using parameterized SQL."""

from datetime import date, datetime
from typing import Any, Literal, TypedDict

from asyncpg import Connection

from app.db.queries.utils import escape_like


class EvaluationInputsRow(TypedDict):
    id: int
    brand_id: int
    last_edited_by: int
    category_type: str | None
    manual_data: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class EvaluationListRow(TypedDict):
    id: int
    brand_name: str
    final_score: float
    verdict: str
    template: str
    evaluator_email: str
    created_at: datetime
    period: str


class GroupedEvaluationRow(TypedDict):
    brand_id: int
    brand_name: str
    evaluation_count: int
    top_score: float
    top_verdict: str
    latest_date: datetime


class BrandEvaluationRow(TypedDict):
    id: int
    final_score: float
    verdict: str
    template: str
    evaluator_email: str
    created_at: datetime
    period: str


class EvaluationDetailRow(TypedDict):
    id: int
    brand_id: int
    brand_name: str
    raw_data: dict[str, Any]
    final_score: float
    verdict: str
    template: str
    score_breakdown: list[dict[str, Any]]
    calculator_results: dict[str, Any]
    manual_inputs: dict[str, Any]
    email_output: str | None
    rule_version: int
    created_at: datetime
    period: str
    evaluator_email: str


class InsertedEvaluationRow(TypedDict):
    id: int
    brand_id: int
    final_score: float
    verdict: str
    template: str
    created_at: datetime
    period: str


async def get_evaluation_inputs(
    conn: Connection,
    brand_id: int,
) -> EvaluationInputsRow | None:
    """Get evaluation inputs for a brand (shared — one row per brand)."""
    row = await conn.fetchrow(
        """
        SELECT id, brand_id, last_edited_by, category_type, manual_data,
               created_at, updated_at
        FROM evaluation_inputs
        WHERE brand_id = $1
        """,
        brand_id,
    )
    return dict(row) if row else None


async def upsert_evaluation_inputs(
    conn: Connection,
    brand_id: int,
    last_edited_by: int,
    category_type: str | None,
    manual_data: dict[str, Any] | None,
) -> EvaluationInputsRow:
    """Insert or update evaluation inputs for a brand (shared).

    Uses COALESCE to preserve existing values when new values are None.
    Conflict target is (brand_id) — one row per brand.
    """
    row = await conn.fetchrow(
        """
        INSERT INTO evaluation_inputs (brand_id, last_edited_by, category_type, manual_data, updated_at)
        VALUES ($1, $2, $3, $4, NOW())
        ON CONFLICT (brand_id) DO UPDATE SET
            last_edited_by = EXCLUDED.last_edited_by,
            category_type = COALESCE(EXCLUDED.category_type, evaluation_inputs.category_type),
            manual_data = COALESCE(EXCLUDED.manual_data, evaluation_inputs.manual_data),
            updated_at = NOW()
        RETURNING id, brand_id, last_edited_by, category_type, manual_data, created_at, updated_at
        """,
        brand_id,
        last_edited_by,
        category_type,
        manual_data,
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
    period: str = "",
) -> InsertedEvaluationRow:
    """Insert a new evaluation record (immutable snapshot).

    Always creates a new record — never upserts.
    Returns the new record's id, brand_id, final_score, verdict, template, created_at, period.
    """
    row = await conn.fetchrow(
        """
        INSERT INTO evaluations (
            brand_id, user_id, template, final_score, verdict,
            score_breakdown, calculator_results, manual_inputs,
            rule_version, email_output, period
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING id, brand_id, final_score, verdict, template, created_at, period
        """,
        brand_id,
        user_id,
        template,
        final_score,
        verdict,
        score_breakdown,
        calculator_results,
        manual_inputs,
        rule_version,
        email_output,
        period,
    )
    return dict(row)


def _build_filter_clauses(
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[str, list[Any], int]:
    """Build conditional WHERE clauses for evaluation list/count queries.

    Returns (where_clause, params, next_param_idx) with dynamic $N numbering.
    """
    conditions: list[str] = []
    params: list[Any] = []
    param_idx = 1

    if search:
        escaped = escape_like(search)
        conditions.append(f"b.brand_name ILIKE '%' || ${param_idx} || '%' ESCAPE '\\'")
        params.append(escaped)
        param_idx += 1

    if date_from:
        conditions.append(f"e.created_at >= ${param_idx}")
        params.append(date_from)
        param_idx += 1

    if date_to:
        conditions.append(f"e.created_at < (${param_idx} + interval '1 day')")
        params.append(date_to)
        param_idx += 1

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    return where_clause, params, param_idx


async def list_evaluations(
    conn: Connection,
    *,
    limit: int,
    offset: int,
    sort_by: Literal["created_at", "final_score"],
    sort_order: Literal["asc", "desc"],
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[EvaluationListRow]:
    """List evaluations with JOIN on brand_vp_data and users.

    Returns lightweight rows (no heavy JSONB columns).
    sort_by is validated via Literal type at router level — safe for f-string.
    Filters conditionally by search (brand_name ILIKE) and date range.
    """
    where_clause, params, param_idx = _build_filter_clauses(search, date_from, date_to)
    limit_param = f"${param_idx}"
    offset_param = f"${param_idx + 1}"
    params.extend([limit, offset])

    query = f"""
        SELECT e.id, b.brand_name, e.final_score, e.verdict, e.template,
               COALESCE(u.email, 'Pengguna Dihapus') AS evaluator_email, e.created_at,
               COALESCE(e.period, '') AS period
        FROM evaluations e
        JOIN brand_vp_data b ON e.brand_id = b.id
        LEFT JOIN users u ON e.user_id = u.id
        {where_clause}
        ORDER BY e.{sort_by} {sort_order}
        LIMIT {limit_param} OFFSET {offset_param}
    """
    rows = await conn.fetch(query, *params)
    return [dict(row) for row in rows]


async def count_evaluations(
    conn: Connection,
    *,
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> int:
    """Return total number of evaluations, optionally filtered by search and date range."""
    where_clause, params, _ = _build_filter_clauses(search, date_from, date_to)

    query = f"""
        SELECT COUNT(*)
        FROM evaluations e
        JOIN brand_vp_data b ON e.brand_id = b.id
        {where_clause}
    """
    row = await conn.fetchval(query, *params)
    return row or 0


async def get_evaluation_by_id(
    conn: Connection,
    evaluation_id: int,
) -> EvaluationDetailRow | None:
    """Get full evaluation details by ID, with brand name and evaluator email joins."""
    row = await conn.fetchrow(
        """
        SELECT e.id, e.brand_id, b.brand_name, b.raw_data,
               e.final_score, e.verdict, e.template,
               e.score_breakdown, e.calculator_results, e.manual_inputs,
               e.email_output, e.rule_version, e.created_at,
               COALESCE(e.period, '') AS period,
               COALESCE(u.email, 'Pengguna Dihapus') AS evaluator_email
        FROM evaluations e
        JOIN brand_vp_data b ON e.brand_id = b.id
        LEFT JOIN users u ON e.user_id = u.id
        WHERE e.id = $1
        """,
        evaluation_id,
    )
    return dict(row) if row else None


async def list_grouped_evaluations(
    conn: Connection,
    *,
    limit: int,
    offset: int,
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[GroupedEvaluationRow]:
    """List evaluations grouped by brand with aggregate data.

    Returns one row per brand with evaluation count, top score/verdict,
    and latest date. Sorted by latest evaluation date descending.
    Paginated by brand (not by individual evaluation).
    """
    where_clause, params, param_idx = _build_filter_clauses(search, date_from, date_to)
    limit_param = f"${param_idx}"
    offset_param = f"${param_idx + 1}"
    params.extend([limit, offset])

    query = f"""
        SELECT e.brand_id,
               b.brand_name,
               COUNT(*) AS evaluation_count,
               MAX(e.final_score) AS top_score,
               (ARRAY_AGG(e.verdict ORDER BY e.final_score DESC))[1] AS top_verdict,
               MAX(e.created_at) AS latest_date
        FROM evaluations e
        JOIN brand_vp_data b ON e.brand_id = b.id
        {where_clause}
        GROUP BY e.brand_id, b.brand_name
        ORDER BY MAX(e.created_at) DESC
        LIMIT {limit_param} OFFSET {offset_param}
    """
    rows = await conn.fetch(query, *params)
    return [dict(row) for row in rows]


async def count_grouped_evaluations(
    conn: Connection,
    *,
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> int:
    """Count distinct brands that have evaluations matching the filters."""
    where_clause, params, _ = _build_filter_clauses(search, date_from, date_to)

    query = f"""
        SELECT COUNT(DISTINCT e.brand_id)
        FROM evaluations e
        JOIN brand_vp_data b ON e.brand_id = b.id
        {where_clause}
    """
    row = await conn.fetchval(query, *params)
    return row or 0


async def list_evaluations_by_brand(
    conn: Connection,
    brand_id: int,
    *,
    limit: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[list[BrandEvaluationRow], int]:
    """Fetch individual evaluations for a specific brand.

    Returns (rows, total) where total is the count before limit is applied.
    Sorted by created_at DESC. Supports optional limit and date filter.
    """
    conditions: list[str] = ["e.brand_id = $1"]
    params: list[Any] = [brand_id]
    param_idx = 2

    if date_from:
        conditions.append(f"e.created_at >= ${param_idx}")
        params.append(date_from)
        param_idx += 1

    if date_to:
        conditions.append(f"e.created_at < (${param_idx} + interval '1 day')")
        params.append(date_to)
        param_idx += 1

    where_clause = "WHERE " + " AND ".join(conditions)

    # Get total count first
    count_query = f"""
        SELECT COUNT(*)
        FROM evaluations e
        {where_clause}
    """
    total = await conn.fetchval(count_query, *params) or 0

    # Fetch rows with optional limit
    limit_clause = ""
    if limit is not None:
        limit_clause = f"LIMIT ${param_idx}"
        params.append(limit)

    query = f"""
        SELECT e.id, e.final_score, e.verdict, e.template,
               COALESCE(u.email, 'Pengguna Dihapus') AS evaluator_email, e.created_at,
               COALESCE(e.period, '') AS period
        FROM evaluations e
        LEFT JOIN users u ON e.user_id = u.id
        {where_clause}
        ORDER BY e.created_at DESC
        {limit_clause}
    """
    rows = await conn.fetch(query, *params)
    return [dict(row) for row in rows], total


async def delete_evaluation(
    conn: Connection,
    evaluation_id: int,
) -> bool:
    """Hard delete an evaluation by ID. Returns True if a row was deleted."""
    result = await conn.execute(
        "DELETE FROM evaluations WHERE id = $1",
        evaluation_id,
    )
    return result == "DELETE 1"


