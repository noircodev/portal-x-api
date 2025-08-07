from django.contrib.gis.geos import Point
import pandas as pd
from django.core.management.base import BaseCommand
from event.models import (Location, Country, City, ZipCode)
import os
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Import locations and postal codes from a CSV dataset"

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_dir, 'resources/us_cities_mini.csv')

        self.stdout.write(self.style.SUCCESS("Reading dataset..."))
        for state in Location.objects.filter(active=True):
            df = pd.read_csv(file_path, comment='#')
            for _, row in df.iterrows():
                if row['state_id'] == state.state_code:

                    try:

                        self.stdout.write(self.style.SUCCESS(
                            f"Processing {row['city_ascii']} in {row['state_name']}..."))
                        state_name = row['state_name']
                        state_code = row['state_id']
                        city_name = row['city']
                        city_ascii = row['city_ascii']
                        timezone = row['timezone']
                        lat = float(row['lat'])
                        lng = float(row['lng'])
                        county_name = row.get('county_name', '')

                        zip_codes = row['zips']
                        # TODO: make country an argument
                        country = Country.objects.filter(
                            iso2_code__iexact="us").first()
                        if not country:
                            country = Country.objects.create(
                                country_name="United States", iso2_code="us", iso3_code="usa")
                        region = Location.objects.filter(
                            state_name__iexact=state_name,
                            state_code__iexact=state_code,

                        ).first()
                        # Check if location exists
                        if not region:
                            region = Location.objects.create(
                                state_name=state_name,
                                state_code=state_code,
                                country=country,
                                timezone=timezone,
                                lat=lat,
                                lng=lng,
                            )
                        print(region)
                        # Create or update the city
                        # NOTE: I'm using city_ascii as the unique identifier
                        # NOTE: as city_name have been manually altered in the dataset
                        city, created = City.objects.update_or_create(
                            city_ascii=city_ascii,
                            region=region,
                            defaults={
                                "city_name": city_name,
                                "timezone": timezone,
                                "coords": Point(lat, lng),
                                "lat": lat,
                                "lng": lng,
                                "county_name": county_name,
                                "active": True,
                            },
                        )
                        # Create zip codes
                        zip_codes_list = []
                        for zip_code in zip_codes.split():
                            postal_code, pc_created = ZipCode.objects.get_or_create(
                                city=city, zip_code=zip_code,
                                state=city.region,
                            )

                            zip_codes_list.append(postal_code)
                            if pc_created:
                                self.stdout.write(self.style.SUCCESS(
                                    f"Linked zip code {zip_code} to {city.city_name}"))
                        # Add zip codes to the city
                        city.area_code.set(zip_codes_list)

                        if created:
                            self.stdout.write(self.style.SUCCESS(
                                f"Created new city: {city}"))

                    except IntegrityError as e:
                        self.stdout.write(self.style.ERROR(
                            f"Error processing {row['city_ascii']} in {row['state_name']}: {e}"))
                        continue

        self.stdout.write(self.style.SUCCESS("Import completed successfully!"))
