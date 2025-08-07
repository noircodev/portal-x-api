
from decimal import Decimal, ROUND_HALF_UP
import pytz
import random
from ..factory.user_agents import user_agents
from collections import namedtuple
import json
import time
from bs4 import BeautifulSoup
import re
import requests
import logging
from datetime import datetime, date
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.utils.text import slugify
from event.models import Event, SearchPhrase, Country, City, ZipCode, Location
from event.app_settings import app_settings
from django.contrib.gis.geos import Point

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseEngine:
    BASE_URL = ""
    API_KEY = ""

    def construct_query(self, search_phrase: SearchPhrase):
        return [
            f"{search_phrase.query} events in {city.city_ascii}, {city.region.state_code}"
            for location in search_phrase.get_locations
            for city in location.get_cities()
        ]

    def fetch_data(self, query):
        raise NotImplementedError(
            "Subclasses must implement fetch_data method")

    def parse_data(self, data):
        raise NotImplementedError(
            "Subclasses must implement parse_data method")

    def parse_datetime(self, date_str):
        current_year = datetime.now().year
        try:
            parsed_date = datetime.strptime(date_str, "%b %d, %Y")
        except ValueError:
            try:
                parsed_date = datetime.strptime(
                    f"{date_str}, {current_year}", "%b %d, %Y")
            except ValueError:
                return None
        return parsed_date

    def format_venue(self, address):
        return ", ".join(address) if isinstance(address, list) else address

    def download_image(self, image_url, title):
        if image_url:
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                img = img.convert("RGB")
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                filename = f"{slugify(title)}.jpg"
                logger.info(f"Image downloaded successfully: {filename}")
                return ContentFile(img_io.getvalue(), name=filename)
            except Exception as e:
                logger.error(f"Failed to download image {image_url}: {e}")
        return None

    def save_event(self, event_data, city, event_source="serp_api_google_event"):
        if city:
            for data in event_data:

                event, created = Event.objects.get_or_create(
                    title=data["title"],
                    start_date=data["start_date"],
                    # when=data["when"],
                    city=city,
                    defaults={
                        "description": data.get("description", ""),
                        "venue": self.format_venue(data.get("venue")),
                        "link": data.get("link"),
                        "event_source": event_source,
                        "valid": True,
                    },
                )
                event_image = None
                if created:
                    event_image = self.download_image(
                        data.get("image"), data.get("title"))

                if event_image:
                    event.event_image = event_image
                    event.save()
                    logger.info(f"Image linked to event: {event.title}")
                logger.info(
                    f"Event {'created' if created else 'updated'}: {event.title}")
            return event, created

    def process(self, search_phrase: SearchPhrase):
        for location in search_phrase.get_locations:
            for city in location.get_cities():
                query = f"{search_phrase.query} events in {city.city_ascii}, {location.state_code}"
                logger.info(f"Processing query: {query}")
                response = self.fetch_data(query)
                if response:
                    event_data = self.parse_data(response)
                    self.save_event(event_data, city)

    def fetch_events(self):
        for query in SearchPhrase.objects.filter(active=True):
            self.process(query)


class SerpAPIGoogleEngine(BaseEngine):
    BASE_URL = app_settings.SERP_API_ENDPOINT
    API_KEY = app_settings.SERP_API_KEY

    def fetch_data(self, query):
        params = {"api_key": self.API_KEY, "q": query,
                  "engine": "google_events", "hl": 'en', "gl": "us"}
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json() if 'error' not in response.json() else False
        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code in [403, 404, 429, 500, 502]:
                    logger.error(f"Error fetching data: {e}")
            else:
                logger.error(f"Request error: {e}")
            return False

    def parse_data(self, data):
        events = []
        for item in data.get("events_results", []):
            events.append({
                "title": item.get("title"),
                "start_date": self.parse_datetime(item['date'].get("start_date")),
                # "when": item['date'].get("when"),
                "description": item.get("description", ""),
                "venue": item.get("address"),
                "link": item.get("link"),
                "image": item.get("image"),
            })
        return events


