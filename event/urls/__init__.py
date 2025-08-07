from .location_urls import urlpatterns as location_url_patterns
from .event_urls import urlpatterns as event_url_paterns

urlpatterns = location_url_patterns + event_url_paterns
