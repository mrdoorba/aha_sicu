"""Unit tests for email schema validation (PB-DA-015)."""

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.modules.email.schemas import SendEmailRequest


def _valid_request(**overrides) -> dict:
    """Build a valid SendEmailRequest dict with optional overrides."""
    base = {
        "evaluation_id": 1,
        "recipients": ["user@ahacommerce.co.id"],
    }
    base.update(overrides)
    return base


class TestEmailDomainAllowlist:
    """Tests for email recipient domain allowlist validation."""

    @patch("app.modules.email.schemas.settings")
    def test_send_email_rejects_when_external_domain(self, mock_settings):
        """Rejects recipients outside allowed domains when allowlist is set."""
        mock_settings.email_allowed_domains = "ahacommerce.co.id"
        with pytest.raises(ValidationError, match="Recipients outside allowed domains"):
            SendEmailRequest(**_valid_request(recipients=["attacker@evil.com"]))

    @patch("app.modules.email.schemas.settings")
    def test_send_email_accepts_when_allowed_domain(self, mock_settings):
        """Accepts recipients within allowed domains."""
        mock_settings.email_allowed_domains = "ahacommerce.co.id"
        req = SendEmailRequest(**_valid_request(recipients=["user@ahacommerce.co.id"]))
        assert len(req.recipients) == 1

    @patch("app.modules.email.schemas.settings")
    def test_send_email_allows_any_domain_when_allowlist_empty(self, mock_settings):
        """Allows all recipients when allowlist is not configured (open sending)."""
        mock_settings.email_allowed_domains = ""
        req = SendEmailRequest(**_valid_request(recipients=["anyone@anydomain.com"]))
        assert len(req.recipients) == 1

    @patch("app.modules.email.schemas.settings")
    def test_send_email_accepts_when_multiple_allowed_domains(self, mock_settings):
        """Accepts recipients from any of the comma-separated allowed domains."""
        mock_settings.email_allowed_domains = "ahacommerce.co.id,partner.com"
        req = SendEmailRequest(**_valid_request(
            recipients=["user@ahacommerce.co.id"],
            cc=["partner@partner.com"],
        ))
        assert len(req.recipients) == 1
        assert len(req.cc) == 1

    @patch("app.modules.email.schemas.settings")
    def test_send_email_rejects_cc_with_external_domain(self, mock_settings):
        """Rejects CC recipients outside allowed domains."""
        mock_settings.email_allowed_domains = "ahacommerce.co.id"
        with pytest.raises(ValidationError, match="Recipients outside allowed domains"):
            SendEmailRequest(**_valid_request(
                recipients=["user@ahacommerce.co.id"],
                cc=["attacker@evil.com"],
            ))

    @patch("app.modules.email.schemas.settings")
    def test_send_email_rejects_bcc_with_external_domain(self, mock_settings):
        """Rejects BCC recipients outside allowed domains."""
        mock_settings.email_allowed_domains = "ahacommerce.co.id"
        with pytest.raises(ValidationError, match="Recipients outside allowed domains"):
            SendEmailRequest(**_valid_request(
                recipients=["user@ahacommerce.co.id"],
                bcc=["spy@evil.com"],
            ))
