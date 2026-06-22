"""Tests for the stateless POST /email/preview endpoint.

This endpoint renders an email body straight from a posted, in-memory
ScoringResult-shaped payload (no DB lookup) so the pre-save scoring screen can
re-render the report in any language. It reuses the single `render_email`
renderer, so its output must match the committed golden fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path

from unittest.mock import patch

import pytest

_GOLDEN_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures" / "email_golden"
_FIXTURE = json.loads((_GOLDEN_DIR / "fixture.json").read_text(encoding="utf-8"))


def _payload() -> dict:
    """Build a ScoringResult-shaped request body from the golden fixture.

    The golden fixture is stored in the renderer's evaluation-dict shape
    (`score_breakdown` + `calculator_results.scoring_summary`); the POST body
    uses the ScoringResult shape the score endpoint returns (`category_scores`
    + hoisted summary fields).
    """
    summary = _FIXTURE["calculator_results"]["scoring_summary"]
    return {
        "category_scores": _FIXTURE["score_breakdown"],
        "conclusion": summary.get("conclusion", ""),
        "conclusion_i18n": summary.get("conclusion_i18n"),
        "marketing_estimation": summary.get("marketing_estimation", ""),
        "marketing_budget": summary.get("marketing_budget", ""),
        "marketing_budget_i18n": summary.get("marketing_budget_i18n"),
        "closing_message": summary.get("closing_message", ""),
        "closing_message_i18n": summary.get("closing_message_i18n"),
        "calculator_results": _FIXTURE["calculator_results"],
        "brand_name": _FIXTURE["brand_name"],
        "period": _FIXTURE["period"],
    }


class TestPreviewPost:
    @pytest.mark.parametrize("lang", ["id", "th", "en"])
    async def test_renders_text_from_posted_result(self, client, auth_headers, lang) -> None:
        user, headers, auth_ctx = auth_headers("member")
        golden = (_GOLDEN_DIR / f"{lang}.txt").read_text(encoding="utf-8")

        with auth_ctx:
            response = client.post(
                f"/api/v1/email/preview?language={lang}&format=text",
                json=_payload(),
                headers=headers,
            )

        assert response.status_code == 200
        assert response.text == golden

    async def test_defaults_to_text_format(self, client, auth_headers) -> None:
        user, headers, auth_ctx = auth_headers("member")
        golden = (_GOLDEN_DIR / "id.txt").read_text(encoding="utf-8")

        with auth_ctx:
            response = client.post(
                "/api/v1/email/preview?language=id",
                json=_payload(),
                headers=headers,
            )

        assert response.status_code == 200
        assert response.text == golden

    async def test_renders_html_when_requested(self, client, auth_headers) -> None:
        user, headers, auth_ctx = auth_headers("member")

        with (
            auth_ctx,
            patch(
                "app.modules.email.router.asset_to_data_uri",
                side_effect=lambda name: f"cid:{name}",
            ),
        ):
            response = client.post(
                "/api/v1/email/preview?language=id&format=html",
                json=_payload(),
                headers=headers,
            )

        assert response.status_code == 200
        body = response.text
        assert body.startswith("<!DOCTYPE html>")
        # Section/category content comes through the one HTML renderer.
        assert "Kopi Kenangan" in body

    async def test_language_switch_changes_output(self, client, auth_headers) -> None:
        user, headers, auth_ctx = auth_headers("member")

        with auth_ctx:
            id_resp = client.post(
                "/api/v1/email/preview?language=id&format=text",
                json=_payload(),
                headers=headers,
            )
            th_resp = client.post(
                "/api/v1/email/preview?language=th&format=text",
                json=_payload(),
                headers=headers,
            )

        assert id_resp.status_code == 200
        assert th_resp.status_code == 200
        assert id_resp.text != th_resp.text
