from django.utils.translation import gettext as _
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem  # Import AdminOnlyMenuItem for menu registration
from flags.state import flag_enabled
from ropon_data.reports.aging_networks import AgingObservingNetworksView  # Import the view class for aging networks report
from wagtail_guide.settings import wagtail_guide_settings
from ropon.panels.welcome_panel import RoponWelcomePanel  # Import from panels package

# Feature flags definitions
FLAG_REMOVE_SIDE_PANEL_OPTIONS = 'ROPON.REMOVE_SIDE_PANEL_OPTIONS'
FLAG_ENABLE_AGING_NETWORKS = 'ROPON.REPORTS.AGING_OBSERVING_NETWORKS'
FLAG_ENABLE_WAGTAIL_GUIDE = 'ROPON.ENABLE_WAGTAIL_GUIDE'
FLAG_MODERATOR_USER_MANAGEMENT = 'ROPON.AUTH.MODERATOR_USER_MANAGEMENT'


@hooks.register('construct_homepage_panels')
def add_ropon_welcome_panel(request, panels):
    """
    Add the RoPON welcome panel to the Wagtail admin homepage.
    
    This panel appears immediately after the top heading panel and provides
    basic navigation information and links for RoPON administrators.
    
    The panel is shown to all authenticated users who have access to the admin.
    
    Args:
        request: HTTP request object
        panels: List of panel objects to modify in-place
    """
    # Add the welcome panel with appropriate ordering
    panels.append(RoponWelcomePanel())


# Hook to remove summary items (statistics panel) from the admin homepage
# This is registered after the panels hook to ensure proper execution order
@hooks.register('construct_homepage_summary_items', order=999)
def remove_homepage_summary_items(request, summary_items):
    """
    Removes all summary items from the Wagtail admin homepage.
    This effectively hides the top statistics/reports panel.
    
    Uses high order value to ensure this runs after other summary item hooks.
    """
    summary_items.clear()


class AgingObservingNetworksMenuItem(MenuItem):
    """
    Custom menu item for the Aging Observing Networks report.
    Only shown when the corresponding feature flag is enabled.
    
    This class extends MenuItem to provide conditional visibility based on feature flags.
    """
    def is_shown(self, request):
        """
        Only show the menu item if the feature flag is enabled.
        
        Args:
            request: The HTTP request object
            
        Returns:
            bool: Whether to show the menu item
        """
        return flag_enabled(FLAG_ENABLE_AGING_NETWORKS)
    

@hooks.register('register_reports_menu_item')
def register_aging_networks_report():
    """
    Register the aging networks report in the Reports menu.
    The visibility is controlled by the AgingObservingNetworksMenuItem class.
    
    Returns:
        MenuItem: The menu item for aging networks report
    """
    return AgingObservingNetworksMenuItem(
        _('Aging Observing Networks'),
        reverse('aging_networks'),
        name='aging-networks',
        icon_name="time",
        order=200
    )


@hooks.register('register_admin_urls')
def register_aging_networks_url():
    """
    Register the URL for the aging networks report.
    These URLs are always registered, but access can be controlled via views.
    
    Returns:
        list: List of URL path objects for the aging networks report
    """
    return [
        path('reports/aging-networks/', 
             AgingObservingNetworksView.as_view(), 
             name='aging_networks'),
        path('reports/aging-networks/results/', 
             AgingObservingNetworksView.as_view(results_only=True), 
             name='aging_networks_results')
    ]


def get_menu_items_to_remove(user_group):
    """
    Returns a list of menu items to remove based on user group and enabled features.
    
    This function centralizes all flag condition processing for menu items,
    including the FLAG_REMOVE_SIDE_PANEL_OPTIONS check.
    
    Args:
        user_group: The user group name ('Moderators', 'Editors', or None)
            
    Returns:
        - items_to_remove: List of menu item names to remove if should_remove_items is True
    """
    
    items_to_remove = []
     # Check wagtail guide feature flag for both roles
    if not flag_enabled(FLAG_ENABLE_WAGTAIL_GUIDE):
        items_to_remove.append(wagtail_guide_settings.WAGTAIL_GUIDE_MENU_LABEL.lower())
   
    # Check FLAG_REMOVE_SIDE_PANEL_OPTIONS flag - centralized here to avoid duplication
    should_remove_items = flag_enabled(FLAG_REMOVE_SIDE_PANEL_OPTIONS)
        
    # If flag is not enabled or unknown group, return empty list
    if not should_remove_items or user_group not in ('Moderators', 'Editors'):
        # For Editors, we need special handling even when FLAG_REMOVE_SIDE_PANEL_OPTIONS is off
        if user_group == 'Editors':
            # Return basic restrictions that always apply to Editors
            items_to_remove.extend(['ropon pages', 'documents', 'images'])
       
        return items_to_remove
    
    # Initialize list with common items to remove for both roles when flag is enabled
    items_to_remove.extend([ 'help',])
    
    # Role-specific items based on enabled features
    if user_group == 'Moderators':
        # For Moderators, conditionally show reports based on aging networks flag
        if not flag_enabled(FLAG_ENABLE_AGING_NETWORKS):
            items_to_remove.append('reports')
            
    elif user_group == 'Editors':
        # For Editors, always hide reports and ropon_pages regardless of flags
        items_to_remove.extend(['ropon pages', 'reports','images', 'documents','organizations'])
    
        
    return items_to_remove


