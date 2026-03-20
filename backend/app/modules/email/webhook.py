"""Brevo webhook endpoint for email delivery status tracking."""

import logging
import secrets
from datetime import datetime, timezone

from asyncpg import Connection
from fastapi import APIRouter, Depends, Header, HTTPException

from app.config import settings
from app.core.dependencies import get_db_connection
from app.db.queries.email_history import update_email_status_by_message_id
from app.modules.email.schemas import BrevoWebhookEvent

logger = logging.getLogger(__name__)

webhook_router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

_MAX_BATCH_SIZE = 100

_BREVO_EVENT_TO_STATUS: dict[str, str] = {
    "sent": "sent",
    "delivered": "delivered",
    "softBounce": "bounced",
    "hardBounce": "bounced",
    "opened": "opened",
    "uniqueOpened": "opened",
    "click": "clicked",
    "spam": "spam",
    "blocked": "blocked",
    "invalid": "invalid",
    "deferred": "deferred",
}

_BOUNCE_BLOCK_EVENTS: frozenset[str] = frozenset({
    "softBounce", "hardBounce", "blocked", "invalid",
})


async def verify_webhook_secret(
    authorization: str = Header(...),
) -> None:
    """Validate the webhook bearer token against configured secret."""
    if not settings.brevo_webhook_secret:
        raise HTTPException(status_code=401, detail="Webhook not configured")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    if not secrets.compare_digest(parts[1], settings.brevo_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


@webhook_router.post(
    "/brevo",
    dependencies=[Depends(verify_webhook_secret)],
    status_code=200,
)
async def brevo_webhook(
    payload: list[BrevoWebhookEvent] | BrevoWebhookEvent,
    conn: Connection = Depends(get_db_connection),
) -> dict:
    """Receive Brevo webhook events and update email delivery status."""
    events = payload if isinstance(payload, list) else [payload]

    if len(events) > _MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size {len(events)} exceeds limit of {_MAX_BATCH_SIZE}",
        )

    processed = 0
    for event in events:
        status = _BREVO_EVENT_TO_STATUS.get(event.event)
        if not status:
            logger.warning("Unmapped Brevo event: %s for message_id=%s", event.event, event.message_id)
            continue

        event_at = (
            datetime.fromtimestamp(event.ts_epoch / 1000, tz=timezone.utc)
            if event.ts_epoch
            else datetime.now(timezone.utc)
        )

        error_detail = event.reason if event.event in _BOUNCE_BLOCK_EVENTS and event.reason else None

        # Log event type + message_id only — NOT recipient email (PII protection)
        logger.info("Brevo webhook: event=%s message_id=%s", event.event, event.message_id)

        await update_email_status_by_message_id(
            conn,
            message_id=event.message_id,
            new_status=status,
            event_at=event_at,
            error_detail=error_detail,
        )
        processed += 1

    return {"processed": processed}
