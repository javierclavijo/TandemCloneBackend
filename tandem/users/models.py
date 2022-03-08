from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import AvailableLanguage, ProficiencyLevel, Interest, AbstractChatMessage, \
    AbstractChatMessageTranslation


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


class UserChatMessage(AbstractChatMessage):
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_user_chat_messages"
    )
    recipient = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_user_chat_messages'
    )

    class Meta:
        ordering = ['-timestamp']
        constraints = [
            models.CheckConstraint(
                name='author_not_equals_recipient',
                check=~models.Q(recipient=models.F('author'))
            )
        ]


class UserChatMessageTranslation(AbstractChatMessageTranslation):
    # TODO check if the model makes sense (especially its constraint)
    message = models.ForeignKey(
        to='UserChatMessage',
        on_delete=models.CASCADE,
        related_name='translations'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='user_unique_language_message',
                fields=['language', 'message']
            )
        ]


class UserChatMessageCorrection(models.Model):
    message = models.OneToOneField(
        to='UserChatMessage',
        on_delete=models.CASCADE,
        related_name='correction',
    )
