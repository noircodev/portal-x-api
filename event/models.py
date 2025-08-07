
from django.contrib.gis.geos import Point
from django.contrib.gis.db import models as gis_models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils.text import Truncator
from django.utils import timezone
from django.db import models
from task.utils.common_timezone import TIMEZONE_CHOICES


class Country(models.Model):
    class Meta:
        ordering = ['country_name']
        verbose_name_plural = "Countries"
    country_name = models.CharField(max_length=100)
    iso2_code = models.CharField(max_length=20)
    iso3_code = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    valided = models.BooleanField(default=True)

    def __str__(self):
        return self.country_name


class Location(models.Model):
    class Meta:
        verbose_name_plural = "States"
        verbose_name = "State"
        ordering = ['state_name', 'state_code']
    state_name = models.CharField(max_length=250)
    short_name = models.CharField(max_length=250, blank=True, null=True)
    state_code = models.CharField(max_length=5)
    timezone = models.CharField(
        max_length=250, choices=TIMEZONE_CHOICES, default='America/New_York')
    lat = models.CharField(max_length=15)
    lng = models.CharField(max_length=15)
    radius_km = models.PositiveIntegerField(default=300)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def get_zip_codes(self):
        return City.objects.filter(region=self)

    def __str__(self):
        return f"{self.state_name} - {self.state_code}"

    def get_cities(self):
        return City.objects.filter(region=self, active=True)

    @property
    def get_city_code(self):
        return f"{self.state_code}".lower()


class City(models.Model):
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['region__state_name', 'city_ascii']
    city_name = models.CharField(max_length=250)
    city_ascii = models.CharField(max_length=250)
    county_name = models.CharField(max_length=250, blank=True, null=True)
    region = models.ForeignKey(Location, on_delete=models.CASCADE)
    coords = gis_models.PointField(geography=True)
    lat = models.DecimalField(max_digits=10, decimal_places=6)
    lng = models.DecimalField(max_digits=10, decimal_places=6)
    # postal_code = models.CharField(max_length=250, blank=True, null=True)
    metro_code = models.CharField(max_length=250, blank=True, null=True)
    timezone = models.CharField(max_length=100, blank=True, null=True)
    dma_code = models.CharField(max_length=250, blank=True, null=True)
    eventbrite_slug = models.CharField(max_length=50, blank=True, null=True)
    all_event_in_slug = models.CharField(max_length=50, blank=True, null=True)
    # for faster search
    area_code = models.ManyToManyField(
        "ZipCode", blank=True, related_name='rel_cities')
    active = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city_name}-{self.region.state_code}"

    def get_city_name(self):
        if self.city_name:
            return self.city_name
        return self.city_ascii or "Unknown City"

    def save(self, *args, **kwargs):
        if (not self.coords) and (self.lat and self.lng):
            self.coords = Point(
                round(float(self.lat), 4),
                round(float(self.lng), 4),
            )
        super(City, self).save(*args, **kwargs)

    @property
    def get_eventbrite_slug(self):
        if self.eventbrite_slug:
            return self.eventbrite_slug
        elif self.region.state_code.lower() == 'ny':
            return f"{self.region.state_code.lower()}--new-york--{slugify(self.city_ascii)}"
        return f"{self.region.state_code.lower()}--{slugify(self.city_ascii)}"

    @property
    def get_all_event_in_slug(self):
        '''Sample slug:
            st-louis/afrobeats
        '''
        if self.all_event_in_slug:
            return self.all_event_in_slug
        return f"{slugify(self.city_ascii)}"


class ZipCode(models.Model):
    zip_code = models.CharField(max_length=20, unique=True)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='rel_zip_codes')
    state = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='rel_zip_codes')
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Zip Codes"
        ordering = ['zip_code']

    def __str__(self):
        return f"{self.zip_code} - {self.city.county_name}, {self.state.state_name}"


class SearchPhrase(models.Model):
    class Meta:
        ordering = ['query']
        verbose_name_plural = "Search Phrases"
    query = models.CharField(max_length=250)
    location = models.ManyToManyField(Location)
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='search_phrase', null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    @property
    def get_locations(self):
        return self.location.all()

    def get_location_count(self):
        return self.location.all().count()

    def get_added_by(self):
        return self.added_by.get_full_name() if self.added_by else "System"

    def __str__(self):
        return self.query


class Event(models.Model):
    EVENT_SOURCE_CHOICES = (
        ("all_events_in", "All Events In"),
        ("eventbrite", "Eventbrite"),
        ("user_submitted", "User Submitted"),
        ("serp_api_google_event", "Google Event Search"),
        ("artidea", "Art Idea"),
        ("added_by_admin", "Added by Admin"),
        ("luma", "Luma"),
        ("ticketmaster", "Ticketmaster"),
    )

    class Meta:
        ordering = ['start_date', 'title',]

    title = models.CharField(max_length=300)
    valid = models.BooleanField(default=False)
    event_image = models.FileField(upload_to='event', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    when = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    venue = models.CharField(max_length=400)
    event_source = models.CharField(
        max_length=50, choices=EVENT_SOURCE_CHOICES, default="serp_api_google_event")
    link = models.URLField(blank=True, null=True)
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, related_name="events")
    submitter_first_name = models.CharField(
        max_length=300, blank=True, null=True)
    submitter_last_name = models.CharField(
        max_length=300, blank=True, null=True)
    submitter_email = models.EmailField(max_length=300, blank=True, null=True)
    submitter_phone = models.CharField(max_length=300, blank=True, null=True)
    submitter = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    submitter_account_created = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    @property
    def is_active(self):
        return bool(self.start_date >= timezone.now().date())

    def __str__(self):
        return self.title

    @property
    def get_event_image(self):
        if self.event_image:
            return self.event_image.url
        return '/static/home/assets/img/error/no-image-placeholder.jpg'


class RecentSearch(models.Model):
    class Meta:
        ordering = ['-last_searched']
        verbose_name_plural = "Recent Searches"
    cookies_id = models.CharField(max_length=200, blank=True, null=True)
    search_keyword = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    last_searched = models.DateTimeField(auto_now=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return Truncator(self.search_keyword).chars(300)


class BetaSubscriber(models.Model):
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Beta Subscribers"

    first_name = models.CharField(max_length=300,)
    last_name = models.CharField(max_length=300,)
    phone = models.CharField(max_length=300,)
    email = models.EmailField(max_length=300,)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class AppVersion(models.Model):
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "App Versions"

    version = models.CharField(max_length=50, unique=True)
    release_notes = models.CharField(max_length=500, blank=True, null=True)
    commit_hash = models.CharField(max_length=100, blank=True, null=True)
    commit_branch = models.CharField(max_length=100, blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.version
