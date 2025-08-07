from event.models import AppVersion
from django import template
import tomllib  # For Python 3.11 and later
from django.conf import settings
from pathlib import Path

register = template.Library()


@register.simple_tag(name='app_version')
def get_app_version():
    default_version = '1.0.0'
    pyproject_path = Path(settings.BASE_DIR) / 'pyproject.toml'
    if pyproject_path.exists():
        try:
            with open(pyproject_path, 'rb') as f:
                pyproject_data = tomllib.load(f)
                # Adjust the path to match your tool structure (e.g., 'tool.poetry' or 'project')
                version = (
                    pyproject_data.get('project', {}).get('version')
                    or pyproject_data.get('tool', {}).get('poetry', {}).get('version')
                )
                if version:
                    return version
        except Exception:
            pass
    return default_version


@register.inclusion_tag(filename='account/snippets/app_version.html', name='current_app_version')
def get_current_app_version():
    version = AppVersion.objects.first()
    return {'version': version}
