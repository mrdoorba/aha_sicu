"""Calculator service — orchestrates I/O for calculator execution."""

from typing import Any

from app.calculators.ads_keyword import calculate_ads_keyword
from app.core.exceptions import AppException
from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.db.queries import calculator_results as calc_queries
from app.db.queries import evaluations as eval_queries
from app.db.queries import uploads as upload_queries
from app.modules.evaluations.schemas import CalculatorResultResponse


async def run_ads_keyword_calculator(
    brand_id: int, user_id: int
) -> CalculatorResultResponse:
    """Execute the Ads Keyword Calculator for a brand.

    Loads required data from brand_uploads and evaluation_inputs,
    runs the pure calculator function, and stores the result.

    Raises:
        AppException: BRAND_NOT_FOUND if brand doesn't exist.
        AppException: CALC_MISSING_DATA if required uploads or inputs are missing.
    """
    async with db.connection() as conn:
        async with conn.transaction():
            # Validate brand exists
            brand = await brand_queries.get_brand_by_id(conn, brand_id)
            if not brand:
                raise AppException(
                    code="BRAND_NOT_FOUND",
                    detail="Brand not found",
                    status_code=404,
                )

            # Load CPC Ad Report
            cpc_upload = await upload_queries.get_upload_by_type(
                conn, brand_id, "cpc_ad_report"
            )
            if not cpc_upload:
                raise AppException(
                    code="CALC_MISSING_DATA",
                    detail="CPC Ad Report (cpc_ad_report) has not been uploaded for this brand",
                )

            # Load Keyword/Placement Report
            keyword_upload = await upload_queries.get_upload_by_type(
                conn, brand_id, "keyword_report"
            )
            if not keyword_upload:
                raise AppException(
                    code="CALC_MISSING_DATA",
                    detail="Keyword/Placement Report (keyword_report) has not been uploaded for this brand",
                )

            # Load total_products (AK1) from manual data
            eval_inputs = await eval_queries.get_evaluation_inputs(
                conn, brand_id, user_id
            )
            total_products = _extract_total_products(eval_inputs)

            # Extract parsed data
            cpc_data: list[dict[str, Any]] = cpc_upload["parsed_data"]["data"]
            keyword_data: list[dict[str, Any]] = keyword_upload["parsed_data"]["data"]

            # Run pure calculator
            result = calculate_ads_keyword(cpc_data, keyword_data, total_products)

            # Store result
            row = await calc_queries.upsert_result(
                conn,
                brand_id=brand_id,
                calculator_type="ads_keyword",
                details=result.details,
                output_text=result.output_text,
            )

    return CalculatorResultResponse(
        calculator_type=row["calculator_type"],
        output_text=row["output_text"],
        details=row["details"],
        calculated_at=row["calculated_at"],
    )


def _extract_total_products(eval_inputs: dict | None) -> int:
    """Extract total_products from evaluation_inputs.manual_data.

    Path: manual_data → products → productCount

    Raises:
        AppException: CALC_MISSING_DATA if not available.
    """
    if not eval_inputs:
        raise AppException(
            code="CALC_MISSING_DATA",
            detail="Manual input 'total_products' (productCount) is required "
            "for Ads Keyword Calculator",
        )

    manual_data = eval_inputs.get("manual_data")
    if not manual_data:
        raise AppException(
            code="CALC_MISSING_DATA",
            detail="Manual input 'total_products' (productCount) is required "
            "for Ads Keyword Calculator",
        )

    products = manual_data.get("products")
    if not products:
        raise AppException(
            code="CALC_MISSING_DATA",
            detail="Manual input 'total_products' (productCount) is required "
            "for Ads Keyword Calculator",
        )

    product_count = products.get("productCount")
    if product_count is None:
        raise AppException(
            code="CALC_MISSING_DATA",
            detail="Manual input 'total_products' (productCount) is required "
            "for Ads Keyword Calculator",
        )

    try:
        return int(product_count)
    except (TypeError, ValueError) as e:
        raise AppException(
            code="CALC_MISSING_DATA",
            detail="Manual input 'total_products' (productCount) must be a valid number",
        ) from e
