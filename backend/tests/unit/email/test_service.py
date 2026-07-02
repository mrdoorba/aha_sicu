"""Tests for email service: composition, SMTP send, CID images."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import AppException
from app.modules.email.service import (
    _load_asset,
    send_evaluation_email,
    smtp_send_html,
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
# smtp_send_html
# ---------------------------------------------------------------------------
class TestSmtpSendHtml:
    """Test the HTML+inline-image MIME build and SMTP dispatch."""

    _PNG = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    async def test_builds_multipart_with_inline_images_and_sends(self) -> None:
        captured = {}

        async def fake_send(message, **kwargs):
            captured["message"] = message
            captured["kwargs"] = kwargs

        with (
            patch("app.modules.email.service.aiosmtplib.send", side_effect=fake_send),
            patch("app.modules.email.service.settings") as mock_settings,
        ):
            mock_settings.email_smtp_host = "smtp.gmail.com"
            mock_settings.email_smtp_port = 587
            mock_settings.email_smtp_user = "sender@aha.com"
            mock_settings.email_smtp_app_password = "app-pw"

            msgid = await smtp_send_html(
                subject="Test Subject",
                from_name="AHA Commerce",
                from_email="noreply@aha.com",
                to_emails=["a@example.com"],
                cc_emails=["cc@example.com"],
                bcc_emails=["bcc@example.com"],
                html_content='<p>Hi <img src="cid:img-1"></p>',
                text_content="Hi",
                images=[(self._PNG, "png", "img-1")],
            )

        # Message-ID returned, brackets stripped
        assert "@" in msgid and "<" not in msgid

        message = captured["message"]
        assert message["Subject"] == "Test Subject"
        assert message["From"] == "AHA Commerce <noreply@aha.com>"
        assert message["Cc"] == "cc@example.com"

        # bcc goes only on the envelope, never in headers
        assert message["Bcc"] is None
        assert captured["kwargs"]["recipients"] == ["a@example.com", "cc@example.com", "bcc@example.com"]

        # Structure: multipart/alternative (text + multipart/related(html + image))
        html_part = message.get_payload()[1]
        related_payloads = html_part.get_payload()
        assert related_payloads[0].get_content_type() == "text/html"
        img_part = related_payloads[1]
        assert img_part.get_content_type() == "image/png"
        assert img_part["Content-ID"] == "<img-1>"

    async def test_auth_error_raises_app_exception(self) -> None:
        import aiosmtplib

        with (
            patch("app.modules.email.service.aiosmtplib.send",
                  side_effect=aiosmtplib.SMTPAuthenticationError(535, "bad")),
            patch("app.modules.email.service.settings") as mock_settings,
        ):
            mock_settings.email_smtp_host = "smtp.gmail.com"
            mock_settings.email_smtp_port = 587
            mock_settings.email_smtp_user = "sender@aha.com"
            mock_settings.email_smtp_app_password = "bad-pw"

            with pytest.raises(AppException) as exc_info:
                await smtp_send_html(
                    subject="S", from_name="N", from_email="noreply@aha.com",
                    to_emails=["a@example.com"], cc_emails=None, bcc_emails=None,
                    html_content="<p>Hi</p>", text_content="Hi", images=[],
                )

        assert exc_info.value.code == "GMAIL_SMTP_AUTH_ERROR"
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
        mock_render_fn: MagicMock,
    ) -> None:
        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.email_enabled = False
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"

            await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                render_html_fn=mock_render_fn,
            )

        # Check the render function received the image srcs
        call_kwargs = mock_render_fn.call_args[1]
        assert "header_src" in call_kwargs
        assert "footer_src" in call_kwargs

    async def test_uses_custom_subject(
        self,
        sample_evaluation_data: dict,
        mock_render_fn: MagicMock,
    ) -> None:
        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.email_enabled = False
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                subject="Custom Subject",
                render_html_fn=mock_render_fn,
            )

        assert result.success is True

    async def test_debug_mode_writes_file(
        self,
        sample_evaluation_data: dict,
        mock_render_fn: MagicMock,
    ) -> None:
        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.email_enabled = False
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
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

    async def test_sends_via_smtp_when_enabled(
        self,
        sample_evaluation_data: dict,
        mock_render_fn: MagicMock,
    ) -> None:
        with (
            patch("app.modules.email.service.settings") as mock_settings,
            patch("app.modules.email.service.smtp_send_html") as mock_send,
        ):
            mock_settings.email_enabled = True
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"
            mock_send.return_value = "smtp-msg-123"

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                render_html_fn=mock_render_fn,
            )

        assert result.success is True
        assert result.message_id == "smtp-msg-123"
        mock_send.assert_called_once()

    async def test_subject_auto_generated_format(
        self,
        sample_evaluation_data: dict,
        mock_render_fn: MagicMock,
    ) -> None:
        """Subject should be 'Laporan Evaluasi Brand: [Brand] - [Period]'."""
        with (
            patch("app.modules.email.service.settings") as mock_settings,
            patch("app.modules.email.service.smtp_send_html") as mock_send,
        ):
            mock_settings.email_enabled = True
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"
            mock_send.return_value = "smtp-msg-123"

            await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                render_html_fn=mock_render_fn,
            )

        call_kwargs = mock_send.call_args[1]
        expected_subject = "[ID] 🏥 AHA Store Internal Check Up (Store ICU) - Kopi Kenangan Januari 2026"
        assert call_kwargs["subject"] == expected_subject

    async def test_passes_note_to_render_fn(
        self,
        sample_evaluation_data: dict,
        mock_render_fn: MagicMock,
    ) -> None:
        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.email_enabled = False
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"

            await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                render_html_fn=mock_render_fn,
                note="My custom note",
            )

        call_kwargs = mock_render_fn.call_args[1]
        assert call_kwargs["note"] == "My custom note"

    async def test_multi_recipient_with_cc_bcc(
        self,
        sample_evaluation_data: dict,
        mock_render_fn: MagicMock,
    ) -> None:
        with (
            patch("app.modules.email.service.settings") as mock_settings,
            patch("app.modules.email.service.smtp_send_html") as mock_send,
        ):
            mock_settings.email_enabled = True
            mock_settings.email_from_name = "AHA Commerce"
            mock_settings.email_from_email = "noreply@aha.com"
            mock_send.return_value = "smtp-msg-123"

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["a@example.com", "b@example.com"],
                render_html_fn=mock_render_fn,
                cc=["cc@example.com"],
                bcc=["bcc@example.com"],
            )

        send_kwargs = mock_send.call_args[1]
        assert send_kwargs["to_emails"] == ["a@example.com", "b@example.com"]
        assert send_kwargs["cc_emails"] == ["cc@example.com"]
        assert send_kwargs["bcc_emails"] == ["bcc@example.com"]

        assert result.recipients == ["a@example.com", "b@example.com"]
