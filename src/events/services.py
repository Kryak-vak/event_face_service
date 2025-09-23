import logging
import random
import string
from uuid import uuid4

from django.db import transaction

from .exceptions import AlreadyRegisteredError, EventClosedError
from .models import Event, EventRegistration, OutboxMessage

logger = logging.getLogger(__name__)


def generate_confirmation_code(length=8):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def register_event(event: Event, full_name: str, email: str) -> None:
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

        message_id = uuid4()
        OutboxMessage.objects.create(
            id=message_id,
            topic="event_registration_created",
            payload={
                "message_id": str(message_id),
                "registration_id": str(registration.id),
                "event_id": str(registration.event.id),
                "full_name": registration.full_name,
                "email": registration.email,
                "email_message": f"Код подтверждения: {registration.confirmation_code}",
            }
        )

