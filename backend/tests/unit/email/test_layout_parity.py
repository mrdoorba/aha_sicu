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

from app.modules.email.layout import render_email, render_plain_email_message

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


class TestPlainMessagePicEmail:
    """The [EMAIL TO: ...] line must reflect the address actually sent."""

    def test_uses_supplied_pic_email(self) -> None:
        # User-edited PIC list (comma-separated) wins over the stored brand email.
        out = render_plain_email_message(
            {**_FIXTURE, "brand_raw_data": {"email": "stored@brand.com"}},
            language="id",
            pic_email="a@primaku.com, b@primaku.com",
        )
        assert out.startswith("[EMAIL TO: a@primaku.com, b@primaku.com]")

    def test_falls_back_to_stored_email_when_omitted(self) -> None:
        out = render_plain_email_message(
            {**_FIXTURE, "brand_raw_data": {"email": "stored@brand.com"}},
            language="id",
        )
        assert out.startswith("[EMAIL TO: stored@brand.com]")

    def test_empty_when_neither_present(self) -> None:
        # The original bug: blank stored email and no override → empty line.
        out = render_plain_email_message(
            {**_FIXTURE, "brand_raw_data": {}}, language="id"
        )
        assert out.startswith("[EMAIL TO: ]")
