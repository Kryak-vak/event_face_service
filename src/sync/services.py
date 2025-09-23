import logging
from datetime import date
from enum import Enum
from urllib.parse import parse_qs, urlencode, urlparse

from django.conf import settings
from django.db import DatabaseError, IntegrityError, transaction
from django.utils.dateparse import parse_datetime
from httpx import HTTPStatusError, RequestError
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from core.http_clients import EventApiClient
from events.models import Event, Venue

logger = logging.getLogger(__name__)


class SyncResult(Enum):
    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"


def sync_events(
        provider_url: str = settings.EVENT_PROVIDER_API_URL,
        from_date: date | None = None,
        sync_all: bool = False
    ) -> tuple[int, int, int]:
    
    if not from_date and not sync_all:
        last_updated_event = Event.objects.order_by("updated_at").last()
        if last_updated_event:
            from_date = last_updated_event.updated_at.date().isoformat()
    
    url = provider_url
    if not sync_all and from_date:
        url += "?" + urlencode({"changed_at": from_date})
    
    created_total, updated_total, failed_total = 0, 0, 0
    venue_cache = {}
    with EventApiClient() as client:
        while True:
            try:
                next_batch_url, events = fetch_event_batch(url, client)
            except (HTTPStatusError, RequestError, RetryError) as e:
                logger.exception(
                    f"Unable to fetch events from events-provider url={url}: {e}"
                )
                raise
            
            created, updated, failed = create_event_batch(
                events, venue_cache
            )
            created_total += created
            updated_total += updated
            failed_total += failed

            cursor = parse_qs(urlparse(url).query).get("cursor", "")
            logger.info(
                f"Synced batch ({cursor=}): "
                f"{created} created, {updated} updated, {failed} failed"
            )

            if not next_batch_url:
                break

            url = next_batch_url

    return created_total, updated_total, failed_total


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((RequestError, HTTPStatusError))
)
def fetch_event_batch(batch_url: str, client: EventApiClient) -> tuple[str, list[dict]]:
    resp = client.get(batch_url, timeout=30)
    resp.raise_for_status()
    resp_json = resp.json()

    next_batch_url = resp_json["next"]
    events = resp_json["results"]

    return next_batch_url, events


def create_event_batch(
        events: list[dict], venue_cache: dict[str, Venue]
    ) -> tuple[int, int, int]:
    created, updated, failed = 0, 0, 0
    for event in events:
        try:
            venue_data = event["place"]
            venue_id = venue_data["id"]

            with transaction.atomic():
                if venue_id in venue_cache:
                    venue = venue_cache[venue_id]
                else:
                    venue = create_or_update_venue(venue_data)
                    venue_cache[venue_id] = venue

                _, sync_result = create_or_update_event(event, venue)
            
            if sync_result == SyncResult.CREATED:
                created += 1
            elif sync_result == SyncResult.UPDATED:
                updated += 1
        except KeyError as e:
            logger.error(f"Missing required key in event: {e}")
            failed += 1
            continue
        except (IntegrityError, DatabaseError) as e:
            logger.exception(f"Database error while creating/updating event: {e}")
            failed += 1
            continue

    return created, updated, failed


def create_or_update_venue(venue_data: dict) -> Venue:
    provider_id=venue_data["id"]
    defaults={
        "name": venue_data["name"]
    }
    
    try:
        venue = (
            Venue.objects.get(provider_id=provider_id)
        )
        changed = False
        for field, value in defaults.items():
            if getattr(venue, field) != value:
                setattr(venue, field, value)
                changed = True
        
        if changed:
            venue.save(update_fields=tuple(defaults.keys()))
    except Venue.DoesNotExist:
        venue = Venue.objects.create(provider_id=provider_id, **defaults)
    
    return venue


def create_or_update_event(
        event_data: dict, venue: Venue
    ) -> tuple[Event, SyncResult]:
    provider_id = event_data["id"]
    defaults = {
        "name": event_data["name"],
        "event_time": parse_datetime(event_data["event_time"]),
        "registration_deadline": parse_datetime(event_data["registration_deadline"]),
        "status": event_data["status"],
        "venue": venue,
    }

    try:
        event = (
            Event.objects
            .select_related("venue")
            .get(provider_id=provider_id)
        )
        changed = False
        for field, value in defaults.items():
            if getattr(event, field) != value:
                setattr(event, field, value)
                changed = True
        
        if changed:
            event.save(update_fields=tuple(defaults.keys()))
            return event, SyncResult.UPDATED
        
        return event, SyncResult.UNCHANGED
    except Event.DoesNotExist:
        event = Event.objects.create(provider_id=provider_id, **defaults)
        return event, SyncResult.CREATED
