from rest_framework.routers import DefaultRouter
from event.views.location_views import CountryViewSet, LocationViewSet, CityViewSet
from django.urls import (path, include)

router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'cities', CityViewSet, basename='city')

urlpatterns = [
    path('api/', include(router.urls)),
]
