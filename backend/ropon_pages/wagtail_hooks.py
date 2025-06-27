
from wagtail import hooks
from .views import RoponPageViewSet

# Register the viewsets
@hooks.register('register_admin_viewset')
def register_ropon_page_viewset():
    return RoponPageViewSet("ropon_pages")