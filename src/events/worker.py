import logging
import time

from django.conf import settings
from django.db import DatabaseError, transaction
from django.utils import timezone
from httpx import HTTPStatusError, RequestError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from core.http_clients import EventApiClient

from .models import OutboxMessage

logger = logging.getLogger(__name__)

def process_outbox(batch_size=100, sleep_seconds=1):
    while True:
        with transaction.atomic():
            messages = (OutboxMessage.objects
                        .filter(sent=False)
                        .select_for_update(skip_locked=True)
                        .order_by("created_at")[:batch_size])
            
            with EventApiClient() as client:
                for msg in messages:
                    try:
                        payload = {
                            "id": msg.id,
                            "email": msg.payload["email"],
                            "message": msg.payload["email_message"],
                        }

                        make_notification_request(client, payload)

                        msg.sent = True
                        msg.sent_at = timezone.now()
                        msg.save()
                    except (HTTPStatusError, RequestError) as e:
                        logger.exception(
                            f"Unable to send outbox message ({msg.id}): {e}"
                        )
                        raise
                    except (DatabaseError) as e:
                        logger.exception(
                            f"Database error while saving outbox message {msg.id}: {e}"
                        )

        time.sleep(sleep_seconds)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((RequestError, HTTPStatusError))
)
def make_notification_request(client: EventApiClient, payload: dict, timeout: int = 10) -> None:
    resp = client.post(
        settings.NOTIFICATIONS_API_URL,
        json=payload,
        timeout=timeout
    )
    resp.raise_for_status()
