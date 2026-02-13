"""Evaluations API endpoints."""

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query

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
    EvaluationDetailResponse,
    EvaluationInputsUpdate,
    EvaluationListResponse,
    EvaluationStateResponse,
    RunAllResponse,
    RunCalculatorItem,
    SaveEvaluationRequest,
    SaveEvaluationResponse,
    ScoringRequest,
    ScoringResponse,
    SingleCalculatorStatus,
)
from app.modules.evaluations.service import (
    generate_score,
    get_evaluation_detail,
    get_evaluation_state,
    list_evaluations,
    save_evaluation,
    save_evaluation_inputs,
)

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.get("", response_model=EvaluationListResponse)
async def list_evaluations_endpoint(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: Literal["created_at", "final_score"] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    search: str | None = Query(default=None, max_length=200),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
) -> EvaluationListResponse:
    """List all evaluations with pagination and sorting.

    Returns paginated evaluation history with brand names and evaluator emails.
    Supports filtering by search (brand name) and date range (date_from, date_to).
    """
    return await list_evaluations(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{evaluation_id}", response_model=EvaluationDetailResponse)
async def get_evaluation_detail_endpoint(
    evaluation_id: int,
    current_user: dict = Depends(get_current_user),
) -> EvaluationDetailResponse:
    """Get full details of a single evaluation by ID."""
    return await get_evaluation_detail(evaluation_id=evaluation_id)


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
    """Return all stored calculator results for a brand.

    Returns an empty list if brand_id doesn't exist or has no results.
    This is intentional for read-only list endpoints (vs POST endpoints
    which validate brand existence and return 400).
    """
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


@router.post(
    "/brands/{brand_id}/score",
    response_model=ScoringResponse,
)
async def score_evaluation(
    brand_id: int,
    body: ScoringRequest,
    current_user: dict = Depends(get_current_user),
) -> ScoringResponse:
    """Generate the final score for a brand evaluation.

    Runs the scoring calculator with current manual inputs + calculator results.
    Returns the complete scoring result (scores, messages, email, whatsapp).
    Returns 400 if required data is missing.
    """
    return await generate_score(
        brand_id=brand_id,
        user_id=current_user["id"],
        template=body.template,
        verdict=body.verdict,
        store_name=body.store_name,
        period=body.period,
        brand_name=body.brand_name,
        email=body.email,
    )


@router.post(
    "/brands/{brand_id}/save",
    response_model=SaveEvaluationResponse,
)
async def save_evaluation_endpoint(
    brand_id: int,
    body: SaveEvaluationRequest,
    current_user: dict = Depends(get_current_user),
) -> SaveEvaluationResponse:
    """Save a completed evaluation as a permanent record.

    Creates a new immutable evaluation record (INSERT-only).
    Multiple saves for the same brand create separate records (history).
    Returns 404 if brand doesn't exist, 422 if required fields are missing.
    """
    return await save_evaluation(
        brand_id=brand_id,
        user_id=current_user["id"],
        template=body.template,
        final_score=body.final_score,
        verdict=body.verdict,
        score_breakdown=body.score_breakdown,
        calculator_results=body.calculator_results,
        manual_inputs=body.manual_inputs,
        rule_version=body.rule_version,
        email_output=body.email_output,
        evaluator_email=current_user["email"],
    )
