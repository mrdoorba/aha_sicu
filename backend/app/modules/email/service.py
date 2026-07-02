"""Email composition and SMTP sending service."""

import asyncio
import base64
import logging
from collections.abc import Callable
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path

import aiosmtplib

from app.config import settings
from app.core.exceptions import AppException
from app.modules.email.schemas import SendEmailResponse
from app.modules.email.template import _get_strings

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).parent / "assets"


def _load_asset(filename: str) -> bytes:
    """Read an image file from the assets directory."""
    path = ASSETS_DIR / filename
    return path.read_bytes()


def asset_to_data_uri(filename: str) -> str:
    """Load an asset and return it as a data URI string."""
    data = _load_asset(filename)
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


async def gmail_smtp_send(
    *,
    subject: str,
    body_text: str,
    from_name: str,
    from_email: str,
    to_emails: list[str],
    cc_emails: list[str] | None = None,
    bcc_emails: list[str] | None = None,
) -> str:
    """Send a plain-text email via Gmail SMTP with App Password auth.

    Returns the Message-ID header value (with angle brackets stripped).
    """
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{from_name} <{from_email}>" if from_name else from_email
    message["To"] = ", ".join(to_emails)
    if cc_emails:
        message["Cc"] = ", ".join(cc_emails)
    msgid = make_msgid(domain="ahacommerce.id")
    message["Message-ID"] = msgid
    message.set_content(body_text)

    envelope_recipients = list(to_emails) + list(cc_emails or []) + list(bcc_emails or [])

    try:
        await aiosmtplib.send(
            message,
            recipients=envelope_recipients,
            hostname=settings.gmail_smtp_host,
            port=settings.gmail_smtp_port,
            start_tls=True,
            username=settings.gmail_smtp_user,
            password=settings.gmail_smtp_app_password,
            timeout=30.0,
        )
    except aiosmtplib.SMTPAuthenticationError as exc:
        raise AppException(
            code="GMAIL_SMTP_AUTH_ERROR",
            detail=f"Gmail SMTP authentication failed — check app password: {exc}",
            status_code=502,
        ) from exc
    except (aiosmtplib.SMTPConnectError, aiosmtplib.SMTPServerDisconnected) as exc:
        raise AppException(
            code="GMAIL_SMTP_CONNECTION_ERROR",
            detail=f"Could not connect to Gmail SMTP: {exc}",
            status_code=502,
        ) from exc
    except asyncio.TimeoutError as exc:
        raise AppException(
            code="GMAIL_SMTP_TIMEOUT",
            detail=f"Gmail SMTP request timed out: {exc}",
            status_code=504,
        ) from exc
    except aiosmtplib.SMTPException as exc:
        raise AppException(
            code="GMAIL_SMTP_ERROR",
            detail=f"Gmail SMTP error: {exc}",
            status_code=502,
        ) from exc

    return msgid.strip("<>")


async def smtp_send_html(
    *,
    subject: str,
    from_name: str,
    from_email: str,
    to_emails: list[str],
    cc_emails: list[str] | None,
    bcc_emails: list[str] | None,
    html_content: str,
    text_content: str,
    images: list[tuple[bytes, str, str]],
) -> str:
    """Send an HTML email with inline CID images via SMTP.

    Builds a multipart/alternative (text + multipart/related html+images)
    message and sends it with the /send account's SMTP credentials
    (``email_smtp_*``) — distinct from /send-plain's ``gmail_smtp_*``.
    Returns the Message-ID header value (angle brackets stripped).
    """
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{from_name} <{from_email}>" if from_name else from_email
    message["To"] = ", ".join(to_emails)
    if cc_emails:
        message["Cc"] = ", ".join(cc_emails)
    msgid = make_msgid(domain="ahacommerce.id")
    message["Message-ID"] = msgid
    message.set_content(text_content)
    message.add_alternative(html_content, subtype="html")

    html_part = message.get_payload()[1]
    for data, subtype, cid in images:
        html_part.add_related(data, maintype="image", subtype=subtype, cid=f"<{cid}>")

    envelope_recipients = list(to_emails) + list(cc_emails or []) + list(bcc_emails or [])

    try:
        await aiosmtplib.send(
            message,
            recipients=envelope_recipients,
            hostname=settings.email_smtp_host,
            port=settings.email_smtp_port,
            start_tls=True,
            username=settings.email_smtp_user or from_email,
            password=settings.email_smtp_app_password,
            timeout=30.0,
        )
    except aiosmtplib.SMTPAuthenticationError as exc:
        raise AppException(
            code="GMAIL_SMTP_AUTH_ERROR",
            detail=f"Gmail SMTP authentication failed — check app password: {exc}",
            status_code=502,
        ) from exc
    except (aiosmtplib.SMTPConnectError, aiosmtplib.SMTPServerDisconnected) as exc:
        raise AppException(
            code="GMAIL_SMTP_CONNECTION_ERROR",
            detail=f"Could not connect to Gmail SMTP: {exc}",
            status_code=502,
        ) from exc
    except asyncio.TimeoutError as exc:
        raise AppException(
            code="GMAIL_SMTP_TIMEOUT",
            detail=f"Gmail SMTP request timed out: {exc}",
            status_code=504,
        ) from exc
    except aiosmtplib.SMTPException as exc:
        raise AppException(
            code="GMAIL_SMTP_ERROR",
            detail=f"Gmail SMTP error: {exc}",
            status_code=502,
        ) from exc

    return msgid.strip("<>")