class EventbriteWebScraperPlusAPI(BaseEngine):
    def __init__(self):
        self.html_content = None
        self.server_data = None
        self.BASE_URL = app_settings.EVENTBRITE_API_ENDPOINT
        self.API_KEY = app_settings.EVENTBRITE_API_KEY
        self.RATE_LIMIT_WAIT = 5
        self.HTML_RATE_LIMIT_WAIT = 30
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(user_agents)
        })

    def construct_query(self, search_phrase: SearchPhrase):
        Search = namedtuple("Search", ['search', 'cities'])
        search = slugify(f"{search_phrase.query}")
        cities = [
            city for location in search_phrase.get_locations
            for city in location.get_cities() if city.get_eventbrite_slug
        ]
        return Search(search, cities)

    def fetch_html(self, url: str):
        try:
            time.sleep(self.HTML_RATE_LIMIT_WAIT)
            response = self.session.get(url, timeout=120)
            response.raise_for_status()
            self.html_content = response.text
            logger.info("Successfully fetched HTML content.")
            return True
        except requests.RequestException as e:
            logger.error(f"Error fetching HTML: {e}")
            return False

    def extract_script_data(self):
        if not self.html_content:
            return False

        soup = BeautifulSoup(self.html_content, "html.parser")
        script_tag = soup.find(
            "script", text=re.compile(r"window\.__SERVER_DATA__"))
        if not script_tag:
            return False

        match = re.search(
            r"window\.__SERVER_DATA__\s*=\s*({.*?});", script_tag.string, re.DOTALL)
        if not match:
            return False

        try:
            self.server_data = json.loads(match.group(1))
            return True
        except json.JSONDecodeError:
            return False

    def get_event_ids_from_results(self):
        if not self.server_data:
            return []
        events = self.server_data.get("search_data", {}).get(
            "events", {}).get("results", [])
        return [event.get("id") for event in events if event.get("id")]

    def get_event_id(self, search_url):
        if self.fetch_html(search_url) and self.extract_script_data():
            return self.get_event_ids_from_results()
        return []

    def fetch_data(self, query):
        event_ids = self.get_event_id(query)
        if not event_ids:
            return []

        headers = {"Authorization": f"Bearer {self.API_KEY}"}
        params = {"expand": "venue"}
        events_json = []
        for event_id in event_ids:
            try:
                response = self.session.get(
                    f"{self.BASE_URL}{event_id}/", params=params, headers=headers)
                response.raise_for_status()
                events_json.append(response.json())
                time.sleep(self.RATE_LIMIT_WAIT)
            except requests.RequestException as e:
                logger.error(
                    f"Error fetching data for event '{event_id}': {e}")
        return events_json

    def parse_data(self, events_list: list):
        events = []
        for event in events_list:
            start_date_str = event['start'].get("utc")
            event_timezone = event['start'].get("timezone")
            start_date = datetime.strptime(
                start_date_str, "%Y-%m-%dT%H:%M:%SZ") if start_date_str else None

            if start_date:
                tz_aware = pytz.utc.localize(start_date)
                start_date_in_timezone = tz_aware.astimezone(
                    pytz.timezone(event_timezone))
                when = start_date_in_timezone.strftime(
                    "%B %d, %Y at %I:%M %p %Z")
            else:
                when = None

            events.append({
                "title": event['name'].get("text"),
                "start_date": start_date,
                # "when": when,
                "description": event.get("summary", ""),
                "venue": event['venue']['address'].get("localized_address_display"),
                "link": event.get("url"),
                "image": event['logo'].get("url") if event.get("logo") else None,
                "venue_raw": event['venue'],
            })
        return events

    def process(self, search_phrase: SearchPhrase):
        search_query = self.construct_query(search_phrase)
        for location in search_phrase.get_locations:
            for _city in location.get_cities():
                search_url = f"https://www.eventbrite.com/d/{_city.get_eventbrite_slug}/{search_query.search}/?page=1&lang=en"
                logger.info(f"Processing search: {search_url}")
                response = self.fetch_data(search_url)
                if not response:
                    continue

                event_data_list = self.parse_data(response)
                for event_data in event_data_list:
                    venue = event_data.pop("venue_raw", None)
                    if not venue:
                        continue

                    address = venue.get('address', {})
                    city_name = address.get("city")
                    region_code = address.get("region").strip(
                    ).upper() if address.get("region") else None
                    lat_str = address.get("latitude")
                    lng_str = address.get("longitude")
                    zip_code = address.get("postal_code")
                    country_code = address.get("country", "US").strip(
                    ).upper() if address.get("country") else "US"

                    if not city_name or not region_code:
                        logger.warning(
                            f"Missing city/state info for event: {event_data.get('title')}")
                        continue

                    try:
                        lat = Decimal(lat_str)
                        lng = Decimal(lng_str)
                    except Exception:
                        logger.warning(
                            f"Invalid coordinates for city {city_name}")
                        lat, lng = Decimal("0.0"), Decimal("0.0")

                    region = location

                    region, _ = Location.objects.get_or_create(
                        state_code__iexact=region_code,
                        country__iso2_code__iexact=country_code,
                        defaults={
                            "state_code": region_code,
                            "state_name": region.state_name,
                            "short_name": region.short_name,
                            "timezone": region.timezone,
                            "lat": region.lat,
                            "lng": region.lng,
                            "country": region.country,
                            "active": False
                        }
                    )

                    city_name = city_name.strip().title()
                    matched_city, _ = City.objects.get_or_create(
                        city_ascii__iexact=city_name,
                        region__state_code=region_code,
                        defaults={
                            "region": region,
                            "city_name": city_name,
                            "city_ascii": city_name,
                            "lat": lat,
                            "lng": lng,
                            "coords": Point(float(lng), float(lat)),
                            "active": False,
                            "timezone": region.timezone
                        }
                    )

                    if zip_code:
                        area_code, _ = ZipCode.objects.get_or_create(
                            zip_code=zip_code,
                            defaults={
                                "city": matched_city,
                                "state": region,
                            }
                        )
                        matched_city.area_code.add(area_code)
                        matched_city.save()

                    self.save_event([event_data], matched_city, "eventbrite")


