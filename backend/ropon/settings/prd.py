from .base import *

from environs import Env

env = Env()
DEBUG = False

SECRET_KEY = env("DJANGO_SECRET_KEY")

MEDIA_ROOT = "/srv/media/"

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env.str('EMAIL_HOST', )
EMAIL_PORT = env.int('EMAIL_PORT', default=465)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER',)
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD',)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=True)
EMAIL_TIMEOUT = env.int('EMAIL_TIMEOUT', default=5)
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', )

