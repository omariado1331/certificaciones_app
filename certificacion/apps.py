from django.apps import AppConfig


class CertificacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'certificacion'

    def ready(self):
        import certificacion.signals
