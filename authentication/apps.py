"""
App configuration for the authentication application.
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuration settings for the authentication app.
    Defines the app’s name, default primary key field type,
    and human-readable verbose name.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
    verbose_name = "Authentication"
