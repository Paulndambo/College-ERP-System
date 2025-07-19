from django.apps import AppConfig


class ProcurementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.procurement"

    def ready(self):
        import apps.accounting.signals