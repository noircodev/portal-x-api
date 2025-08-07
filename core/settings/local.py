from .base import *
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',

    }
}

DATABASES = {
    'default': {

        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    }
}

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
DEFAULT_SUPPORT_EMAIL = config('DEFAULT_SUPPORT_EMAIL')
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = '/tmp/app-messages'


MEILISEARCH_URL = "http://127.0.0.1:7700"
MEILISEARCH_MASTER_KEY = config('MEILISEARCH_MASTER_KEY', default='')
