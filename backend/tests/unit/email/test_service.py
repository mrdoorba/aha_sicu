"""Tests for email service: composition, SendGrid send, CID images."""

import base64
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.exceptions import AppException
from app.modules.email.service import (
    _build_sendgrid_payload,
    _decode_chart_image,
    _load_asset,
    _strip_base64_prefix,
    send_evaluation_email,
    sendgrid_send,
)


# ---------------------------------------------------------------------------
# _load_asset
# ---------------------------------------------------------------------------
class TestLoadAsset:
    """Test loading images from the assets directory."""

    def test_loads_header_image(self) -> None:
        data = _load_asset("aha-e-mail-header-2026.png")
        assert isinstance(data, bytes)
        assert len(data) > 0
        # Should start with PNG signature
        assert data[:4] == b"\x89PNG"

    def test_loads_footer_image(self) -> None:
        data = _load_asset("aha-e-mail-footer-2026.png")
        assert isinstance(data, bytes)
        assert len(data) > 0


# ---------------------------------------------------------------------------
# _strip_base64_prefix / _decode_chart_image
# ---------------------------------------------------------------------------
class TestBase64Handling:
    """Test base64 prefix stripping and chart image decoding."""

    def test_strip_data_uri_prefix(self) -> None:
        raw = "data:image/png;base64,iVBORw0KGgo="
        assert _strip_base64_prefix(raw) == "iVBORw0KGgo="

    def test_strip_no_prefix(self) -> None:
        raw = "iVBORw0KGgo="
        assert _strip_base64_prefix(raw) == "iVBORw0KGgo="

    def test_decode_valid_base64(self, sample_base64_png: str) -> None:
        result = _decode_chart_image(sample_base64_png)
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_decode_with_data_uri_prefix(self, sample_base64_png: str) -> None:
        prefixed = f"data:image/png;base64,{sample_base64_png}"
        result = _decode_chart_image(prefixed)
        assert isinstance(result, bytes)

    def test_decode_invalid_base64_raises(self) -> None:
        with pytest.raises(AppException) as exc_info:
            _decode_chart_image("!!!not-valid-base64!!!")
        assert exc_info.value.code == "INVALID_CHART_IMAGE"
        assert exc_info.value.status_code == 422


# ---------------------------------------------------------------------------
# _build_sendgrid_payload
# ---------------------------------------------------------------------------
class TestBuildSendGridPayload:
    """Test SendGrid API payload construction with CID images."""

    _PNG = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    def _build_simple_payload(self) -> dict:
        return _build_sendgrid_payload(
            subject="Test Subject",
            from_name="AHA Commerce",
            from_email="noreply@aha.com",
            to_emails=["recipient@example.com"],
            html_content="<html><body>Hello</body></html>",
            text_content="Hello",
            images=[
                (self._PNG, "png", "header-cid"),
                (self._PNG, "png", "footer-cid"),
                (self._PNG, "png", "chart-cid"),
            ],
        )

    def test_subject_set(self) -> None:
        payload = self._build_simple_payload()
        assert payload["subject"] == "Test Subject"

    def test_from_fields(self) -> None:
        payload = self._build_simple_payload()
        assert payload["from"]["email"] == "noreply@aha.com"
        assert payload["from"]["name"] == "AHA Commerce"

    def test_to_recipients(self) -> None:
        payload = self._build_simple_payload()
        assert payload["personalizations"][0]["to"] == [{"email": "recipient@example.com"}]

    def test_multiple_to_recipients(self) -> None:
        payload = _build_sendgrid_payload(
            subject="Test",
            from_name="AHA",
            from_email="noreply@aha.com",
            to_emails=["a@example.com", "b@example.com", "c@example.com"],
            html_content="<p>Hi</p>",
            text_content="Hi",
            images=[],
        )
        to_list = payload["personalizations"][0]["to"]
        assert len(to_list) == 3
        assert {"email": "a@example.com"} in to_list

    def test_cc_set_when_provided(self) -> None:
        payload = _build_sendgrid_payload(
            subject="Test",
            from_name="AHA",
            from_email="noreply@aha.com",
            to_emails=["a@example.com"],
            cc_emails=["cc1@example.com", "cc2@example.com"],
            html_content="<p>Hi</p>",
            text_content="Hi",
            images=[],
        )
        cc_list = payload["personalizations"][0]["cc"]
        assert len(cc_list) == 2

    def test_bcc_set_when_provided(self) -> None:
        payload = _build_sendgrid_payload(
            subject="Test",
            from_name="AHA",
            from_email="noreply@aha.com",
            to_emails=["a@example.com"],
            bcc_emails=["bcc@example.com"],
            html_content="<p>Hi</p>",
            text_content="Hi",
            images=[],
        )
        bcc_list = payload["personalizations"][0]["bcc"]
        assert bcc_list == [{"email": "bcc@example.com"}]

    def test_no_cc_when_empty(self) -> None:
        payload = self._build_simple_payload()
        assert "cc" not in payload["personalizations"][0]

    def test_has_html_and_text_content(self) -> None:
        payload = self._build_simple_payload()
        content_types = [c["type"] for c in payload["content"]]
        assert "text/plain" in content_types
        assert "text/html" in content_types

    def test_attaches_three_inline_images(self) -> None:
        payload = self._build_simple_payload()
        assert len(payload["attachments"]) == 3

    def test_attachments_have_inline_disposition(self) -> None:
        payload = self._build_simple_payload()
        for att in payload["attachments"]:
            assert att["disposition"] == "inline"
            assert att["type"] == "image/png"
            assert att["content_id"] in ("header-cid", "footer-cid", "chart-cid")

    def test_attachment_content_is_base64(self) -> None:
        payload = self._build_simple_payload()
        for att in payload["attachments"]:
            decoded = base64.b64decode(att["content"])
            assert decoded[:4] == b"\x89PNG"

    def test_no_attachments_when_no_images(self) -> None:
        payload = _build_sendgrid_payload(
            subject="Test",
            from_name="AHA",
            from_email="noreply@aha.com",
            to_emails=["a@example.com"],
            html_content="<p>Hi</p>",
            text_content="Hi",
            images=[],
        )
        assert "attachments" not in payload


