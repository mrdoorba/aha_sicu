"""Tests for SendGrid configuration and email schemas."""

import os
from unittest.mock import patch


import pytest
from pydantic import ValidationError

from app.config import Settings
from app.modules.email.schemas import SendEmailRequest, SendEmailResponse


class TestSendGridConfigDefaults:
    """Test that SendGrid config fields have correct defaults."""

    def test_sendgrid_api_key_default_empty(self) -> None:
        s = Settings(_env_file=None)
        assert s.sendgrid_api_key == ""

    def test_email_from_name_default(self) -> None:
        s = Settings(_env_file=None)
        assert s.email_from_name == "AHA Commerce"

    def test_email_from_email_default_empty(self) -> None:
        s = Settings(_env_file=None)
        assert s.email_from_email == ""

    def test_email_enabled_default(self) -> None:
        s = Settings(_env_file=None)
        assert s.email_enabled is False


class TestSendGridConfigEnvOverrides:
    """Test that all SendGrid fields can be overridden via env vars."""

    def test_sendgrid_api_key_override(self) -> None:
        with patch.dict(os.environ, {"SENDGRID_API_KEY": "SG.test-key"}):
            s = Settings(_env_file=None)
            assert s.sendgrid_api_key == "SG.test-key"

    def test_email_from_name_override(self) -> None:
        with patch.dict(os.environ, {"EMAIL_FROM_NAME": "My Brand"}):
            s = Settings(_env_file=None)
            assert s.email_from_name == "My Brand"

    def test_email_from_email_override(self) -> None:
        with patch.dict(os.environ, {"EMAIL_FROM_EMAIL": "noreply@brand.com"}):
            s = Settings(_env_file=None)
            assert s.email_from_email == "noreply@brand.com"

    def test_email_enabled_override(self) -> None:
        with patch.dict(os.environ, {"EMAIL_ENABLED": "true"}):
            s = Settings(_env_file=None)
            assert s.email_enabled is True


class TestSendEmailRequestSchema:
    """Test SendEmailRequest validation."""

    @patch("app.modules.email.schemas.settings")
    def test_validates_recipients_as_email(self, mock_settings) -> None:
        mock_settings.email_allowed_domains = "example.com"
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

    @patch("app.modules.email.schemas.settings")
    def test_chart_image_defaults_to_empty(self, mock_settings) -> None:
        mock_settings.email_allowed_domains = "example.com"
        req = SendEmailRequest(
            evaluation_id=1,
            recipients=["test@example.com"],
        )
        assert req.chart_image == ""

    @patch("app.modules.email.schemas.settings")
    def test_subject_optional(self, mock_settings) -> None:
        mock_settings.email_allowed_domains = "example.com"
        req = SendEmailRequest(
            evaluation_id=1,
            recipients=["test@example.com"],
            chart_image="abc123",
        )
        assert req.subject is None

    @patch("app.modules.email.schemas.settings")
    def test_subject_max_length(self, mock_settings) -> None:
        mock_settings.email_allowed_domains = "example.com"
        with pytest.raises(ValidationError, match="subject"):
            SendEmailRequest(
                evaluation_id=1,
                recipients=["test@example.com"],
                chart_image="abc123",
                subject="x" * 201,
            )

    @patch("app.modules.email.schemas.settings")
    def test_subject_within_max_length(self, mock_settings) -> None:
        mock_settings.email_allowed_domains = "example.com"
        req = SendEmailRequest(
            evaluation_id=1,
            recipients=["test@example.com"],
            chart_image="abc123",
            subject="x" * 200,
        )
        assert len(req.subject) == 200

    @patch("app.modules.email.schemas.settings")
    def test_cc_bcc_default_empty(self, mock_settings) -> None:
        mock_settings.email_allowed_domains = "example.com"
        req = SendEmailRequest(
            evaluation_id=1,
            recipients=["test@example.com"],
            chart_image="abc123",
        )
        assert req.cc == []
        assert req.bcc == []

    @patch("app.modules.email.schemas.settings")
    def test_note_optional(self, mock_settings) -> None:
        mock_settings.email_allowed_domains = "example.com"
        req = SendEmailRequest(
            evaluation_id=1,
            recipients=["test@example.com"],
            chart_image="abc123",
        )
        assert req.note is None

    @patch("app.modules.email.schemas.settings")
    def test_total_recipients_validation(self, mock_settings) -> None:
        mock_settings.email_allowed_domains = "example.com"
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
