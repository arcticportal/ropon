from django.apps import AppConfig
from .signal_handlers import update_owner_authorization_on_publish
from wagtail.signals import page_published

class RoponDataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ropon_data"
    verbose_name = 'ROPON Data'

    def ready(self):

        # Connect the update_owner_authorization_on_publish function to the page_published signal
        from .models import ObservingNetworkPage
        page_published.connect(update_owner_authorization_on_publish, sender=ObservingNetworkPage)