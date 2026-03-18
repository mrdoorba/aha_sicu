"""Evaluation service for managing evaluation inputs."""

import asyncio
import logging
import math
from datetime import date
from typing import Any, Literal

from asyncpg import Connection

from app.calculators.scoring import calculate_score
from app.core.exceptions import AppException, CalculatorException
from app.core.utils import ensure_dict
from app.db.queries.utils import paginate
from app.calculators.engine import check_calculator_readiness, run_ready_calculators
from app.db.queries import brands as brand_queries
from app.db.queries import calculator_results as calc_queries
from app.db.queries import evaluations as eval_queries
from app.db.queries import rules as rules_queries
from app.calculators.scoring.models import TranslatableText
from app.modules.evaluations.schemas import (
    BrandEvaluationItem,
    BrandEvaluationListResponse,
    BrandRawData,
    CalculatorResultItem,
    CalculatorResultsListResponse,
    CalculatorStatusResponse,
    CategoryScoreItem,
    EvaluationDetailResponse,
    EvaluationListItem,
    EvaluationListResponse,
    EvaluationStateResponse,
    GroupedEvaluationItem,
    GroupedEvaluationListResponse,
    RowScoreItem,
    RunAllResponse,
    RunCalculatorItem,
    SaveEvaluationResponse,
    ScoringResponse,
    SingleCalculatorStatus,
    TranslatableTextSchema,
)
logger = logging.getLogger(__name__)


def _to_schema(t: TranslatableText | None) -> TranslatableTextSchema | None:
    """Convert a TranslatableText dataclass to its Pydantic schema."""
    if t is None:
        return None
    return TranslatableTextSchema(key=t.key, vars=t.vars)


def _to_schema_list(
    items: list[TranslatableText] | None,
) -> list[TranslatableTextSchema] | None:
    """Convert a list of TranslatableText dataclasses to Pydantic schemas."""
    if items is None:
        return None
    return [TranslatableTextSchema(key=t.key, vars=t.vars) for t in items]


async def list_evaluations(
    *,
    conn: Connection,
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

    limit, offset = paginate(page, limit)

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
            period=row.get("period", ""),
        )
        for row in rows
    ]

    return EvaluationListResponse(
        items=items, total=total, page=page, limit=limit, pages=pages
    )


