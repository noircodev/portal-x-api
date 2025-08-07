import random
from django.dispatch import receiver
import requests
import logging
from bs4 import BeautifulSoup
import json
from django.utils.dateparse import parse_datetime

from event.factory import user_agents

logger = logging.getLogger(__name__)


class LumaEventScraper:
    def __init__(self, event_url):
        self.event_url = event_url
        self.html = None
        self.event_data = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                  (KHTML, like Gecko) Chrome/114.0.5735.103 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })

    def fetch_html(self):
        try:
            response = self.session.get(self.event_url, timeout=30)
            response.raise_for_status()
            self.html = response.text
            logger.info(f"Fetched Luma event HTML from {self.event_url}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to fetch Luma event page: {e}")
            return False

    def extract_json_ld(self):
        soup = BeautifulSoup(self.html, "html.parser")
        script_tag = soup.find("script", type="application/ld+json")
        if not script_tag:
            logger.warning("No <script type='application/ld+json'> found.")
            return None

        try:
            data = json.loads(script_tag.string)
            if data.get("@type") == "Event":
                self.event_data = data
                logger.info("Successfully extracted Luma event data.")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
        return None

    def normalize_event_data(self):
        data = self.event_data
        location = data.get("location", {}).get("address", {})
        geo = data.get("location", {}).get("geo", {})
        image = data.get("image", [])
        return {
            "title": data.get("name"),
            "description": data.get("description", ""),
            "venue": location.get("streetAddress"),
            "city": location.get("addressLocality"),
            "state": location.get("addressRegion"),
            "country": location.get("addressCountry", {}).get("name", "United States"),
            "latitude": geo.get("latitude"),
            "longitude": geo.get("longitude"),
            "image_url": image[0] if isinstance(image, list) and image else None,
            "start_date": parse_datetime(data.get("startDate")),
            "end_date": parse_datetime(data.get("endDate")),
            "link": data.get("url", self.event_url),
            "organizers": [org.get("name") for org in data.get("organizer", [])],
        }

    def run(self):
        if not self.fetch_html():
            return False
        if not self.extract_json_ld():
            return False
        event = self.normalize_event_data()
        logger.info(f"Luma event signal emitted: {event['title']}")
        return event
