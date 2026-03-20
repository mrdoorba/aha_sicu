"""Email module request/response schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.config import settings

_KNOWN_BREVO_EVENTS: frozenset[str] = frozenset({
    "sent", "delivered", "softBounce", "hardBounce",
    "opened", "uniqueOpened", "click", "spam",
    "blocked", "invalid", "deferred",
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
    sent_at: str


class EmailHistoryListResponse(BaseModel):
    """Paginated email history response."""

    items: list[EmailHistoryItem]
    total: int
    page: int
    limit: int
    pages: int


class BrevoWebhookEvent(BaseModel):
    """Single Brevo webhook event payload."""

    model_config = ConfigDict(populate_by_name=True)

    event: str
    email: str = ""
    message_id: str = Field(default="", alias="message-id")
    ts_epoch: int = 0
    date: str = ""
    subject: str = ""
    reason: str = ""
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_event_type(self) -> "BrevoWebhookEvent":
        if self.event not in _KNOWN_BREVO_EVENTS:
            raise ValueError(f"Unknown Brevo event: {self.event}")
        return self
