from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from django.core.files.storage import default_storage
from core.tasks import convert720px
import os
from django_rq import enqueue
import django_rq
from core.tasks import convert_to_hls_480p





@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        print('New video created')

        # OPTION A: run synchronously (simple, but can block admin while ffmpeg runs)
        # convert_to_hls_480p(instance.id, instance.video_file.path)

        # OPTION B: enqueue in background via RQ (better)
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_to_hls_480p, instance.id, instance.video_file.path)

@receiver(post_delete, sender=Video)
def delete_related_file(sender, instance, **kwargs):
    """
    Deletes the file associated with the MyModel instance
    after the instance itself is deleted from the database.
    """
    if instance.video_file:  # Replace with your file field name
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)