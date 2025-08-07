import logging
import requests
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.utils.text import slugify
from decimal import Decimal

from event.models import Event, City, Location, Country

logger = logging.getLogger(__name__)


class EventSaver:
    def __init__(self, event_data, event_source="luma"):
        self.data = event_data
        self.event_source = event_source

    def get_country(self):
        country_name = self.data.get("country", "United States")
        country, _ = Country.objects.get_or_create(
            country_name__iexact=country_name,
            defaults={
                "country_name": country_name,
                "iso2_code": country_name[:2].upper(),
                "iso3_code": country_name[:3].upper()
            }
        )
        return country

    def get_state(self, country):
        state = self.data.get("state").strip(
        ) if self.data.get("state") else None
        if not state:
            logger.warning("State code not found in event data.")
            return None
        state = Location.objects.filter(state_name__iexact=state,
                                        country=country).first()
        return state

    def get_city(self, region):
        if region:
            city, _ = City.objects.get_or_create(city_name__iexact=self.data['city'],
                                                 region=region,
                                                 defaults={
                'city_name': self.data['city'],
                'region': region,
                'city_ascii': self.data.get('city', ),
                'lat': Decimal(self.data.get('latitude', 0.0)),
                'lng': Decimal(self.data.get('longitude', 0.0)),
            }
            )

            return city
        return None

    def download_image(self, image_url, title):
        if image_url:
            try:
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    raise ValueError("Invalid image content type")

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

    def save(self):
        country = self.get_country()
        region = self.get_state(country)
        city = self.get_city(region)

        if not city:
            # If city is not found, log a warning and skip saving the event
            # TODO: Create a notification or alert for manual review
            logger.warning(
                f"Skipping event '{self.data.get('title')}' due to missing city.")
            return None, False

        event, created = Event.objects.get_or_create(
            title=self.data["title"],
            start_date=self.data["start_date"],
            city=city,
            defaults={
                "description": self.data.get("description", ""),
                "venue": self.data.get("venue", ""),
                "link": self.data.get("link", ""),
                "event_source": self.event_source,
                "when": self.data.get("when", ""),
                "valid": True,
            }
        )

        if created and self.data.get("image_url"):
            image_file = self.download_image(
                self.data["image_url"], self.data["title"])
            if image_file:
                event.event_image = image_file
                event.save()
                logger.info(f"Image attached to event: {event.title}")

        logger.info(
            f"Event {'created' if created else 'already exists'}: {event.title}")
        return event, created
