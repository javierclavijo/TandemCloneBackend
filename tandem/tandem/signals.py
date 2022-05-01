from PIL import Image
from django.db.models.signals import post_save
from django.dispatch import receiver

from communities.models import Channel
from users.models import CustomUser


@receiver(post_save, sender=Channel)
@receiver(post_save, sender=CustomUser)
def optimize_image(sender, instance, **kwargs):
    """
    Resizes an image and applies compression to it to lower its size.
    Sources: https://stackoverflow.com/a/13211834, https://stackoverflow.com/a/70686579
    """
    if instance.image:
        with Image.open(instance.image.path) as image:
            image.thumbnail((400, 400), Image.LANCZOS)
            image.save(instance.image.path, optimize=True, quality=85)
