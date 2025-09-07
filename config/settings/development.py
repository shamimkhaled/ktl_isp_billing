
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']


# Database - Use PostgreSQL for Docker, SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='ktl_isp_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': config('DB_SSLMODE', default='prefer'),
        },
    }
}

# Fallback to SQLite if PostgreSQL is not available (for local development)
import os
if not os.environ.get('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery settings for development
CELERY_TASK_ALWAYS_EAGER = config('CELERY_ALWAYS_EAGER', default=False, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = True

# Additional development tools
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

# Debug toolbar configuration
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Disable caching in development
CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'




