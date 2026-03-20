"""Email composition and SMTP sending service."""

import asyncio
import base64
import logging
import smtplib
from collections.abc import Callable
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path

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


def _strip_base64_prefix(data: str) -> str:
    """Strip data URI prefix (e.g. 'data:image/png;base64,') if present."""
    if "," in data and data.startswith("data:"):
        return data.split(",", 1)[1]
    return data


def _decode_chart_image(chart_image_b64: str) -> bytes | None:
    """Decode a base64 chart image string, stripping data URI prefix first.

    Returns None if the input is empty (chart capture was skipped).
    """
    if not chart_image_b64:
        return None
    stripped = _strip_base64_prefix(chart_image_b64)
    try:
        return base64.b64decode(stripped, validate=True)
    except Exception as exc:
        raise AppException(
            code="INVALID_CHART_IMAGE",
            detail=f"Failed to decode chart image: {exc}",
            status_code=422,
        ) from exc


def build_email_message(
    *,
    subject: str,
    from_name: str,
    from_email: str,
    to_emails: list[str],
    cc_emails: list[str] | None = None,
    bcc_emails: list[str] | None = None,
    html_content: str,
    text_content: str,
    images: list[tuple[bytes, str, str]],
) -> EmailMessage:
    """Build a multipart email with CID inline images."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = ", ".join(to_emails)

    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)

    msg.set_content(text_content)
    msg.add_alternative(html_content, subtype="html")

    if images:
        # Get the HTML alternative part (second payload in multipart/alternative)
        alt_parts = msg.get_payload()
        if len(alt_parts) >= 2:
            html_part = alt_parts[1]
            html_part.make_related()
            for data, subtype, cid in images:
                html_part.add_related(
                    data,
                    maintype="image",
                    subtype=subtype,
                    cid=cid,
                )

    return msg


def _smtp_send_sync(
    msg: EmailMessage,
    *,
    to_addrs: list[str] | None = None,
) -> str:
    """Send an email message synchronously via SMTP."""
    try:
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30)
        try:
            if settings.smtp_use_tls:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg, to_addrs=to_addrs)
            return msg.get("Message-ID", "")
        finally:
            server.quit()
    except smtplib.SMTPAuthenticationError as exc:
        raise AppException(
            code="SMTP_AUTH_ERROR",
            detail=f"SMTP authentication failed: {exc}",
            status_code=502,
        ) from exc
    except smtplib.SMTPConnectError as exc:
        raise AppException(
            code="SMTP_CONNECTION_ERROR",
            detail=f"Could not connect to SMTP server: {exc}",
            status_code=502,
        ) from exc
    except TimeoutError as exc:
        raise AppException(
            code="SMTP_TIMEOUT",
            detail=f"SMTP connection timed out: {exc}",
            status_code=504,
        ) from exc


async def smtp_send(
    msg: EmailMessage,
    to_addrs: list[str] | None = None,
) -> str:
    """Async wrapper around synchronous SMTP send."""
    return await asyncio.to_thread(_smtp_send_sync, msg, to_addrs=to_addrs)


async def send_evaluation_email(
    *,
    evaluation_data: dict,
    recipients: list[str],
    chart_image_b64: str,
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

    chart_bytes = _decode_chart_image(chart_image_b64)

    header_bytes = _load_asset("aha-e-mail-header-2026.png")
    footer_bytes = _load_asset("aha-e-mail-footer-2026.png")

    header_msgid = make_msgid(domain="ahacommerce.id")
    footer_msgid = make_msgid(domain="ahacommerce.id")
    header_cid = header_msgid.strip("<>")
    footer_cid = footer_msgid.strip("<>")

    chart_cid = ""
    if chart_bytes:
        chart_msgid = make_msgid(domain="ahacommerce.id")
        chart_cid = chart_msgid.strip("<>")

    chart_src = f"cid:{chart_cid}" if chart_cid else ""
    html_content = render_html_fn(
        evaluation_data=evaluation_data,
        chart_src=chart_src,
        header_src=f"cid:{header_cid}",
        footer_src=f"cid:{footer_cid}",
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
    ]
    if chart_bytes and chart_cid:
        images.append((chart_bytes, "png", chart_cid))

    msg = build_email_message(
        subject=subject,
        from_name=settings.smtp_from_name,
        from_email=settings.smtp_from_email,
        to_emails=recipients,
        cc_emails=cc,
        bcc_emails=bcc,
        html_content=html_content,
        text_content=text_content,
        images=images,
    )

    all_addrs = list(recipients) + (cc or []) + (bcc or [])

    try:
        message_id = await smtp_send(msg, all_addrs)
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
