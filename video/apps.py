"""
App configuration for the video application.
"""

from django.apps import AppConfig


class VideoConfig(AppConfig):
    """
    Configuration for the video app, including import of signal handlers
    when the application is ready.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "video"
    verbose_name = "Video"

    def ready(self):
        """
        Import signal handlers to ensure they are registered when the app loads.
        """
        from .api import signals