@hooks.register('construct_main_menu')
def hide_pages_menu(request, menu_items):
    """
    Wagtail hook to modify the main menu based on user role and feature flags.
    
    Applies menu item filtering based on centralized logic in get_menu_items_to_remove.
    The FLAG_REMOVE_SIDE_PANEL_OPTIONS check is handled only in get_menu_items_to_remove
    to avoid duplication.
    
    Args:
        request: The HTTP request object
        menu_items: List of menu items to filter
    """
    # Always remove page explorer menu item for non-superusers
    if not request.user.is_superuser:
        # Filter out explorer for all non-superusers
        menu_items[:] = [item for item in menu_items if item.name != 'explorer']
        
        # Get user group
        user_group = None
        if request.user.groups.filter(name='Moderators').exists():
            user_group = 'Moderators'
        elif request.user.groups.filter(name='Editors').exists():
            user_group = 'Editors'
        
        # Apply menu restrictions based on user group and feature flags
        # FLAG_REMOVE_SIDE_PANEL_OPTIONS is handled inside get_menu_items_to_remove
        if user_group:
            items_to_remove = get_menu_items_to_remove(user_group)
            if items_to_remove:
                # Apply the restrictions if any items need to be removed
                menu_items[:] = [item for item in menu_items if item.label.lower() not in items_to_remove]


@hooks.register('construct_reports_menu')
def construct_reports_menu(request, menu_items):
    """
    Modify the Reports menu for non-superusers.
    
    When both aging networks and side panel flags are enabled, show only the aging networks
    report for non-superusers.
    
    Args:
        request: The HTTP request object
        menu_items: List of menu items to filter
    """
    if not request.user.is_superuser:
        # Component-based approach: Only show aging networks report when both flags are enabled
        if flag_enabled(FLAG_ENABLE_AGING_NETWORKS) and flag_enabled(FLAG_REMOVE_SIDE_PANEL_OPTIONS):
            menu_items[:] = [item for item in menu_items if item.name == 'aging-networks']


@hooks.register('construct_settings_menu')
def hide_settings_menu(request, menu_items):
    """
    Wagtail hook to modify the settings menu based on user role and feature flags.
    
    Applies menu item filtering based on centralized logic in get_menu_items_to_remove.
    
    Args:
        request: The HTTP request object
        menu_items: List of menu items to filter
    """
    # Always remove settings menu item for non-superusers
    user_group = None
    if request.user.groups.filter(name='Moderators').exists():
        user_group = 'Moderators'
    elif request.user.groups.filter(name='Editors').exists():
        user_group = 'Editors'
    
    # Apply menu restrictions based on user group and feature flags
    if user_group:
        items_to_remove = get_settings_items_to_remove(user_group)
        if items_to_remove:
            # Apply the restrictions if any items need to be removed
            menu_items[:] = [item for item in menu_items if item.label.lower() not in items_to_remove]

def get_settings_items_to_remove(user_group):
    """
    Returns a list of settings items to remove based on user group and enabled features.
    
    This function centralizes all flag condition processing for settings items.
    
    Args:
        user_group: The user group name ('Moderators', 'Editors', or None)
            
    Returns:
        - items_to_remove: List of settings item names to remove if should_remove_items is True
    """
    
    items_to_remove = []
    
    
    # Role-specific items based on enabled features
    if user_group == 'Moderators':
        if not flag_enabled(FLAG_MODERATOR_USER_MANAGEMENT):
            # For Moderators, conditionally show reports based on aging networks flag
            items_to_remove.append('users')

        if not flag_enabled(FLAG_ENABLE_WAGTAIL_GUIDE):
            items_to_remove.append('manage editor guide')

    
        
    return items_to_remove


@hooks.register('insert_global_admin_css')
def global_admin_css():
    return '<link rel="stylesheet" href="/static/ropon/css/ropon.css">'

