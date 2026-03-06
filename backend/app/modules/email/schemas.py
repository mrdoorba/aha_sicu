"""Email module request/response schemas."""

from pydantic import BaseModel, EmailStr, Field


class SendEmailRequest(BaseModel):
    """Request body for sending an evaluation email."""

    evaluation_id: int
    recipient: EmailStr
    chart_image: str = Field(description="Base64-encoded PNG chart image")
    subject: str | None = Field(default=None, max_length=200)


class SendEmailResponse(BaseModel):
    """Response after sending (or previewing) an email."""

    success: bool
    message_id: str
    recipient: str