# ---------------------------------------------------------------------------
# sendgrid_send
# ---------------------------------------------------------------------------
class TestSendGridSend:
    """Test SendGrid API call via httpx."""

    async def test_returns_message_id_on_success(self) -> None:
        mock_response = httpx.Response(
            202,
            headers={"X-Message-Id": "sg-msg-123"},
            request=httpx.Request("POST", "https://api.sendgrid.com/v3/mail/send"),
        )

        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("app.modules.email.service.settings") as mock_settings:
                mock_settings.sendgrid_api_key = "SG.test-key"

                result = await sendgrid_send({"test": "payload"})

        assert result == "sg-msg-123"
        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args
        assert "Bearer SG.test-key" in call_kwargs[1]["headers"]["Authorization"]

    async def test_raises_auth_error_on_401(self) -> None:
        mock_response = httpx.Response(
            401,
            request=httpx.Request("POST", "https://api.sendgrid.com/v3/mail/send"),
        )

        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("app.modules.email.service.settings") as mock_settings:
                mock_settings.sendgrid_api_key = "SG.bad-key"

                with pytest.raises(AppException) as exc_info:
                    await sendgrid_send({"test": "payload"})

        assert exc_info.value.code == "SENDGRID_AUTH_ERROR"
        assert exc_info.value.status_code == 502

    async def test_raises_rate_limit_on_429(self) -> None:
        mock_response = httpx.Response(
            429,
            request=httpx.Request("POST", "https://api.sendgrid.com/v3/mail/send"),
        )

        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("app.modules.email.service.settings") as mock_settings:
                mock_settings.sendgrid_api_key = "SG.test-key"

                with pytest.raises(AppException) as exc_info:
                    await sendgrid_send({"test": "payload"})

        assert exc_info.value.code == "SENDGRID_RATE_LIMIT"
        assert exc_info.value.status_code == 429

    async def test_raises_api_error_on_500(self) -> None:
        mock_response = httpx.Response(
            500,
            text="Internal Server Error",
            request=httpx.Request("POST", "https://api.sendgrid.com/v3/mail/send"),
        )

        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("app.modules.email.service.settings") as mock_settings:
                mock_settings.sendgrid_api_key = "SG.test-key"

                with pytest.raises(AppException) as exc_info:
                    await sendgrid_send({"test": "payload"})

        assert exc_info.value.code == "SENDGRID_API_ERROR"
        assert exc_info.value.status_code == 502

    async def test_raises_timeout_error(self) -> None:
        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.TimeoutException("timed out")
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("app.modules.email.service.settings") as mock_settings:
                mock_settings.sendgrid_api_key = "SG.test-key"

                with pytest.raises(AppException) as exc_info:
                    await sendgrid_send({"test": "payload"})

        assert exc_info.value.code == "SENDGRID_TIMEOUT"
        assert exc_info.value.status_code == 504

    async def test_raises_connection_error(self) -> None:
        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.ConnectError("connection refused")
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("app.modules.email.service.settings") as mock_settings:
                mock_settings.sendgrid_api_key = "SG.test-key"

                with pytest.raises(AppException) as exc_info:
                    await sendgrid_send({"test": "payload"})

        assert exc_info.value.code == "SENDGRID_CONNECTION_ERROR"
        assert exc_info.value.status_code == 502