class EventbriteWebScraperPlusAPI(BaseEngine):
    def __init__(self):
        self.html_content = None
        self.server_data = None
        self.BASE_URL = app_settings.EVENTBRITE_API_ENDPOINT
        self.API_KEY = app_settings.EVENTBRITE_API_KEY
        self.RATE_LIMIT_WAIT = 5
        self.HTML_RATE_LIMIT_WAIT = 30
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(user_agents)
        })

    def construct_query(self, search_phrase: SearchPhrase):
        Search = namedtuple("Search", ['search', 'cities'])
        search = slugify(f"{search_phrase.query}")
        cities = [
            city for location in search_phrase.get_locations
            for city in location.get_cities() if city.get_eventbrite_slug
        ]
        return Search(search, cities)

    def fetch_html(self, url: str):
        try:
            time.sleep(self.HTML_RATE_LIMIT_WAIT)
            response = self.session.get(url, timeout=120)
            response.raise_for_status()
            self.html_content = response.text
            logger.info("Successfully fetched HTML content.")
            return True
        except requests.RequestException as e:
            logger.error(f"Error fetching HTML: {e}")
            return False

    def extract_script_data(self):
        if not self.html_content:
            return False

        soup = BeautifulSoup(self.html_content, "html.parser")
        script_tag = soup.find(
            "script", text=re.compile(r"window\.__SERVER_DATA__"))
        if not script_tag:
            return False

        match = re.search(
            r"window\.__SERVER_DATA__\s*=\s*({.*?});", script_tag.string, re.DOTALL)
        if not match:
            return False

        try:
            self.server_data = json.loads(match.group(1))
            return True
        except json.JSONDecodeError:
            return False

    def get_event_ids_from_results(self):
        if not self.server_data:
            return []
        events = self.server_data.get("search_data", {}).get(
            "events", {}).get("results", [])
        return [event.get("id") for event in events if event.get("id")]

    def get_event_id(self, search_url):
        if self.fetch_html(search_url) and self.extract_script_data():
            return self.get_event_ids_from_results()
        return []

    def fetch_data(self, query):
        event_ids = self.get_event_id(query)
        if not event_ids:
            return []

        headers = {"Authorization": f"Bearer {self.API_KEY}"}
        params = {"expand": "venue"}
        events_json = []
        for event_id in event_ids:
            try:
                response = self.session.get(
                    f"{self.BASE_URL}{event_id}/", params=params, headers=headers)
                response.raise_for_status()
                events_json.append(response.json())
                time.sleep(self.RATE_LIMIT_WAIT)
            except requests.RequestException as e:
                logger.error(
                    f"Error fetching data for event '{event_id}': {e}")
        return events_json

    def parse_data(self, events_list: list):
        events = []
        for event in events_list:
            start_date_str = event['start'].get("utc")
            event_timezone = event['start'].get("timezone")
            start_date = datetime.strptime(
                start_date_str, "%Y-%m-%dT%H:%M:%SZ") if start_date_str else None

            if start_date:
                tz_aware = pytz.utc.localize(start_date)
                start_date_in_timezone = tz_aware.astimezone(
                    pytz.timezone(event_timezone))
                when = start_date_in_timezone.strftime(
                    "%B %d, %Y at %I:%M %p %Z")
            else:
                when = None

            events.append({
                "title": event['name'].get("text"),
                "start_date": start_date,
                # "when": when,
                "description": event.get("summary", ""),
                "venue": event['venue']['address'].get("localized_address_display"),
                "link": event.get("url"),
                "image": event['logo'].get("url") if event.get("logo") else None,
                "venue_raw": event['venue'],
            })
        return events

    def resolve_location(self, address_data):
        city_name = address_data.get("city")
        region_code = address_data.get("region", "").strip().upper()
        country_code = address_data.get("country", "").strip().upper()
        zip_code = address_data.get("postal_code")

        if not (city_name and region_code and country_code):
            return None, None, None

        EIGHT_PLACES = Decimal("0.00000001")

        try:
            lat = Decimal(str(address_data.get("latitude", "0.0"))).quantize(EIGHT_PLACES, rounding=ROUND_HALF_UP)
            lng = Decimal(str(address_data.get("longitude", "0.0"))).quantize(EIGHT_PLACES, rounding=ROUND_HALF_UP)
        except:
            lat = Decimal("0.0").quantize(EIGHT_PLACES)
            lng = Decimal("0.0").quantize(EIGHT_PLACES)

        country, _ = Country.objects.get_or_create(
            iso2_code__iexact=country_code,
            defaults={
                "iso2_code": country_code,
                "iso3_code": country_code,
                "country_name": country_code
            }
        )

        region, _ = Location.objects.get_or_create(
            state_code__iexact=region_code,
            country=country,
            defaults={
                "state_code": region_code,
                "state_name": region_code,
                "short_name": region_code,
                "timezone": "America/New_York",
                "lat": lat,
                "lng": lng,
                "active": False
            }
        )

        city_name_clean = city_name.strip().title()
        city, _ = City.objects.get_or_create(
            city_ascii__iexact=city_name_clean,
            region=region,
            defaults={
                "city_name": city_name_clean,
                "lat": lat,
                "lng": lng,
                "coords": Point(float(lng), float(lat)),
                "active": False,
                "timezone": region.timezone
            }
        )

        if zip_code:
            zip_obj, _ = ZipCode.objects.get_or_create(
                zip_code=zip_code,
                defaults={
                    "city": city,
                    "state": region
                }
            )
            city.area_code.add(zip_obj)
            city.save()

        return country, region, city

    def process(self, search_phrase: SearchPhrase):
        search_query = self.construct_query(search_phrase)
        for location in search_phrase.get_locations:
            for _city in location.get_cities():
                search_url = f"https://www.eventbrite.com/d/{_city.get_eventbrite_slug}/{search_query.search}/?page=1&lang=en"
                logger.info(f"Processing search: {search_url}")
                response = self.fetch_data(search_url)
                if not response:
                    continue

                event_data_list = self.parse_data(response)
                for event_data in event_data_list:
                    venue = event_data.pop("venue_raw", None)
                    if not venue:
                        continue

                    address = venue.get('address', {})
                    result = self.resolve_location(address)
                    if not result:
                        logger.warning(
                            f"Skipping event due to unresolved location: {event_data.get('title')}")
                        continue

                    country, region, city = result
                    self.save_event([event_data], city, "eventbrite")


