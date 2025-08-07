# from event.models import AppVersion
# from django import template
# import json
# from django.conf import settings
# from pathlib import Path
# register = template.Library()


# @register.simple_tag(name='app_version')
# def get_app_version():
#     default_version = '1.0.0'
#     project_dir = settings.BASE_DIR
#     version_file_path = Path(project_dir) / 'DEPLOYED_VERSION.json'
#     if version_file_path.exists():
#         with open(version_file_path, 'r') as version_file:
#             try:
#                 version_data = json.load(version_file)
#                 default_version = version_data.get('version', default_version)
#             except json.JSONDecodeError:
#                 pass
#     return default_version


# @register.inclusion_tag(filename='account/snippets/app_version.html', name='current_app_version')
# def get_current_app_version():
#     version = AppVersion.objects.first()
#     return {'version': version}
