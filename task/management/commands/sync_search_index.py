from django.utils import timezone
import meilisearch
from django.core.management.base import BaseCommand
from django.conf import settings
from event.models import Event, City, ZipCode


class Command(BaseCommand):
    help = "Sync Event, City, and Zip Code data to Meilisearch"

    def handle(self, *args, **kwargs):
        client = meilisearch.Client(
            settings.MEILISEARCH_URL,
            settings.MEILISEARCH_MASTER_KEY
        )

        # Indexes
        event_index = client.index("events")
        city_index = client.index("cities")
        zip_index = client.index("zip_codes")

        # Clean old documents
        event_index.delete_all_documents()
        city_index.delete_all_documents()
        zip_index.delete_all_documents()

        # Events
        events = [
            {
                "id": e.pk,
                "title": e.title,
                # "event_city_id": e.city.pk,
                # "event_city_name": e.city.city_name,
            }

            for e in Event.objects.filter(
                start_date__gte=timezone.now().date(), city__isnull=False
            )
        ]
        if events:
            event_index.add_documents(events)

            event_index.update_settings({
                "searchableAttributes": ["title"],
                # "filterableAttributes": ["event_city_id", "event_city_name"],# This is problematic with Meilisearch
                "typoTolerance": {
                    "enabled": True,
                    "minWordSizeForTypos": {
                        "oneTypo": 5,
                        "twoTypos": 9
                    }
                }
            })

        self.stdout.write(self.style.SUCCESS(
            f"Indexed {len(events)} events."))

        # Cities (keep for other search types)
        cities = []
        for c in City.objects.all():
            cities.append({
                "id": c.pk,
                "name": c.city_ascii,
                "city_name": c.city_name,
                "city_ascii": c.city_ascii,
                "state": c.region.state_name,
                "short_name": c.region.short_name if c.region.short_name else None,
            })

        if cities:
            city_index.add_documents(cities)
            city_index.update_settings({
                "searchableAttributes": ["name", "city_name", "city_ascii"],
                "filterableAttributes": ["state", "short_name"],
            })
            self.stdout.write(self.style.SUCCESS(
                f"Indexed {len(cities)} cities."))

        # Zip Codes
        zips = []
        for z in ZipCode.objects.filter(active=True):
            zips.append({
                "id": z.pk,
                "zip_code": z.zip_code,
                "city_name": z.city.city_ascii,
                "state_name": z.state.state_name,
            })

        if zips:
            zip_index.add_documents(zips)
            zip_index.update_settings({
                "searchableAttributes": ["zip_code"],
                "filterableAttributes": ["city_name", "state_name"],
            })
            self.stdout.write(self.style.SUCCESS(
                f"Indexed {len(zips)} zip codes."))

        self.stdout.write(self.style.SUCCESS("Meilisearch indexing complete."))
