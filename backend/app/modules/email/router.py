"""Email API endpoints for sending and previewing evaluation reports."""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.config import settings
from app.core.dependencies import get_current_user
from app.core.exceptions import AppException
from app.modules.email.schemas import SendEmailRequest, SendEmailResponse
from app.modules.email.service import send_evaluation_email
from app.modules.email.template import render_email_html
from app.modules.evaluations.service import get_evaluation_detail

router = APIRouter(prefix="/api/v1/email", tags=["email"])


@router.post("/send", response_model=SendEmailResponse)
async def send_email_endpoint(
    body: SendEmailRequest,
    current_user: dict = Depends(get_current_user),
) -> SendEmailResponse:
    """Send an evaluation report email.

    Fetches evaluation data, renders the HTML template with the provided
    chart image, and sends (or previews in debug mode) the email.
    """
    evaluation = await get_evaluation_detail(evaluation_id=body.evaluation_id)
    eval_dict = evaluation.model_dump()

    return await send_evaluation_email(
        evaluation_data=eval_dict,
        recipient=body.recipient,
        chart_image_b64=body.chart_image,
        subject=body.subject,
        render_html_fn=render_email_html,
    )


@router.get("/preview/{evaluation_id}")
async def preview_email_endpoint(
    evaluation_id: int,
    current_user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Preview the evaluation email as rendered HTML (dev/staging only).

    Returns the HTML that would be sent, with placeholder CIDs for images.
    Only available when debug mode is enabled.
    """
    if not settings.debug:
        raise AppException(
            code="PREVIEW_NOT_AVAILABLE",
            detail="Email preview is only available in debug mode",
            status_code=404,
        )

    evaluation = await get_evaluation_detail(evaluation_id=evaluation_id)
    eval_dict = evaluation.model_dump()

    # Placeholder CIDs -- images won't render in browser but HTML structure is visible
    html = render_email_html(
        evaluation_data=eval_dict,
        chart_cid="placeholder-chart@ahacommerce.id",
        header_cid="placeholder-header@ahacommerce.id",
        footer_cid="placeholder-footer@ahacommerce.id",
    )

    return HTMLResponse(content=html)
