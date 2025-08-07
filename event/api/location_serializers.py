from rest_framework import serializers
from event.models import Country, Location, City


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "country_name", "iso2_code", "iso3_code"]


class LocationSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Location
        fields = ["id", "state_name", "short_name", "state_code", "lat", "lng", "country"]


class CitySerializer(serializers.ModelSerializer):
    region = LocationSerializer(read_only=True)

    class Meta:
        model = City
        fields = ["id", "city_name", "city_ascii", "lat", "lng", "region"]
