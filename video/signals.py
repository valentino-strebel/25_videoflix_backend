from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Video
import os
import django_rq

from core.tasks import convert_to_hls, ALLOWED_RESOLUTIONS


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        print('New video created')

        queue = django_rq.get_queue('default', autocommit=True)

        for res in ALLOWED_RESOLUTIONS:
            queue.enqueue(convert_to_hls, instance.id, instance.video_file.path, res)


@receiver(post_delete, sender=Video)
def delete_related_file(sender, instance, **kwargs):
    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)