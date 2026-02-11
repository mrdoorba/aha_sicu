"""Evaluations API endpoints."""

from fastapi import APIRouter, Depends

from app.calculators.engine import check_calculator_readiness, run_ready_calculators
from app.core.dependencies import get_current_user
from app.db.connection import db
from app.db.queries.calculator_results import get_results_by_brand
from app.modules.evaluations.calculator_service import (
    run_ads_keyword_calculator as _run_ads_keyword,
    run_discount_calculator as _run_discount,
    run_top_sku_calculator as _run_top_sku,
)
from app.modules.evaluations.schemas import (
    CalculatorResultItem,
    CalculatorResultResponse,
    CalculatorResultsListResponse,
    CalculatorStatusResponse,
    EvaluationInputsUpdate,
    EvaluationStateResponse,
    RunAllResponse,
    RunCalculatorItem,
    SingleCalculatorStatus,
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


@router.get(
    "/brands/{brand_id}/calculators/results",
    response_model=CalculatorResultsListResponse,
)
async def get_calculator_results(
    brand_id: int,
    current_user: dict = Depends(get_current_user),
) -> CalculatorResultsListResponse:
    """Return all stored calculator results for a brand."""
    async with db.connection() as conn:
        rows = await get_results_by_brand(conn=conn, brand_id=brand_id)

    results = [
        CalculatorResultItem(
            calculator_type=row["calculator_type"],
            output_text=row["output_text"],
            details=row["details"],
            calculated_at=row["calculated_at"],
        )
        for row in rows
    ]
    return CalculatorResultsListResponse(brand_id=brand_id, results=results)


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


@router.post(
    "/brands/{brand_id}/calculators/discount",
    response_model=CalculatorResultResponse,
)
async def run_discount_calculator(
    brand_id: int,
    current_user: dict = Depends(get_current_user),
) -> CalculatorResultResponse:
    """Execute the Discount Check Calculator for a brand.

    Loads order export data, runs the calculator,
    and stores the result. Returns 400 if required data is missing.
    """
    return await _run_discount(
        brand_id=brand_id, user_id=current_user["id"]
    )


@router.post(
    "/brands/{brand_id}/calculators/top_sku",
    response_model=CalculatorResultResponse,
)
async def run_top_sku_calculator(
    brand_id: int,
    current_user: dict = Depends(get_current_user),
) -> CalculatorResultResponse:
    """Execute the Top SKU Calculator for a brand.

    Loads order export and mass update data, runs the calculator,
    and stores the result. Returns 400 if required data is missing.
    """
    return await _run_top_sku(
        brand_id=brand_id, user_id=current_user["id"]
    )


@router.post(
    "/brands/{brand_id}/calculators/run-all",
    response_model=RunAllResponse,
)
async def run_all_calculators(
    brand_id: int,
    current_user: dict = Depends(get_current_user),
) -> RunAllResponse:
    """Run all calculators whose required files are available for a brand.

    Returns per-calculator results (success, skipped, or error).
    """
    async with db.connection() as conn:
        raw_results = await run_ready_calculators(
            brand_id=brand_id, user_id=current_user["id"], conn=conn
        )

    results = [
        RunCalculatorItem(
            calculator_type=item["calculator_type"],
            status=item["status"],
            result=item.get("result"),
            reason=item.get("reason"),
        )
        for item in raw_results
    ]
    return RunAllResponse(results=results)


@router.get(
    "/brands/{brand_id}/calculators/status",
    response_model=CalculatorStatusResponse,
)
async def get_calculator_status(
    brand_id: int,
    current_user: dict = Depends(get_current_user),
) -> CalculatorStatusResponse:
    """Return the readiness status of each calculator for a brand."""
    async with db.connection() as conn:
        readiness = await check_calculator_readiness(brand_id=brand_id, conn=conn)

    calculators = {
        calc_type: SingleCalculatorStatus(**status_info)
        for calc_type, status_info in readiness.items()
    }
    return CalculatorStatusResponse(brand_id=brand_id, calculators=calculators)
