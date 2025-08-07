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
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.openapi import OpenApiTypes


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for Country model."""

    class Meta:
        model = Country
        fields = ["country_name", "iso2_code", "iso3_code"]


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location (State) model."""
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Location
        fields = ["state_name", "state_code", "lat", "lng", "country"]


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model."""
    region = LocationSerializer(read_only=True)

    class Meta:
        model = City
        fields = ["id", "city_name", "city_ascii", "lat", "lng", "region"]


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model with nested city information."""
    city = CitySerializer(read_only=True)

    @extend_schema_field(OpenApiTypes.URI)
    def get_event_image(self, obj):
        """Get event image URL or default placeholder."""
        return obj.get_event_image

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "event_image",
            "start_date",
            "end_date",
            "description",
            "venue",
            "link",
            "city",
            "featured",
        ]


class SubmitEventSerializer(serializers.ModelSerializer):
    """Serializer for submitting new events with optional user account creation."""

    # Additional fields for user information
    create_account = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Create a user account for the event submitter"
    )
    first_name = serializers.CharField(
        max_length=100,
        help_text="Submitter's first name"
    )
    last_name = serializers.CharField(
        max_length=100,
        help_text="Submitter's last name"
    )
    email = serializers.EmailField(
        max_length=100,
        help_text="Submitter's email address"
    )
    phone = serializers.CharField(
        max_length=15,
        required=False,
        help_text="Submitter's phone number (optional)"
    )
    event_image = serializers.ImageField(
        required=False,
        help_text="Event banner image (optional)"
    )

    class Meta:
        model = Event
        fields = [
            "event_image",
            "title",
            "start_date",
            "end_date",
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
        extra_kwargs = {
            'title': {'help_text': 'Event title'},
            'start_date': {'help_text': 'Event start date (YYYY-MM-DD)'},
            'end_date': {'help_text': 'Event end date (YYYY-MM-DD), optional'},
            'city': {'help_text': 'City where the event takes place'},
            'when': {'help_text': 'Time description (e.g., "7:00 PM - 10:00 PM")'},
            'description': {'help_text': 'Detailed event description'},
            'venue': {'help_text': 'Event venue name and address'},
            'link': {'help_text': 'External event link (optional)'},
        }

    def validate_email(self, value):
        """Validate that email is unique if creating account."""
        create_account = self.initial_data.get('create_account', False)
        if create_account and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def _generate_unique_username(self, base_username):
        """Generate a unique username based on email."""
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username}{suffix}"
        return username

    def _create_account(self, validated_data):
        """Create a new user account."""
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
        """Create a new event with submitter information."""
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
    """Serializer for submitting events via external links."""

    event_url = serializers.URLField(
        help_text="URL to scrape event information from supported platforms"
    )

    def validate_event_url(self, value):
        """Validate the event URL is from a supported domain."""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("The event link must start with http:// or https://")

        domain = self._slugify_domain(value)
        event_sources = {"lu-ma": "luma"}

        if domain not in event_sources:
            raise serializers.ValidationError(
                f"The event link is not supported. Supported domains: {', '.join(event_sources.keys())}"
            )

        self.event_source = event_sources[domain]
        return value

    def _slugify_domain(self, link):
        """Extract and slugify domain from URL."""
        parsed_url = urlparse(link)
        netloc = re.sub(r'^www\.', '', parsed_url.netloc)
        return netloc.replace('.', '-')

    def create(self, validated_data):
        """Scrape event data from the provided URL."""
        scrapper = Scrapper(event_url=validated_data['event_url'], scrapper=self.event_source)
        event_data = scrapper.run()
        if event_data:
            event_scraped.send(__class__, event_data=event_data, source=self.event_source)
        return validated_data


class BetaSubscriberSerializer(serializers.ModelSerializer):
    """Serializer for beta program subscribers."""

    class Meta:
        model = BetaSubscriber
        fields = ['first_name', 'last_name', 'phone', 'email']
        extra_kwargs = {
            'first_name': {'help_text': 'Subscriber first name'},
            'last_name': {'help_text': 'Subscriber last name'},
            'phone': {'help_text': 'Subscriber phone number'},
            'email': {'help_text': 'Subscriber email address'},
        }

    def validate_email(self, value):
        """Validate email uniqueness."""
        if BetaSubscriber.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        """Validate phone number uniqueness."""
        if BetaSubscriber.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value


class SearchQuerySerializer(serializers.Serializer):
    """Serializer for search query parameters."""

    q = serializers.CharField(
        required=True,
        help_text="Search keyword for events",
        min_length=1,
        max_length=200
    )


class SuggestionQuerySerializer(serializers.Serializer):
    """Serializer for search suggestion query parameters."""

    q = serializers.CharField(
        required=True,
        help_text="Query string for autocomplete suggestions",
        min_length=1,
        max_length=100
    )


class SearchSuggestionResponseSerializer(serializers.Serializer):
    """Response serializer for search suggestions."""

    name = serializers.CharField(help_text="Suggestion name")
    type = serializers.ChoiceField(
        choices=[('Event', 'Event'), ('City', 'City'), ('ZipCode', 'Zip Code')],
        help_text="Type of suggestion"
    )


class ApiResponseSerializer(serializers.Serializer):
    """Generic API response serializer."""

    status = serializers.CharField(help_text="Response status")
    success = serializers.BooleanField(help_text="Success indicator")
    message = serializers.CharField(help_text="Response message")


class IndexResponseSerializer(ApiResponseSerializer):
    """Response serializer for index/home page."""

    events = EventSerializer(many=True, help_text="List of upcoming events")
    featured_events = EventSerializer(many=True, help_text="List of featured events")


class ErrorResponseSerializer(serializers.Serializer):
    """Error response serializer."""

    detail = serializers.CharField(help_text="Error message")
    field_errors = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        required=False,
        help_text="Field-specific validation errors"
    )


# For better doc


# Additional utility serializers for better documentation


class PaginationResponseSerializer(serializers.Serializer):
    """Standard pagination response format."""
    count = serializers.IntegerField(help_text="Total number of items")
    next = serializers.URLField(allow_null=True, help_text="URL to next page")
    previous = serializers.URLField(allow_null=True, help_text="URL to previous page")
    results = serializers.ListField(help_text="List of results")


class ValidationErrorSerializer(serializers.Serializer):
    """Standard validation error response."""
    field_name = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of validation errors for this field"
    )

    class Meta:
        # This allows for dynamic field names in validation errors
        extra_kwargs = {'field_name': {'help_text': 'Field-specific validation errors'}}


# Custom field extensions for better documentation
class CustomChoiceField(serializers.ChoiceField):
    """Custom choice field with better OpenAPI documentation."""

    @extend_schema_field({
        'type': 'string',
        'enum': [],  # Will be populated automatically
        'description': 'Available choices will be listed here'
    })
    def to_representation(self, value):
        return super().to_representation(value)


# Event-specific utility serializers
class EventStatusSerializer(serializers.Serializer):
    """Event status information."""
    is_active = serializers.BooleanField(help_text="Whether the event is still upcoming")
    days_until_event = serializers.IntegerField(help_text="Number of days until event starts")
    is_featured = serializers.BooleanField(help_text="Whether the event is featured")


class EventStatsSerializer(serializers.Serializer):
    """Event statistics for dashboard."""
    total_events = serializers.IntegerField(help_text="Total number of events")
    active_events = serializers.IntegerField(help_text="Number of active/upcoming events")
    featured_events = serializers.IntegerField(help_text="Number of featured events")
    cities_with_events = serializers.IntegerField(help_text="Number of cities with events")