class AlleventsInScraper(BaseEngine):
    BASE_URL = "https://allevents.in"
    RATE_LIMIT_WAIT = 5

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": random.choice(user_agents)})
        self.html_content = None
        self.events_data = []

    def construct_query(self, search_phrase: SearchPhrase):
        # Return namedtuple with search slug and cities list similar to Eventbrite scraper
        Search = namedtuple("Search", ['search', 'cities'])
        search_slug = slugify(search_phrase.query)
        cities = [
            city for location in search_phrase.get_locations
            for city in location.get_cities() if city.city_ascii
        ]
        return Search(search_slug, cities)

    def fetch_html(self, url: str):
        try:
            time.sleep(self.RATE_LIMIT_WAIT)
            response = self.session.get(url, timeout=120)
            response.raise_for_status()
            self.html_content = response.text
            logger.info(f"Fetched HTML from {url}")
            return True
        except requests.RequestException as e:
            logger.error(f"Error fetching HTML from {url}: {e}")
            return False

    def extract_events_data(self):
        if not self.html_content:
            logger.warning("No HTML content to extract from.")
            return False

        soup = BeautifulSoup(self.html_content, "html.parser")
        scripts = soup.find_all(
            "script", string=re.compile(r"_this\.events_data\s*=")
        )
        if not scripts:
            logger.warning("No <script> tag with _this.events_data found.")
            return False

        script_text = None
        for script in scripts:
            if "_this.events_data" in script.text:
                script_text = script.text
                break

        if not script_text:
            logger.warning("Script with _this.events_data not found.")
            return False

        match = re.search(
            r'_this\.events_data\s*=\s*(\[\{.*?\}\]);', script_text, re.DOTALL)
        if not match:
            logger.warning("Failed to extract _this.events_data JSON block.")
            return False

        raw_json = match.group(1)
        cleaned_json = raw_json.replace("undefined", "null")

        try:
            self.events_data = json.loads(cleaned_json)
            logger.info(
                f"Extracted {len(self.events_data)} events from allevents.in")
            return True
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return False

    def transform_events(self):
        result = []
        for event in self.events_data:
            venue = event.get("venue", {})
            # Convert Unix timestamp string to datetime if possible
            start_time = None
            try:
                # allevents.in timestamp looks like seconds since epoch in string
                start_time_unix = int(event.get("start_time", "0"))
                start_time = datetime.fromtimestamp(
                    start_time_unix, tz=pytz.UTC)
            except (ValueError, TypeError):
                start_time = None

            transformed = {
                "title": event.get("eventname"),
                "description": event.get("short_description"),
                "start_date": start_time,
                # "when": start_time.strftime("%B %d, %Y at %I:%M %p %Z") if start_time else None,
                "venue": event.get("location"),
                "city_name": venue.get("city"),
                "state_code": venue.get("state"),
                "latitude": float(venue.get("latitude")) if venue.get("latitude") else None,
                "longitude": float(venue.get("longitude")) if venue.get("longitude") else None,
                "link": event.get("event_url"),
                "categories": event.get("categories"),
                "image": event.get("thumb_url"),
            }
            result.append(transformed)
        return result

    def save_city(self, city_name, state_code, latitude, longitude):
        if not city_name or not state_code:
            return None
        city_obj, created = City.objects.get_or_create(
            city_ascii=city_name,
            region__state_code__iexact=state_code,
            defaults={
                "city_name": city_name,
                "lat": latitude or 0.0,
                "lng": longitude or 0.0,
                "coords": Point(longitude or 0.0, latitude or 0.0),
            },
        )
        # Attempt to link the region (state)
        if created or not city_obj.region:
            from event.models import Location  # Import here to avoid circular
            try:
                region = Location.objects.get(state_code__iexact=state_code)
                city_obj.region = region
                city_obj.save()
            except Location.DoesNotExist:
                logger.warning(
                    f"Location with state_code '{state_code}' not found for city {city_name}")
        return city_obj

    def save_event(self, event_data):
        city = self.save_city(
            event_data.get("city_name"),
            event_data.get("state_code"),
            event_data.get("latitude"),
            event_data.get("longitude"),
        )
        if not city:
            logger.warning(
                f"Skipping event '{event_data.get('title')}' due to missing city/region.")
            return None, False

        event, created = Event.objects.get_or_create(
            title=event_data["title"],
            start_date=event_data["start_date"],
            # when=event_data.get("when"),
            city=city,
            defaults={
                "description": event_data.get("description", ""),
                "venue": event_data.get("venue"),
                "link": event_data.get("link"),
                "event_source": "all_events_in",
                "valid": True,
            },
        )
        event_image = None
        if created and event_data.get("image"):
            event_image = self.download_image(
                event_data.get("image"), event_data["title"])
        if event_image:
            event.event_image = event_image
            event.save()
            logger.info(f"Image linked to event: {event.title}")
        logger.info(
            f"Event {'created' if created else 'updated'}: {event.title}")
        return event, created

    def process(self, search_phrase: SearchPhrase):
        search_query = self.construct_query(search_phrase)
        for city in search_query.cities:
            search_url = f"{self.BASE_URL}/{city.get_all_event_in_slug}/{search_query.search}/"
            logger.info(f"Processing allevents.in URL: {search_url}")
            if not self.fetch_html(search_url):
                continue

            if not self.extract_events_data():
                continue

            events = self.transform_events()
            for event_data in events:
                self.save_event(event_data)


