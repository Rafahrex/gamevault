from django.apps import AppConfig


class ForoConfig(AppConfig):
    name = 'foro'

    def ready(self):
        # Registra los receptores del paradigma orientado a eventos.
        from . import signals  # noqa: F401
