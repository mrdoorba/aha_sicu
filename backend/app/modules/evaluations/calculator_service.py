"""Calculator service — orchestrates I/O for calculator execution."""

from typing import Any

from app.calculators.ads_keyword import calculate_ads_keyword
from app.calculators.discount import calculate_discount
from app.core.exceptions import CalculatorException
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
        CalculatorException: BRAND_NOT_FOUND if brand doesn't exist.
        CalculatorException: CALC_MISSING_DATA if required uploads or inputs are missing.
        CalculatorException: CALC_EXECUTION_FAILED if calculator raises an unexpected error.
    """
    async with db.connection() as conn:
        async with conn.transaction():
            # Validate brand exists
            brand = await brand_queries.get_brand_by_id(conn, brand_id)
            if not brand:
                raise CalculatorException(
                    code="BRAND_NOT_FOUND",
                    detail="Brand not found",
                    status_code=404,
                )

            # Load CPC Ad Report
            cpc_upload = await upload_queries.get_upload_by_type(
                conn, brand_id, "cpc_ad_report"
            )
            if not cpc_upload:
                raise CalculatorException(
                    code="CALC_MISSING_DATA",
                    detail="CPC Ad Report (cpc_ad_report) has not been uploaded for this brand",
                )

            # Load Keyword/Placement Report
            keyword_upload = await upload_queries.get_upload_by_type(
                conn, brand_id, "keyword_report"
            )
            if not keyword_upload:
                raise CalculatorException(
                    code="CALC_MISSING_DATA",
                    detail="Keyword/Placement Report (keyword_report) has not been uploaded for this brand",
                )

            # Load total_products (AK1) from manual data
            eval_inputs = await eval_queries.get_evaluation_inputs(
                conn, brand_id, user_id
            )
            total_products = _extract_total_products(eval_inputs)

            # Extract and validate parsed data structure
            cpc_data = _extract_parsed_data(cpc_upload, "cpc_ad_report")
            keyword_data = _extract_parsed_data(keyword_upload, "keyword_report")

            # Run pure calculator
            try:
                result = calculate_ads_keyword(cpc_data, keyword_data, total_products)
            except Exception as e:
                raise CalculatorException(
                    code="CALC_EXECUTION_FAILED",
                    detail=f"Ads Keyword Calculator failed: {e}",
                    status_code=500,
                ) from e

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


def _extract_parsed_data(upload: dict, file_type: str) -> list[dict[str, Any]]:
    """Extract and validate parsed_data.data from a brand upload record.

    Raises:
        CalculatorException: CALC_MISSING_DATA if parsed_data structure is invalid.
    """
    parsed_data = upload.get("parsed_data")
    if not isinstance(parsed_data, dict):
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail=f"Upload '{file_type}' has invalid parsed_data structure",
        )

    data = parsed_data.get("data")
    if not isinstance(data, list):
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail=f"Upload '{file_type}' has invalid parsed_data.data structure",
        )

    return data


# Required columns per calculator file type
_REQUIRED_COLUMNS: dict[str, frozenset[str]] = {
    "order_export": frozenset({
        "No. Pesanan",
        "Nama Produk",
        "Harga Awal",
        "Harga Setelah Diskon",
        "Jumlah",
        "Voucher Ditanggung Penjual",
        "Paket Diskon",
    }),
}


def _validate_columns(
    parsed_data: dict, file_type: str
) -> None:
    """Validate that parsed_data contains all required columns for the file type.

    Raises:
        CalculatorException: CALC_MISSING_DATA if required columns are missing.
    """
    required = _REQUIRED_COLUMNS.get(file_type)
    if not required:
        return

    columns = parsed_data.get("columns")
    if not isinstance(columns, list):
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail=f"Upload '{file_type}' has no column metadata",
        )

    available = set(columns)
    missing = required - available
    if missing:
        missing_sorted = sorted(missing)
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail=f"Upload '{file_type}' is missing required columns: {', '.join(missing_sorted)}",
        )


def _extract_total_products(eval_inputs: dict | None) -> int:
    """Extract total_products from evaluation_inputs.manual_data.

    Path: manual_data → products → productCount

    Raises:
        CalculatorException: CALC_MISSING_DATA if not available.
    """
    if not eval_inputs:
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail="Manual input 'total_products' (productCount) is required "
            "for Ads Keyword Calculator",
        )

    manual_data = eval_inputs.get("manual_data")
    if not manual_data:
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail="Manual input 'total_products' (productCount) is required "
            "for Ads Keyword Calculator",
        )

    products = manual_data.get("products")
    if not products:
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail="Manual input 'total_products' (productCount) is required "
            "for Ads Keyword Calculator",
        )

    product_count = products.get("productCount")
    if product_count is None:
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail="Manual input 'total_products' (productCount) is required "
            "for Ads Keyword Calculator",
        )

    try:
        return int(product_count)
    except (TypeError, ValueError) as e:
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail="Manual input 'total_products' (productCount) must be a valid number",
        ) from e


async def run_discount_calculator(
    brand_id: int, user_id: int  # noqa: ARG001 — kept for API consistency with other calculators
) -> CalculatorResultResponse:
    """Execute the Discount Check Calculator for a brand.

    Loads order_export parsed data from brand_uploads,
    runs the pure calculator function, and stores the result.

    Args:
        brand_id: The brand to run the calculator for.
        user_id: Unused — kept for consistent interface with run_ads_keyword_calculator.

    Raises:
        CalculatorException: BRAND_NOT_FOUND if brand doesn't exist.
        CalculatorException: CALC_MISSING_DATA if order_export not uploaded or missing columns.
        CalculatorException: CALC_EXECUTION_FAILED if calculator raises an unexpected error.
    """
    async with db.connection() as conn:
        async with conn.transaction():
            # Validate brand exists
            brand = await brand_queries.get_brand_by_id(conn, brand_id)
            if not brand:
                raise CalculatorException(
                    code="BRAND_NOT_FOUND",
                    detail="Brand not found",
                    status_code=404,
                )

            # Load Order Export
            order_upload = await upload_queries.get_upload_by_type(
                conn, brand_id, "order_export"
            )
            if not order_upload:
                raise CalculatorException(
                    code="CALC_MISSING_DATA",
                    detail="Order Export (order_export) has not been uploaded for this brand",
                )

            # Extract and validate parsed data structure + required columns
            _validate_columns(order_upload.get("parsed_data", {}), "order_export")
            order_data = _extract_parsed_data(order_upload, "order_export")

            # Run pure calculator
            try:
                result = calculate_discount(order_data)
            except Exception as e:
                raise CalculatorException(
                    code="CALC_EXECUTION_FAILED",
                    detail=f"Discount Check Calculator failed: {e}",
                    status_code=500,
                ) from e

            # Store result
            row = await calc_queries.upsert_result(
                conn,
                brand_id=brand_id,
                calculator_type="discount",
                details=result.details,
                output_text=result.output_text,
            )

    return CalculatorResultResponse(
        calculator_type=row["calculator_type"],
        output_text=row["output_text"],
        details=row["details"],
        calculated_at=row["calculated_at"],
    )
