from django.utils import timezone
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import tomllib  # or import tomli as tomllib for Python <3.11
from datetime import datetime
import pytz
from event.models import AppVersion


class Command(BaseCommand):
    help = "Save current app version to the database"

    def add_arguments(self, parser):
        parser.add_argument('--commit', type=str, help='Commit hash')
        parser.add_argument('--branch', type=str, help='Commit branch')
        parser.add_argument('--message', type=str, help='Commit message')
        parser.add_argument('--deployed', type=str, help='Deployment timestamp in UTC (e.g. 2025-07-07 20:14:00 UTC)')

    def handle(self, *args, **options):
        default_version = '1.0.0'
        pyproject_path = Path(settings.BASE_DIR) / 'pyproject.toml'

        version = default_version
        try:
            with open(pyproject_path, 'rb') as f:
                toml_data = tomllib.load(f)
                version = (
                    toml_data.get("project", {}).get("version")
                    or toml_data.get("tool", {}).get("poetry", {}).get("version")
                    or default_version
                )
        except Exception as e:
            self.stderr.write(f"⚠️ Failed to read version from pyproject.toml: {e}")

        release_notes = options.get('message') or ''
        commit_hash = options.get('commit') or ''
        commit_branch = options.get('branch') or ''
        deployed_str = options.get('deployed')

        if deployed_str:
            try:
                naive_dt = datetime.strptime(deployed_str, "%Y-%m-%d %H:%M:%S %Z")
                release_date = pytz.utc.localize(naive_dt)
            except Exception as e:
                self.stderr.write(f"⚠️ Invalid deployed timestamp: {e}")
                release_date = timezone.now()
        else:
            release_date = timezone.now()

        AppVersion.objects.create(
            version=version,
            release_notes=release_notes,
            commit_hash=commit_hash,
            commit_branch=commit_branch,
            release_date=release_date,
        )

        self.stdout.write(self.style.SUCCESS("✅ App version saved successfully!"))
        self.stdout.write(f"Current app version: {version}")
        self.stdout.write(f"Release date: {release_date.strftime('%Y-%m-%d %H:%M:%S')} (UTC)")
        self.stdout.write(f"Commit hash: {commit_hash}")
        self.stdout.write(f"Commit branch: {commit_branch}")
# This command reads the app version from pyproject.toml and saves it to the AppVersion model.
# It also handles the case where the file might not exist or the version is not found.
# You can run this command using `python manage.py create_app_version` to update the app version in the database.
# Make sure to adjust the model fields and logic as per your actual requirements.
# This command is useful for keeping track of the app version in your database, especially for deployment
# and release management purposes.
