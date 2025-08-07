from event.signals import event_scraped
from django.dispatch import receiver
from event.factory.scrapers.event_saver import EventSaver


@receiver(event_scraped)
def handle_luma_event_scraped(sender, event_data, source, **kwargs):
    if event_data.get('event_source') != 'luma':
        event = EventSaver(event_data)
        event.save()
