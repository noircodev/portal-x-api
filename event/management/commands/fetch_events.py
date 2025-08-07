from event.factory.engine import SearchEngine
from django.core.management.base import BaseCommand
from event.factory.engine import (SearchEngine)


class Command(BaseCommand):
    help = "Fetch and update event list"

    def add_arguments(self, parser):
        parser.add_argument(
            '-e', "--engine",
            help="Specify event search engine (`serp_api_google_event`, `eventbrite`, `all_events`, `artidea)",
            action="store",
            dest="engine",
            default='serp_api_google_event'  # Default value if not provided
        )

    def handle(self, *args, **kwargs):
        engine = kwargs.get('engine')
        search = SearchEngine(engine=engine)
        if search.engine:
            search.perform_search()
            self.stdout.write(self.style.SUCCESS(
                "Event search completed successfully"))
        else:
            self.stdout.write(self.style.ERROR(
                "Invalid search engine specified"))
