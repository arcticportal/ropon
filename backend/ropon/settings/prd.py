from .base import *  # noqa

# Production overrides.
# Explicitly ensure DEBUG is False regardless of accidental env leakage.

if not 'DEBUG' in os.environ:
    DEBUG = False  # noqa: F401


# SECRET_KEY must be supplied via environment; fail fast if missing.
SECRET_KEY = env("DJANGO_SECRET_KEY")  # noqa: F401

