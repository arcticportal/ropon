from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-$t2b@&=)*2ts41g-ybjf_kb*dydu@yzgdu-t#d2fo!$c+=a5kh"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

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

try:
    from .local import *
except ImportError:
    pass
