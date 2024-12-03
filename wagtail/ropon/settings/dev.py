from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-$t2b@&=)*2ts41g-ybjf_kb*dydu@yzgdu-t#d2fo!$c+=a5kh"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
                 

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://ropon.arcticportal.org",
]


try:
    from .local import *
except ImportError:
    pass
