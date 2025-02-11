from wagtail.api.v2.views import PagesAPIViewSet

from .models import ObservingNetworkPage

class ObservingNetworkPageViewSet(PagesAPIViewSet):
    model = ObservingNetworkPage

    listing_default_fields = PagesAPIViewSet.listing_default_fields + [
        'date_last_modified',
        'ropon_id'
        ]
    meta_fields =  ["locale",
                    "detail_url",
                    "slug",
                    "first_published_at",
                    "date_last_modified",
                    "alias_of"
    ]

    