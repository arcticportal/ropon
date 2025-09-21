from .base import *  # noqa

# Development overrides.
# Provide a non-secret default key ONLY for dev if not supplied.
if not SECRET_KEY or SECRET_KEY == 'seccret':  # value from base fallback
    SECRET_KEY = "django-insecure-dev-ONLY-not-for-production"  # noqa: F401

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'ropon_pages': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
