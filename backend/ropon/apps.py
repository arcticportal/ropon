
from wagtail.users.apps import WagtailUsersAppConfig

class RoponUsersAppConfig(WagtailUsersAppConfig):
    """
    Custom AppConfig for Wagtail users that uses our custom UserViewSet.
    
    This config replaces the default wagtail.users app config and uses
    our custom RoponUserViewSet to provide role-based access control.
    Following the approach in:
    https://docs.wagtail.org/en/v6.2.3/advanced_topics/customisation/custom_user_models.html
    """
    
    # Path to our custom UserViewSet that implements the role-based permissions
    user_viewset = "ropon_auth.viewsets.RoponUserViewSet"