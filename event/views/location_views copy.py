from rest_framework import viewsets
from event.models import Country, Location, City
from event.api.serializers import CountrySerializer, LocationSerializer, CitySerializer
from event.api.permissions import ReadOnlyOrAuthenticated


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [ReadOnlyOrAuthenticated]


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.select_related("country").all()
    serializer_class = LocationSerializer
    permission_classes = [ReadOnlyOrAuthenticated]


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.select_related("region", "region__country").all()
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAuthenticated]
