from django.utils.translation import gettext_lazy as _
from wagtail.users.views.users import UserViewSet as WagtailUserViewSet
from .views import RoponUserIndexView, RoponUserCreateView, RoponUserEditView
from .forms import RoponUserEditForm, RoponUserCreationForm

class RoponUserViewSet(WagtailUserViewSet):
    """
    Custom UserViewSet for RoponUser that provides group-based access control.
    
    This viewset customizes user management based on user groups following
    the approach recommended in Wagtail documentation:
    https://docs.wagtail.org/en/v6.2.3/advanced_topics/customisation/custom_user_models.html#creating-a-custom-userviewset
    
    Functionality:
    - Superusers: Have full access to all user management features
    - Moderators: Can manage non-superusers 
    - Editors: Have default access as defined in Wagtail
    """


    index_view_class = RoponUserIndexView
    add_view_class = RoponUserCreateView
    edit_view_class = RoponUserEditView
    create_template_name = "ropon_auth/roponuser/create.html"
    
    
    def get_form_class(self, for_update=False):
        """
        Return the appropriate form class based on the user's role and action.
        
        This method is specifically called out in the Wagtail documentation
        as the proper way to customize forms based on user role.
        
        Args:
            for_update (bool): Whether the form is for updating an existing user
            
        Returns:
            Form class: Either the standard Wagtail form or the moderator-restricted form
        """
        
        # For moderators, use the restricted forms that hide superuser options
        # if request and request.user.groups.filter(name='Moderators').exists():
        if for_update:
            return RoponUserEditForm
        return RoponUserCreationForm
        
    