"""Evaluation service for managing evaluation inputs."""

import json
import logging
import math
from datetime import date
from typing import Any, Literal

from app.calculators.scoring import calculate_score
from app.core.exceptions import AppException, CalculatorException
from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.db.queries import calculator_results as calc_queries
from app.db.queries import evaluations as eval_queries
from app.db.queries import rules as rules_queries
from app.modules.evaluations.schemas import (
    CategoryScoreItem,
    EvaluationDetailResponse,
    EvaluationListItem,
    EvaluationListResponse,
    EvaluationStateResponse,
    RowScoreItem,
    SaveEvaluationResponse,
    ScoringResponse,
)
from app.services.event_broadcaster import sync_broadcaster

logger = logging.getLogger(__name__)


def _ensure_dict(value: Any) -> dict:
    """Ensure a value is a dict, parsing JSON string if needed.

    Handles legacy double-encoded JSONB data where asyncpg returns a
    string instead of a dict due to prior json.dumps() before insert.
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
    return {}


async def list_evaluations(
    *,
    page: int,
    limit: int,
    sort_by: Literal["created_at", "final_score"],
    sort_order: Literal["asc", "desc"],
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> EvaluationListResponse:
    """Return a paginated list of evaluations.

    Handles pagination math and delegates to DB queries.
    Filters conditionally by brand name search and date range.
    """
    if date_from and date_to and date_from > date_to:
        raise AppException(
            code="VALIDATION_ERROR",
            detail="date_from must not be after date_to",
            status_code=422,
        )

    offset = (page - 1) * limit

    async with db.connection() as conn:
        rows = await eval_queries.list_evaluations(
            conn,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
            date_from=date_from,
            date_to=date_to,
        )
        total = await eval_queries.count_evaluations(
            conn, search=search, date_from=date_from, date_to=date_to,
        )

    pages = math.ceil(total / limit) if total > 0 else 0

    items = [
        EvaluationListItem(
            id=row["id"],
            brand_name=row["brand_name"],
            final_score=float(row["final_score"]),
            verdict=row["verdict"],
            template=row["template"],
            evaluator_email=row["evaluator_email"],
            created_at=row["created_at"],
        )
        for row in rows
    ]

    return EvaluationListResponse(
        items=items, total=total, page=page, limit=limit, pages=pages
    )


async def get_evaluation_detail(evaluation_id: int) -> EvaluationDetailResponse:
    """Get full details of a single evaluation by ID.

    Raises:
        AppException: If evaluation not found (404).
    """
    async with db.connection() as conn:
        row = await eval_queries.get_evaluation_by_id(conn, evaluation_id)

    if not row:
        raise AppException(
            code="EVAL_NOT_FOUND",
            detail="Evaluation not found",
            status_code=404,
        )

    return EvaluationDetailResponse(
        id=row["id"],
        brand_id=row["brand_id"],
        brand_name=row["brand_name"],
        final_score=float(row["final_score"]),
        verdict=row["verdict"],
        template=row["template"],
        score_breakdown=row["score_breakdown"],
        calculator_results=row["calculator_results"],
        manual_inputs=row["manual_inputs"],
        email_output=row["email_output"],
        evaluator_email=row["evaluator_email"],
        created_at=row["created_at"],
        rule_version=row["rule_version"],
    )


async def get_evaluation_state(
    brand_id: int, user_id: int
) -> EvaluationStateResponse:
    """Get the current evaluation state for a brand+user pair.

    Returns null values if no evaluation inputs exist yet.
    """
    async with db.connection() as conn:
        row = await eval_queries.get_evaluation_inputs(conn, brand_id, user_id)

    if not row:
        return EvaluationStateResponse(brand_id=brand_id)

    return EvaluationStateResponse(
        brand_id=row["brand_id"],
        category_type=row["category_type"],
        manual_data=row["manual_data"],
        updated_at=row["updated_at"],
    )


async def generate_score(
    brand_id: int,
    user_id: int,
    template: str,
    verdict: str,
    store_name: str,
    period: str,
    brand_name: str,
    email: str | None = None,
) -> ScoringResponse:
    """Generate the final score for a brand evaluation.

    Loads manual data and calculator results from DB, runs the
    scoring calculator (pure function), and returns the result.

    Raises:
        CalculatorException: BRAND_NOT_FOUND if brand doesn't exist.
        CalculatorException: CALC_MISSING_DATA if manual data not available.
    """
    async with db.connection() as conn:
        # Validate brand exists
        brand = await brand_queries.get_brand_by_id(conn, brand_id)
        if not brand:
            raise CalculatorException(
                code="BRAND_NOT_FOUND",
                detail="Brand not found",
                status_code=404,
            )

        # Load manual data
        eval_inputs = await eval_queries.get_evaluation_inputs(conn, brand_id, user_id)
        manual_data = _ensure_dict((eval_inputs or {}).get("manual_data"))

        if not manual_data:
            raise CalculatorException(
                code="CALC_MISSING_DATA",
                detail="No manual data available for scoring. Please fill in evaluation inputs first.",
            )

        # Load calculator results
        calc_rows = await calc_queries.get_results_by_brand(conn, brand_id)

        # Load scoring rules — always use the unified "default" template
        rule_row = await rules_queries.get_rules_by_template(conn, "default")

    rules_jsonb = rule_row["rules"] if rule_row else None
    rule_version = rule_row["version"] if rule_row else 1

    calculator_results: dict[str, dict] = {}
    for row in calc_rows:
        calculator_results[row["calculator_type"]] = {
            "details": row["details"],
            "output_text": row["output_text"],
        }

    # Run pure scoring calculator
    try:
        result = calculate_score(
            manual_data=manual_data,
            calculator_results=calculator_results,
            template=template,
            verdict=verdict,
            store_name=store_name,
            period=period,
            brand_name=brand_name,
            email=email,
            rules=rules_jsonb,
            rule_version=rule_version,
        )
    except Exception as e:
        raise CalculatorException(
            code="CALC_EXECUTION_FAILED",
            detail=f"Scoring calculator failed: {e}",
            status_code=500,
        ) from e

    # Convert to response schema
    category_scores = [
        CategoryScoreItem(
            category=cat.category,
            score=cat.score,
            max_score=cat.max_score,
            rows=[
                RowScoreItem(
                    row=r.row,
                    metric=r.metric,
                    value=r.value,
                    benchmark=r.benchmark,
                    verdict=r.verdict,
                    message=r.message,
                    score=r.score,
                )
                for r in cat.rows
            ],
            available=cat.available,
        )
        for cat in result.category_scores
    ]

    return ScoringResponse(
        total_score=result.total_score,
        category_scores=category_scores,
        verdict=result.verdict,
        conclusion=result.conclusion,
        marketing_estimation=result.marketing_estimation,
        marketing_percentage=result.marketing_percentage,
        marketing_budget=result.marketing_budget,
        closing_message=result.closing_message,
        email_subject=result.email_subject,
        email_body=result.email_body,
        whatsapp_link=result.whatsapp_link,
        template=result.template,
        rule_version=result.rule_version,
    )


async def save_evaluation(
    brand_id: int,
    user_id: int,
    template: str,
    final_score: float,
    verdict: str,
    score_breakdown: list[dict],
    calculator_results: dict,
    manual_inputs: dict,
    rule_version: int = 1,
    email_output: str | None = None,
    evaluator_email: str = "",
) -> SaveEvaluationResponse:
    """Save a completed evaluation as a permanent, immutable record.

    Validates that the brand exists, then inserts a new evaluation record.
    Each call creates a NEW record (INSERT-only, no upsert).
    Broadcasts a new_evaluation SSE event after successful save.

    Raises:
        AppException: If brand not found (404).
    """
    async with db.connection() as conn:
        async with conn.transaction():
            brand = await brand_queries.get_brand_by_id(conn, brand_id)
            if not brand:
                raise AppException(
                    code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
                )

            row = await eval_queries.insert_evaluation(
                conn,
                brand_id=brand_id,
                user_id=user_id,
                template=template,
                final_score=final_score,
                verdict=verdict,
                score_breakdown=score_breakdown,
                calculator_results=calculator_results,
                manual_inputs=manual_inputs,
                rule_version=rule_version,
                email_output=email_output,
            )

    # Broadcast OUTSIDE the transaction — save already committed
    try:
        await sync_broadcaster.broadcast(
            "new_evaluation",
            {
                "evaluation_id": row["id"],
                "brand_name": brand["brand_name"],
                "score": final_score,
                "evaluator": evaluator_email,
                "created_at": row["created_at"].isoformat(),
            },
        )
    except Exception:
        logger.warning("Failed to broadcast new_evaluation event", exc_info=True)

    return SaveEvaluationResponse(
        id=row["id"],
        brand_id=row["brand_id"],
        final_score=float(row["final_score"]),
        verdict=row["verdict"],
        template=row["template"],
        created_at=row["created_at"],
    )


async def save_evaluation_inputs(
    brand_id: int,
    user_id: int,
    category_type: str | None,
    manual_data: dict[str, Any] | None,
) -> EvaluationStateResponse:
    """Upsert evaluation inputs for a brand+user pair.

    Validates that the brand exists before saving.

    Raises:
        AppException: If brand not found (404).
    """
    async with db.connection() as conn:
        async with conn.transaction():
            brand = await brand_queries.get_brand_by_id(conn, brand_id)
            if not brand:
                raise AppException(
                    code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
                )

            row = await eval_queries.upsert_evaluation_inputs(
                conn,
                brand_id=brand_id,
                user_id=user_id,
                category_type=category_type,
                manual_data=manual_data,
            )

    return EvaluationStateResponse(
        brand_id=row["brand_id"],
        category_type=row["category_type"],
        manual_data=row["manual_data"],
        updated_at=row["updated_at"],
    )
