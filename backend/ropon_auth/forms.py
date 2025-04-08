from django.utils.translation import gettext_lazy as _
from wagtail.users.forms import UserEditForm, UserCreationForm


class RoponUserEditForm(UserEditForm):
    """
    Custom user edit form for moderators that restricts certain fields.
    
    This form extends Wagtail's UserEditForm as recommended in the documentation:
    https://docs.wagtail.org/en/v6.2.3/advanced_topics/customisation/custom_user_models.html
    
    Modifications:
    - Removes the is_superuser field for moderators
    - Ensures edited users cannot be made superusers
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form with restricted fields for moderators.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        request_user_is_superuser = kwargs.pop('request_user_is_superuser', False)
        super().__init__(*args, **kwargs)
        
        # Remove the is_superuser field for moderators if present
        if not request_user_is_superuser:
            del self.fields['is_superuser']
    
   

class RoponUserCreationForm(UserCreationForm):
    """
    Custom user creation form that allows moderators to create users with restricted capabilities.
    
    This form extends Wagtail's UserCreationForm as recommended in the documentation:
    https://docs.wagtail.org/en/v6.2.3/advanced_topics/customisation/custom_user_models.html
    
    Modifications:
    - Removes the is_superuser field for moderators
    - Ensures created users cannot be made superusers
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form with restricted fields for moderators.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """

        request_user_is_superuser = kwargs.pop('request_user_is_superuser', False)
        # Call the parent constructor
        super().__init__(*args, **kwargs)
        
        # Remove the is_superuser field for moderators
        if not request_user_is_superuser:
            # Remove the is_superuser field for moderators
            del self.fields['is_superuser']
            
    