"""Evaluation service for managing evaluation inputs."""

from typing import Any

from app.core.exceptions import AppException
from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.db.queries import evaluations as eval_queries
from app.modules.evaluations.schemas import EvaluationStateResponse


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
