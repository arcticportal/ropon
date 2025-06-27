from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-$t2b@&=)*2ts41g-ybjf_kb*dydu@yzgdu-t#d2fo!$c+=a5kh"

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Django Email server settings SMTP backend
# https://docs.djangoproject.com/en/5.1/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env.str('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=465)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER','')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD','')
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=True)
EMAIL_TIMEOUT = env.int('EMAIL_TIMEOUT', default=5)
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', '')



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