async def list_grouped_evaluations(
    *,
    conn: Connection,
    page: int,
    limit: int,
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> GroupedEvaluationListResponse:
    """Return a paginated list of evaluations grouped by brand."""
    if date_from and date_to and date_from > date_to:
        raise AppException(
            code="VALIDATION_ERROR",
            detail="date_from must not be after date_to",
            status_code=422,
        )

    limit, offset = paginate(page, limit)

    rows = await eval_queries.list_grouped_evaluations(
        conn,
        limit=limit,
        offset=offset,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )
    total = await eval_queries.count_grouped_evaluations(
        conn, search=search, date_from=date_from, date_to=date_to,
    )

    pages = math.ceil(total / limit) if total > 0 else 0

    items = [
        GroupedEvaluationItem(
            brand_id=row["brand_id"],
            brand_name=row["brand_name"],
            evaluation_count=row["evaluation_count"],
            top_score=float(row["top_score"]),
            top_verdict=row["top_verdict"],
            latest_date=row["latest_date"],
        )
        for row in rows
    ]

    return GroupedEvaluationListResponse(
        items=items, total=total, page=page, limit=limit, pages=pages
    )


async def list_evaluations_by_brand(
    brand_id: int,
    *,
    conn: Connection,
    limit: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> BrandEvaluationListResponse:
    """Return evaluations for a specific brand with optional limit."""
    rows, total = await eval_queries.list_evaluations_by_brand(
        conn,
        brand_id,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
    )

    items = [
        BrandEvaluationItem(
            id=row["id"],
            final_score=float(row["final_score"]),
            verdict=row["verdict"],
            template=row["template"],
            evaluator_email=row["evaluator_email"],
            created_at=row["created_at"],
            period=row.get("period", ""),
        )
        for row in rows
    ]

    return BrandEvaluationListResponse(items=items, total=total)


async def delete_evaluation(conn: Connection, evaluation_id: int) -> bool:
    """Delete an evaluation by ID. Returns True if deleted, raises 404 if not found."""
    # Get brand info before delete (for sheet sync)
    brand_info = await eval_queries.get_evaluation_brand_info(conn, evaluation_id)

    deleted = await eval_queries.delete_evaluation(conn, evaluation_id)

    if not deleted:
        raise AppException(
            code="EVAL_NOT_FOUND",
            detail="Evaluation not found",
            status_code=404,
        )

    # Fire-and-forget: remove brand from sheet if no evaluations remain
    if brand_info:
        remaining = await eval_queries.count_evaluations_by_brand_id(
            conn, brand_info["brand_id"]
        )
        if remaining == 0:
            asyncio.create_task(
                _sync_remove_brand_from_sheet_safe(brand_info["brand_name"])
            )

    return True


async def get_evaluation_detail(conn: Connection, evaluation_id: int) -> EvaluationDetailResponse:
    """Get full details of a single evaluation by ID.

    Raises:
        AppException: If evaluation not found (404).
    """
    row = await eval_queries.get_evaluation_by_id(conn, evaluation_id)

    if not row:
        raise AppException(
            code="EVAL_NOT_FOUND",
            detail="Evaluation not found",
            status_code=404,
        )

    # Map VP sheet raw_data keys to clean keys for email composition
    raw_data = ensure_dict(row.get("raw_data"))
    brand_raw_data = BrandRawData(
        email=raw_data.get("Email"),
        pic_name=raw_data.get("Nama PIC/ Jabatan*"),
        store_link=raw_data.get("Link Shopee Mall / LazMall"),
        kategori=raw_data.get("Kategori"),
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
        period=row.get("period", ""),
        marketplace=row.get("marketplace", "ID"),
        brand_raw_data=brand_raw_data,
    )


async def get_evaluation_state(
    conn: Connection,
    brand_id: int,
) -> EvaluationStateResponse:
    """Get the current evaluation state for a brand (shared).

    Returns null values if no evaluation inputs exist yet.
    """
    row = await eval_queries.get_evaluation_inputs(conn, brand_id)

    if not row:
        return EvaluationStateResponse(brand_id=brand_id)

    return EvaluationStateResponse(
        brand_id=row["brand_id"],
        category_type=row["category_type"],
        manual_data=row["manual_data"],
        updated_at=row["updated_at"],
    )


async def generate_score(
    conn: Connection,
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
    # Validate brand exists
    brand = await brand_queries.get_brand_by_id(conn, brand_id)
    if not brand:
        raise CalculatorException(
            code="BRAND_NOT_FOUND",
            detail="Brand not found",
            status_code=404,
        )

    # Load manual data (shared — one row per brand)
    eval_inputs = await eval_queries.get_evaluation_inputs(conn, brand_id)
    manual_data = ensure_dict((eval_inputs or {}).get("manual_data"))

    if not manual_data:
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail="No manual data available for scoring. Please fill in evaluation inputs first.",
        )

    # Load calculator results
    calc_rows = await calc_queries.get_results_by_brand(conn, brand_id)

    # Load scoring rules — always use the unified "default" template
    # Marketplace comes from eval_inputs — determines which rules row to use
    marketplace = (eval_inputs or {}).get("marketplace", "ID")
    rule_row = await rules_queries.get_rules_by_template_and_marketplace(
        conn, "default", marketplace=marketplace
    )

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
            marketplace=marketplace,
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
                    metric_i18n=_to_schema(r.metric_i18n),
                    value_i18n=_to_schema(r.value_i18n),
                    message_i18n=_to_schema(r.message_i18n),
                    benchmark_i18n=_to_schema(r.benchmark_i18n),
                )
                for r in cat.rows
            ],
            available=cat.available,
            category_i18n=_to_schema(cat.category_i18n),
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
        template=result.template,
        rule_version=result.rule_version,
        conclusion_i18n=_to_schema_list(result.conclusion_i18n),
        marketing_budget_i18n=_to_schema(result.marketing_budget_i18n),
        closing_message_i18n=_to_schema(result.closing_message_i18n),
        email_subject_i18n=_to_schema(result.email_subject_i18n),
    )