class ArtIdeaScraper(BaseEngine):
    CURRENT_YEAR = datetime.now().year
    BASE_URL = f"https://www.artidea.org/festival{CURRENT_YEAR}"
    EVENT_BASE_URL = "https://www.artidea.org"
    CITY_NAME = "New Haven"
    STATE_CODE = "CT"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(user_agents)
        })

    def fetch_html(self, url):
        logger.info(f"Fetching URL: {url}")
        try:
            time.sleep(3)
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def get_event_links(self):
        html = self.fetch_html(self.BASE_URL)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        links = []
        selector = f".field-event-reference .thumbnail a[href^='/event/{self.CURRENT_YEAR}/']"
        for div in soup.select(selector):
            href = div.get("href")
            if href:
                links.append(self.EVENT_BASE_URL + href)
        return list(set(links))  # deduplicate

    def parse_event_page(self, url, city):
        html = self.fetch_html(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        title = soup.find("h1")
        title = title.text.strip() if title else ""

        image_tag = soup.select_one(".field-photos img")
        image_url = image_tag.get("src") if image_tag else None

        date_text = soup.select_one(
            ".paragraphs-items-field-dates-and-times .show-time")
        when = date_text.text.strip() if date_text else None

        # Try parsing date with city timezone awareness
        start_date = None
        try:
            if when:
                match = re.search(r"(\w{3,9})\s+(\d{1,2}),\s+(\d{4})", when)
                if match:
                    naive_date = datetime.strptime("{} {} {}".format(
                        match.group(1), match.group(2), match.group(3)), "%B %d %Y")
                    tz = pytz.timezone(city.timezone)
                    start_date = tz.localize(naive_date)
        except Exception as e:
            logger.warning(f"Date parsing failed for URL {url}: {e}")
            start_date = None

        venue_tag = soup.select_one(".field-venue h3")
        venue = venue_tag.text.strip() if venue_tag else ""

        desc_tag = soup.select_one(".field-body")
        description = "\n".join(
            [p.text.strip() for p in desc_tag.find_all("p")]) if desc_tag else ""

        if not (title and start_date):
            logger.warning(
                f"Skipping event due to missing title or start_date: {url}")
            return None

        if start_date.date() < date.today():
            logger.info(f"Skipping past event: {title} on {start_date.date()}")
            return None

        return {
            "title": title,
            "description": description,
            "start_date": start_date.date(),  # only store date part
            # "when": when,
            "venue": venue,
            "link": url,
            "image": image_url,
        }

    def get_city(self):
        try:
            location = Location.objects.get(state_code__iexact=self.STATE_CODE)
            city, _ = City.objects.get_or_create(
                city_ascii=self.CITY_NAME,
                region=location,
                defaults={
                    "city_name": self.CITY_NAME,
                    "lat": Decimal("41.3083"),
                    "lng": Decimal("-72.9279"),
                    "coords": Point(-72.9279, 41.3083),
                    "active": True,
                    "timezone": location.timezone,
                }
            )
            return city
        except Location.DoesNotExist:
            logger.error("Connecticut state Location not found.")
            return None

    def fetch_events(self):
        city = self.get_city()
        if not city:
            return

        links = self.get_event_links()
        logger.info(f"Found {len(links)} ArtIdea events.")
        for link in links:
            logger.info(f"Processing event URL: {link}")
            event_data = self.parse_event_page(link, city)
            if event_data:
                self.save_event([event_data], city, event_source="artidea")


class SearchEngine:
    def __init__(self, engine='serp_api_google_event'):
        if engine == 'serp_api_google_event':
            self.engine = SerpAPIGoogleEngine()
        elif engine == 'eventbrite':
            self.engine = EventbriteWebScraperPlusAPI()
        elif engine == 'all_events':
            self.engine = AlleventsInScraper()
        elif engine == 'artidea':
            self.engine = ArtIdeaScraper()
        else:
            self.engine = None

    def perform_search(self):
        if self.engine:
            self.engine.fetch_events()
        else:
            logger.error("Invalid search engine specified")
