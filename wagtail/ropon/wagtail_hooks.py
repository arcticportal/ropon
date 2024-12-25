
from wagtail import hooks


# Hide the pages menu item for non-superusers
@hooks.register('construct_main_menu')
def hide_pages_menu(request, menu_items):
    print(f"{request.user}")
    print(f"{request.user.is_superuser}")
    print(f"{[item.name for item in menu_items]}")
    if not request.user.is_superuser:
        menu_items[:] = [item for item in menu_items if item.name != 'explorer']
