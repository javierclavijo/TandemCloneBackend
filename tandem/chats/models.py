import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from common.models import AvailableLanguage


class AbstractChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(
        max_length=2048
    )
    timestamp = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        abstract = True


class AbstractChatMessageTranslation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.CharField(
        max_length=2,
        choices=AvailableLanguage.choices
    )
    translated_content = models.TextField(
        max_length=4096
    )

    class Meta:
        abstract = True


class AbstractChatMessageCorrection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.CharField(
        max_length=2,
        choices=AvailableLanguage.choices
    )
    corrected_content = models.TextField(
        max_length=4096
    )

    class Meta:
        abstract = True


class UserChatMessage(AbstractChatMessage):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(
        to='UserChat',
        blank=False,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_user_chat_messages"
    )

    class Meta:
        ordering = ['-timestamp']


class UserChat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        blank=False,
        related_name="chats"
    )


class UserChatMessageTranslation(AbstractChatMessageTranslation):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.OneToOneField(
        to='chats.UserChatMessage',
        on_delete=models.CASCADE,
        related_name='correction',
    )


class ChannelChatMessage(AbstractChatMessage):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_channel_chat_messages"
    )
    channel = models.ForeignKey(
        to='communities.Channel',
        on_delete=models.CASCADE,
        related_name='messages'
    )

    class Meta:
        ordering = ['-timestamp']


class ChannelChatMessageTranslation(AbstractChatMessageTranslation):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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


class ChannelChatMessageCorrection(AbstractChatMessageCorrection):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
