"""Unit tests for evaluation schema Literal type enforcement."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.modules.evaluations.schemas import (
    EvaluationListItem,
    GroupedEvaluationItem,
    RunCalculatorItem,
    SaveEvaluationResponse,
    SingleCalculatorStatus,
)


class TestSingleCalculatorStatus:
    def test_rejects_when_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            SingleCalculatorStatus(
                status="hacked",
                has_result=False,
                required_files=[],
                available_files=[],
                missing_files=[],
            )

    def test_accepts_when_valid_status_ready(self) -> None:
        s = SingleCalculatorStatus(
            status="ready",
            has_result=True,
            required_files=["file.xlsx"],
            available_files=["file.xlsx"],
            missing_files=[],
        )
        assert s.status == "ready"

    def test_accepts_when_valid_status_pending(self) -> None:
        s = SingleCalculatorStatus(
            status="pending",
            has_result=False,
            required_files=["file.xlsx"],
            available_files=[],
            missing_files=["file.xlsx"],
        )
        assert s.status == "pending"


class TestRunCalculatorItem:
    def test_rejects_when_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            RunCalculatorItem(calculator_type="vp", status="invalid")

    def test_accepts_when_valid_status_success(self) -> None:
        item = RunCalculatorItem(
            calculator_type="vp", status="success", result={"score": 80}
        )
        assert item.status == "success"

    def test_accepts_when_valid_status_skipped(self) -> None:
        item = RunCalculatorItem(
            calculator_type="vp", status="skipped", reason="missing data"
        )
        assert item.status == "skipped"

    def test_accepts_when_valid_status_error(self) -> None:
        item = RunCalculatorItem(
            calculator_type="vp", status="error", reason="calc failed"
        )
        assert item.status == "error"


class TestEvaluationListItem:
    def test_rejects_when_invalid_verdict(self) -> None:
        with pytest.raises(ValidationError):
            EvaluationListItem(
                id=1,
                brand_name="Test",
                final_score=80.0,
                verdict="INVALID",
                template="fashion",
                evaluator_email="a@b.com",
                created_at=datetime.now(),
            )

    def test_rejects_when_invalid_template(self) -> None:
        with pytest.raises(ValidationError):
            EvaluationListItem(
                id=1,
                brand_name="Test",
                final_score=80.0,
                verdict="✔️",
                template="invalid_template",
                evaluator_email="a@b.com",
                created_at=datetime.now(),
            )

    def test_accepts_when_valid_types(self) -> None:
        item = EvaluationListItem(
            id=1,
            brand_name="Test",
            final_score=80.0,
            verdict="✔️",
            template="fashion",
            evaluator_email="a@b.com",
            created_at=datetime.now(),
        )
        assert item.verdict == "✔️"
        assert item.template == "fashion"

    def test_accepts_when_stock_verdict(self) -> None:
        item = EvaluationListItem(
            id=1,
            brand_name="Test",
            final_score=60.0,
            verdict="❌ Stock",
            template="fashion",
            evaluator_email="a@b.com",
            created_at=datetime.now(),
        )
        assert item.verdict == "❌ Stock"

    def test_accepts_when_non_fashion_template(self) -> None:
        item = EvaluationListItem(
            id=1,
            brand_name="Test",
            final_score=60.0,
            verdict="❌",
            template="non_fashion",
            evaluator_email="a@b.com",
            created_at=datetime.now(),
        )
        assert item.template == "non_fashion"


class TestGroupedEvaluationItem:
    def test_rejects_when_invalid_top_verdict(self) -> None:
        with pytest.raises(ValidationError):
            GroupedEvaluationItem(
                brand_id=1,
                brand_name="Test",
                evaluation_count=3,
                top_score=90.0,
                top_verdict="Bad",
                latest_date=datetime.now(),
            )

    def test_accepts_when_valid_top_verdict(self) -> None:
        item = GroupedEvaluationItem(
            brand_id=1,
            brand_name="Test",
            evaluation_count=3,
            top_score=90.0,
            top_verdict="❌ Non Mall",
            latest_date=datetime.now(),
        )
        assert item.top_verdict == "❌ Non Mall"


class TestSaveEvaluationResponse:
    def test_rejects_when_invalid_verdict(self) -> None:
        with pytest.raises(ValidationError):
            SaveEvaluationResponse(
                id=1,
                brand_id=1,
                final_score=80.0,
                verdict="invalid",
                template="fashion",
                created_at=datetime.now(),
            )

    def test_accepts_when_valid(self) -> None:
        resp = SaveEvaluationResponse(
            id=1,
            brand_id=1,
            final_score=80.0,
            verdict="❌ Opex",
            template="non_fashion",
            created_at=datetime.now(),
        )
        assert resp.verdict == "❌ Opex"
        assert resp.template == "non_fashion"
