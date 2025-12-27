from django.apps import AppConfig


class MedicalAlertsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "medical_alerts"

    def ready(self):
        import medical_alerts.tasks
