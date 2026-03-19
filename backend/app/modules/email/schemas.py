"""Email module request/response schemas."""

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.config import settings


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
            raise ValueError(
                "Email sending is not configured. Set EMAIL_ALLOWED_DOMAINS."
            )
        allowed = {d.strip().lower() for d in allowed_raw.split(",") if d.strip()}
        all_emails = list(self.recipients) + list(self.cc) + list(self.bcc)
        blocked = []
        for e in all_emails:
            email_str = str(e)
            parts = email_str.split("@")
            if len(parts) != 2:
                continue  # EmailStr already validated format; skip as defense-in-depth
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
