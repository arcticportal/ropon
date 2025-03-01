
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from .blocks import RoponPageHeadingBlock, RoponPageImageChooserBlock, RoponPageRichTextBlock
from wagtail.api import APIField
from wagtail.search import index
from flags.state import flag_enabled

FLAG_REMOVE_PREVIEW_OPTIONS = 'ROPON.REMOVE_PREVIEW_OPTIONS'

# Ropon Page models.


class RoponPage(Page):
    body = StreamField([
        ('heading', RoponPageHeadingBlock()),
        ('paragraph', RoponPageRichTextBlock()),
        ('image', RoponPageImageChooserBlock()),
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

    # disable preview for this page type
      # diable preview for Observing Network Page
    def is_previewable(self):
        if flag_enabled(FLAG_REMOVE_PREVIEW_OPTIONS):
            return False
        return super().is_previewable()
    
  


# Ropon Page Listing model
class RoponPageListing(Page):
    max_count = 1  # Only one instance allowed
    parent_page_types = ['home.HomePage']
    subpage_types = ['ropon_pages.RoponPage']

    content_panels = Page.content_panels 