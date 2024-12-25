
from wagtail import hooks


# Hide the pages menu item for non-superusers
@hooks.register('construct_main_menu')
def hide_pages_menu(request, menu_items):
   
    if not request.user.is_superuser:
        menu_items[:] = [item for item in menu_items if item.name != 'explorer']

    # hide the ropon pages menu item for Editors Group
    if request.user.groups.filter(name='Editors').exists():
        menu_items[:] = [item for item in menu_items if item.name not in[ 'ropon_pages','documents','images']]