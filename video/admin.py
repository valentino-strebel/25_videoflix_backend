"""
Admin configuration for the Video model.
"""

from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Admin interface for managing video entries.
    Provides search, filtering, and ordering capabilities.
    """

    list_display = ("id", "title", "category", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)
