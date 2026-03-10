"""Unit tests for calculator orchestration engine."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.calculators.engine import (
    CALCULATOR_REGISTRY,
    FILE_TO_CALCULATORS,
    _build_skip_reason,
    _has_total_products,
    check_calculator_readiness,
    clear_dependent_results,
    run_calculators_for_upload,
    run_ready_calculators,
)


# ---------------------------------------------------------------------------
# Test data fixtures
# ---------------------------------------------------------------------------


def _make_upload(file_type: str) -> dict:
    return {"file_type": file_type, "id": 1, "brand_id": 1}


def _make_result(calculator_type: str) -> dict:
    return {
        "calculator_type": calculator_type,
        "details": {},
        "output_text": "test",
        "calculated_at": datetime(2026, 2, 11, 10, 0, tzinfo=timezone.utc),
    }


def _make_eval_inputs(has_products: bool = True) -> dict:
    manual_data = {"products": {"productCount": 80}} if has_products else {}
    return {"manual_data": manual_data}


# ---------------------------------------------------------------------------
# Dependency map completeness tests
# ---------------------------------------------------------------------------


class TestDependencyMaps:
    def test_file_to_calculator_mapping_completeness(self):
        """Every file type in required_files appears in FILE_TO_CALCULATORS."""
        all_file_types = set()
        for config in CALCULATOR_REGISTRY.values():
            all_file_types.update(config.required_files)

        for file_type in all_file_types:
            assert file_type in FILE_TO_CALCULATORS, (
                f"File type '{file_type}' is required by a calculator "
                f"but missing from FILE_TO_CALCULATORS"
            )

    def test_calculator_to_files_mapping_completeness(self):
        """Every calculator in FILE_TO_CALCULATORS appears in CALCULATOR_REGISTRY."""
        all_calculators = set()
        for calcs in FILE_TO_CALCULATORS.values():
            all_calculators.update(calcs)

        for calc in all_calculators:
            assert calc in CALCULATOR_REGISTRY, (
                f"Calculator '{calc}' in FILE_TO_CALCULATORS "
                f"but missing from CALCULATOR_REGISTRY"
            )

    def test_ads_keyword_requires_two_files_and_manual(self):
        config = CALCULATOR_REGISTRY["ads_keyword"]
        assert config.required_files == ("cpc_ad_report", "keyword_report")
        assert "total_products" in config.required_manual

    def test_discount_requires_order_export_only(self):
        config = CALCULATOR_REGISTRY["discount"]
        assert config.required_files == ("order_export",)
        assert config.required_manual == ()

    def test_top_sku_requires_two_files(self):
        config = CALCULATOR_REGISTRY["top_sku"]
        assert config.required_files == ("order_export", "mass_update")
        assert config.required_manual == ()

    def test_order_export_triggers_discount_and_top_sku(self):
        assert set(FILE_TO_CALCULATORS["order_export"]) == {"discount", "top_sku"}

    def test_mass_update_triggers_top_sku(self):
        assert FILE_TO_CALCULATORS["mass_update"] == ["top_sku"]

    def test_cpc_triggers_ads_keyword(self):
        assert FILE_TO_CALCULATORS["cpc_ad_report"] == ["ads_keyword"]

    def test_keyword_triggers_ads_keyword(self):
        assert FILE_TO_CALCULATORS["keyword_report"] == ["ads_keyword"]


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_has_total_products_valid(self):
        assert _has_total_products({"products": {"productCount": 80}}) is True

    def test_has_total_products_zero_is_valid(self):
        """productCount=0 is falsy but present, so should return True."""
        assert _has_total_products({"products": {"productCount": 0}}) is True

    def test_has_total_products_missing_products_key(self):
        assert _has_total_products({"other": "data"}) is False

    def test_has_total_products_missing_count(self):
        assert _has_total_products({"products": {}}) is False

    def test_has_total_products_none(self):
        assert _has_total_products(None) is False

    def test_has_total_products_not_dict(self):
        assert _has_total_products("string") is False

    def test_build_skip_reason_missing_files(self):
        info = {"missing_files": ["order_export"], "missing_manual": []}
        reason = _build_skip_reason(info)
        assert "order_export" in reason

    def test_build_skip_reason_missing_manual(self):
        info = {"missing_files": [], "missing_manual": ["total_products"]}
        reason = _build_skip_reason(info)
        assert "total_products" in reason

    def test_build_skip_reason_both_missing(self):
        info = {"missing_files": ["keyword_report"], "missing_manual": ["total_products"]}
        reason = _build_skip_reason(info)
        assert "keyword_report" in reason
        assert "total_products" in reason


# ---------------------------------------------------------------------------
# check_calculator_readiness tests
# ---------------------------------------------------------------------------


class TestCheckCalculatorReadiness:
    @pytest.mark.anyio
    async def test_all_files_present_is_ready(self):
        """All required files and manual data present → all calculators ready."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.upload_queries") as mock_uq,
            patch("app.calculators.engine.eval_queries") as mock_eq,
            patch("app.calculators.engine.calc_queries") as mock_cq,
        ):
            mock_uq.get_uploads_by_brand = AsyncMock(return_value=[
                _make_upload("cpc_ad_report"),
                _make_upload("keyword_report"),
                _make_upload("order_export"),
                _make_upload("mass_update"),
            ])
            mock_eq.get_evaluation_inputs = AsyncMock(
                return_value=_make_eval_inputs(has_products=True)
            )
            mock_cq.get_results_by_brand = AsyncMock(return_value=[])

            result = await check_calculator_readiness(1, mock_conn)

        assert result["ads_keyword"]["status"] == "ready"
        assert result["discount"]["status"] == "ready"
        assert result["top_sku"]["status"] == "ready"

    @pytest.mark.anyio
    async def test_missing_file_is_pending(self):
        """Missing keyword_report → ads_keyword pending."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.upload_queries") as mock_uq,
            patch("app.calculators.engine.eval_queries") as mock_eq,
            patch("app.calculators.engine.calc_queries") as mock_cq,
        ):
            mock_uq.get_uploads_by_brand = AsyncMock(return_value=[
                _make_upload("cpc_ad_report"),
                _make_upload("order_export"),
            ])
            mock_eq.get_evaluation_inputs = AsyncMock(
                return_value=_make_eval_inputs(has_products=True)
            )
            mock_cq.get_results_by_brand = AsyncMock(return_value=[])

            result = await check_calculator_readiness(1, mock_conn)

        assert result["ads_keyword"]["status"] == "pending"
        assert "keyword_report" in result["ads_keyword"]["missing_files"]
        assert result["discount"]["status"] == "ready"
        assert result["top_sku"]["status"] == "pending"
        assert "mass_update" in result["top_sku"]["missing_files"]

    @pytest.mark.anyio
    async def test_ads_keyword_missing_manual_input(self):
        """All files present but no total_products → ads_keyword pending."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.upload_queries") as mock_uq,
            patch("app.calculators.engine.eval_queries") as mock_eq,
            patch("app.calculators.engine.calc_queries") as mock_cq,
        ):
            mock_uq.get_uploads_by_brand = AsyncMock(return_value=[
                _make_upload("cpc_ad_report"),
                _make_upload("keyword_report"),
                _make_upload("order_export"),
                _make_upload("mass_update"),
            ])
            mock_eq.get_evaluation_inputs = AsyncMock(
                return_value=_make_eval_inputs(has_products=False)
            )
            mock_cq.get_results_by_brand = AsyncMock(return_value=[])

            result = await check_calculator_readiness(1, mock_conn)

        assert result["ads_keyword"]["status"] == "pending"
        assert "total_products" in result["ads_keyword"]["missing_manual"]
        assert result["discount"]["status"] == "ready"
        assert result["top_sku"]["status"] == "ready"

    @pytest.mark.anyio
    async def test_ads_keyword_all_present(self):
        """All files + manual data → ads_keyword ready."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.upload_queries") as mock_uq,
            patch("app.calculators.engine.eval_queries") as mock_eq,
            patch("app.calculators.engine.calc_queries") as mock_cq,
        ):
            mock_uq.get_uploads_by_brand = AsyncMock(return_value=[
                _make_upload("cpc_ad_report"),
                _make_upload("keyword_report"),
            ])
            mock_eq.get_evaluation_inputs = AsyncMock(
                return_value=_make_eval_inputs(has_products=True)
            )
            mock_cq.get_results_by_brand = AsyncMock(return_value=[])

            result = await check_calculator_readiness(1, mock_conn)

        assert result["ads_keyword"]["status"] == "ready"
        assert result["ads_keyword"]["missing_files"] == []
        assert result["ads_keyword"]["missing_manual"] == []

    @pytest.mark.anyio
    async def test_has_result_reflects_existing_results(self):
        """Existing calculator result → has_result=True + calculated_at."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.upload_queries") as mock_uq,
            patch("app.calculators.engine.eval_queries") as mock_eq,
            patch("app.calculators.engine.calc_queries") as mock_cq,
        ):
            mock_uq.get_uploads_by_brand = AsyncMock(return_value=[
                _make_upload("order_export"),
            ])
            mock_eq.get_evaluation_inputs = AsyncMock(return_value=None)
            mock_cq.get_results_by_brand = AsyncMock(return_value=[
                _make_result("discount"),
            ])

            result = await check_calculator_readiness(1, mock_conn)

        assert result["discount"]["has_result"] is True
        assert result["discount"]["calculated_at"] is not None
        assert result["top_sku"]["has_result"] is False
        assert result["top_sku"]["calculated_at"] is None

    @pytest.mark.anyio
    async def test_no_evaluation_inputs_at_all(self):
        """No evaluation_inputs → ads_keyword missing total_products."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.upload_queries") as mock_uq,
            patch("app.calculators.engine.eval_queries") as mock_eq,
            patch("app.calculators.engine.calc_queries") as mock_cq,
        ):
            mock_uq.get_uploads_by_brand = AsyncMock(return_value=[
                _make_upload("cpc_ad_report"),
                _make_upload("keyword_report"),
            ])
            mock_eq.get_evaluation_inputs = AsyncMock(return_value=None)
            mock_cq.get_results_by_brand = AsyncMock(return_value=[])

            result = await check_calculator_readiness(1, mock_conn)

        assert result["ads_keyword"]["status"] == "pending"
        assert "total_products" in result["ads_keyword"]["missing_manual"]



# ---------------------------------------------------------------------------
# run_ready_calculators tests
# ---------------------------------------------------------------------------


class _FakeResult:
    """Fake CalculatorResultResponse with model_dump."""

    def __init__(self, calc_type: str):
        self.calculator_type = calc_type
        self.output_text = "test output"
        self.details = {"key": "value"}
        self.calculated_at = datetime(2026, 2, 11, 10, 0, tzinfo=timezone.utc)

    def model_dump(self, mode: str = "python") -> dict:
        return {
            "calculator_type": self.calculator_type,
            "output_text": self.output_text,
            "details": self.details,
            "calculated_at": self.calculated_at.isoformat() if mode == "json" else self.calculated_at,
        }


class TestRunReadyCalculators:
    @pytest.mark.anyio
    async def test_runs_only_ready_calculators(self):
        """Only ready calculators are run; pending ones are skipped."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.check_calculator_readiness") as mock_check,
            patch("app.calculators.engine.CALCULATOR_REGISTRY") as mock_registry,
        ):
            mock_check.return_value = {
                "discount": {
                    "status": "ready",
                    "has_result": False,
                    "required_files": ["order_export"],
                    "required_manual": [],
                    "available_files": ["order_export"],
                    "missing_files": [],
                    "missing_manual": [],
                    "calculated_at": None,
                },
                "top_sku": {
                    "status": "pending",
                    "has_result": False,
                    "required_files": ["order_export", "mass_update"],
                    "required_manual": [],
                    "available_files": ["order_export"],
                    "missing_files": ["mass_update"],
                    "missing_manual": [],
                    "calculated_at": None,
                },
                "ads_keyword": {
                    "status": "pending",
                    "has_result": False,
                    "required_files": ["cpc_ad_report", "keyword_report"],
                    "required_manual": ["total_products"],
                    "available_files": [],
                    "missing_files": ["cpc_ad_report", "keyword_report"],
                    "missing_manual": ["total_products"],
                    "calculated_at": None,
                },
            }

            runner = AsyncMock(return_value=_FakeResult("discount"))
            mock_config = AsyncMock()
            mock_config.runner = runner
            mock_registry.__getitem__ = lambda self, key: mock_config

            results = await run_ready_calculators(1, mock_conn)

        success_items = [r for r in results if r["status"] == "success"]
        skipped_items = [r for r in results if r["status"] == "skipped"]

        assert len(success_items) == 1
        assert success_items[0]["calculator_type"] == "discount"
        assert len(skipped_items) == 2

    @pytest.mark.anyio
    async def test_skips_pending_calculators(self):
        """Pending calculators get status='skipped' with reason."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.check_calculator_readiness") as mock_check,
        ):
            mock_check.return_value = {
                "discount": {
                    "status": "pending",
                    "has_result": False,
                    "required_files": ["order_export"],
                    "required_manual": [],
                    "available_files": [],
                    "missing_files": ["order_export"],
                    "missing_manual": [],
                    "calculated_at": None,
                },
            }

            results = await run_ready_calculators(1, mock_conn)

        assert len(results) == 1
        assert results[0]["status"] == "skipped"
        assert "order_export" in results[0]["reason"]

    @pytest.mark.anyio
    async def test_failure_isolation(self):
        """One calculator failure doesn't prevent others from running."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.check_calculator_readiness") as mock_check,
            patch("app.calculators.engine.CALCULATOR_REGISTRY") as mock_registry,
        ):
            mock_check.return_value = {
                "discount": {
                    "status": "ready",
                    "has_result": False,
                    "required_files": ["order_export"],
                    "required_manual": [],
                    "available_files": ["order_export"],
                    "missing_files": [],
                    "missing_manual": [],
                    "calculated_at": None,
                },
                "top_sku": {
                    "status": "ready",
                    "has_result": False,
                    "required_files": ["order_export", "mass_update"],
                    "required_manual": [],
                    "available_files": ["order_export", "mass_update"],
                    "missing_files": [],
                    "missing_manual": [],
                    "calculated_at": None,
                },
            }

            failing_runner = AsyncMock(side_effect=Exception("Calculator broke"))
            success_runner = AsyncMock(return_value=_FakeResult("top_sku"))

            failing_config = AsyncMock()
            failing_config.runner = failing_runner
            success_config = AsyncMock()
            success_config.runner = success_runner

            def get_config(self, key):
                if key == "discount":
                    return failing_config
                return success_config

            mock_registry.__getitem__ = get_config

            results = await run_ready_calculators(1, mock_conn)

        statuses = {r["calculator_type"]: r["status"] for r in results}
        assert statuses["discount"] == "error"
        assert statuses["top_sku"] == "success"


