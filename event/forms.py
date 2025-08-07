from event.factory.scrapers import Scrapper
from event.signals import event_scraped
import re
from urllib.parse import urlparse
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
import meilisearch
from django.db.models import (Q, Count, F)
from django.utils.text import slugify
from accounts.signals import (user_signed_up)
from django.contrib.auth.models import User
from .models import Event, RecentSearch
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.db.models import Q, Case, When, Value, BooleanField
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django import forms
from event.models import (Event, City, RecentSearch, BetaSubscriber)
from django.db.models import (Case, When, Value, BooleanField, Q)

from django.conf import settings

PROD_ENV = getattr(settings, 'PRODUCTION_ENV', False)
GUEST_COOKIE_NAME = getattr(
    settings, 'GUEST_COOKIE_NAME', '_guest_user_cookies')


class SearchSuggestionForm(forms.Form):
    q = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None

    @property
    def search_filter(self):
        query = self.cleaned_data.get('q')
        if not query:
            return []

        events = Event.objects.filter(
            title__icontains=query
        ).values_list("title", flat=True)

        cities = City.objects.filter(
            Q(city_ascii__icontains=query) |
            Q(city_name__icontains=query)
            # Q(postal_code__icontains=query)
        ).values_list("city_ascii", flat=True)

        return list(events) + list(cities)


# res = client.index("events").search("Afro")
# print(res["hits"])
# res = client.index("cities").search("New York")
# print(res["hits"])
# doc = client.index("events").get_document("1")  # replace with a real ID
# print(doc)


class MeilisearchSearchSuggestionForm(forms.Form):
    q = forms.CharField(required=True)

    @property
    def search_filter(self):
        client = meilisearch.Client(
            settings.MEILISEARCH_URL, settings.MEILISEARCH_MASTER_KEY)

        query = self.cleaned_data.get('q')
        if not query:
            return []

        events = client.index("events").search(query).get("hits", [])
        cities = client.index("cities").search(query).get("hits", [])
        zips = client.index("zip_codes").search(query).get("hits", [])

        results = [{"name": e["title"], "type": "Event"} for e in events]
        results += [{"name": c["city_name"], "type": "City"} for c in cities]
        results += [{"name": z["zip_code"], "type": "ZipCode"} for z in zips]

        # Deduplicate by name
        seen = set()
        unique_results = []
        for item in results:
            key = item["name"].lower()
            if key not in seen:
                seen.add(key)
                unique_results.append(item)
        return unique_results


class BaseEventSearchForm2(forms.Form):
    q = forms.CharField(required=True)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def create_search_history(self, query: str) -> bool:
        cookies_id = self.request.COOKIES.get(GUEST_COOKIE_NAME)
        if cookies_id and not RecentSearch.objects.filter(
            cookies_id=cookies_id,
            search_keyword__iexact=query
        ).exists():
            RecentSearch.objects.create(
                cookies_id=cookies_id,
                search_keyword=query.lower(),
            )
            return True
        return False

    @property
    def filter_event(self):
        query = self.cleaned_data.get("q")
        if not query:
            return Event.objects.none()
        self.create_search_history(query)
        return self._filter_events_by_query(query)

    def _filter_events_by_query(self, query: str):
        raise NotImplementedError(
            "Subclasses must implement _filter_events_by_query."
        )


class BaseEventSearchForm(forms.Form):
    q = forms.CharField(required=True)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def create_search_history(self, query: str) -> bool:
        cookies_id = self.request.COOKIES.get(GUEST_COOKIE_NAME)
        if cookies_id and not RecentSearch.objects.filter(
            cookies_id=cookies_id,
            search_keyword__iexact=query
        ).exists():
            RecentSearch.objects.create(
                cookies_id=cookies_id,
                search_keyword=query.lower(),
            )
            return True
        return False

    @property
    def filter_event(self):
        query = self.cleaned_data.get("q")
        if not query:
            return Event.objects.none()
        self.create_search_history(query)
        return self._filter_events_by_query(query)

    def _filter_events_by_query(self, query: str):
        raise NotImplementedError(
            "Subclasses must implement _filter_events_by_query."
        )

    def get_event_recommendation(self):
        query = self.cleaned_data.get("q")
        search_query = SearchQuery(query) if query else None

        # Base queryset: upcoming events
        events = Event.objects.filter(start_date__gte=timezone.now().date())

        # Full-text search vector
        if search_query:
            search_vector = (
                SearchVector('title', weight='A') +
                SearchVector('venue', weight='B') +
                SearchVector('city__city_ascii', weight='B') +
                SearchVector('city__region__state_code', weight='C') +
                SearchVector('city__area_code', weight='B')
            )
            events = events.annotate(
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.05).order_by('-rank', 'start_date')
        else:
            events = events.order_by('start_date')

        # Add location filtering if possible
        try:
            lat = float(self.request.latitude)
            lng = float(self.request.longitude)
            user_location = Point(lng, lat, srid=4326)
            radius_km = 100  # Broader radius for recommendations

            nearby_city_ids = City.objects.annotate(
                distance=Distance('coords', user_location)
            ).filter(
                distance__lte=radius_km * 1000,
                active=True
            ).values_list('id', flat=True)

            events = events.filter(city__in=nearby_city_ids)

        except (AttributeError, TypeError, ValueError):
            # No location fallback - global recommendations only
            pass

        return events[:12]


