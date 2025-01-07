from wagtail.api.v2.views import PagesAPIViewSet

from .models import ObservingNetworkPage

class ObservingNetworkPageViewSet(PagesAPIViewSet):
    model = ObservingNetworkPage