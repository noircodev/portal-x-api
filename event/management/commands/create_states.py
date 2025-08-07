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
        file_path = os.path.join(current_dir, 'resources/us_states.csv')
        def bool_converter(x): return x.lower() == 'true'
        country = Country.objects.filter(
            iso2_code__iexact="us").first()
        if not country:
            country = Country.objects.create(
                country_name="United States", iso2_code="us", iso3_code="usa")
        self.stdout.write(self.style.SUCCESS(
            f"Reading dataset {file_path}..."))
        df = pd.read_csv(file_path, comment='#', converters={
                         'active': bool_converter})
        for _, row in df.iterrows():
            if row['active']:
                if row['state_id'].lower() == 'ny':
                    short_name = "NYC"
                else:
                    short_name = None
                Location.objects.get_or_create(
                    state_name=row['state_name'],
                    state_code=row['state_id'],
                    defaults={
                        "timezone": row['timezone'],
                        'country': country,
                        "lat": row['lat'],
                        "lng": row['lng'],
                        'short_name': short_name,
                    }

                )
