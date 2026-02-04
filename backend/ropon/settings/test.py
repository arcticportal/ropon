"""
Django settings optimized for testing.

These settings focus on test performance while maintaining test validity.
"""
from .base import *  # noqa

# Use a faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations during tests for faster database setup
# This is safe because test databases are created from scratch
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use in-memory SQLite for faster tests (if possible)
# However, if tests require PostgreSQL features, keep PostgreSQL but optimize it
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': env.str('POSTGRES_DB', default='test_postgres'),
        'USER': env.str('POSTGRES_USER', default='postgres'),
        'PASSWORD': env.str('POSTGRES_PASSWORD', default='postgres'), 
        'HOST': env.str('POSTGRES_HOST', default='db'),
        'PORT': env.str('POSTGRES_PORT', default='5432'),
        # Performance optimizations for test database
        'TEST': {
            'NAME': 'test_postgres',
        },
        'OPTIONS': {
            # Reduce fsync calls for test database
            'options': '-c fsync=off -c synchronous_commit=off -c full_page_writes=off',
        },
    }
}

# Disable debug mode in tests
DEBUG = False

# Disable template caching for tests
TEMPLATES[0]['OPTIONS']['loaders'] = [  # noqa: F405
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

# Use local memory cache instead of Redis for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

# Disable logging during tests to reduce I/O
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Disable whitenoise during tests (not needed)
MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m.lower()]  # noqa: F405

# Disable email backend for faster tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable static file storage hashing for tests
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Reduce media/static complexity in tests
MEDIA_ROOT = os.path.join(BASE_DIR, "test_media")  # noqa: F405
STATIC_ROOT = os.path.join(BASE_DIR, "test_static")  # noqa: F405

# Disable password validators for faster user creation in tests
AUTH_PASSWORD_VALIDATORS = []

# Disable Wagtail features not needed in tests
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAIL_ENABLE_WHATS_NEW_BANNER = False

# Use simple secret key for tests
SECRET_KEY = 'test-secret-key-not-for-production'
