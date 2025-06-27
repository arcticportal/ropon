from django.db import models

from wagtail.models import Page


class HomePage(Page):
    is_creatable = False
