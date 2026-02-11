"""Calculator orchestration engine — decides when to run calculators."""

import logging
from typing import Any

from asyncpg import Connection

from app.db.queries import calculator_results as calc_queries
from app.db.queries import evaluations as eval_queries
from app.db.queries import uploads as upload_queries
from app.modules.evaluations.calculator_service import (
    run_ads_keyword_calculator,
    run_discount_calculator,
    run_top_sku_calculator,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dependency maps
# ---------------------------------------------------------------------------

# Which files each calculator requires
CALCULATOR_REQUIRED_FILES: dict[str, list[str]] = {
    "ads_keyword": ["cpc_ad_report", "keyword_report"],
    "discount": ["order_export"],
    "top_sku": ["order_export", "mass_update"],
}

# Which manual inputs each calculator requires
CALCULATOR_REQUIRED_MANUAL: dict[str, list[str]] = {
    "ads_keyword": ["total_products"],
}

# Which calculators are affected by each uploaded file type
FILE_TO_CALCULATORS: dict[str, list[str]] = {
    "cpc_ad_report": ["ads_keyword"],
    "keyword_report": ["ads_keyword"],
    "order_export": ["discount", "top_sku"],
    "mass_update": ["top_sku"],
}

# Map calculator type → runner function
_CALCULATOR_RUNNERS = {
    "ads_keyword": run_ads_keyword_calculator,
    "discount": run_discount_calculator,
    "top_sku": run_top_sku_calculator,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _has_total_products(manual_data: Any) -> bool:
    """Check if total_products (productCount) exists in manual_data."""
    if not isinstance(manual_data, dict):
        return False
    products = manual_data.get("products")
    if not isinstance(products, dict):
        return False
    return products.get("productCount") is not None


def _build_skip_reason(status_info: dict) -> str:
    """Build a human-readable skip reason from a readiness status dict."""
    parts: list[str] = []
    if status_info["missing_files"]:
        parts.append(f"Missing required files: {', '.join(status_info['missing_files'])}")
    if status_info["missing_manual"]:
        parts.append(f"Missing required manual inputs: {', '.join(status_info['missing_manual'])}")
    return "; ".join(parts) if parts else "Not ready"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def check_calculator_readiness(
    brand_id: int, conn: Connection, *, user_id: int | None = None
) -> dict[str, dict]:
    """Check which calculators are ready to run for a brand.

    Args:
        brand_id: The brand to check.
        conn: Database connection.
        user_id: When provided, check this specific user's manual data
            (used before execution to avoid readiness/execution mismatch).
            When None, check any user's manual data (general status view).

    Returns a dict keyed by calculator_type with readiness status:
    - status: "ready" or "pending"
    - has_result: whether a result already exists
    - required_files, available_files, missing_files
    - required_manual, missing_manual
    - calculated_at: timestamp of existing result or None
    """
    # Get available uploads for this brand
    uploads = await upload_queries.get_uploads_by_brand(conn, brand_id)
    available_file_types = {u["file_type"] for u in uploads}

    # Check manual data availability
    if user_id is not None:
        eval_inputs = await eval_queries.get_evaluation_inputs(conn, brand_id, user_id)
    else:
        eval_inputs = await eval_queries.get_any_evaluation_inputs(conn, brand_id)
    has_manual_total_products = _has_total_products(
        eval_inputs["manual_data"] if eval_inputs else None
    )

    # Get existing calculator results
    existing_results = await calc_queries.get_results_by_brand(conn, brand_id)
    result_map = {r["calculator_type"]: r for r in existing_results}

    statuses: dict[str, dict] = {}
    for calc_type, required_files in CALCULATOR_REQUIRED_FILES.items():
        available = [f for f in required_files if f in available_file_types]
        missing = [f for f in required_files if f not in available_file_types]

        required_manual = CALCULATOR_REQUIRED_MANUAL.get(calc_type, [])
        missing_manual: list[str] = []
        if "total_products" in required_manual and not has_manual_total_products:
            missing_manual.append("total_products")

        existing = result_map.get(calc_type)
        has_result = existing is not None
        calculated_at = existing["calculated_at"] if existing else None

        status = "ready" if not missing and not missing_manual else "pending"

        statuses[calc_type] = {
            "status": status,
            "has_result": has_result,
            "required_files": required_files,
            "required_manual": required_manual,
            "available_files": available,
            "missing_files": missing,
            "missing_manual": missing_manual,
            "calculated_at": calculated_at,
        }

    return statuses


async def run_ready_calculators(
    brand_id: int, user_id: int, conn: Connection
) -> list[dict]:
    """Run all calculators whose dependencies are satisfied.

    Returns a list of per-calculator results:
    - {calculator_type, status="success", result={...}}
    - {calculator_type, status="skipped", reason="..."}
    - {calculator_type, status="error", reason="..."}
    """
    readiness = await check_calculator_readiness(brand_id, conn, user_id=user_id)
    results: list[dict] = []

    for calc_type, status_info in readiness.items():
        if status_info["status"] != "ready":
            results.append({
                "calculator_type": calc_type,
                "status": "skipped",
                "reason": _build_skip_reason(status_info),
            })
            continue

        try:
            runner = _CALCULATOR_RUNNERS[calc_type]
            result = await runner(brand_id, user_id)
            results.append({
                "calculator_type": calc_type,
                "status": "success",
                "result": result.model_dump(mode="json"),
            })
        except Exception as e:
            logger.warning(
                "Calculator %s failed for brand %d: %s",
                calc_type, brand_id, e, exc_info=True,
            )
            results.append({
                "calculator_type": calc_type,
                "status": "error",
                "reason": f"Calculator execution failed: {calc_type}",
            })

    return results


async def run_calculators_for_upload(
    brand_id: int, file_type: str, user_id: int, conn: Connection
) -> list[dict]:
    """Run only the calculators affected by a specific file upload.

    Used by the upload pipeline for targeted auto-execute.
    """
    affected_calculators = FILE_TO_CALCULATORS.get(file_type, [])
    if not affected_calculators:
        return []

    readiness = await check_calculator_readiness(brand_id, conn, user_id=user_id)
    results: list[dict] = []

    for calc_type in affected_calculators:
        status_info = readiness.get(calc_type)
        if not status_info or status_info["status"] != "ready":
            reason = (
                _build_skip_reason(status_info)
                if status_info
                else f"Unknown calculator: {calc_type}"
            )
            results.append({
                "calculator_type": calc_type,
                "status": "skipped",
                "reason": reason,
            })
            continue

        try:
            runner = _CALCULATOR_RUNNERS[calc_type]
            result = await runner(brand_id, user_id)
            results.append({
                "calculator_type": calc_type,
                "status": "success",
                "result": result.model_dump(mode="json"),
            })
        except Exception as e:
            logger.warning(
                "Calculator %s failed for brand %d after upload: %s",
                calc_type, brand_id, e, exc_info=True,
            )
            results.append({
                "calculator_type": calc_type,
                "status": "error",
                "reason": f"Calculator execution failed: {calc_type}",
            })

    return results


async def clear_dependent_results(
    brand_id: int, file_type: str, conn: Connection
) -> int:
    """Clear calculator results that depend on a given file type.

    Used before re-running calculators after a file re-upload.
    Returns the count of deleted result rows.
    """
    affected = FILE_TO_CALCULATORS.get(file_type, [])
    if not affected:
        return 0
    return await calc_queries.delete_results_by_types(conn, brand_id, affected)
