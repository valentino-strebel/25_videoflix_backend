"""
Signal handlers for processing uploaded videos and cleaning up related files.
"""

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from ..models import Video
import os
import django_rq

from core.api.tasks import convert_to_hls, ALLOWED_RESOLUTIONS


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Trigger HLS conversion jobs when a new video is created.

    When a new Video instance is saved with an attached file,
    queued background tasks are created for each allowed resolution.

    Args:
        sender: The model class (Video).
        instance (Video): The saved video instance.
        created (bool): Indicates whether this is a new instance.
        **kwargs: Additional signal arguments.
    """
    if created and instance.video_file:
        queue = django_rq.get_queue("default", autocommit=True)
        for res in ALLOWED_RESOLUTIONS:
            queue.enqueue(convert_to_hls, instance.id, instance.video_file.path, res)


@receiver(post_delete, sender=Video)
def delete_related_file(sender, instance, **kwargs):
    """
    Remove the video file from storage when the associated Video instance is deleted.

    Args:
        sender: The model class (Video).
        instance (Video): The deleted video instance.
        **kwargs: Additional signal arguments.
    """
    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)
