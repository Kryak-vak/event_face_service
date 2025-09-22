from datetime import date

from django.core.management.base import BaseCommand

from sync.models import SyncLog
from sync.services import sync_events


class Command(BaseCommand):
    help = "Synchronize events from provider"

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true", help="Full sync")
        parser.add_argument("--date",
                            type=date.fromisoformat,
                            help="Sync events changed since this date (YYYY-MM-DD)")

    def handle(self, *args, **options):
        created, updated = sync_events(
            from_date=options["date"], sync_all=options["all"]
        )

        SyncLog.objects.create(created_count=created, updated_count=updated)
        self.stdout.write(
            self.style.SUCCESS(f"Sync done: {created} created, {updated} updated")
        )