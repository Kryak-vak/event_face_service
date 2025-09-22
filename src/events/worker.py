import logging
import time

import httpx
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import OutboxMessage

logger = logging.getLogger(__name__)

def process_outbox(batch_size=100, sleep_seconds=1):
    headers = {
        "Content-Type": "application/json",
        "owner_id": settings.OWNER_ID
    }

    while True:
        with transaction.atomic():
            messages = (OutboxMessage.objects
                        .filter(sent=False)
                        .select_for_update(skip_locked=True)
                        .order_by("created_at")[:batch_size])

            for msg in messages:
                try:
                    resp = httpx.post(
                        settings.NOTIFICATIONS_API_URL,
                        headers=headers,
                        json=msg.payload,
                        timeout=10
                    )
                    resp.raise_for_status()

                    msg.sent = True
                    msg.sent_at = timezone.now()
                    msg.save()
                except Exception as e:
                    logger.error(f"Failed to send outbox message {msg.id}: {e}")

        time.sleep(sleep_seconds)
