from django.apps import AppConfig


class ResultSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'result_system'

    def ready(self):
        import result_system.signals
