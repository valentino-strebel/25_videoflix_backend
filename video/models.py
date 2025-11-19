"""
Model definition for video content, including metadata, media files,
and category classification.
"""

from django.db import models


class Video(models.Model):
    """
    Represents a video entry with title, description, thumbnail, category,
    creation timestamp, and an associated uploaded video file.
    """

    DRAMA = "Drama"
    ROMANCE = "Romance"
    ACTION = "Action"
    COMEDY = "Comedy"

    CATEGORY_CHOICES = [
        (DRAMA, "Drama"),
        (ROMANCE, "Romance"),
        (ACTION, "Action"),
        (COMEDY, "Comedy"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="thumbnails/")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    video_file = models.FileField(upload_to="videos")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """
        Return a readable string representation of the video instance.
        """
        return f"{self.id} – {self.title}"
