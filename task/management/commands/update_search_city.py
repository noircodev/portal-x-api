from django.core.management.base import BaseCommand
from django.conf import settings
from event.models import (SearchPhrase, Location, )


class Command(BaseCommand):
    help = "Sync Event, City, and Zip Code data to Meilisearch"

    def handle(self, *args, **kwargs):
        active_region = Location.objects.filter(active=True)
        search = SearchPhrase.objects.filter(active=True)
        for phrase in search:
            self.stdout.write(self.style.SUCCESS(
                f"Updating regions for {phrase.query}."))

            phrase.location.set(active_region)
            phrase.save()
        self.stdout.write(self.style.SUCCESS(
            "Search regions updated successfully."))
