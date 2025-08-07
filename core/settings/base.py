from decouple import Csv, config
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', cast=bool)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'django.contrib.gis',
    # project apps
    'event',
    'accounts',
    'sys_monitor',
    'task',
    # project dependencies
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    "drf_spectacular",
    "drf_spectacular_sidecar",
    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'event.middleware.guest_user.SetGuestUserCookiesMiddleware',
    # 'event.middleware.visitor.GeolocationMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

# static and media files storage
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'env_static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


SITE_ID = 1
SIGNUP_REDIRECT_URL = 'account_home'
LOGIN_REDIRECT_URL = 'account_home'

ACCOUNT_LOGOUT_REDIRECT_URL = 'account_login'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_USERNAME_BLACKLIST = config('ACCOUNT_USERNAME_BLACKLIST', cast=Csv())


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Events

EVENT_ENGINES = ['ticketmaster', 'serpapi_google_event',]

SERP_API_KEY = config('SERP_API_KEY')
SERP_API_ENDPOINT = config('SERP_API_ENDPOINT')
EVENTBRITE_API_KEY = config('EVENTBRITE_API_KEY')
EVENTBRITE_API_ENDPOINT = config('EVENTBRITE_API_ENDPOINT')
SERP_API_ENDPOINT = config('SERP_API_ENDPOINT')
TICKET_MASTER_API_KEY = config('TICKET_MASTER_API_KEY')


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'event.api.authentication.BearerTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',

    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'EXCEPTION_HANDLER': 'event.api.utils.event_exception.event_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Default: use session auth (preferred for same-domain setup)
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',  # Optional: for API tokens
    ],

    # Default permissions: read-only for unauthenticated users
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],

    # Pagination (can be overridden per view)
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 24,
}


ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv())

# Geolocation
GEOIP_PATH = os.path.join(BASE_DIR, 'geodb')


SPECTACULAR_SETTINGS = {
    "TITLE": "Portal X API",
    "DESCRIPTION": "API documentation for Portal X Project",
    "VERSION": "1.0.0",
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',

    # Authentication
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,

    # Schema generation
    'GENERATE_UNIQUE_PARAMETER_NAMES': True,
    'SORT_OPERATION_PARAMETERS': True,

    # Tags
    "TAGS": [
        {"name": "Events", "description": "Endpoints related to event listing, submission, and search"},
        {"name": "Search", "description": "Endpoints for Meilisearch-powered search suggestions"},
        {"name": "Beta", "description": "Endpoints for joining the beta program"},
    ],

    # Custom preprocessing
    # 'PREPROCESSING_HOOKS': [
    #     'core.urls.custom_preprocessing_hook',
    # ],

    # Swagger UI settings
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayOperationId': True,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
        'displayRequestDuration': True,
        'docExpansion': 'list',
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
    },

    # ReDoc settings
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'expandResponses': '200,201',
        'pathInMiddlePanel': True,
        'nativeScrollbars': True,
        'theme': {
            'colors': {
                'primary': {
                    'main': '#1976d2'
                }
            }
        }
    },

    # Schema customization
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
    ],

    # Extensions
    'EXTENSIONS': [
        'drf_spectacular.extensions.DjangoChoiceFieldExtension',
        'drf_spectacular.extensions.DjangoFilterExtension',
    ],

    # Disable auto schema for certain views if needed
    'DISABLE_ERRORS_AND_WARNINGS': False,
}
