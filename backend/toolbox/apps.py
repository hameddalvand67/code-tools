from django.apps import AppConfig


class ToolboxConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "toolbox"
    verbose_name = "کدتولز"

    def ready(self):
        from . import signals  # noqa: F401
