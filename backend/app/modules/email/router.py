"""Email API endpoints for sending and previewing evaluation reports."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from app.core.dependencies import get_current_user
from app.modules.email.schemas import SendEmailRequest, SendEmailResponse
from app.modules.email.service import asset_to_data_uri, send_evaluation_email
from app.modules.email.template import render_email_html
from app.modules.evaluations.service import get_evaluation_detail

router = APIRouter(prefix="/api/v1/email", tags=["email"])

from app.modules.email.template import _get_strings


def _chart_placeholder_svg(language: str = "id") -> str:
    """Generate chart placeholder SVG with localized text."""
    S = _get_strings(language)
    text = S["chart_placeholder"]
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        "width='600' height='300' viewBox='0 0 600 300'%3E"
        "%3Crect width='600' height='300' fill='%23f0f0f0'/%3E"
        "%3Ctext x='300' y='150' text-anchor='middle' fill='%23999' "
        "font-family='Arial' font-size='14'%3E"
        f"{text}%3C/text%3E%3C/svg%3E"
    )


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
        recipients=[str(r) for r in body.recipients],
        chart_image_b64=body.chart_image,
        subject=body.subject,
        render_html_fn=render_email_html,
        cc=[str(c) for c in body.cc] if body.cc else None,
        bcc=[str(b) for b in body.bcc] if body.bcc else None,
        note=body.note,
        language=current_user.get("language", "id"),
    )


@router.get("/preview/{evaluation_id}")
async def preview_email_endpoint(
    evaluation_id: int,
    current_user: dict = Depends(get_current_user),
    note: str | None = Query(default=None, max_length=500),
) -> HTMLResponse:
    """Preview the evaluation email as rendered HTML.

    Returns the HTML that would be sent, with data URI images for browser
    rendering. Protected by authentication (no debug guard needed).
    """
    evaluation = await get_evaluation_detail(evaluation_id=evaluation_id)
    eval_dict = evaluation.model_dump()

    # Convert header/footer assets to data URIs for browser rendering
    header_src = asset_to_data_uri("aha-e-mail-header-2026.png")
    footer_src = asset_to_data_uri("aha-e-mail-footer-2026.png")

    language = current_user.get("language", "id")
    html = render_email_html(
        evaluation_data=eval_dict,
        chart_src=_chart_placeholder_svg(language),
        header_src=header_src,
        footer_src=footer_src,
        note=note,
        language=language,
    )

    return HTMLResponse(content=html)
