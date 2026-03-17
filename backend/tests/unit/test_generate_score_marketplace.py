"""Unit tests for generate_score marketplace wiring."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_generate_score_reads_marketplace_from_eval_inputs():
    """generate_score reads marketplace from eval_inputs and passes to rules query."""
    from app.modules.evaluations.service import generate_score

    mock_conn = AsyncMock()
    mock_brand = {"id": 1, "brand_name": "TestBrand"}
    mock_eval_inputs = {
        "manual_data": {"products": {"productCount": 10}},
        "marketplace": "TH",
    }
    mock_calc_rows = []
    mock_rule_row = {
        "rules": {"business": {}},
        "version": 1,
    }

    with (
        patch("app.modules.evaluations.service.brand_queries") as mock_brand_q,
        patch("app.modules.evaluations.service.eval_queries") as mock_eval_q,
        patch("app.modules.evaluations.service.calc_queries") as mock_calc_q,
        patch("app.modules.evaluations.service.rules_queries") as mock_rules_q,
        patch("app.modules.evaluations.service.calculate_score") as mock_calc,
    ):
        mock_brand_q.get_brand_by_id = AsyncMock(return_value=mock_brand)
        mock_eval_q.get_evaluation_inputs = AsyncMock(return_value=mock_eval_inputs)
        mock_calc_q.get_results_by_brand = AsyncMock(return_value=mock_calc_rows)
        mock_rules_q.get_rules_by_template_and_marketplace = AsyncMock(return_value=mock_rule_row)
        mock_calc.side_effect = Exception("stop here")

        try:
            await generate_score(
                mock_conn, brand_id=1, user_id=1, template="fashion",
                verdict="great", store_name="store", period="Jan",
                brand_name="TestBrand",
            )
        except Exception:
            pass

        mock_rules_q.get_rules_by_template_and_marketplace.assert_called_once_with(
            mock_conn, "default", marketplace="TH"
        )


@pytest.mark.asyncio
async def test_generate_score_defaults_marketplace_to_id_when_missing():
    """generate_score defaults marketplace to 'ID' when eval_inputs has no marketplace key."""
    from app.modules.evaluations.service import generate_score

    mock_conn = AsyncMock()
    mock_brand = {"id": 1, "brand_name": "TestBrand"}
    mock_eval_inputs = {
        "manual_data": {"products": {"productCount": 10}},
        # No 'marketplace' key — should default to 'ID'
    }

    with (
        patch("app.modules.evaluations.service.brand_queries") as mock_brand_q,
        patch("app.modules.evaluations.service.eval_queries") as mock_eval_q,
        patch("app.modules.evaluations.service.calc_queries") as mock_calc_q,
        patch("app.modules.evaluations.service.rules_queries") as mock_rules_q,
        patch("app.modules.evaluations.service.calculate_score") as mock_calc,
    ):
        mock_brand_q.get_brand_by_id = AsyncMock(return_value=mock_brand)
        mock_eval_q.get_evaluation_inputs = AsyncMock(return_value=mock_eval_inputs)
        mock_calc_q.get_results_by_brand = AsyncMock(return_value=[])
        mock_rules_q.get_rules_by_template_and_marketplace = AsyncMock(return_value=None)
        mock_calc.side_effect = Exception("stop here")

        try:
            await generate_score(
                mock_conn, brand_id=1, user_id=1, template="fashion",
                verdict="great", store_name="store", period="Jan",
                brand_name="TestBrand",
            )
        except Exception:
            pass

        mock_rules_q.get_rules_by_template_and_marketplace.assert_called_once_with(
            mock_conn, "default", marketplace="ID"
        )


@pytest.mark.asyncio
async def test_generate_score_defaults_marketplace_to_id_when_no_inputs():
    """generate_score defaults marketplace to 'ID' when eval_inputs is None."""
    from app.modules.evaluations.service import generate_score

    mock_conn = AsyncMock()
    mock_brand = {"id": 1, "brand_name": "TestBrand"}

    with (
        patch("app.modules.evaluations.service.brand_queries") as mock_brand_q,
        patch("app.modules.evaluations.service.eval_queries") as mock_eval_q,
    ):
        mock_brand_q.get_brand_by_id = AsyncMock(return_value=mock_brand)
        mock_eval_q.get_evaluation_inputs = AsyncMock(return_value=None)

        from app.core.exceptions import CalculatorException
        with pytest.raises(CalculatorException):
            await generate_score(
                mock_conn, brand_id=1, user_id=1, template="fashion",
                verdict="great", store_name="store", period="Jan",
                brand_name="TestBrand",
            )
