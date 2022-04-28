import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


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


class FriendChatMessage(AbstractChatMessage):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(
        to='FriendChat',
        blank=False,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_friend_chat_messages"
    )

    class Meta:
        ordering = ['-timestamp']


class FriendChat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        blank=False,
        related_name="friend_chats"
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
