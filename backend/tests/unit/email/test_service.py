"""Tests for email service: composition, CID images, SMTP send."""

import smtplib
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import AppException
from app.modules.email.service import (
    _decode_chart_image,
    _load_asset,
    _smtp_send_sync,
    _strip_base64_prefix,
    build_email_message,
    send_evaluation_email,
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
# build_email_message
# ---------------------------------------------------------------------------
class TestBuildEmailMessage:
    """Test email message construction with CID images."""

    def _build_simple_msg(self) -> EmailMessage:
        return build_email_message(
            subject="Test Subject",
            from_name="AHA Commerce",
            from_email="noreply@aha.com",
            to_emails=["recipient@example.com"],
            html_content="<html><body>Hello</body></html>",
            text_content="Hello",
            images=[
                (b"\x89PNG-header", "png", "header-cid"),
                (b"\x89PNG-footer", "png", "footer-cid"),
                (b"\x89PNG-chart", "png", "chart-cid"),
            ],
        )

    def test_subject_header(self) -> None:
        msg = self._build_simple_msg()
        assert msg["Subject"] == "Test Subject"

    def test_from_header_with_display_name(self) -> None:
        msg = self._build_simple_msg()
        assert "AHA Commerce" in msg["From"]
        assert "noreply@aha.com" in msg["From"]

    def test_to_header_single(self) -> None:
        msg = self._build_simple_msg()
        assert msg["To"] == "recipient@example.com"

    def test_to_header_multiple(self) -> None:
        msg = build_email_message(
            subject="Test",
            from_name="AHA",
            from_email="noreply@aha.com",
            to_emails=["a@example.com", "b@example.com", "c@example.com"],
            html_content="<p>Hi</p>",
            text_content="Hi",
            images=[],
        )
        assert msg["To"] == "a@example.com, b@example.com, c@example.com"

    def test_cc_header_set_when_provided(self) -> None:
        msg = build_email_message(
            subject="Test",
            from_name="AHA",
            from_email="noreply@aha.com",
            to_emails=["a@example.com"],
            cc_emails=["cc1@example.com", "cc2@example.com"],
            html_content="<p>Hi</p>",
            text_content="Hi",
            images=[],
        )
        assert msg["Cc"] == "cc1@example.com, cc2@example.com"

    def test_bcc_header_not_set(self) -> None:
        msg = build_email_message(
            subject="Test",
            from_name="AHA",
            from_email="noreply@aha.com",
            to_emails=["a@example.com"],
            bcc_emails=["bcc@example.com"],
            html_content="<p>Hi</p>",
            text_content="Hi",
            images=[],
        )
        assert msg["Bcc"] is None

    def test_no_cc_header_when_empty(self) -> None:
        msg = self._build_simple_msg()
        assert msg["Cc"] is None

    def test_has_html_alternative(self) -> None:
        msg = self._build_simple_msg()
        # Walk the message parts - should find text/html
        html_found = False
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_found = True
                break
        assert html_found, "No text/html part found in message"

    def test_has_text_fallback(self) -> None:
        msg = self._build_simple_msg()
        text_found = False
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                text_found = True
                break
        assert text_found, "No text/plain part found in message"

    def test_attaches_three_cid_images(self) -> None:
        msg = self._build_simple_msg()
        image_parts = [
            p for p in msg.walk() if p.get_content_type() == "image/png"
        ]
        assert len(image_parts) == 3

    def test_cid_references_match(self) -> None:
        msg = self._build_simple_msg()
        cids_found = []
        for part in msg.walk():
            if part.get_content_type() == "image/png":
                content_id = part.get("Content-ID", "")
                # Strip angle brackets for comparison
                cid = content_id.strip("<>")
                cids_found.append(cid)
        assert "header-cid" in cids_found
        assert "footer-cid" in cids_found
        assert "chart-cid" in cids_found

    def test_from_formatted_as_display_name_email(self) -> None:
        msg = build_email_message(
            subject="Test",
            from_name="My Brand",
            from_email="brand@example.com",
            to_emails=["to@example.com"],
            html_content="<p>Hi</p>",
            text_content="Hi",
            images=[],
        )
        from_header = msg["From"]
        assert "My Brand" in from_header
        assert "brand@example.com" in from_header


# ---------------------------------------------------------------------------
# _smtp_send_sync
# ---------------------------------------------------------------------------
class TestSmtpSendSync:
    """Test synchronous SMTP send with error categorization."""

    def test_calls_starttls_login_send(self, mock_smtp: tuple) -> None:
        mock_class, mock_instance = mock_smtp
        msg = EmailMessage()
        msg["Message-ID"] = "<test123@ahacommerce.id>"

        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.smtp_host = "smtp.gmail.com"
            mock_settings.smtp_port = 587
            mock_settings.smtp_user = "user@gmail.com"
            mock_settings.smtp_password = "secret"
            mock_class.return_value = mock_instance

            _smtp_send_sync(msg)

        mock_class.assert_called_once_with("smtp.gmail.com", 587, timeout=30)
        mock_instance.starttls.assert_called_once()
        mock_instance.login.assert_called_once_with("user@gmail.com", "secret")
        mock_instance.send_message.assert_called_once_with(msg, to_addrs=None)

    def test_sends_with_explicit_to_addrs(self, mock_smtp: tuple) -> None:
        mock_class, mock_instance = mock_smtp
        msg = EmailMessage()
        msg["Message-ID"] = "<test123@ahacommerce.id>"
        all_addrs = ["a@example.com", "b@example.com", "bcc@example.com"]

        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.smtp_host = "smtp.gmail.com"
            mock_settings.smtp_port = 587
            mock_settings.smtp_user = "user@gmail.com"
            mock_settings.smtp_password = "secret"
            mock_class.return_value = mock_instance

            _smtp_send_sync(msg, to_addrs=all_addrs)

        mock_instance.send_message.assert_called_once_with(msg, to_addrs=all_addrs)

    def test_raises_smtp_auth_error(self, mock_smtp: tuple) -> None:
        mock_class, mock_instance = mock_smtp
        mock_instance.login.side_effect = smtplib.SMTPAuthenticationError(
            535, b"Authentication failed"
        )
        msg = EmailMessage()

        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.smtp_host = "smtp.gmail.com"
            mock_settings.smtp_port = 587
            mock_settings.smtp_user = "user@gmail.com"
            mock_settings.smtp_password = "wrong"
            mock_class.return_value = mock_instance

            with pytest.raises(AppException) as exc_info:
                _smtp_send_sync(msg)
            assert exc_info.value.code == "SMTP_AUTH_ERROR"
            assert exc_info.value.status_code == 502

    def test_raises_smtp_connection_error(self, mock_smtp: tuple) -> None:
        mock_class, _ = mock_smtp
        mock_class.side_effect = smtplib.SMTPConnectError(
            421, b"Connection refused"
        )
        msg = EmailMessage()

        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.smtp_host = "smtp.gmail.com"
            mock_settings.smtp_port = 587

            with pytest.raises(AppException) as exc_info:
                _smtp_send_sync(msg)
            assert exc_info.value.code == "SMTP_CONNECTION_ERROR"
            assert exc_info.value.status_code == 502

    def test_raises_smtp_timeout(self, mock_smtp: tuple) -> None:
        mock_class, _ = mock_smtp
        mock_class.side_effect = TimeoutError("Connection timed out")
        msg = EmailMessage()

        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.smtp_host = "smtp.gmail.com"
            mock_settings.smtp_port = 587

            with pytest.raises(AppException) as exc_info:
                _smtp_send_sync(msg)
            assert exc_info.value.code == "SMTP_TIMEOUT"
            assert exc_info.value.status_code == 504


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
            mock_settings.smtp_from_name = "AHA Commerce"
            mock_settings.smtp_from_email = "noreply@aha.com"

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
            mock_settings.smtp_from_name = "AHA Commerce"
            mock_settings.smtp_from_email = "noreply@aha.com"

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
            mock_settings.smtp_from_name = "AHA Commerce"
            mock_settings.smtp_from_email = "noreply@aha.com"

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

    async def test_sends_via_smtp_when_enabled(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        with (
            patch("app.modules.email.service.settings") as mock_settings,
            patch("app.modules.email.service.smtp_send") as mock_send,
        ):
            mock_settings.email_enabled = True
            mock_settings.smtp_from_name = "AHA Commerce"
            mock_settings.smtp_from_email = "noreply@aha.com"
            mock_send.return_value = "<msg123@ahacommerce.id>"

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
            )

        assert result.success is True
        assert result.message_id == "<msg123@ahacommerce.id>"
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
            patch("app.modules.email.service.smtp_send") as mock_send,
            patch(
                "app.modules.email.service.build_email_message"
            ) as mock_build,
        ):
            mock_settings.email_enabled = True
            mock_settings.smtp_from_name = "AHA Commerce"
            mock_settings.smtp_from_email = "noreply@aha.com"
            mock_send.return_value = "<msg@test>"

            mock_msg = MagicMock()
            mock_build.return_value = mock_msg

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
            mock_settings.smtp_from_name = "AHA Commerce"
            mock_settings.smtp_from_email = "noreply@aha.com"

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
            patch("app.modules.email.service.smtp_send") as mock_send,
            patch("app.modules.email.service.build_email_message") as mock_build,
        ):
            mock_settings.email_enabled = True
            mock_settings.smtp_from_name = "AHA Commerce"
            mock_settings.smtp_from_email = "noreply@aha.com"
            mock_send.return_value = "<msg@test>"
            mock_build.return_value = MagicMock()

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["a@example.com", "b@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
                cc=["cc@example.com"],
                bcc=["bcc@example.com"],
            )

        # Verify build_email_message called with correct params
        build_kwargs = mock_build.call_args[1]
        assert build_kwargs["to_emails"] == ["a@example.com", "b@example.com"]
        assert build_kwargs["cc_emails"] == ["cc@example.com"]
        assert build_kwargs["bcc_emails"] == ["bcc@example.com"]

        # Verify smtp_send called with all addresses
        send_call_args = mock_send.call_args
        # Second positional arg is to_addrs
        assert "a@example.com" in send_call_args[0][1]
        assert "bcc@example.com" in send_call_args[0][1]

        assert result.recipients == ["a@example.com", "b@example.com"]
