"""Tests for the Gmail SMTP transport (gmail_smtp_send)."""

import asyncio
from email.message import EmailMessage
from unittest.mock import AsyncMock, patch

import aiosmtplib
import pytest

from app.core.exceptions import AppException
from app.modules.email.service import gmail_smtp_send


def _call_kwargs() -> dict:
    return dict(
        subject="Hello",
        body_text="Body line one.\nBody line two.",
        from_name="AHA Commerce",
        from_email="bot@ahacommerce.net",
        to_emails=["pic@brand.com"],
    )


class TestGmailSmtpSendSuccess:
    """Happy-path behavior."""

    @pytest.mark.asyncio
    async def test_returns_message_id_on_success(self) -> None:
        with patch("app.modules.email.service.aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = ({}, "250 OK")
            msgid = await gmail_smtp_send(**_call_kwargs())
        assert msgid
        assert "@ahacommerce.id" in msgid
        assert not msgid.startswith("<") and not msgid.endswith(">")

    @pytest.mark.asyncio
    async def test_send_called_with_starttls_and_credentials(self) -> None:
        with (
            patch("app.modules.email.service.aiosmtplib.send", new_callable=AsyncMock) as mock_send,
            patch("app.modules.email.service.settings") as mock_settings,
        ):
            mock_settings.gmail_smtp_host = "smtp.gmail.com"
            mock_settings.gmail_smtp_port = 587
            mock_settings.gmail_smtp_user = "bot@ahacommerce.net"
            mock_settings.gmail_smtp_app_password = "abcd efgh ijkl mnop"
            mock_send.return_value = ({}, "250 OK")

            await gmail_smtp_send(**_call_kwargs())

        args, kwargs = mock_send.call_args
        assert kwargs["hostname"] == "smtp.gmail.com"
        assert kwargs["port"] == 587
        assert kwargs["start_tls"] is True
        assert kwargs["username"] == "bot@ahacommerce.net"
        assert kwargs["password"] == "abcd efgh ijkl mnop"
        assert kwargs["timeout"] == 30.0

    @pytest.mark.asyncio
    async def test_message_carries_subject_from_to_and_body(self) -> None:
        captured: dict = {}

        async def capture(message, **_kwargs):
            captured["msg"] = message
            return ({}, "250 OK")

        with patch("app.modules.email.service.aiosmtplib.send", side_effect=capture):
            await gmail_smtp_send(**_call_kwargs())

        msg = captured["msg"]
        assert isinstance(msg, EmailMessage)
        assert msg["Subject"] == "Hello"
        assert "AHA Commerce" in msg["From"] and "bot@ahacommerce.net" in msg["From"]
        assert msg["To"] == "pic@brand.com"
        assert "Body line one." in msg.get_content()
        assert msg["Message-ID"]

    @pytest.mark.asyncio
    async def test_cc_in_headers_and_envelope_bcc_omitted_from_headers(self) -> None:
        captured: dict = {}

        async def capture(message, **kwargs):
            captured["msg"] = message
            captured["recipients"] = kwargs.get("recipients")
            return ({}, "250 OK")

        with patch("app.modules.email.service.aiosmtplib.send", side_effect=capture):
            await gmail_smtp_send(
                **_call_kwargs(),
                cc_emails=["cc@brand.com"],
                bcc_emails=["bcc@brand.com"],
            )

        msg = captured["msg"]
        assert msg["Cc"] == "cc@brand.com"
        # Bcc must not leak into the message headers
        assert msg.get("Bcc") is None
        # But it must reach the SMTP envelope
        assert "bcc@brand.com" in captured["recipients"]
        assert "cc@brand.com" in captured["recipients"]
        assert "pic@brand.com" in captured["recipients"]


class TestGmailSmtpSendFailures:
    """Each aiosmtplib exception class maps to the right AppException."""

    @pytest.mark.asyncio
    async def test_auth_error_maps_to_502(self) -> None:
        with patch(
            "app.modules.email.service.aiosmtplib.send",
            side_effect=aiosmtplib.SMTPAuthenticationError(535, "bad password"),
        ):
            with pytest.raises(AppException) as exc_info:
                await gmail_smtp_send(**_call_kwargs())
        assert exc_info.value.code == "GMAIL_SMTP_AUTH_ERROR"
        assert exc_info.value.status_code == 502

    @pytest.mark.asyncio
    async def test_connect_error_maps_to_502(self) -> None:
        with patch(
            "app.modules.email.service.aiosmtplib.send",
            side_effect=aiosmtplib.SMTPConnectError("cannot connect"),
        ):
            with pytest.raises(AppException) as exc_info:
                await gmail_smtp_send(**_call_kwargs())
        assert exc_info.value.code == "GMAIL_SMTP_CONNECTION_ERROR"
        assert exc_info.value.status_code == 502

    @pytest.mark.asyncio
    async def test_server_disconnected_maps_to_connection_error(self) -> None:
        with patch(
            "app.modules.email.service.aiosmtplib.send",
            side_effect=aiosmtplib.SMTPServerDisconnected("disconnected"),
        ):
            with pytest.raises(AppException) as exc_info:
                await gmail_smtp_send(**_call_kwargs())
        assert exc_info.value.code == "GMAIL_SMTP_CONNECTION_ERROR"

    @pytest.mark.asyncio
    async def test_timeout_maps_to_504(self) -> None:
        with patch(
            "app.modules.email.service.aiosmtplib.send",
            side_effect=asyncio.TimeoutError(),
        ):
            with pytest.raises(AppException) as exc_info:
                await gmail_smtp_send(**_call_kwargs())
        assert exc_info.value.code == "GMAIL_SMTP_TIMEOUT"
        assert exc_info.value.status_code == 504

    @pytest.mark.asyncio
    async def test_generic_smtp_exception_maps_to_502(self) -> None:
        with patch(
            "app.modules.email.service.aiosmtplib.send",
            side_effect=aiosmtplib.SMTPException("something went wrong"),
        ):
            with pytest.raises(AppException) as exc_info:
                await gmail_smtp_send(**_call_kwargs())
        assert exc_info.value.code == "GMAIL_SMTP_ERROR"
        assert exc_info.value.status_code == 502
