"""Email composition and Brevo transactional email sending service."""

import base64
import logging
from collections.abc import Callable
from pathlib import Path

import httpx

from app.config import settings
from app.core.exceptions import AppException
from app.modules.email.schemas import SendEmailResponse
from app.modules.email.template import _get_strings

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).parent / "assets"

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


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


def _bytes_to_data_uri(data: bytes, subtype: str = "png") -> str:
    """Convert raw image bytes to a base64 data URI."""
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/{subtype};base64,{b64}"


def _replace_cid_with_data_uri(
    html: str,
    cid_map: dict[str, str],
) -> str:
    """Replace cid: references in HTML with base64 data URIs.

    Args:
        html: HTML string containing cid: references.
        cid_map: Mapping of CID string to data URI string.
    """
    for cid, data_uri in cid_map.items():
        html = html.replace(f"cid:{cid}", data_uri)
    return html


async def brevo_send(
    *,
    sender_name: str,
    sender_email: str,
    to_emails: list[str],
    subject: str,
    html_content: str,
    text_content: str,
    cc_emails: list[str] | None = None,
    bcc_emails: list[str] | None = None,
    api_key: str,
) -> str:
    """Send an email via the Brevo transactional email API.

    Returns the Brevo messageId on success.
    Raises AppException with categorized error codes on failure.
    """
    payload: dict = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": addr} for addr in to_emails],
        "subject": subject,
        "htmlContent": html_content,
        "textContent": text_content,
        "headers": {"X-Mailin-Tag": "evaluation-report"},
    }

    if cc_emails:
        payload["cc"] = [{"email": addr} for addr in cc_emails]
    if bcc_emails:
        payload["bcc"] = [{"email": addr} for addr in bcc_emails]

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(BREVO_API_URL, json=payload, headers=headers)

    if response.status_code == 201:
        data = response.json()
        return data.get("messageId", "")

    body = response.text
    logger.error("Brevo API error %s: %s", response.status_code, body)

    if response.status_code == 401:
        raise AppException(
            code="BREVO_AUTH_ERROR",
            detail=f"Brevo authentication failed: {body}",
            status_code=502,
        )
    if response.status_code == 429:
        raise AppException(
            code="BREVO_RATE_LIMIT",
            detail=f"Brevo rate limit exceeded: {body}",
            status_code=429,
        )
    if response.status_code == 400:
        raise AppException(
            code="BREVO_VALIDATION_ERROR",
            detail=f"Brevo validation error: {body}",
            status_code=422,
        )
    raise AppException(
        code="BREVO_API_ERROR",
        detail=f"Brevo API error ({response.status_code}): {body}",
        status_code=502,
    )


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
        language: Language code for email strings.

    Returns:
        SendEmailResponse with success status and message ID.
    """
    brand_name = evaluation_data.get("brand_name", "Unknown")
    period = evaluation_data.get("period", "")
    evaluation_id = evaluation_data.get("id", 0)

    # Auto-generate subject if not provided
    S = _get_strings(language)
    if not subject:
        subject = S["subject"].format(brand_name=brand_name, period=period)

    # Decode chart image
    chart_bytes = _decode_chart_image(chart_image_b64)

    # Load branded assets
    header_bytes = _load_asset("aha-e-mail-header-2026.png")
    footer_bytes = _load_asset("aha-e-mail-footer-2026.png")

    # Build CID placeholders (reused for data URI conversion)
    header_cid = "header-cid"
    footer_cid = "footer-cid"
    chart_cid = "chart-cid" if chart_bytes else ""

    # Render HTML using the provided function (pass cid: URIs as before)
    chart_src = f"cid:{chart_cid}" if chart_cid else ""
    html_content = render_html_fn(
        evaluation_data=evaluation_data,
        chart_src=chart_src,
        header_src=f"cid:{header_cid}",
        footer_src=f"cid:{footer_cid}",
        note=note,
        language=language,
    )

    # Replace CID references with base64 data URIs for Brevo
    cid_map: dict[str, str] = {
        header_cid: _bytes_to_data_uri(header_bytes),
        footer_cid: _bytes_to_data_uri(footer_bytes),
    }
    if chart_bytes and chart_cid:
        cid_map[chart_cid] = _bytes_to_data_uri(chart_bytes)

    html_content = _replace_cid_with_data_uri(html_content, cid_map)

    # Plain text fallback — use partner score (pass ratio) to match dashboard
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

    # Fail-closed: require API key when email is enabled
    if not settings.brevo_api_key:
        raise AppException(
            code="BREVO_CONFIG_ERROR",
            detail="BREVO_API_KEY is required when EMAIL_ENABLED=true",
            status_code=500,
        )

    try:
        message_id = await brevo_send(
            sender_name=settings.brevo_sender_name,
            sender_email=settings.brevo_sender_email,
            to_emails=recipients,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            cc_emails=cc,
            bcc_emails=bcc,
            api_key=settings.brevo_api_key,
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
