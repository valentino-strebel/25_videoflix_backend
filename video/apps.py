from django.apps import AppConfig
from . import signals


class VideoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "video"
    verbose_name = "Video"
    def ready(self):
        from . import signals