from event.models import BetaSubscriber
from event.signals import event_scraped
from event.factory.scrapers import Scrapper
from urllib.parse import urlparse
import re
from django.utils.text import slugify
from event.models import Event
from django.contrib.auth.models import User
from rest_framework import serializers
from event.models import Event, City, Location, Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["country_name", "iso2_code", "iso3_code"]


class LocationSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Location
        fields = ["state_name", "state_code", "lat", "lng", "country"]


class CitySerializer(serializers.ModelSerializer):
    region = LocationSerializer()

    class Meta:
        model = City
        fields = ["id", "city_name", "city_ascii", "lat", "lng", "region"]


class SimpleCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ["id", "city_name", "city_ascii", "lat", "lng", "region"]


class EventSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = Event
        fields = [
            "title",
            "event_image",
            "start_date",
            "end_date",
            "description",
            "venue",
            "link",
            "city",
        ]


class SubmitEventSerializer(serializers.ModelSerializer):
    create_account = serializers.BooleanField(required=False, default=False)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    phone = serializers.CharField(max_length=15, required=False)
    event_image = serializers.ImageField(required=False)  # Optional banner upload

    class Meta:
        model = Event
        fields = [
            "event_image",
            "title",
            "start_date",
            "city",
            "when",
            "description",
            "venue",
            "event_source",
            "link",
            "first_name",
            "last_name",
            "email",
            "phone",
            "create_account",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def _generate_unique_username(self, base_username):
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username}{suffix}"
        return username

    def _create_account(self, validated_data):
        email = validated_data['email']
        base_username = slugify(email.split('@')[0])
        username = self._generate_unique_username(base_username)

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_unusable_password()
        user.save()
        return user

    def create(self, validated_data):
        create_account = validated_data.pop('create_account', False)
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        phone = validated_data.pop('phone', '')

        event = Event(**validated_data)
        event.submitter_first_name = first_name
        event.submitter_last_name = last_name
        event.submitter_email = email
        event.submitter_phone = phone
        event.submitter_account_created = False

        if create_account:
            user = self._create_account({
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            })
            event.submitter = user
            event.submitter_account_created = True

        event.save()
        return event


class SubmitEventLinkSerializer(serializers.Serializer):
    event_url = serializers.URLField()

    def validate_event_url(self, value):
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("The event link must start with http:// or https://")
        domain = self._slugify_domain(value)
        event_sources = {"lu-ma": "luma"}
        if domain not in event_sources:
            raise serializers.ValidationError(
                "The event link is not supported. Supported domains: " + ", ".join(event_sources.keys())
            )
        self.event_source = event_sources[domain]
        return value

    def _slugify_domain(self, link):
        parsed_url = urlparse(link)
        netloc = re.sub(r'^www\.', '', parsed_url.netloc)
        return netloc.replace('.', '-')

    def create(self, validated_data):
        scrapper = Scrapper(event_url=validated_data['event_url'], scrapper=self.event_source)
        event_data = scrapper.run()
        if event_data:
            event_scraped.send(__class__, event_data=event_data, source=self.event_source)
        return validated_data


class BetaSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BetaSubscriber
        fields = ['first_name', 'last_name', 'phone', 'email']

    def validate_email(self, value):
        if BetaSubscriber.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        if BetaSubscriber.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value


class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=True, help_text="Search keyword for events")


class SuggestionQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=True, help_text="Query for suggestions")
