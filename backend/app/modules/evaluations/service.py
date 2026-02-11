"""Evaluation service for managing evaluation inputs."""

from typing import Any

from app.calculators.scoring import calculate_score
from app.core.exceptions import AppException, CalculatorException
from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.db.queries import calculator_results as calc_queries
from app.db.queries import evaluations as eval_queries
from app.modules.evaluations.schemas import (
    CategoryScoreItem,
    EvaluationStateResponse,
    RowScoreItem,
    ScoringResponse,
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
        manual_data = (eval_inputs or {}).get("manual_data") or {}

        if not manual_data:
            raise CalculatorException(
                code="CALC_MISSING_DATA",
                detail="No manual data available for scoring. Please fill in evaluation inputs first.",
            )

        # Load calculator results
        calc_rows = await calc_queries.get_results_by_brand(conn, brand_id)

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