async def send_evaluation_email(
    *,
    evaluation_data: dict,
    recipients: list[str],
    subject: str | None = None,
    render_html_fn: Callable,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    note: str | None = None,
    language: str = "id",
) -> SendEmailResponse:
    """Compose and send (or preview) an evaluation email."""
    brand_name = evaluation_data.get("brand_name", "Unknown")
    period = evaluation_data.get("period", "")
    evaluation_id = evaluation_data.get("id", 0)

    S = _get_strings(language)
    if not subject:
        subject = S["subject"].format(brand_name=brand_name, period=period)

    header_bytes = _load_asset("aha-e-mail-header-2026.png")
    footer_bytes = _load_asset("aha-e-mail-footer-2026.png")
    syb_bytes = _load_asset("syb-color-3.png")

    from email.utils import make_msgid

    header_msgid = make_msgid(domain="ahacommerce.id")
    footer_msgid = make_msgid(domain="ahacommerce.id")
    syb_msgid = make_msgid(domain="ahacommerce.id")
    header_cid = header_msgid.strip("<>")
    footer_cid = footer_msgid.strip("<>")
    syb_cid = syb_msgid.strip("<>")

    html_content = render_html_fn(
        evaluation_data=evaluation_data,
        header_src=f"cid:{header_cid}",
        footer_src=f"cid:{footer_cid}",
        syb_src=f"cid:{syb_cid}",
        note=note,
        language=language,
    )

    categories = evaluation_data.get("score_breakdown", [])
    checks = 0
    total_verdicts = 0
    for cat in categories:
        for row in cat.get("rows", []):
            v = row.get("verdict", "")
            if v == "\u2714\ufe0f":
                checks += 1
                total_verdicts += 1
            elif v == "\u274c":
                total_verdicts += 1
    partner_score = round((checks / total_verdicts) * 100) if total_verdicts > 0 else "N/A"
    text_content = (
        f"{S['brand_report']}: {brand_name}\n"
        f"{S['plain_period']}: {period}\n"
        f"{S['plain_score']}: {partner_score}\n"
    )

    if not settings.email_enabled:
        preview_path = Path(f"/tmp/email_preview_{evaluation_id}.html")
        preview_path.write_text(html_content, encoding="utf-8")
        logger.info("Email preview saved to %s", preview_path)
        return SendEmailResponse(
            success=True,
            message_id="debug-file",
            recipients=recipients,
        )

    images = [
        (header_bytes, "png", header_cid),
        (footer_bytes, "png", footer_cid),
        (syb_bytes, "png", syb_cid),
    ]

    try:
        message_id = await smtp_send_html(
            subject=subject,
            from_name=settings.email_from_name,
            from_email=settings.email_from_email,
            to_emails=recipients,
            cc_emails=cc,
            bcc_emails=bcc,
            html_content=html_content,
            text_content=text_content,
            images=images,
        )
        return SendEmailResponse(
            success=True,
            message_id=message_id,
            recipients=recipients,
        )
    except AppException:
        raise
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", recipients, exc)
        raise AppException(
            code="EMAIL_SEND_FAILED",
            detail=f"Failed to send email: {exc}",
            status_code=500,
        ) from exc
