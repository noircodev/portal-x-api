from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SERP_API_ENDPOINT = "https://2e6f913b-08d8-4465-9f79-3fecc6edc280.mock.pstmn.io"
SERP_API_KEY = getattr(settings, 'SERP_API_KEY', None)
EVENT_ENGINES = getattr(settings, 'EVENT_ENGINES', None)
EVENTBRITE_API_KEY = getattr(settings, 'EVENTBRITE_API_KEY', None)
EVENTBRITE_API_ENDPOINT = getattr(settings, 'EVENTBRITE_API_ENDPOINT', None)

SERP_API_ENDPOINT = getattr(
    settings, 'SERP_API_ENDPOINT', SERP_API_ENDPOINT)

TICKET_MASTER_API_KEY = getattr(
    settings, 'TICKET_MASTER_API_KEY', None)


class AppSettings:
    def __init__(self):
        self.keys = {
            "SERP_API_KEY": SERP_API_KEY,
            "SERP_API_ENDPOINT": SERP_API_ENDPOINT,
            "TICKET_MASTER_API_KEY": TICKET_MASTER_API_KEY,
            "EVENTBRITE_API_KEY": EVENTBRITE_API_KEY,
            "EVENTBRITE_API_ENDPOINT": EVENTBRITE_API_ENDPOINT,
        }

    def __getattr__(self, item):
        """Raise an error if an API key is not initialized."""
        if item in self.keys:
            if self.keys[item] is None:
                raise ImproperlyConfigured(f"{item} is not initialized.")
            return self.keys[item]
        raise AttributeError(
            f"'{__class__}' object has no attribute '{item}'")

    def get_all_keys(self):
        """Returns all API keys as a dictionary, raising an error for any uninitialized key."""
        for key, value in self.keys.items():
            if value is None:
                raise ImproperlyConfigured(f"{key} is not initialized.")
        return self.keys


app_settings = AppSettings()
