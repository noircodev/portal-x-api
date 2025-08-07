# urls.py - URL patterns for the converted APIViews

from django.urls import path
from event.views.location_views import (
    # Country Views - Separate approach
    CountryListView,
    CountryDetailView,
    CountryCreateView,
    CountryUpdateView,
    CountryDeleteView,

    # Location Views - Separate approach
    LocationListView,
    LocationDetailView,
    LocationCreateView,
    LocationUpdateView,
    LocationDeleteView,

    # City Views - Separate approach
    CityListView,
    CityDetailView,
    CityCreateView,
    CityUpdateView,
    CityDeleteView,

    # Alternative combined approach
    CountryAPIView,
)

# Option 1: Separate views for each operation (Recommended for REST best practices)
urlpatterns = [
    # Country endpoints
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('countries/create/', CountryCreateView.as_view(), name='country-create'),
    path('countries/<int:pk>/', CountryDetailView.as_view(), name='country-detail'),
    path('countries/<int:pk>/update/', CountryUpdateView.as_view(), name='country-update'),
    path('countries/<int:pk>/delete/', CountryDeleteView.as_view(), name='country-delete'),

    # Location/State endpoints
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('locations/create/', LocationCreateView.as_view(), name='location-create'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),
    path('locations/<int:pk>/update/', LocationUpdateView.as_view(), name='location-update'),
    path('locations/<int:pk>/delete/', LocationDeleteView.as_view(), name='location-delete'),

    # Alternative: More RESTful URLs (shorter)
    path('states/', LocationListView.as_view(), name='state-list'),
    path('states/create/', LocationCreateView.as_view(), name='state-create'),
    path('states/<int:pk>/', LocationDetailView.as_view(), name='state-detail'),
    path('states/<int:pk>/update/', LocationUpdateView.as_view(), name='state-update'),
    path('states/<int:pk>/delete/', LocationDeleteView.as_view(), name='state-delete'),

    # City endpoints
    path('cities/', CityListView.as_view(), name='city-list'),
    path('cities/create/', CityCreateView.as_view(), name='city-create'),
    path('cities/<int:pk>/', CityDetailView.as_view(), name='city-detail'),
    path('cities/<int:pk>/update/', CityUpdateView.as_view(), name='city-update'),
    path('cities/<int:pk>/delete/', CityDeleteView.as_view(), name='city-delete'),
]

# Option 2: More RESTful approach (similar to ViewSet routing)
rest_urlpatterns = [
    # Countries
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('countries/', CountryCreateView.as_view(), name='country-create'),  # Same URL, different method
    path('countries/<int:pk>/', CountryDetailView.as_view(), name='country-detail'),
    path('countries/<int:pk>/', CountryUpdateView.as_view(), name='country-update'),  # Same URL, different method
    path('countries/<int:pk>/', CountryDeleteView.as_view(), name='country-delete'),  # Same URL, different method

    # Locations/States
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('locations/', LocationCreateView.as_view(), name='location-create'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),
    path('locations/<int:pk>/', LocationUpdateView.as_view(), name='location-update'),
    path('locations/<int:pk>/', LocationDeleteView.as_view(), name='location-delete'),

    # Cities
    path('cities/', CityListView.as_view(), name='city-list'),
    path('cities/', CityCreateView.as_view(), name='city-create'),
    path('cities/<int:pk>/', CityDetailView.as_view(), name='city-detail'),
    path('cities/<int:pk>/', CityUpdateView.as_view(), name='city-update'),
    path('cities/<int:pk>/', CityDeleteView.as_view(), name='city-delete'),
]

# Option 3: Combined APIView approach (single endpoint per resource)
combined_urlpatterns = [
    # Combined views (handles multiple HTTP methods in single view)
    path('countries/', CountryAPIView.as_view(), name='countries'),
    path('countries/<int:pk>/', CountryAPIView.as_view(), name='country-detail'),

    # You can create similar combined views for Location and City
    # path('locations/', LocationAPIView.as_view(), name='locations'),
    # path('locations/<int:pk>/', LocationAPIView.as_view(), name='location-detail'),
    # path('cities/', CityAPIView.as_view(), name='cities'),
    # path('cities/<int:pk>/', CityAPIView.as_view(), name='city-detail'),
]

