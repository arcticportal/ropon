from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail import hooks
from .models import RoponPage

class RoponPageViewSet(PageListingViewSet):
    model = RoponPage
    icon = 'doc-full'  # You can change this icon
    menu_label = 'RoPON Pages'
    menu_name = 'ropon_pages'
    list_display = ('title', 'slug', 'live')
    search_fields = ('title', 'body')
    menu_order = 200  # Determines the order in the Wagtail admin menu
    add_to_admin_menu = True

# Register the viewsets
@hooks.register('register_admin_viewset')
def register_ropon_page_viewset():
    return RoponPageViewSet("ropon_pages")