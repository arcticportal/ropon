from django.db import models

from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageChooserBlock
from .blocks import HeadingBlock, RoponImageChooserBlock, RoponRichTextBlock
from wagtail.api import APIField
from wagtail.search import index
# Ropon Page models.


class RoponPage(Page):
    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', RoponRichTextBlock()),
        ('image', RoponImageChooserBlock()),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    # Parent page / subpage type rules
    parent_page_types = ['ropon_pages.RoponPageListing']  # Allows RoponPage to be a top-level page
    subpage_types = []

    api_fields = [
        APIField('title'),
        APIField('body'),
    ]

    #search index coniguration
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

# Ropon Page Listing model
class RoponPageListing(Page):
    max_count = 1  # Only one instance allowed
    parent_page_types = ['home.HomePage']
    subpage_types = ['ropon_pages.RoponPage']

    content_panels = Page.content_panels 