async def save_evaluation(
    conn: Connection,
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
    period: str = "",
    marketplace: str = "ID",
) -> SaveEvaluationResponse:
    """Save a completed evaluation as a permanent, immutable record.

    Validates that the brand exists, then inserts a new evaluation record.
    Each call creates a NEW record (INSERT-only, no upsert).
    Raises:
        AppException: If brand not found (404).
    """
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
            period=period,
            marketplace=marketplace,
        )

    # Fire-and-forget: sync brand to eval sheet
    brand_name = brand["brand_name"]
    asyncio.create_task(_sync_brand_to_sheet_safe(brand_name))

    return SaveEvaluationResponse(
        id=row["id"],
        brand_id=row["brand_id"],
        final_score=float(row["final_score"]),
        verdict=row["verdict"],
        template=row["template"],
        created_at=row["created_at"],
        period=row.get("period", ""),
    )


async def get_calculator_results(conn: Connection, brand_id: int) -> CalculatorResultsListResponse:
    """Return all stored calculator results for a brand.

    Returns an empty list if brand_id doesn't exist or has no results.
    """
    rows = await calc_queries.get_results_by_brand(conn=conn, brand_id=brand_id)

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


async def get_calculator_status(conn: Connection, brand_id: int) -> CalculatorStatusResponse:
    """Return the readiness status of each calculator for a brand."""
    readiness = await check_calculator_readiness(brand_id=brand_id, conn=conn)

    calculators = {
        calc_type: SingleCalculatorStatus(**status_info)
        for calc_type, status_info in readiness.items()
    }
    return CalculatorStatusResponse(brand_id=brand_id, calculators=calculators)


async def run_all_calculators_service(conn: Connection, brand_id: int) -> RunAllResponse:
    """Run all calculators whose required files are available for a brand.

    Returns per-calculator results (success, skipped, or error).
    """
    raw_results = await run_ready_calculators(brand_id=brand_id, conn=conn)

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


async def save_evaluation_inputs(
    conn: Connection,
    brand_id: int,
    last_edited_by: int,
    category_type: str | None,
    manual_data: dict[str, Any] | None,
    marketplace: str = "ID",
) -> EvaluationStateResponse:
    """Upsert evaluation inputs for a brand (shared).

    Validates that the brand exists before saving.

    Raises:
        AppException: If brand not found (404).
    """
    async with conn.transaction():
        brand = await brand_queries.get_brand_by_id(conn, brand_id)
        if not brand:
            raise AppException(
                code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
            )

        row = await eval_queries.upsert_evaluation_inputs(
            conn,
            brand_id=brand_id,
            last_edited_by=last_edited_by,
            category_type=category_type,
            manual_data=manual_data,
            marketplace=marketplace,
        )

    return EvaluationStateResponse(
        brand_id=row["brand_id"],
        category_type=row["category_type"],
        manual_data=row["manual_data"],
        updated_at=row["updated_at"],
    )


async def _sync_brand_to_sheet_safe(brand_name: str) -> None:
    """Fire-and-forget wrapper for eval sheet sync on save."""
    try:
        from app.modules.sync.eval_sheet_service import sync_brand_to_sheet
        await sync_brand_to_sheet(brand_name)
    except Exception:
        logger.exception(f"Failed to sync brand '{brand_name}' to eval sheet")


async def _sync_remove_brand_from_sheet_safe(brand_name: str) -> None:
    """Fire-and-forget wrapper for eval sheet sync on delete."""
    try:
        from app.modules.sync.eval_sheet_service import remove_brand_from_sheet
        await remove_brand_from_sheet(brand_name)
    except Exception:
        logger.exception(f"Failed to remove brand '{brand_name}' from eval sheet")
