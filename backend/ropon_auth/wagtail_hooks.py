from django.utils.translation import gettext as _

FLAG_MODERATOR_USER_MANAGEMENT = 'ROPON.AUTH.MODERATOR_USER_MANAGEMENT'



# class RoponUserAdminMenuItem(MenuItem):
#     """
#     Custom menu item for the Ropon user management.
#     Only shown when the corresponding feature flag is enabled.
    
#     This class extends MenuItem to provide conditional visibility based on feature flags.
#     """
#     def is_shown(self, request):
#         """
#         Only show the menu item if the feature flag is enabled.
        
#         Args:
#             request: The HTTP request object
            
#         Returns:
#             bool: Whether to show the menu item
#         """
#         return flag_enabled(FLAG_MODERATOR_USER_MANAGEMENT) and request.user.groups.filter(name='Moderators').exists()

# @hooks.register('register_admin_menu_item')
# def register_user_management_menu_item():
#     """
#     Register the user management menu item in the admin interface.
#     The visibility is controlled by the feature flag.
    
#     Returns:
#         MenuItem: The menu item for user management
#     """
#     return RoponUserAdminMenuItem(
#         _('Users'),
#         reverse('wagtailusers_users:index'),
#         name='user-management',
#         icon_name="user",
#         order=500
#     )
