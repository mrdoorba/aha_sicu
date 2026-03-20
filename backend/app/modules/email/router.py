"""Email API endpoints for sending and previewing evaluation reports."""

import logging
from datetime import date

from asyncpg import Connection
from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from app.config import settings
from app.core.dependencies import get_current_user, get_db_connection, require_role
from app.db.queries.email_history import (
    delete_email_history_by_ids,
    insert_email_history,
    list_email_history,
    list_email_history_by_evaluation,
)
from app.core.audit import record_audit_event
from app.modules.email.schemas import (
    DeleteEmailHistoryRequest,
    DeleteEmailHistoryResponse,
    EmailHistoryItem,
    EmailHistoryListResponse,
    SendEmailRequest,
    SendEmailResponse,
)
from app.modules.email.service import asset_to_data_uri, send_evaluation_email
from app.modules.email.template import _get_strings, render_email_html
from app.modules.evaluations.service import get_evaluation_detail

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/email", tags=["email"])


@router.get("/history", response_model=EmailHistoryListResponse)
async def list_history_endpoint(
    current_user: dict = Depends(require_role("leader", "admin")),
    conn: Connection = Depends(get_db_connection),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="sent_at"),
    sort_order: str = Query(default="desc"),
    search: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    status: str | None = Query(default=None),
) -> EmailHistoryListResponse:
    """List all email history with pagination and filtering.

    Requires leader or admin role.
    """
    result = await list_email_history(
        conn,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        date_from=date_from,
        date_to=date_to,
        status_filter=status,
    )
    return EmailHistoryListResponse(
        items=[EmailHistoryItem(**row) for row in result["items"]],
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        pages=result["pages"],
    )


@router.get("/history/{evaluation_id}", response_model=list[EmailHistoryItem])
async def evaluation_history_endpoint(
    evaluation_id: int,
    current_user: dict = Depends(require_role("leader", "admin")),
    conn: Connection = Depends(get_db_connection),
) -> list[EmailHistoryItem]:
    """List email history for a specific evaluation.

    Requires leader or admin role.
    """
    rows = await list_email_history_by_evaluation(conn, evaluation_id)
    return [EmailHistoryItem(**row) for row in rows]


@router.delete("/history", response_model=DeleteEmailHistoryResponse)
async def delete_history_endpoint(
    body: DeleteEmailHistoryRequest,
    current_user: dict = Depends(require_role("admin")),
    conn: Connection = Depends(get_db_connection),
) -> DeleteEmailHistoryResponse:
    """Batch-delete email history entries. Requires admin role."""
    deleted = await delete_email_history_by_ids(conn, ids=body.ids)
    await record_audit_event(
        conn,
        action="email_history.delete",
        actor_id=current_user["id"],
        actor_email=current_user["email"],
        target_type="email_history",
        target_id=",".join(str(i) for i in body.ids),
        details={"ids": body.ids, "deleted": deleted},
    )
    return DeleteEmailHistoryResponse(deleted=deleted)


@router.post("/send", response_model=SendEmailResponse)
async def send_email_endpoint(
    body: SendEmailRequest,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection),
) -> SendEmailResponse:
    """Send an evaluation report email.

    Fetches evaluation data, renders the HTML template with the provided
    chart image, and sends (or previews in debug mode) the email.
    Logs the result to email_history.
    """
    evaluation = await get_evaluation_detail(conn=conn, evaluation_id=body.evaluation_id)
    eval_dict = evaluation.model_dump()

    recipient_str = ", ".join(str(r) for r in body.recipients)
    subject = body.subject or ""

    try:
        result = await send_evaluation_email(
            evaluation_data=eval_dict,
            recipients=[str(r) for r in body.recipients],
            chart_image_b64=body.chart_image,
            subject=body.subject,
            render_html_fn=render_email_html,
            cc=[str(c) for c in body.cc] if body.cc else None,
            bcc=[str(b) for b in body.bcc] if body.bcc else None,
            note=body.note,
            language=body.language,
        )
    except Exception as send_exc:
        # Log failed send to history (silently — logging must not block error propagation)
        try:
            await insert_email_history(
                conn,
                evaluation_id=body.evaluation_id,
                sender_email=settings.smtp_from_email or "",
                recipient_email=recipient_str,
                cc_emails=[str(c) for c in body.cc] if body.cc else None,
                bcc_emails=[str(b) for b in body.bcc] if body.bcc else None,
                subject=subject,
                status="failed",
                message_id=None,
                error_detail=str(send_exc),
            )
        except Exception:
            logger.exception("Failed to log email failure to history")
        raise

    # Log successful send to history (silently)
    try:
        await insert_email_history(
            conn,
            evaluation_id=body.evaluation_id,
            sender_email=settings.smtp_from_email or "",
            recipient_email=recipient_str,
            cc_emails=[str(c) for c in body.cc] if body.cc else None,
            bcc_emails=[str(b) for b in body.bcc] if body.bcc else None,
            subject=subject,
            status="sent",
            message_id=result.message_id,
            error_detail=None,
        )
    except Exception:
        logger.exception("Failed to log email success to history")

    return result


@router.get("/preview/{evaluation_id}")
async def preview_email_endpoint(
    evaluation_id: int,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection),
    note: str | None = Query(default=None, max_length=500),
    language: str | None = Query(default=None),
) -> HTMLResponse:
    """Preview the evaluation email as rendered HTML.

    Returns the HTML that would be sent, with data URI images for browser
    rendering. Protected by authentication (no debug guard needed).
    Accepts an optional `language` query param to override the user's
    default language for the preview.
    """
    evaluation = await get_evaluation_detail(conn=conn, evaluation_id=evaluation_id)
    eval_dict = evaluation.model_dump()

    # Convert header/footer assets to data URIs for browser rendering
    header_src = asset_to_data_uri("aha-e-mail-header-2026.png")
    footer_src = asset_to_data_uri("aha-e-mail-footer-2026.png")

    lang = language or current_user.get("language", "id")
    html = render_email_html(
        evaluation_data=eval_dict,
        chart_src=_chart_placeholder_svg(lang),
        header_src=header_src,
        footer_src=footer_src,
        note=note,
        language=lang,
    )

    return HTMLResponse(content=html)


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
