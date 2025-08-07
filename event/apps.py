from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'event'
    verbose_name = "Event Management"

    def ready(self):
        # Import signals to ensure they are registered
        from event import signals
        from event import process_event
