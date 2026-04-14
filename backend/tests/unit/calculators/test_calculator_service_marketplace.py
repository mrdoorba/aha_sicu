"""Tests for marketplace wiring in calculator_service.

Verifies that run_discount_calculator and run_top_sku_calculator
read marketplace from evaluation_inputs and pass it through to the
pure calculator functions.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

MODULE = "app.modules.evaluations.calculator_service"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_brand() -> dict:
    return {"id": 1, "name": "Test Brand"}


def _make_upload(file_type: str) -> dict:
    return {
        "id": 1,
        "brand_id": 1,
        "file_type": file_type,
        "parsed_data": {
            "columns": [
                "No. Pesanan",
                "Nama Produk",
                "Harga Awal",
                "Harga Setelah Diskon",
                "Jumlah",
                "Diskon Dari Penjual",
                "Voucher Ditanggung Penjual",
                "Paket Diskon (Diskon dari Penjual)",
                "Nomor Referensi SKU",
                "Nama Variasi",
                "Jumlah Produk di Pesan",
                "Cashback Koin",
                "Diskon Dari Shopee",
                "Kode Variasi",
            ],
            "data": [],
        },
    }


def _make_eval_inputs(marketplace: str = "TH") -> dict:
    return {
        "marketplace": marketplace,
        "manual_data": {
            "business": {"salesMonth0": 12_500_000},
            "promoTools": {"komisiProgramAfiliasi": 625_000},
        },
    }


def _make_result_row() -> dict:
    return {
        "calculator_type": "discount",
        "output_text": "ok",
        "details": {},
        "calculated_at": datetime(2026, 3, 17, tzinfo=timezone.utc),
    }


def _mock_db():
    """Build a mock db with connection → transaction async context managers."""
    mock_conn = AsyncMock()

    @asynccontextmanager
    async def _mock_transaction():
        yield

    mock_conn.transaction = _mock_transaction

    mock_db = MagicMock()
    mock_db.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_db.connection.return_value.__aexit__ = AsyncMock(return_value=False)
    return mock_db, mock_conn


# ---------------------------------------------------------------------------
# Discount calculator — marketplace wiring
# ---------------------------------------------------------------------------


class TestDiscountCalculatorMarketplace:

    async def test_passes_marketplace_th_when_eval_inputs_has_th(self):
        """should pass marketplace='TH' to calculate_discount when eval_inputs has TH"""
        mock_db_obj, _mock_conn = _mock_db()
        calc_result = MagicMock()
        calc_result.details = {}
        calc_result.output_text = "ok"

        with (
            patch(f"{MODULE}.db", mock_db_obj),
            patch(f"{MODULE}.brand_queries") as mock_bq,
            patch(f"{MODULE}.upload_queries") as mock_uq,
            patch(f"{MODULE}.eval_queries") as mock_eq,
            patch(f"{MODULE}.calc_queries") as mock_cq,
            patch(f"{MODULE}.calculate_discount") as mock_calc,
        ):
            mock_bq.get_brand_by_id = AsyncMock(return_value=_make_brand())
            mock_uq.get_upload_by_type = AsyncMock(
                return_value=_make_upload("order_export")
            )
            mock_eq.get_evaluation_inputs = AsyncMock(
                return_value=_make_eval_inputs("TH")
            )
            mock_cq.upsert_result = AsyncMock(return_value=_make_result_row())
            mock_calc.return_value = calc_result

            from app.modules.evaluations.calculator_service import (
                run_discount_calculator,
            )

            await run_discount_calculator(brand_id=1)

            mock_calc.assert_called_once()
            _, kwargs = mock_calc.call_args
            assert kwargs["marketplace"] == "TH"
            assert kwargs["current_month_revenue"] == 12_500_000
            assert kwargs["affiliate_commission"] == 625_000


    async def test_defaults_to_id_when_eval_inputs_is_none(self):
        """should pass marketplace='ID' to calculate_discount when eval_inputs is None"""
        mock_db_obj, _mock_conn = _mock_db()
        calc_result = MagicMock()
        calc_result.details = {}
        calc_result.output_text = "ok"

        with (
            patch(f"{MODULE}.db", mock_db_obj),
            patch(f"{MODULE}.brand_queries") as mock_bq,
            patch(f"{MODULE}.upload_queries") as mock_uq,
            patch(f"{MODULE}.eval_queries") as mock_eq,
            patch(f"{MODULE}.calc_queries") as mock_cq,
            patch(f"{MODULE}.calculate_discount") as mock_calc,
        ):
            mock_bq.get_brand_by_id = AsyncMock(return_value=_make_brand())
            mock_uq.get_upload_by_type = AsyncMock(
                return_value=_make_upload("order_export")
            )
            mock_eq.get_evaluation_inputs = AsyncMock(return_value=None)
            mock_cq.upsert_result = AsyncMock(return_value=_make_result_row())
            mock_calc.return_value = calc_result

            from app.modules.evaluations.calculator_service import (
                run_discount_calculator,
            )

            await run_discount_calculator(brand_id=1)

            mock_calc.assert_called_once()
            _, kwargs = mock_calc.call_args
            assert kwargs["marketplace"] == "ID"
            assert kwargs["current_month_revenue"] is None
            assert kwargs["affiliate_commission"] is None


# ---------------------------------------------------------------------------
# Top SKU calculator — marketplace wiring
# ---------------------------------------------------------------------------


class TestTopSkuCalculatorMarketplace:

    async def test_passes_marketplace_th_when_eval_inputs_has_th(self):
        """should pass marketplace='TH' to calculate_top_sku when eval_inputs has TH"""
        mock_db_obj, _mock_conn = _mock_db()
        calc_result = MagicMock()
        calc_result.details = {}
        calc_result.output_text = "ok"
        result_row = _make_result_row()
        result_row["calculator_type"] = "top_sku"

        with (
            patch(f"{MODULE}.db", mock_db_obj),
            patch(f"{MODULE}.brand_queries") as mock_bq,
            patch(f"{MODULE}.upload_queries") as mock_uq,
            patch(f"{MODULE}.eval_queries") as mock_eq,
            patch(f"{MODULE}.calc_queries") as mock_cq,
            patch(f"{MODULE}.calculate_top_sku") as mock_calc,
        ):
            mock_bq.get_brand_by_id = AsyncMock(return_value=_make_brand())
            # get_upload_by_type is called twice: order_export then mass_update
            mock_uq.get_upload_by_type = AsyncMock(
                side_effect=[
                    _make_upload("order_export"),
                    _make_upload("mass_update"),
                ]
            )
            mock_eq.get_evaluation_inputs = AsyncMock(
                return_value=_make_eval_inputs("TH")
            )
            mock_cq.upsert_result = AsyncMock(return_value=result_row)
            mock_calc.return_value = calc_result

            from app.modules.evaluations.calculator_service import (
                run_top_sku_calculator,
            )

            await run_top_sku_calculator(brand_id=1)

            mock_calc.assert_called_once()
            _, kwargs = mock_calc.call_args
            assert kwargs["marketplace"] == "TH"


    async def test_defaults_to_id_when_eval_inputs_is_none(self):
        """should pass marketplace='ID' to calculate_top_sku when eval_inputs is None"""
        mock_db_obj, _mock_conn = _mock_db()
        calc_result = MagicMock()
        calc_result.details = {}
        calc_result.output_text = "ok"
        result_row = _make_result_row()
        result_row["calculator_type"] = "top_sku"

        with (
            patch(f"{MODULE}.db", mock_db_obj),
            patch(f"{MODULE}.brand_queries") as mock_bq,
            patch(f"{MODULE}.upload_queries") as mock_uq,
            patch(f"{MODULE}.eval_queries") as mock_eq,
            patch(f"{MODULE}.calc_queries") as mock_cq,
            patch(f"{MODULE}.calculate_top_sku") as mock_calc,
        ):
            mock_bq.get_brand_by_id = AsyncMock(return_value=_make_brand())
            mock_uq.get_upload_by_type = AsyncMock(
                side_effect=[
                    _make_upload("order_export"),
                    _make_upload("mass_update"),
                ]
            )
            mock_eq.get_evaluation_inputs = AsyncMock(return_value=None)
            mock_cq.upsert_result = AsyncMock(return_value=result_row)
            mock_calc.return_value = calc_result

            from app.modules.evaluations.calculator_service import (
                run_top_sku_calculator,
            )

            await run_top_sku_calculator(brand_id=1)

            mock_calc.assert_called_once()
            _, kwargs = mock_calc.call_args
            assert kwargs["marketplace"] == "ID"
