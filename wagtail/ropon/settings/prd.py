from .base import *

DEBUG = False


MEDIA_ROOT = "/srv/media/"

try:
    from .local import *
except ImportError:
    pass