# Option 4: Nested resources (if you want hierarchical URLs)
nested_urlpatterns = [
    # Countries
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('countries/<int:pk>/', CountryDetailView.as_view(), name='country-detail'),

    # States within countries
    path('countries/<int:country_id>/states/', LocationListView.as_view(), name='country-states'),
    path('countries/<int:country_id>/states/<int:pk>/', LocationDetailView.as_view(), name='country-state-detail'),

    # Cities within states
    path('states/<int:state_id>/cities/', CityListView.as_view(), name='state-cities'),
    path('states/<int:state_id>/cities/<int:pk>/', CityDetailView.as_view(), name='state-city-detail'),

    # Direct access to all locations and cities
    path('states/', LocationListView.as_view(), name='location-list'),
    path('states/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),
    path('cities/', CityListView.as_view(), name='city-list'),
    path('cities/<int:pk>/', CityDetailView.as_view(), name='city-detail'),
]

# You can also create custom views for specific use cases
custom_urlpatterns = [
    # Custom endpoints for specific business logic
    path('countries/active/', CountryListView.as_view(), {'active_only': True}, name='active-countries'),
    path('cities/by-region/<int:region_id>/', CityListView.as_view(), name='cities-by-region'),
    path('locations/with-cities/', LocationListView.as_view(), {'with_cities_only': True}, name='locations-with-cities'),
]

# Final recommended URL structure (combining the best of both worlds)
recommended_urlpatterns = [
    # Geography endpoints
    path('geography/countries/', CountryListView.as_view(), name='country-list'),
    path('geography/countries/create/', CountryCreateView.as_view(), name='country-create'),
    path('geography/countries/<int:pk>/', CountryDetailView.as_view(), name='country-detail'),
    path('geography/countries/<int:pk>/update/', CountryUpdateView.as_view(), name='country-update'),
    path('geography/countries/<int:pk>/delete/', CountryDeleteView.as_view(), name='country-delete'),

    path('geography/states/', LocationListView.as_view(), name='location-list'),
    path('geography/states/create/', LocationCreateView.as_view(), name='location-create'),
    path('geography/states/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),
    path('geography/states/<int:pk>/update/', LocationUpdateView.as_view(), name='location-update'),
    path('geography/states/<int:pk>/delete/', LocationDeleteView.as_view(), name='location-delete'),

    path('geography/cities/', CityListView.as_view(), name='city-list'),
    path('geography/cities/create/', CityCreateView.as_view(), name='city-create'),
    path('geography/cities/<int:pk>/', CityDetailView.as_view(), name='city-detail'),
    path('geography/cities/<int:pk>/update/', CityUpdateView.as_view(), name='city-update'),
    path('geography/cities/<int:pk>/delete/', CityDeleteView.as_view(), name='city-delete'),
]

# If you need to maintain backward compatibility with ViewSet URLs
# You can use DefaultRouter-like patterns:
viewset_compatible_urlpatterns = [
    # Country ViewSet equivalent
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('countries/', CountryCreateView.as_view(), name='country-list'),  # POST to same URL
    path('countries/<int:pk>/', CountryDetailView.as_view(), name='country-detail'),
    path('countries/<int:pk>/', CountryUpdateView.as_view(), name='country-detail'),  # PUT/PATCH to same URL
    path('countries/<int:pk>/', CountryDeleteView.as_view(), name='country-detail'),  # DELETE to same URL

    # Location ViewSet equivalent
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('locations/', LocationCreateView.as_view(), name='location-list'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),
    path('locations/<int:pk>/', LocationUpdateView.as_view(), name='location-detail'),
    path('locations/<int:pk>/', LocationDeleteView.as_view(), name='location-detail'),

    # City ViewSet equivalent
    path('cities/', CityListView.as_view(), name='city-list'),
    path('cities/', CityCreateView.as_view(), name='city-list'),
    path('cities/<int:pk>/', CityDetailView.as_view(), name='city-detail'),
    path('cities/<int:pk>/', CityUpdateView.as_view(), name='city-detail'),
    path('cities/<int:pk>/', CityDeleteView.as_view(), name='city-detail'),
]
