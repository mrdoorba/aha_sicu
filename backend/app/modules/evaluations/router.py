"""Evaluations API endpoints."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.modules.evaluations.calculator_service import (
    run_ads_keyword_calculator as _run_ads_keyword,
)
from app.modules.evaluations.schemas import (
    CalculatorResultResponse,
    EvaluationInputsUpdate,
    EvaluationStateResponse,
)
from app.modules.evaluations.service import get_evaluation_state, save_evaluation_inputs

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.get("/brands/{brand_id}", response_model=EvaluationStateResponse)
async def get_evaluation(
    brand_id: int,
    current_user: dict = Depends(get_current_user),
) -> EvaluationStateResponse:
    """Get evaluation state for a brand.

    Returns the current user's evaluation inputs for this brand.
    If no inputs exist, returns the same shape with null values.
    """
    return await get_evaluation_state(
        brand_id=brand_id, user_id=current_user["id"]
    )


@router.put("/brands/{brand_id}", response_model=EvaluationStateResponse)
async def update_evaluation(
    brand_id: int,
    body: EvaluationInputsUpdate,
    current_user: dict = Depends(get_current_user),
) -> EvaluationStateResponse:
    """Save evaluation inputs for a brand.

    Upserts evaluation_inputs record for this user+brand.
    Returns 404 if brand doesn't exist.
    """
    return await save_evaluation_inputs(
        brand_id=brand_id,
        user_id=current_user["id"],
        category_type=body.category_type,
        manual_data=body.manual_data,
    )


@router.post(
    "/brands/{brand_id}/calculators/ads_keyword",
    response_model=CalculatorResultResponse,
)
async def run_ads_keyword_calculator(
    brand_id: int,
    current_user: dict = Depends(get_current_user),
) -> CalculatorResultResponse:
    """Execute the Ads Keyword Calculator for a brand.

    Loads required CSV data and manual inputs, runs the calculator,
    and stores the result. Returns 400 if required data is missing.
    """
    return await _run_ads_keyword(
        brand_id=brand_id, user_id=current_user["id"]
    )