# ---------------------------------------------------------------------------
# run_calculators_for_upload tests
# ---------------------------------------------------------------------------


class TestRunCalculatorsForUpload:
    @pytest.mark.anyio
    async def test_order_export_triggers_discount_and_checks_top_sku(self):
        """Uploading order_export triggers discount + checks top_sku."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.check_calculator_readiness") as mock_check,
            patch("app.calculators.engine.CALCULATOR_REGISTRY") as mock_registry,
        ):
            mock_check.return_value = {
                "discount": {
                    "status": "ready",
                    "has_result": False,
                    "required_files": ["order_export"],
                    "required_manual": [],
                    "available_files": ["order_export"],
                    "missing_files": [],
                    "missing_manual": [],
                    "calculated_at": None,
                },
                "top_sku": {
                    "status": "pending",
                    "has_result": False,
                    "required_files": ["order_export", "mass_update"],
                    "required_manual": [],
                    "available_files": ["order_export"],
                    "missing_files": ["mass_update"],
                    "missing_manual": [],
                    "calculated_at": None,
                },
            }

            runner = AsyncMock(return_value=_FakeResult("discount"))
            mock_config = AsyncMock()
            mock_config.runner = runner
            mock_registry.__getitem__ = lambda self, key: mock_config

            results = await run_calculators_for_upload(1, "order_export", mock_conn)

        assert len(results) == 2
        types = {r["calculator_type"] for r in results}
        assert types == {"discount", "top_sku"}
        discount_r = next(r for r in results if r["calculator_type"] == "discount")
        top_sku_r = next(r for r in results if r["calculator_type"] == "top_sku")
        assert discount_r["status"] == "success"
        assert top_sku_r["status"] == "skipped"

    @pytest.mark.anyio
    async def test_mass_update_triggers_only_top_sku_check(self):
        """Uploading mass_update triggers only top_sku check."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.check_calculator_readiness") as mock_check,
            patch("app.calculators.engine.CALCULATOR_REGISTRY") as mock_registry,
        ):
            mock_check.return_value = {
                "top_sku": {
                    "status": "ready",
                    "has_result": False,
                    "required_files": ["order_export", "mass_update"],
                    "required_manual": [],
                    "available_files": ["order_export", "mass_update"],
                    "missing_files": [],
                    "missing_manual": [],
                    "calculated_at": None,
                },
            }

            runner = AsyncMock(return_value=_FakeResult("top_sku"))
            mock_config = AsyncMock()
            mock_config.runner = runner
            mock_registry.__getitem__ = lambda self, key: mock_config

            results = await run_calculators_for_upload(1, "mass_update", mock_conn)

        assert len(results) == 1
        assert results[0]["calculator_type"] == "top_sku"
        assert results[0]["status"] == "success"

    @pytest.mark.anyio
    async def test_cpc_triggers_only_ads_keyword_check(self):
        """Uploading cpc_ad_report triggers only ads_keyword check."""
        mock_conn = AsyncMock()

        with (
            patch("app.calculators.engine.check_calculator_readiness") as mock_check,
        ):
            mock_check.return_value = {
                "ads_keyword": {
                    "status": "pending",
                    "has_result": False,
                    "required_files": ["cpc_ad_report", "keyword_report"],
                    "required_manual": ["total_products"],
                    "available_files": ["cpc_ad_report"],
                    "missing_files": ["keyword_report"],
                    "missing_manual": ["total_products"],
                    "calculated_at": None,
                },
            }

            results = await run_calculators_for_upload(1, "cpc_ad_report", mock_conn)

        assert len(results) == 1
        assert results[0]["calculator_type"] == "ads_keyword"
        assert results[0]["status"] == "skipped"
        assert "keyword_report" in results[0]["reason"]

    @pytest.mark.anyio
    async def test_unknown_file_type_returns_empty(self):
        """Unknown file type returns empty list."""
        mock_conn = AsyncMock()
        results = await run_calculators_for_upload(1, "unknown_type", mock_conn)
        assert results == []


