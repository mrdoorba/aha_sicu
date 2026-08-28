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


class TestRealBenchmarkNote:
    """The Bisnis section closes with the Real Benchmark disclaimer.

    Standing policy copy, not evaluation data: it must reach both emitters, in
    the recipient's language, and only in the section the layout assigns it to.
    """

    def test_text_closes_business_section_with_the_note(self) -> None:
        out = render_email(_FIXTURE, language="id", fmt="text")
        business = out.split("👥")[0]
        assert "Real Benchmark: Real benchmark akan diambil dari omset" in business
        assert "penentu skema kerjasama." in business

    @pytest.mark.parametrize(
        ("lang", "needle"),
        [
            ("id", "Omset seller center hanya digunakan"),
            ("en", "Seller Center revenue is used solely"),
            ("th", "ยอดขายจาก Seller Center ใช้เพียงเพื่อกำหนดรูปแบบความร่วมมือ"),
        ],
    )
    def test_text_note_follows_the_recipient_language(self, lang: str, needle: str) -> None:
        assert needle in render_email(_FIXTURE, language=lang, fmt="text")

    def test_html_band_sits_in_the_business_card_only(self) -> None:
        out = render_email(_FIXTURE, language="id", fmt="html")
        # ID reports append an English copy below the divider, so the band —
        # like every other section — appears once per language copy.
        assert out.count("Omset seller center hanya digunakan") == 1
        assert out.count("Seller Center revenue is used solely") == 1

        head, _, tail = out.partition("Omset seller center hanya digunakan")
        # The nearest preceding section header is Bisnis, not another category.
        assert head.rindex("Bisnis") > head.rindex("Operasional")
        assert "Tinjauan Pengunjung" not in head[head.rindex("Bisnis"):]

    def test_html_accent_is_a_cell_not_a_one_sided_border(self) -> None:
        # Outlook's Word engine drops border-left but paints cell backgrounds.
        out = render_email(_FIXTURE, language="id", fmt="html")
        # PRIMARY_LIGHT is shared with other blocks, so anchor on the note text
        # and read backwards to the band that wraps it.
        band = out[:out.index("Omset seller center hanya digunakan")]
        assert 'width="3" style="width:3px;background-color:#325FEC' in band[-600:]
        assert "border-left" not in band[-600:]
