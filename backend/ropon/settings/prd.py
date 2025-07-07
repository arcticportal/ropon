from .base import *

# Set DEBUG to False as we now have proper static file handling
DEBUG = False

SECRET_KEY = env("DJANGO_SECRET_KEY")

# WhiteNoise configuration for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')  # Add after SecurityMiddleware

# Override the staticfiles storage to use WhiteNoise
STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}

# Optional but recommended for production - enables Brotli compression if available
WHITENOISE_AUTOREFRESH = False
WHITENOISE_ENABLE_GZIP_COMPRESSION = True

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

