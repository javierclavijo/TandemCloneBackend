from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import AvailableLanguage, ProficiencyLevel, Interest
from chats.models import AbstractChatMessage, AbstractChatMessageTranslation


class CustomUser(AbstractUser):
    friends = models.ManyToManyField(
        to="self",
        blank=True
    )
    description = models.TextField(
        blank=True,
        max_length=2000,
    )
    #   TODO (low priority): add constraint whereby user must have at least one native and one non-native language


class UserLanguage(models.Model):
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
    # TODO: consider whether to make this into a JSONField
