from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from django.core.files.storage import default_storage
from core.tasks import convert720px
import os



@receiver(post_save, sender=Video)

def video_post_save(sender, instance, created, **kwargs):
    print('tesxt')
    if created:
        print('New video created')
        convert720px(instance.video_file.path)

@receiver(post_delete, sender=Video)
def delete_related_file(sender, instance, **kwargs):
    """
    Deletes the file associated with the MyModel instance
    after the instance itself is deleted from the database.
    """
    if instance.video_file:  # Replace with your file field name
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)