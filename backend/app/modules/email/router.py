"""Email API endpoints for sending and previewing evaluation reports."""

import logging
from datetime import date
from pathlib import Path

from typing import Literal

from asyncpg import Connection
from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse, PlainTextResponse

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
    PreviewEmailRequest,
    SendEmailRequest,
    SendEmailResponse,
    SendPlainEmailRequest,
)
from app.modules.email.layout import render_email, render_plain_email_message
from app.modules.email.service import asset_to_data_uri, gmail_smtp_send, send_evaluation_email
from app.modules.email.template import render_email_html
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

    Fetches evaluation data, renders the HTML template, and sends (or previews
    in debug mode) the email. Logs the result to email_history.
    """
    evaluation = await get_evaluation_detail(conn=conn, evaluation_id=body.evaluation_id)
    eval_dict = evaluation.model_dump()

    recipient_str = ", ".join(str(r) for r in body.recipients)
    subject = body.subject or ""

    try:
        result = await send_evaluation_email(
            evaluation_data=eval_dict,
            recipients=[str(r) for r in body.recipients],
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
                sender_email=settings.email_from_email or "",
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
            sender_email=settings.email_from_email or "",
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


@router.post("/send-plain", response_model=SendEmailResponse)
async def send_plain_email_endpoint(
    body: SendPlainEmailRequest,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection),
) -> SendEmailResponse:
    """Send a plain-text evaluation email via Gmail SMTP.

    Validates the evaluation exists (reusing get_evaluation_detail's access
    control), renders the plain-text body server-side from the unified email
    renderer (the client-supplied body is ignored), sends it, and logs the
    result to email_history. In debug mode (gmail_smtp_enabled=False), writes
    the body to /tmp instead of dialing SMTP. Independent of email_enabled (the
    rich /send path's gate).
    """
    evaluation = await get_evaluation_detail(conn=conn, evaluation_id=body.evaluation_id)
    body_text = render_plain_email_message(
        evaluation.model_dump(), language=body.language, pic_email=body.pic_email or None
    )

    recipients = [str(r) for r in body.recipients]
    cc = [str(c) for c in body.cc] if body.cc else None
    bcc = [str(b) for b in body.bcc] if body.bcc else None
    recipient_str = ", ".join(recipients)
    sender_email = settings.gmail_smtp_user or ""

    if not settings.gmail_smtp_enabled:
        preview_path = Path(f"/tmp/email_preview_plain_{body.evaluation_id}.txt")
        preview_path.write_text(
            f"Subject: {body.subject}\nTo: {recipient_str}\n\n{body_text}",
            encoding="utf-8",
        )
        logger.info("Plain email preview saved to %s", preview_path)
        result = SendEmailResponse(
            success=True,
            message_id="debug-file",
            recipients=recipients,
        )
    else:
        try:
            message_id = await gmail_smtp_send(
                subject=body.subject,
                body_text=body_text,
                from_name=settings.email_from_name,
                from_email=sender_email,
                to_emails=recipients,
                cc_emails=cc,
                bcc_emails=bcc,
            )
            result = SendEmailResponse(
                success=True,
                message_id=message_id,
                recipients=recipients,
            )
        except Exception as send_exc:
            try:
                await insert_email_history(
                    conn,
                    evaluation_id=body.evaluation_id,
                    sender_email=sender_email,
                    recipient_email=recipient_str,
                    cc_emails=cc,
                    bcc_emails=bcc,
                    subject=body.subject,
                    status="failed",
                    message_id=None,
                    error_detail=str(send_exc),
                )
            except Exception:
                logger.exception("Failed to log email failure to history")
            raise

    try:
        await insert_email_history(
            conn,
            evaluation_id=body.evaluation_id,
            sender_email=sender_email,
            recipient_email=recipient_str,
            cc_emails=cc,
            bcc_emails=bcc,
            subject=body.subject,
            status="sent",
            message_id=result.message_id,
            error_detail=None,
        )
    except Exception:
        logger.exception("Failed to log email success to history")

    return result


@router.get("/preview/{evaluation_id}", response_class=HTMLResponse, response_model=None)
async def preview_email_endpoint(
    evaluation_id: int,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection),
    note: str | None = Query(default=None, max_length=500),
    language: str | None = Query(default=None),
    format: Literal["html", "text"] = Query(default="html"),
) -> HTMLResponse | PlainTextResponse:
    """Preview the evaluation email as rendered HTML or plain text.

    Both formats come from the single :func:`render_email` renderer. ``html``
    (the default) is the dashboard preview, with data URI images for browser
    rendering. ``text`` is the plain-text body the evaluation page displays and
    Gmail SMTP sends. Protected by authentication (no debug guard needed).
    Accepts an optional `language` query param to override the user's default
    language for the preview.
    """
    evaluation = await get_evaluation_detail(conn=conn, evaluation_id=evaluation_id)
    eval_dict = evaluation.model_dump()

    lang = language or current_user.get("language", "id")

    if format == "text":
        text = render_email(eval_dict, language=lang, fmt="text")
        return PlainTextResponse(content=text)

    # Convert header/footer assets to data URIs for browser rendering
    header_src = asset_to_data_uri("aha-e-mail-header-2026.png")
    footer_src = asset_to_data_uri("aha-e-mail-footer-2026.png")
    syb_src = asset_to_data_uri("syb-color-3.png")

    html = render_email_html(
        evaluation_data=eval_dict,
        header_src=header_src,
        footer_src=footer_src,
        syb_src=syb_src,
        note=note,
        language=lang,
    )

    return HTMLResponse(content=html)


@router.post("/preview", response_class=PlainTextResponse, response_model=None)
async def preview_email_from_result_endpoint(
    body: PreviewEmailRequest,
    current_user: dict = Depends(get_current_user),
    language: str = Query(default="id"),
    format: Literal["html", "text"] = Query(default="text"),
) -> HTMLResponse | PlainTextResponse:
    """Render an email preview from a posted, in-memory ScoringResult payload.

    Stateless: there is no DB lookup, so the pre-save scoring screen can
    re-render its just-computed result in any language. Reuses the single
    :func:`render_email` renderer — no second rendering path.
    """
    result = {
        "brand_name": body.brand_name,
        "period": body.period,
        "score_breakdown": body.category_scores,
        "calculator_results": {
            **body.calculator_results,
            "scoring_summary": {
                "conclusion": body.conclusion,
                "conclusion_i18n": body.conclusion_i18n,
                "marketing_estimation": body.marketing_estimation,
                "marketing_budget": body.marketing_budget,
                "marketing_budget_i18n": body.marketing_budget_i18n,
                "closing_message": body.closing_message,
                "closing_message_i18n": body.closing_message_i18n,
            },
        },
    }

    if format == "text":
        return PlainTextResponse(content=render_email(result, language=language, fmt="text"))

    html = render_email(
        result,
        language=language,
        fmt="html",
        header_src=asset_to_data_uri("aha-e-mail-header-2026.png"),
        footer_src=asset_to_data_uri("aha-e-mail-footer-2026.png"),
        syb_src=asset_to_data_uri("syb-color-3.png"),
    )
    return HTMLResponse(content=html)
