"""
Serializers for representing video data in API responses.
"""

from rest_framework import serializers
from ..models import Video


class VideoListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing video objects with basic metadata and a resolved
    thumbnail URL. Generates an absolute URL if the request context is available.
    """

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ["id", "created_at", "title", "description", "thumbnail_url", "category"]

    def get_thumbnail_url(self, obj):
        """
        Return an absolute thumbnail URL if possible, or an empty string if no thumbnail exists.

        Args:
            obj (Video): The video instance being serialized.

        Returns:
            str: The absolute or relative URL to the thumbnail, or an empty string.
        """
        request = self.context.get("request")
        if obj.thumbnail and hasattr(obj.thumbnail, "url"):
            url = obj.thumbnail.url
            return request.build_absolute_uri(url) if request else url
        return ""
