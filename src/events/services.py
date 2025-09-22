import logging
import random
import string

from django.db import transaction

from .exceptions import AlreadyRegisteredError, EventClosedError, NotificationSendError
from .models import Event, EventRegistration, OutboxMessage

logger = logging.getLogger(__name__)


def generate_confirmation_code(length=8):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def register_event(event: Event, full_name: str, email: str, owner_id: str):
    if event.status != Event.Status.OPEN:
        raise EventClosedError("Event is not open for registration.")

    with transaction.atomic():
        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            email=email,
            defaults={
                "full_name": full_name,
                "confirmation_code": generate_confirmation_code()
            }
        )

        if not created:
            raise AlreadyRegisteredError("You are already registered for this event.")

        payload = {
            "owner_id": owner_id,
            "recipients": [email],
            "subject": f"Confirmation for {event.name}",
            "message": f"Conformation code {registration.confirmation_code}"
        }

        OutboxMessage.objects.create(
            topic="event_registration_created",
            payload=payload
        )

    return registration
