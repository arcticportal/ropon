from wagtail.api.v2.views import PagesAPIViewSet
from .models import RoponPage
class RoponPagesAPIViewSet(PagesAPIViewSet):
    model = RoponPage