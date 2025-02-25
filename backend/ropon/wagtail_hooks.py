from wagtail import hooks
from flags.state import flag_enabled

FLAG_SIDE_PANEL_OPTIONS = 'ROPON.REMOVE_SIDE_PANEL_OPTIONS'

def remove_moderator_main_menu_options(menu_items):
    """
    Remove side panel options for Moderators role.
    """

    # Remove the following menu items for Moderators
    MODERATOR_MENU_ITEMS_TO_REMOVE = ['images', 'documents', 'help']
    menu_items[:] = [item for item in menu_items if item.name not in MODERATOR_MENU_ITEMS_TO_REMOVE]

def remove_editor_main_menu_options(menu_items):
    """
    Remove side panel options for Editors role.
    """

    EDITOR_MENU_ITEMS_TO_REMOVE = ['ropon_pages','images', 'documents', 'reports', 'help']

    menu_items[:] = [item for item in menu_items if item.name not in EDITOR_MENU_ITEMS_TO_REMOVE]

# Hide the pages menu item for non-superusers
@hooks.register('construct_main_menu')
def hide_pages_menu(request, menu_items):
  
    # Remove page explorer menu item for non-superusers
    if not request.user.is_superuser:
        menu_items[:] = [item for item in menu_items if item.name != 'explorer']

    # hide the ropon pages menu item for Editors Group
    if request.user.groups.filter(name='Editors').exists():
        menu_items[:] = [item for item in menu_items if item.name not in ['ropon_pages', 'documents', 'images']]
  
    # If the feature flag is enabled, remove the side panel options for Moderators and Editors
    if flag_enabled(FLAG_SIDE_PANEL_OPTIONS):
        if request.user.groups.filter(name='Moderators').exists():
            remove_moderator_main_menu_options(menu_items)
        elif request.user.groups.filter(name='Editors').exists():
            remove_editor_main_menu_options(menu_items)

@hooks.register('construct_reports_menu')
def construct_reports_menu(request, menu_items):
    """
    Modify the Reports menu for Moderators role.
    """
    if flag_enabled(FLAG_SIDE_PANEL_OPTIONS) and request.user.groups.filter(name='Moderators').exists():
        menu_items[:] = [item for item in menu_items if item.name == 'aging-pages']