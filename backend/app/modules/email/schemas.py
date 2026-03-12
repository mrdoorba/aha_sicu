"""Email module request/response schemas."""

from pydantic import BaseModel, EmailStr, Field, model_validator


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


class SendEmailResponse(BaseModel):
    """Response after sending (or previewing) an email."""

    success: bool
    message_id: str
    recipients: list[str]
