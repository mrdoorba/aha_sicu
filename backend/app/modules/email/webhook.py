"""SendGrid Event Webhook endpoint for email delivery status tracking."""

import logging
import secrets
from datetime import datetime, timezone

from asyncpg import Connection
from fastapi import APIRouter, Depends, Header, HTTPException

from app.config import settings
from app.core.dependencies import get_db_connection
from app.db.queries.email_history import update_email_status_by_message_id
from app.modules.email.schemas import SendGridWebhookEvent

logger = logging.getLogger(__name__)

webhook_router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

_MAX_BATCH_SIZE = 100

_SENDGRID_EVENT_TO_STATUS: dict[str, str] = {
    "processed": "sent",
    "delivered": "delivered",
    "bounce": "bounced",
    "dropped": "blocked",
    "open": "opened",
    "click": "clicked",
    "spamreport": "spam",
    "deferred": "deferred",
}

_BOUNCE_DROP_EVENTS: frozenset[str] = frozenset({
    "bounce", "dropped",
})


async def verify_webhook_secret(
    authorization: str = Header(...),
) -> None:
    """Validate the webhook bearer token against configured secret."""
    if not settings.sendgrid_webhook_secret:
        raise HTTPException(status_code=401, detail="Webhook not configured")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    if not secrets.compare_digest(parts[1], settings.sendgrid_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


@webhook_router.post(
    "/sendgrid",
    dependencies=[Depends(verify_webhook_secret)],
    status_code=200,
)
async def sendgrid_webhook(
    payload: list[SendGridWebhookEvent],
    conn: Connection = Depends(get_db_connection),
) -> dict:
    """Receive SendGrid Event Webhook events and update email delivery status."""
    if len(payload) > _MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size {len(payload)} exceeds limit of {_MAX_BATCH_SIZE}",
        )

    processed = 0
    for event in payload:
        status = _SENDGRID_EVENT_TO_STATUS.get(event.event)
        if not status:
            logger.warning("Unmapped SendGrid event: %s for sg_message_id=%s", event.event, event.sg_message_id)
            continue

        event_at = (
            datetime.fromtimestamp(event.timestamp, tz=timezone.utc)
            if event.timestamp
            else datetime.now(timezone.utc)
        )

        error_detail = event.reason if event.event in _BOUNCE_DROP_EVENTS and event.reason else None

        # Log event type + message_id only — NOT recipient email (PII protection)
        logger.info("SendGrid webhook: event=%s sg_message_id=%s", event.event, event.sg_message_id)

        await update_email_status_by_message_id(
            conn,
            message_id=event.sg_message_id,
            new_status=status,
            event_at=event_at,
            error_detail=error_detail,
        )
        processed += 1

    return {"processed": processed}
