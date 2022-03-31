import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from chats.models import AbstractChatMessage, AbstractChatMessageTranslation
from common.models import AvailableLanguage, ProficiencyLevel, Interest


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    friends = models.ManyToManyField(
        to="self",
        blank=True
    )
    description = models.TextField(
        blank=True,
        max_length=2000,
    )


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


class UserInterest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interests'
    )
    interest = models.CharField(
        choices=Interest.choices,
        max_length=32
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_user_interest',
                fields=['user', 'interest']
            )
        ]


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Generates an authentication token whenever a user object is created."""
    if created:
        Token.objects.create(user=instance)
