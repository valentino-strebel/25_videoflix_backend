from django.db import models


class Video(models.Model):
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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id} – {self.title}"