# ---------------------------------------------------------------------------
# send_evaluation_email
# ---------------------------------------------------------------------------
class TestSendEvaluationEmail:
    """Test the main orchestration function."""

    @pytest.fixture
    def mock_render_fn(self) -> MagicMock:
        fn = MagicMock()
        fn.return_value = "<html><body>Rendered email</body></html>"
        return fn

    async def test_generates_default_subject(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.email_enabled = False
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"

            await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
            )

        # Check the render function received chart_src, header_src, footer_src
        call_kwargs = mock_render_fn.call_args[1]
        assert "chart_src" in call_kwargs
        assert "header_src" in call_kwargs
        assert "footer_src" in call_kwargs

    async def test_uses_custom_subject(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.email_enabled = False
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                subject="Custom Subject",
                render_html_fn=mock_render_fn,
            )

        assert result.success is True

    async def test_debug_mode_writes_file(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.email_enabled = False
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
            )

        assert result.success is True
        assert result.message_id == "debug-file"
        assert result.recipients == ["test@example.com"]
        # Check file was written
        preview_path = Path(f"/tmp/email_preview_{sample_evaluation_data['id']}.html")
        assert preview_path.exists()
        content = preview_path.read_text()
        assert "Rendered email" in content

    async def test_sends_via_sendgrid_when_enabled(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        with (
            patch("app.modules.email.service.settings") as mock_settings,
            patch("app.modules.email.service.sendgrid_send") as mock_send,
        ):
            mock_settings.email_enabled = True
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"
            mock_send.return_value = "sg-msg-123"

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
            )

        assert result.success is True
        assert result.message_id == "sg-msg-123"
        mock_send.assert_called_once()

    async def test_subject_auto_generated_format(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        """Subject should be 'Laporan Evaluasi Brand: [Brand] - [Period]'."""
        with (
            patch("app.modules.email.service.settings") as mock_settings,
            patch("app.modules.email.service.sendgrid_send") as mock_send,
            patch("app.modules.email.service._build_sendgrid_payload") as mock_build,
        ):
            mock_settings.email_enabled = True
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"
            mock_send.return_value = "sg-msg-123"
            mock_build.return_value = {"test": "payload"}

            await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
            )

        call_kwargs = mock_build.call_args[1]
        expected_subject = "Laporan Evaluasi Brand: Kopi Kenangan - Januari 2026"
        assert call_kwargs["subject"] == expected_subject

    async def test_passes_note_to_render_fn(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.email_enabled = False
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"

            await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
                note="My custom note",
            )

        call_kwargs = mock_render_fn.call_args[1]
        assert call_kwargs["note"] == "My custom note"

    async def test_multi_recipient_with_cc_bcc(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        with (
            patch("app.modules.email.service.settings") as mock_settings,
            patch("app.modules.email.service.sendgrid_send") as mock_send,
            patch("app.modules.email.service._build_sendgrid_payload") as mock_build,
        ):
            mock_settings.email_enabled = True
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"
            mock_send.return_value = "sg-msg-123"
            mock_build.return_value = {"test": "payload"}

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["a@example.com", "b@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
                cc=["cc@example.com"],
                bcc=["bcc@example.com"],
            )

        build_kwargs = mock_build.call_args[1]
        assert build_kwargs["to_emails"] == ["a@example.com", "b@example.com"]
        assert build_kwargs["cc_emails"] == ["cc@example.com"]
        assert build_kwargs["bcc_emails"] == ["bcc@example.com"]

        assert result.recipients == ["a@example.com", "b@example.com"]