# ---------------------------------------------------------------------------
# clear_dependent_results tests
# ---------------------------------------------------------------------------


class TestClearDependentResults:
    @pytest.mark.anyio
    async def test_order_export_clears_discount_and_top_sku(self):
        mock_conn = AsyncMock()

        with patch("app.calculators.engine.calc_queries") as mock_cq:
            mock_cq.delete_results_by_types = AsyncMock(return_value=2)

            deleted = await clear_dependent_results(1, "order_export", mock_conn)

        assert deleted == 2
        mock_cq.delete_results_by_types.assert_called_once_with(
            mock_conn, 1, ["discount", "top_sku"]
        )

    @pytest.mark.anyio
    async def test_mass_update_clears_top_sku_only(self):
        mock_conn = AsyncMock()

        with patch("app.calculators.engine.calc_queries") as mock_cq:
            mock_cq.delete_results_by_types = AsyncMock(return_value=1)

            deleted = await clear_dependent_results(1, "mass_update", mock_conn)

        assert deleted == 1
        mock_cq.delete_results_by_types.assert_called_once_with(
            mock_conn, 1, ["top_sku"]
        )

    @pytest.mark.anyio
    async def test_cpc_clears_ads_keyword_only(self):
        mock_conn = AsyncMock()

        with patch("app.calculators.engine.calc_queries") as mock_cq:
            mock_cq.delete_results_by_types = AsyncMock(return_value=1)

            deleted = await clear_dependent_results(1, "cpc_ad_report", mock_conn)

        assert deleted == 1
        mock_cq.delete_results_by_types.assert_called_once_with(
            mock_conn, 1, ["ads_keyword"]
        )

    @pytest.mark.anyio
    async def test_keyword_clears_ads_keyword_only(self):
        mock_conn = AsyncMock()

        with patch("app.calculators.engine.calc_queries") as mock_cq:
            mock_cq.delete_results_by_types = AsyncMock(return_value=1)

            deleted = await clear_dependent_results(1, "keyword_report", mock_conn)

        assert deleted == 1
        mock_cq.delete_results_by_types.assert_called_once_with(
            mock_conn, 1, ["ads_keyword"]
        )

    @pytest.mark.anyio
    async def test_unknown_file_type_clears_nothing(self):
        mock_conn = AsyncMock()

        deleted = await clear_dependent_results(1, "unknown_type", mock_conn)

        assert deleted == 0
