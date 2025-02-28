from django.utils.translation import gettext as _
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem  # Import AdminOnlyMenuItem for menu registration
from flags.state import flag_enabled
from ropon_data.reports.aging_networks import AgingObservingNetworksView  # Import the view class for aging networks report

FLAG_REMOVE_SIDE_PANEL_OPTIONS = 'ROPON.REMOVE_SIDE_PANEL_OPTIONS'
FLAG_ENABLE_AGING_NETWORKS = 'ROPON.REPORTS.AGING_OBSERVING_NETWORKS'


class AgingObservingNetworksMenuItem(MenuItem):
    """
    Custom menu item for the Aging Observing Networks report.
    """
    def is_shown(self, request):
        """
        Only show the menu item if the feature flag is enabled.
        """
        return flag_enabled(FLAG_ENABLE_AGING_NETWORKS)
    

@hooks.register('register_reports_menu_item')
def register_aging_networks_report():
    """Register the aging networks report in the Reports menu"""
    return AgingObservingNetworksMenuItem(
        _('Aging Observing Networks'),
        reverse('aging_networks'),
        name='aging-networks',
        icon_name="time",
        order=200
    )

@hooks.register('register_admin_urls')
def register_aging_networks_url():
    """Register the URL for the aging networks report"""
    return [
        path('reports/aging-networks/', 
             AgingObservingNetworksView.as_view(), 
             name='aging_networks'),
        path('reports/aging-networks/results/', 
             AgingObservingNetworksView.as_view(results_only=True), 
             name='aging_networks_results')
    ]

def remove_moderator_main_menu_options(menu_items):
    """
    Remove side panel options for Moderators role.
    """

    # Remove the following menu items for Moderators
    MODERATOR_MENU_ITEMS_TO_REMOVE = ['images', 'documents', 'help']
    
    # If the feature flag is not enabled, remove the reports menu item
    if not flag_enabled(FLAG_ENABLE_AGING_NETWORKS):
        MODERATOR_MENU_ITEMS_TO_REMOVE.append('reports')
    
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
    if flag_enabled(FLAG_REMOVE_SIDE_PANEL_OPTIONS):
        if request.user.groups.filter(name='Moderators').exists():
            remove_moderator_main_menu_options(menu_items)
        elif request.user.groups.filter(name='Editors').exists():
            remove_editor_main_menu_options(menu_items)

@hooks.register('construct_reports_menu')
def construct_reports_menu(request, menu_items):
    """
    Modify the Reports menu for non super users.
    """
    if not request.user.is_superuser:
        
        if flag_enabled(FLAG_ENABLE_AGING_NETWORKS) and flag_enabled(FLAG_REMOVE_SIDE_PANEL_OPTIONS):
        
            menu_items[:] = [item for item in menu_items if item.name == 'aging-networks']