class EventSearchForm(BaseEventSearchForm):
    def _filter_events_by_query(self, query: str):
        search_query = SearchQuery(query)
        search_vector = (
            SearchVector('title', weight='A') +
            SearchVector('city__region__short_name', weight='B') +
            SearchVector('city__city_ascii', weight='B') +
            SearchVector('city__region__state_code', weight='C') +
            SearchVector('city__area_code__zip_code', weight='B')

        )
        return (
            Event.objects.annotate(
                rank=SearchRank(search_vector, search_query),
                active=Case(
                    When(start_date__gte=timezone.now().date(), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                event_timestamp=F('start_date')  # Optional: alias for clarity
            )
            .filter(rank__gte=0.1, active=True)
            # First by date, then by best match
            .order_by('event_timestamp', '-rank')
            .distinct()
        )

        # return (
        #     Event.objects.annotate(
        #         rank=SearchRank(search_vector, search_query),
        #         active=Case(
        #             When(start_date__gte=timezone.now().date(), then=Value(True)),
        #             default=Value(False),
        #             output_field=BooleanField()
        #         )
        #     )
        #     .filter(rank__gte=0.1, active=True)
        #     .order_by('start_date', '-rank', )
        #     .distinct()
        # )


class SubmitEventForm(forms.ModelForm):
    create_account = forms.BooleanField(required=False)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    phone = forms.CharField(max_length=15, required=False)
    event_source = forms.ChoiceField(choices=Event.EVENT_SOURCE_CHOICES)
    event_image = forms.ImageField(required=False)

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
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email already exists.")
        return email

    def _generate_unique_username(self, base_username):
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username}{suffix}"
        return username

    def _create_account(self):
        email = self.cleaned_data['email']
        base_username = slugify(email.split('@')[0])
        username = self._generate_unique_username(base_username)

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        user.set_unusable_password()
        user.save()
        return user

    def save(self, commit=True):
        event = super().save(commit=False)

        # Populate submitter info
        event.submitter_first_name = self.cleaned_data['first_name']
        event.submitter_last_name = self.cleaned_data['last_name']
        event.submitter_email = self.cleaned_data['email']
        event.submitter_phone = self.cleaned_data['phone']
        event.submitter_account_created = False

        if self.cleaned_data.get('create_account'):
            user = self._create_account()
            event.submitter = user
            event.submitter_account_created = True
            user_signed_up.send(sender=self.__class__,
                                user=user, event=event, **self.cleaned_data)

        if commit:
            event.save()
        return event


class SubmitEventLinkForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_sources = {
            "lu-ma": "luma",
        }

    event_url = forms.URLField(
        required=True,
        label="Event Link",
        help_text="Enter the URL of the event page.",
        error_messages={
            'required': 'The event URL is required.',
            'invalid': 'Enter a valid event URL.'
        })

    def clean_event_url(self):
        link = self.cleaned_data.get('event_url')
        if not link.startswith(('http://', 'https://')):
            raise forms.ValidationError(
                "The event link must start with http:// or https://")
        domain = self.slugify_domain()
        if domain not in self.event_sources:
            raise forms.ValidationError(
                "The event link is not supported. Supported domains: " +
                ", ".join(self.event_sources.keys()))
        self.event_source = self.event_sources[domain]
        return link

    def slugify_domain(self):
        link = self.cleaned_data.get('event_url')

        parsed_url = urlparse(link)
        netloc = parsed_url.netloc
        netloc = re.sub(r'^www\.', '', netloc)
        slug = netloc.replace('.', '-')
        return slug

    def save(self, commit=True):

        scrapper = Scrapper(
            event_url=self.cleaned_data['event_url'],
            scrapper=self.event_source
        )
        event_data = scrapper.run()
        if event_data:
            # send signal that an event link has been submitted
            event_scraped.send(__class__, event_data=event_data, source=self.event_source,
                               )

        return self.cleaned_data


class BetaSubscriberForm(forms.ModelForm):
    class Meta:
        model = BetaSubscriber
        fields = ['email', 'phone', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BetaSubscriber.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email already exists.")
        return email

    def save(self, commit=True):
        join_beta = super().save(commit=False)
        if commit:
            join_beta.save()
        return join_beta


# Select appropriate form based on environment
# EventSearchForm = ProdEventSearchForm if PROD_ENV else LocalEventSearchForm
# EventSearchForm = ProdEventSearchForm
