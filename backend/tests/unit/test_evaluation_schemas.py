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


class TestRunCalculatorItem:
    def test_rejects_when_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            RunCalculatorItem(calculator_type="vp", status="invalid")


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
