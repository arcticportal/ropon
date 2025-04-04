from functools import cached_property
from django.utils.translation import gettext_lazy as _

# Import the specific user view classes from Wagtail 6.x
from wagtail.users.views.users import IndexView, CreateView, EditView


class RoponUserIndexView(IndexView):
    """
    Custom user index view for Ropon Users that filters out superusers for moderators.
    
    This view extends Wagtail's users.IndexView for users and adds
    filtering to hide superusers from moderators.
    """
    # Inherit template_name and permission_policy from parent class
    
    @cached_property
    def columns(self):
        """
        override to remove the is_superuser column from list view.
        
        Returns:
            list: List of column definitions for the user index view
        """
        # Use the default columns from the parent class
        l_columns = super().columns
        # Remove the is_superuser column for moderators
        if not self.request.user.is_superuser:
            l_columns= [c for c in l_columns if c.name != 'is_superuser']
        return l_columns
        

    def get_queryset(self):
        """
        Override to filter out superusers for moderators.
        
        Returns:
            QuerySet: Filtered users queryset that excludes superusers
            when the current user is a moderator
        """
        # Get the base queryset from the parent class
        queryset = super().get_queryset()
        
        # Filter out superusers if the current user is not a superuser
        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_superuser=False)
            
        return queryset


class RoponUserCreateView(CreateView):
    """
    Custom user creation view for RoponUser.
    
    It adds a form kwarg to check if the user is a superuser.
    """
    
    def get_form_kwargs(self):
        """
        Override to provide custom form arguments.
        
        Returns:
            dict: The form arguments, including whether the user is a superuser
        """
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "request_user_is_superuser": self.request.user.is_superuser,
            }
        )
        return kwargs


class RoponUserEditView(EditView):
    """
    Custom user edit view .

    This view extends Wagtail's EditView for users and adds
    a form kwarg to check if the user is a superuser. 
    """
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "request_user_is_superuser": self.request.user.is_superuser,
            }
        )
        return kwargs

    