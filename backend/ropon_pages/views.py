from wagtail.admin.viewsets.pages import PageListingViewSet
from .models import RoponPage
# Create your views here.

class RoponPageViewSet(PageListingViewSet):
    model = RoponPage
    icon = 'doc-full'  # You can change this icon
    menu_label = 'RoPON Pages'
    menu_name = 'ropon_pages'
    list_display = ('title', 'slug', 'live')
    search_fields = ('title', 'body')
    menu_order = 250  # Determines the order in the Wagtail admin menu
    add_to_admin_menu = True
