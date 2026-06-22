"""Golden parity tests for the consolidated email renderer.

These tests are the safety net for the layout consolidation. They guarantee:

* ``render_email(fixture, language=lang, fmt="text")`` reproduces, byte-for-byte,
  the output of the (now-deleted) frontend ``buildI18nEmailBody`` for the same
  fixture across {id, th, en}. The text goldens were generated from the real
  frontend builder using the real locale JSON (see
  ``frontend/src/utils/generateEmailGolden.test.ts``).

* ``render_email(fixture, language="id", fmt="html")`` reproduces the original
  ``render_email_html`` output (HTML golden), so the dashboard preview path is
  equally protected through the refactor.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.modules.email.layout import render_email

_GOLDEN_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures" / "email_golden"
_FIXTURE = json.loads((_GOLDEN_DIR / "fixture.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("lang", ["id", "th", "en"])
def test_text_render_matches_frontend_golden(lang: str) -> None:
    golden = (_GOLDEN_DIR / f"{lang}.txt").read_text(encoding="utf-8")
    rendered = render_email(_FIXTURE, language=lang, fmt="text")
    assert rendered == golden


def test_html_render_matches_original_golden() -> None:
    golden = (_GOLDEN_DIR / "html_id.html").read_text(encoding="utf-8")
    rendered = render_email(
        _FIXTURE,
        language="id",
        fmt="html",
        chart_src="cid:chart",
        header_src="cid:header",
        footer_src="cid:footer",
        syb_src="cid:syb",
    )
    assert rendered == golden
