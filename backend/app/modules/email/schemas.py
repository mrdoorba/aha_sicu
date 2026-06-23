"""Email module request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.config import settings

_KNOWN_SENDGRID_EVENTS: frozenset[str] = frozenset({
    "processed", "delivered", "bounce", "dropped",
    "open", "click", "spamreport", "deferred",
})


class SendEmailRequest(BaseModel):
    """Request body for sending an evaluation email."""

    evaluation_id: int
    recipients: list[EmailStr] = Field(min_length=1, max_length=10)
    cc: list[EmailStr] = Field(default_factory=list, max_length=10)
    bcc: list[EmailStr] = Field(default_factory=list, max_length=10)
    chart_image: str = Field(default="", description="Base64-encoded PNG chart image (optional — placeholder used if empty)")
    subject: str | None = Field(default=None, max_length=200)
    note: str | None = Field(default=None, max_length=500)
    language: str = Field(default="id", pattern="^(id|en|th)$")

    @model_validator(mode="after")
    def validate_total_recipients(self) -> "SendEmailRequest":
        total = len(self.recipients) + len(self.cc) + len(self.bcc)
        if total > 10:
            raise ValueError("Total recipients (To + CC + BCC) cannot exceed 10")
        return self

    @model_validator(mode="after")
    def validate_recipient_domains(self) -> "SendEmailRequest":
        allowed_raw = settings.email_allowed_domains
        if not allowed_raw:
            return self  # No allowlist configured — allow all domains
        allowed = {d.strip().lower() for d in allowed_raw.split(",") if d.strip()}
        all_emails = list(self.recipients) + list(self.cc) + list(self.bcc)
        blocked = []
        for e in all_emails:
            email_str = str(e)
            parts = email_str.split("@")
            if len(parts) != 2:
                continue
            if parts[1].lower() not in allowed:
                blocked.append(email_str)
        if blocked:
            raise ValueError(f"Recipients outside allowed domains: {', '.join(blocked)}")
        return self


class SendPlainEmailRequest(BaseModel):
    """Request body for sending a plain-text evaluation email via Gmail SMTP.

    The email body is rendered server-side from ``evaluation_id`` + ``language``
    by the unified email renderer; any client-supplied ``body`` is ignored
    (kept optional for backward compatibility with older clients).
    """

    evaluation_id: int
    recipients: list[EmailStr] = Field(min_length=1, max_length=10)
    cc: list[EmailStr] = Field(default_factory=list, max_length=10)
    bcc: list[EmailStr] = Field(default_factory=list, max_length=10)
    subject: str = Field(min_length=1, max_length=200)
    body: str | None = Field(default=None, max_length=20_000, description="Ignored — body is rendered server-side")
    pic_email: str = Field(default="", max_length=500, description="PIC address(es) for the body's [EMAIL TO: ...] line")
    language: str = Field(default="id", pattern="^(id|en|th)$")

    @model_validator(mode="after")
    def validate_total_recipients(self) -> "SendPlainEmailRequest":
        total = len(self.recipients) + len(self.cc) + len(self.bcc)
        if total > 10:
            raise ValueError("Total recipients (To + CC + BCC) cannot exceed 10")
        return self

    @model_validator(mode="after")
    def validate_recipient_domains(self) -> "SendPlainEmailRequest":
        allowed_raw = settings.email_allowed_domains
        if not allowed_raw:
            return self
        allowed = {d.strip().lower() for d in allowed_raw.split(",") if d.strip()}
        all_emails = list(self.recipients) + list(self.cc) + list(self.bcc)
        blocked = []
        for e in all_emails:
            email_str = str(e)
            parts = email_str.split("@")
            if len(parts) != 2:
                continue
            if parts[1].lower() not in allowed:
                blocked.append(email_str)
        if blocked:
            raise ValueError(f"Recipients outside allowed domains: {', '.join(blocked)}")
        return self


class PreviewEmailRequest(BaseModel):
    """Stateless email-preview payload — a ScoringResult-shaped, in-memory result.

    Used by the pre-save scoring screen, which has no saved evaluation to fetch.
    The fields mirror the score endpoint's response; the router maps them into
    the renderer's evaluation-dict shape and feeds the single ``render_email``.
    Rows and i18n companions are accepted as permissive dicts (the renderer
    reads them positionally as ``{"key", "vars"}`` / row dicts).
    """

    category_scores: list[dict[str, Any]] = Field(default_factory=list)
    conclusion: str = ""
    conclusion_i18n: list[dict[str, Any]] | None = None
    marketing_estimation: str = ""
    marketing_budget: str = ""
    marketing_budget_i18n: dict[str, Any] | None = None
    closing_message: str = ""
    closing_message_i18n: dict[str, Any] | None = None
    calculator_results: dict[str, Any] = Field(default_factory=dict)
    brand_name: str = ""
    period: str = ""


class SendEmailResponse(BaseModel):
    """Response after sending (or previewing) an email."""

    success: bool
    message_id: str
    recipients: list[str]


class EmailHistoryItem(BaseModel):
    """Single email history record."""

    id: int
    evaluation_id: int
    sender_email: str
    recipient_email: str
    cc_emails: list[str] | None = None
    bcc_emails: list[str] | None = None
    subject: str
    status: str
    message_id: str | None = None
    error_detail: str | None = None
    sent_at: datetime


class EmailHistoryListResponse(BaseModel):
    """Paginated email history response."""

    items: list[EmailHistoryItem]
    total: int
    page: int
    limit: int
    pages: int


class DeleteEmailHistoryRequest(BaseModel):
    """Request body for batch-deleting email history entries."""

    ids: list[int] = Field(min_length=1, max_length=100)


class DeleteEmailHistoryResponse(BaseModel):
    """Response after deleting email history entries."""

    deleted: int


class SendGridWebhookEvent(BaseModel):
    """Single SendGrid Event Webhook payload."""

    event: str
    email: str = ""
    sg_message_id: str = ""
    timestamp: int = 0
    reason: str = ""
    type: str = ""

    @model_validator(mode="after")
    def validate_event_type(self) -> "SendGridWebhookEvent":
        if self.event not in _KNOWN_SENDGRID_EVENTS:
            raise ValueError(f"Unknown SendGrid event: {self.event}")
        return self
