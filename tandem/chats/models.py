from django.conf import settings
from django.db import models

# Create your models here.
from django.utils import timezone

from common.models import AvailableLanguage


class AbstractChatMessage(models.Model):
    content = models.TextField(
        max_length=2048
    )
    timestamp = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        abstract = True


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


class AbstractChatMessageTranslation(models.Model):
    # TODO: add original language field to translation and correction models
    # TODO: merge both models
    language = models.CharField(
        max_length=2,
        choices=AvailableLanguage.choices
    )
    translated_content = models.TextField(
        max_length=4096
    )

    class Meta:
        abstract = True


class UserChatMessageTranslation(AbstractChatMessageTranslation):
    # TODO check if the model makes sense (especially its constraint)
    message = models.ForeignKey(
        to='chats.UserChatMessage',
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
        to='chats.UserChatMessage',
        on_delete=models.CASCADE,
        related_name='correction',
    )


class ChannelChatMessage(AbstractChatMessage):
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_channel_chat_messages"
    )
    channel = models.ForeignKey(
        to='channels.Channel',
        on_delete=models.CASCADE,
        related_name='messages'
    )

    class Meta:
        ordering = ['-timestamp']


class ChannelChatMessageTranslation(AbstractChatMessageTranslation):
    message = models.ForeignKey(
        to='ChannelChatMessage',
        on_delete=models.CASCADE,
        related_name='translations'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='channel_unique_language_message',
                fields=['language', 'message']
            )
        ]


class AbstractChatMessageCorrection(models.Model):
    language = models.CharField(
        max_length=2,
        choices=AvailableLanguage.choices
    )
    corrected_content = models.TextField(
        max_length=4096
    )

    class Meta:
        abstract = True


class ChannelChatMessageCorrection(AbstractChatMessageCorrection):
    message = models.OneToOneField(
        to='ChannelChatMessage',
        on_delete=models.CASCADE,
        related_name='correction',
    )
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='author'
    )