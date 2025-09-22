import logging
from datetime import date
from urllib.parse import urlencode

import httpx
from django.conf import settings
from django.db import transaction
from django.utils.dateparse import parse_datetime

from events.models import Event, Venue

logger = logging.getLogger(__name__)


def create_or_update_venue(venue_data: dict) -> Venue | None:
    if not venue_data:
        return None

    try:
        venue, _ = Venue.objects.update_or_create(
            provider_id=venue_data["id"],
            defaults={"name": venue_data["name"]}
        )
        return venue
    except Exception as e:
        logger.exception((
            f"Failed to update_or_create Venue"
            f"(provider_id={venue_data.get("id")}): {e}"
        ))
        return None


def create_or_update_event(
        event_data: dict, venue: Venue | None
    ) -> tuple[Event, bool] | None:
    try:
        event, created = Event.objects.update_or_create(
            provider_id=event_data["id"],
            defaults={
                "name": event_data["name"],
                "date": parse_datetime(event_data["date"]),
                "status": event_data["status"],
                "venue": venue,
            }
        )
        return event, created
    except Exception as e:
        logger.exception((
            f"Failed to update_or_create Event"
            f"(provider_id={event_data.get("id")}): {e}"
        ))
        return None


def sync_events(
        provider_url: str = settings.PROVIDER_API_URL,
        from_date: date | None = None,
        sync_all: bool = False
    ):
    
    if not from_date and not sync_all:
        last_event = Event.objects.order_by("-updated_at").first()
        if last_event:
            from_date = last_event.updated_at.date().isoformat()
    
    url = provider_url
    added, updated = 0, 0

    if not sync_all and from_date:
        url += "?" + urlencode({"changed_at": from_date})

    with httpx.Client() as client:
        resp = client.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, dict):
            if "results" in data:
                events = data["results"]
            elif "events" in data:
                events = data["events"]
            else:
                events = []
        else:
            events = data

    for event in events:
        venue = create_or_update_venue(event.get("venue", {}))
        event_result = create_or_update_event(event, venue)

        if event_result is None:
            continue

        _, created = event_result

        if created:
            added += 1
        else:
            updated += 1

    return added, updated