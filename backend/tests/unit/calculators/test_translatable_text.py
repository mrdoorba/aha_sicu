"""Tests for TranslatableText and i18n-aware model serialization."""

from dataclasses import asdict

from app.calculators.scoring.models import TranslatableText


def test_translatable_text_serializes_to_dict():
    t = TranslatableText(key="scoring.preparationTime.pass", vars={"value": "0.56"})
    result = asdict(t)
    assert result == {"key": "scoring.preparationTime.pass", "vars": {"value": "0.56"}}


def test_translatable_text_empty_vars():
    t = TranslatableText(key="verdict.good", vars={})
    result = asdict(t)
    assert result == {"key": "verdict.good", "vars": {}}
