from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event


class Command(BaseCommand):
    help = "Delete events older than 7 days"

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=7)
        deleted_count, _ = Event.objects.filter(event_time__lt=cutoff).delete()
        self.stdout.write(f"Cleanup done: {deleted_count} deleted")
