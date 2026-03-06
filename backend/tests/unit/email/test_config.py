"""Tests for SMTP configuration and email schemas."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.config import Settings
from app.modules.email.schemas import SendEmailRequest, SendEmailResponse


class TestSmtpConfigDefaults:
    """Test that SMTP config fields have correct defaults."""

    def test_smtp_host_default(self) -> None:
        s = Settings(_env_file=None)
        assert s.smtp_host == "smtp.gmail.com"

    def test_smtp_port_default(self) -> None:
        s = Settings(_env_file=None)
        assert s.smtp_port == 587

    def test_email_enabled_default(self) -> None:
        s = Settings(_env_file=None)
        assert s.email_enabled is False

    def test_smtp_from_name_default(self) -> None:
        s = Settings(_env_file=None)
        assert s.smtp_from_name == "AHA Commerce"

    def test_smtp_user_default_empty(self) -> None:
        s = Settings(_env_file=None)
        assert s.smtp_user == ""

    def test_smtp_password_default_empty(self) -> None:
        s = Settings(_env_file=None)
        assert s.smtp_password == ""

    def test_smtp_from_email_default_empty(self) -> None:
        s = Settings(_env_file=None)
        assert s.smtp_from_email == ""


class TestSmtpConfigEnvOverrides:
    """Test that all SMTP fields can be overridden via env vars."""

    def test_smtp_host_override(self) -> None:
        with patch.dict(os.environ, {"SMTP_HOST": "mail.example.com"}):
            s = Settings(_env_file=None)
            assert s.smtp_host == "mail.example.com"

    def test_smtp_port_override(self) -> None:
        with patch.dict(os.environ, {"SMTP_PORT": "465"}):
            s = Settings(_env_file=None)
            assert s.smtp_port == 465

    def test_email_enabled_override(self) -> None:
        with patch.dict(os.environ, {"EMAIL_ENABLED": "true"}):
            s = Settings(_env_file=None)
            assert s.email_enabled is True

    def test_smtp_user_override(self) -> None:
        with patch.dict(os.environ, {"SMTP_USER": "user@gmail.com"}):
            s = Settings(_env_file=None)
            assert s.smtp_user == "user@gmail.com"

    def test_smtp_password_override(self) -> None:
        with patch.dict(os.environ, {"SMTP_PASSWORD": "app-password-123"}):
            s = Settings(_env_file=None)
            assert s.smtp_password == "app-password-123"

    def test_smtp_from_name_override(self) -> None:
        with patch.dict(os.environ, {"SMTP_FROM_NAME": "My Brand"}):
            s = Settings(_env_file=None)
            assert s.smtp_from_name == "My Brand"

    def test_smtp_from_email_override(self) -> None:
        with patch.dict(os.environ, {"SMTP_FROM_EMAIL": "noreply@brand.com"}):
            s = Settings(_env_file=None)
            assert s.smtp_from_email == "noreply@brand.com"


class TestSendEmailRequestSchema:
    """Test SendEmailRequest validation."""

    def test_validates_recipients_as_email(self) -> None:
        req = SendEmailRequest(
            evaluation_id=1,
            recipients=["test@example.com"],
            chart_image="abc123",
        )
        assert req.recipients == ["test@example.com"]

    def test_rejects_invalid_email(self) -> None:
        with pytest.raises(ValidationError, match="recipients"):
            SendEmailRequest(
                evaluation_id=1,
                recipients=["not-an-email"],
                chart_image="abc123",
            )

    def test_requires_chart_image(self) -> None:
        with pytest.raises(ValidationError, match="chart_image"):
            SendEmailRequest(
                evaluation_id=1,
                recipients=["test@example.com"],
            )

    def test_subject_optional(self) -> None:
        req = SendEmailRequest(
            evaluation_id=1,
            recipients=["test@example.com"],
            chart_image="abc123",
        )
        assert req.subject is None

    def test_subject_max_length(self) -> None:
        with pytest.raises(ValidationError, match="subject"):
            SendEmailRequest(
                evaluation_id=1,
                recipients=["test@example.com"],
                chart_image="abc123",
                subject="x" * 201,
            )

    def test_subject_within_max_length(self) -> None:
        req = SendEmailRequest(
            evaluation_id=1,
            recipients=["test@example.com"],
            chart_image="abc123",
            subject="x" * 200,
        )
        assert len(req.subject) == 200

    def test_cc_bcc_default_empty(self) -> None:
        req = SendEmailRequest(
            evaluation_id=1,
            recipients=["test@example.com"],
            chart_image="abc123",
        )
        assert req.cc == []
        assert req.bcc == []

    def test_note_optional(self) -> None:
        req = SendEmailRequest(
            evaluation_id=1,
            recipients=["test@example.com"],
            chart_image="abc123",
        )
        assert req.note is None

    def test_total_recipients_validation(self) -> None:
        with pytest.raises(ValidationError, match="Total recipients"):
            SendEmailRequest(
                evaluation_id=1,
                recipients=[f"r{i}@example.com" for i in range(6)],
                cc=[f"cc{i}@example.com" for i in range(3)],
                bcc=[f"bcc{i}@example.com" for i in range(2)],
                chart_image="abc123",
            )


class TestSendEmailResponseSchema:
    """Test SendEmailResponse fields."""

    def test_has_required_fields(self) -> None:
        resp = SendEmailResponse(
            success=True,
            message_id="<msg123@example.com>",
            recipients=["test@example.com"],
        )
        assert resp.success is True
        assert resp.message_id == "<msg123@example.com>"
        assert resp.recipients == ["test@example.com"]
