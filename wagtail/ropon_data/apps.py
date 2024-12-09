from django.apps import AppConfig


class RoponDataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ropon_data"
    verbose_name = 'ROPON Data'

    def ready(self):
        import ropon_data.wagtail_hooks  # Ensures wagtail_hooks.py is loaded
