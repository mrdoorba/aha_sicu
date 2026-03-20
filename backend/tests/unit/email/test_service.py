"""Tests for email service: composition, Brevo API send."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.exceptions import AppException
from app.modules.email.service import (
    _decode_chart_image,
    _load_asset,
    _strip_base64_prefix,
    brevo_send,
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
# brevo_send
# ---------------------------------------------------------------------------
class TestBrevoSend:
    """Test Brevo API send with error categorization."""

    async def test_sends_successfully(self) -> None:
        mock_response = httpx.Response(
            status_code=201,
            json={"messageId": "<brevo-msg-123>"},
            request=httpx.Request("POST", BREVO_URL),
        )

        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await brevo_send(
                sender_name="AHA Commerce",
                sender_email="noreply@aha.com",
                to_emails=["test@example.com"],
                subject="Test",
                html_content="<p>Hello</p>",
                text_content="Hello",
                api_key="xkeysib-test",
            )

        assert result == "<brevo-msg-123>"
        call_kwargs = mock_client.post.call_args
        assert call_kwargs[1]["headers"]["api-key"] == "xkeysib-test"

    async def test_sends_with_cc_bcc(self) -> None:
        mock_response = httpx.Response(
            status_code=201,
            json={"messageId": "<brevo-msg-456>"},
            request=httpx.Request("POST", BREVO_URL),
        )

        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            await brevo_send(
                sender_name="AHA",
                sender_email="noreply@aha.com",
                to_emails=["a@example.com"],
                subject="Test",
                html_content="<p>Hi</p>",
                text_content="Hi",
                cc_emails=["cc@example.com"],
                bcc_emails=["bcc@example.com"],
                api_key="xkeysib-test",
            )

        payload = mock_client.post.call_args[1]["json"]
        assert payload["cc"] == [{"email": "cc@example.com"}]
        assert payload["bcc"] == [{"email": "bcc@example.com"}]

    async def test_raises_auth_error_on_401(self) -> None:
        mock_response = httpx.Response(
            status_code=401,
            text="Unauthorized",
            request=httpx.Request("POST", BREVO_URL),
        )

        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(AppException) as exc_info:
                await brevo_send(
                    sender_name="AHA",
                    sender_email="noreply@aha.com",
                    to_emails=["test@example.com"],
                    subject="Test",
                    html_content="<p>Hi</p>",
                    text_content="Hi",
                    api_key="bad-key",
                )

        assert exc_info.value.code == "BREVO_AUTH_ERROR"
        assert exc_info.value.status_code == 502

    async def test_raises_rate_limit_on_429(self) -> None:
        mock_response = httpx.Response(
            status_code=429,
            text="Rate limited",
            request=httpx.Request("POST", BREVO_URL),
        )

        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(AppException) as exc_info:
                await brevo_send(
                    sender_name="AHA",
                    sender_email="noreply@aha.com",
                    to_emails=["test@example.com"],
                    subject="Test",
                    html_content="<p>Hi</p>",
                    text_content="Hi",
                    api_key="xkeysib-test",
                )

        assert exc_info.value.code == "BREVO_RATE_LIMIT"
        assert exc_info.value.status_code == 429

    async def test_raises_api_error_on_500(self) -> None:
        mock_response = httpx.Response(
            status_code=500,
            text="Internal Server Error",
            request=httpx.Request("POST", BREVO_URL),
        )

        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(AppException) as exc_info:
                await brevo_send(
                    sender_name="AHA",
                    sender_email="noreply@aha.com",
                    to_emails=["test@example.com"],
                    subject="Test",
                    html_content="<p>Hi</p>",
                    text_content="Hi",
                    api_key="xkeysib-test",
                )

        assert exc_info.value.code == "BREVO_API_ERROR"
        assert exc_info.value.status_code == 502

    async def test_raises_validation_error_on_400(self) -> None:
        mock_response = httpx.Response(
            status_code=400,
            text="Bad Request",
            request=httpx.Request("POST", BREVO_URL),
        )

        with patch("app.modules.email.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(AppException) as exc_info:
                await brevo_send(
                    sender_name="AHA",
                    sender_email="noreply@aha.com",
                    to_emails=["test@example.com"],
                    subject="Test",
                    html_content="<p>Hi</p>",
                    text_content="Hi",
                    api_key="xkeysib-test",
                )

        assert exc_info.value.code == "BREVO_VALIDATION_ERROR"
        assert exc_info.value.status_code == 422


BREVO_URL = "https://api.brevo.com/v3/smtp/email"


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

            await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
            )

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

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
            )

        assert result.success is True
        assert result.message_id == "debug-file"
        assert result.recipients == ["test@example.com"]
        preview_path = Path(f"/tmp/email_preview_{sample_evaluation_data['id']}.html")
        assert preview_path.exists()
        content = preview_path.read_text()
        assert "Rendered email" in content

    async def test_sends_via_brevo_when_enabled(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        with (
            patch("app.modules.email.service.settings") as mock_settings,
            patch("app.modules.email.service.brevo_send", new_callable=AsyncMock) as mock_send,
        ):
            mock_settings.email_enabled = True
            mock_settings.brevo_api_key = "xkeysib-test"
            mock_settings.brevo_sender_name = "AHA Commerce"
            mock_settings.brevo_sender_email = "noreply@aha.com"
            mock_send.return_value = "<brevo-msg-123>"

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
            )

        assert result.success is True
        assert result.message_id == "<brevo-msg-123>"
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
            patch("app.modules.email.service.brevo_send", new_callable=AsyncMock) as mock_send,
        ):
            mock_settings.email_enabled = True
            mock_settings.brevo_api_key = "xkeysib-test"
            mock_settings.brevo_sender_name = "AHA Commerce"
            mock_settings.brevo_sender_email = "noreply@aha.com"
            mock_send.return_value = "<msg@test>"

            await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
            )

        call_kwargs = mock_send.call_args[1]
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
            patch("app.modules.email.service.brevo_send", new_callable=AsyncMock) as mock_send,
        ):
            mock_settings.email_enabled = True
            mock_settings.brevo_api_key = "xkeysib-test"
            mock_settings.brevo_sender_name = "AHA Commerce"
            mock_settings.brevo_sender_email = "noreply@aha.com"
            mock_send.return_value = "<msg@test>"

            result = await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["a@example.com", "b@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
                cc=["cc@example.com"],
                bcc=["bcc@example.com"],
            )

        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["to_emails"] == ["a@example.com", "b@example.com"]
        assert call_kwargs["cc_emails"] == ["cc@example.com"]
        assert call_kwargs["bcc_emails"] == ["bcc@example.com"]
        assert result.recipients == ["a@example.com", "b@example.com"]

    async def test_raises_config_error_when_api_key_missing(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        with patch("app.modules.email.service.settings") as mock_settings:
            mock_settings.email_enabled = True
            mock_settings.brevo_api_key = ""
            mock_settings.brevo_sender_name = "AHA Commerce"
            mock_settings.brevo_sender_email = "noreply@aha.com"

            with pytest.raises(AppException) as exc_info:
                await send_evaluation_email(
                    evaluation_data=sample_evaluation_data,
                    recipients=["test@example.com"],
                    chart_image_b64=sample_base64_png,
                    render_html_fn=mock_render_fn,
                )

        assert exc_info.value.code == "BREVO_CONFIG_ERROR"
        assert exc_info.value.status_code == 500

    async def test_html_contains_data_uris_not_cids(
        self,
        sample_evaluation_data: dict,
        sample_base64_png: str,
        mock_render_fn: MagicMock,
    ) -> None:
        """Verify CID references are replaced with data URIs before sending."""
        mock_render_fn.return_value = '<img src="cid:header-cid"><img src="cid:footer-cid">'

        with (
            patch("app.modules.email.service.settings") as mock_settings,
            patch("app.modules.email.service.brevo_send", new_callable=AsyncMock) as mock_send,
        ):
            mock_settings.email_enabled = True
            mock_settings.brevo_api_key = "xkeysib-test"
            mock_settings.brevo_sender_name = "AHA Commerce"
            mock_settings.brevo_sender_email = "noreply@aha.com"
            mock_send.return_value = "<msg@test>"

            await send_evaluation_email(
                evaluation_data=sample_evaluation_data,
                recipients=["test@example.com"],
                chart_image_b64=sample_base64_png,
                render_html_fn=mock_render_fn,
            )

        html_sent = mock_send.call_args[1]["html_content"]
        assert "cid:" not in html_sent
        assert "data:image/png;base64," in html_sent
