from django.apps import AppConfig


class RoponDataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ropon_data"
    verbose_name = 'ROPON Data'

    def ready(self):

        # Ensure that the signal handlers are registered when the app is ready
        from ropon_data.signal_handlers import register_signal_handlers

        register_signal_handlers()