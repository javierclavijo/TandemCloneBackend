import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

from chats.models import AbstractChatMessage
from common.models import AvailableLanguage, ProficiencyLevel


def upload_to(instance, filename):
    return f'users/{instance.id}.{filename.split(".")[-1]}'


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), blank=False, unique=True)
    description = models.TextField(
        blank=True,
        max_length=2000,
    )
    image = models.ImageField(upload_to=upload_to, blank=True)


class UserLanguage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.TextField(
        max_length=2,
        choices=AvailableLanguage.choices
    )
    level = models.TextField(
        max_length=2,
        choices=ProficiencyLevel.choices
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='languages'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_user_language',
                fields=['user', 'language']
            )
        ]


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Generates an authentication token whenever a user object is created."""
    if created:
        Token.objects.create(user=instance)
