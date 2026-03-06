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


def _decode_chart_image(chart_image_b64: str) -> bytes:
    """Decode a base64 chart image string, stripping data URI prefix first."""
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
    """Build a multipart email with CID inline images.

    Args:
        subject: Email subject line.
        from_name: Sender display name.
        from_email: Sender email address.
        to_emails: List of recipient email addresses.
        cc_emails: Optional list of CC email addresses.
        bcc_emails: Optional list of BCC email addresses (not set as header).
        html_content: HTML body.
        text_content: Plain text fallback.
        images: List of (data, subtype, cid) tuples for inline images.

    Returns:
        Composed EmailMessage ready to send.
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = ", ".join(to_emails)

    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)
    # BCC: intentionally NOT set as header

    # Plain text fallback
    msg.set_content(text_content)

    # HTML alternative
    msg.add_alternative(html_content, subtype="html")

    # Attach CID images to the HTML part
    if images:
        html_part = None
        for part in msg.walk():
            if part.get_content_type() == "multipart/related":
                html_part = part
                break
            if part.get_content_type() == "text/html":
                html_part = part
                break

        # Get the related part — add_alternative creates multipart/alternative
        # We need to add images as related to the HTML part
        for payload in msg.iter_parts():
            if payload.get_content_type() == "multipart/alternative":
                for sub in payload.iter_parts():
                    if sub.get_content_type() == "text/html":
                        html_part = sub
                        break
                break

        if html_part is not None:
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
    """Send an email message synchronously via SMTP.

    Args:
        msg: The email message to send.
        to_addrs: Explicit list of envelope recipients (includes BCC).
            If None, send_message extracts recipients from headers.

    Returns the Message-ID on success.
    Raises AppException with categorized error codes on failure.
    """
    try:
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30)
        try:
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
) -> SendEmailResponse:
    """Compose and send (or preview) an evaluation email.

    Args:
        evaluation_data: Dict matching EvaluationDetailResponse shape.
        recipients: List of recipient email addresses.
        chart_image_b64: Base64-encoded chart image (may have data URI prefix).
        subject: Optional custom subject. Auto-generated if not provided.
        render_html_fn: Callable that renders HTML from evaluation data and src URIs.
        cc: Optional list of CC email addresses.
        bcc: Optional list of BCC email addresses.
        note: Optional custom note to include in the email body.

    Returns:
        SendEmailResponse with success status and message ID.
    """
    brand_name = evaluation_data.get("brand_name", "Unknown")
    period = evaluation_data.get("period", "")
    evaluation_id = evaluation_data.get("id", 0)

    # Auto-generate subject if not provided
    if not subject:
        subject = f"Laporan Evaluasi Brand: {brand_name} - {period}"

    # Decode chart image
    chart_bytes = _decode_chart_image(chart_image_b64)

    # Load branded assets
    header_bytes = _load_asset("aha-e-mail-header-2026.png")
    footer_bytes = _load_asset("aha-e-mail-footer-2026.png")

    # Generate CIDs (strip angle brackets for HTML src references)
    header_msgid = make_msgid(domain="ahacommerce.id")
    footer_msgid = make_msgid(domain="ahacommerce.id")
    chart_msgid = make_msgid(domain="ahacommerce.id")

    header_cid = header_msgid.strip("<>")
    footer_cid = footer_msgid.strip("<>")
    chart_cid = chart_msgid.strip("<>")

    # Render HTML using the provided function (pass full cid: URIs)
    html_content = render_html_fn(
        evaluation_data=evaluation_data,
        chart_src=f"cid:{chart_cid}",
        header_src=f"cid:{header_cid}",
        footer_src=f"cid:{footer_cid}",
        note=note,
    )

    # Plain text fallback
    final_score = evaluation_data.get("final_score", "N/A")
    verdict = evaluation_data.get("verdict", "N/A")
    text_content = (
        f"Laporan Evaluasi Brand: {brand_name}\n"
        f"Periode: {period}\n"
        f"Skor Akhir: {final_score}\n"
        f"Verdict: {verdict}\n"
    )

    # Debug mode: write to file instead of sending
    if not settings.email_enabled:
        preview_path = Path(f"/tmp/email_preview_{evaluation_id}.html")
        preview_path.write_text(html_content, encoding="utf-8")
        logger.info("Email preview saved to %s", preview_path)
        return SendEmailResponse(
            success=True,
            message_id="debug-file",
            recipients=recipients,
        )

    # Build and send
    images = [
        (header_bytes, "png", header_cid),
        (footer_bytes, "png", footer_cid),
        (chart_bytes, "png", chart_cid),
    ]

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

    # Compute all envelope recipients (To + CC + BCC)
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
