"""Unit tests verifying generate_score reads marketplace from eval_inputs and fetches correct rules."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.evaluations.service import generate_score


def _mock_brand():
    return {"id": 1, "brand_name": "Test Brand", "raw_data": {}}


def _mock_eval_inputs(marketplace="ID"):
    return {
        "id": 1,
        "brand_id": 1,
        "last_edited_by": 1,
        "category_type": "fashion",
        "manual_data": {"products": {"productCount": 50}},
        "marketplace": marketplace,
        "created_at": "2026-02-05",
        "updated_at": "2026-02-05",
    }


def _mock_rule_row(marketplace="ID"):
    threshold = 100_000_000 if marketplace == "ID" else 190_000
    return {
        "id": 1,
        "template": "default",
        "marketplace": marketplace,
        "rules": {"business": {"six_month_avg_threshold": {"threshold": threshold}}},
        "version": 1,
        "updated_by": None,
        "updated_at": "2026-02-12",
    }


def _mock_scoring_result():
    mock_result = MagicMock()
    mock_result.total_score = 75.0
    mock_result.category_scores = []
    mock_result.verdict = "✔️"
    mock_result.conclusion = "Good"
    mock_result.marketing_estimation = ""
    mock_result.marketing_percentage = ""
    mock_result.marketing_budget = ""
    mock_result.closing_message = ""
    mock_result.email_subject = ""
    mock_result.email_body = ""
    mock_result.template = "default"
    mock_result.rule_version = 1
    mock_result.conclusion_i18n = None
    mock_result.marketing_budget_i18n = None
    mock_result.closing_message_i18n = None
    mock_result.email_subject_i18n = None
    return mock_result


@pytest.mark.asyncio
async def test_generate_score_reads_marketplace_from_eval_inputs():
    """generate_score reads marketplace from eval_inputs and passes to rules query."""
    conn = AsyncMock()

    with (
        patch("app.modules.evaluations.service.brand_queries") as mock_bq,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
        patch("app.modules.evaluations.service.calc_queries") as mock_cq,
        patch("app.modules.evaluations.service.rules_queries") as mock_rq,
        patch("app.modules.evaluations.service.calculate_score") as mock_calc,
    ):
        mock_bq.get_brand_by_id = AsyncMock(return_value=_mock_brand())
        mock_eq.get_evaluation_inputs = AsyncMock(return_value=_mock_eval_inputs("TH"))
        mock_cq.get_results_by_brand = AsyncMock(return_value=[])
        mock_rq.get_rules_by_template_and_marketplace = AsyncMock(return_value=_mock_rule_row("TH"))
        mock_calc.return_value = _mock_scoring_result()

        await generate_score(
            conn, brand_id=1, user_id=1, template="default",
            verdict="✔️", store_name="Test", period="Q1",
            brand_name="Test Brand",
        )

        # Verify rules query was called with marketplace='TH'
        mock_rq.get_rules_by_template_and_marketplace.assert_called_once_with(
            conn, "default", marketplace="TH"
        )


@pytest.mark.asyncio
async def test_generate_score_defaults_marketplace_to_id():
    """generate_score defaults marketplace to 'ID' when eval_inputs has no marketplace field."""
    conn = AsyncMock()

    with (
        patch("app.modules.evaluations.service.brand_queries") as mock_bq,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
        patch("app.modules.evaluations.service.calc_queries") as mock_cq,
        patch("app.modules.evaluations.service.rules_queries") as mock_rq,
        patch("app.modules.evaluations.service.calculate_score") as mock_calc,
    ):
        # eval_inputs WITHOUT marketplace field — simulate pre-migration rows
        old_inputs = {
            "id": 1, "brand_id": 1, "last_edited_by": 1,
            "category_type": "fashion",
            "manual_data": {"products": {"productCount": 50}},
            "created_at": "2026-02-05", "updated_at": "2026-02-05",
        }
        mock_bq.get_brand_by_id = AsyncMock(return_value=_mock_brand())
        mock_eq.get_evaluation_inputs = AsyncMock(return_value=old_inputs)
        mock_cq.get_results_by_brand = AsyncMock(return_value=[])
        mock_rq.get_rules_by_template_and_marketplace = AsyncMock(return_value=_mock_rule_row("ID"))
        mock_calc.return_value = _mock_scoring_result()

        await generate_score(
            conn, brand_id=1, user_id=1, template="default",
            verdict="✔️", store_name="Test", period="Q1",
            brand_name="Test Brand",
        )

        # Verify fallback to 'ID' marketplace
        mock_rq.get_rules_by_template_and_marketplace.assert_called_once_with(
            conn, "default", marketplace="ID"
        )


@pytest.mark.asyncio
async def test_generate_score_passes_correct_rules_to_calculator():
    """generate_score passes the THB rules (not ID rules) to calculate_score when marketplace=TH."""
    conn = AsyncMock()

    with (
        patch("app.modules.evaluations.service.brand_queries") as mock_bq,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
        patch("app.modules.evaluations.service.calc_queries") as mock_cq,
        patch("app.modules.evaluations.service.rules_queries") as mock_rq,
        patch("app.modules.evaluations.service.calculate_score") as mock_calc,
    ):
        th_rules = {"business": {"six_month_avg_threshold": {"threshold": 190000}}}
        mock_bq.get_brand_by_id = AsyncMock(return_value=_mock_brand())
        mock_eq.get_evaluation_inputs = AsyncMock(return_value=_mock_eval_inputs("TH"))
        mock_cq.get_results_by_brand = AsyncMock(return_value=[])
        mock_rq.get_rules_by_template_and_marketplace = AsyncMock(return_value={
            "id": 2, "template": "default", "marketplace": "TH",
            "rules": th_rules, "version": 1,
            "updated_by": None, "updated_at": "2026-02-12",
        })
        mock_calc.return_value = _mock_scoring_result()

        await generate_score(
            conn, brand_id=1, user_id=1, template="default",
            verdict="✔️", store_name="Test", period="Q1",
            brand_name="Test Brand",
        )

        # Verify calculate_score received the THB rules, not ID rules
        call_kwargs = mock_calc.call_args[1]
        assert call_kwargs["rules"] == th_rules


@pytest.mark.asyncio
async def test_generate_score_passes_marketplace_to_calculate_score():
    """generate_score passes marketplace='TH' to calculate_score."""
    conn = AsyncMock()

    with (
        patch("app.modules.evaluations.service.brand_queries") as mock_bq,
        patch("app.modules.evaluations.service.eval_queries") as mock_eq,
        patch("app.modules.evaluations.service.calc_queries") as mock_cq,
        patch("app.modules.evaluations.service.rules_queries") as mock_rq,
        patch("app.modules.evaluations.service.calculate_score") as mock_calc,
    ):
        mock_bq.get_brand_by_id = AsyncMock(return_value=_mock_brand())
        mock_eq.get_evaluation_inputs = AsyncMock(return_value=_mock_eval_inputs("TH"))
        mock_cq.get_results_by_brand = AsyncMock(return_value=[])
        mock_rq.get_rules_by_template_and_marketplace = AsyncMock(return_value=_mock_rule_row("TH"))
        mock_calc.return_value = _mock_scoring_result()

        await generate_score(
            conn, brand_id=1, user_id=1, template="default",
            verdict="✔️", store_name="Test", period="Q1",
            brand_name="Test Brand",
        )

        # Verify calculate_score was called with marketplace='TH'
        mock_calc.assert_called_once()
        call_kwargs = mock_calc.call_args[1]
        assert call_kwargs.get("marketplace") == "TH"
