import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from dry_rest_permissions.generics import authenticated_users, allow_staff_or_superuser
from rest_framework.generics import get_object_or_404


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


def upload_to_friend_chat_message(instance, filename):
    return f'friend_chat_messages/{instance.id}.{filename.split(".")[-1]}'


def upload_to_channel_chat_message(instance, filename):
    return f'channel_chat_messages/{instance.id}.{filename.split(".")[-1]}'


class FriendChatMessage(AbstractChatMessage):

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_list_permission(request):
        """ Allow only chat members and staff to access the message list. """
        chat = get_object_or_404(FriendChat, id=request.query_params.get('chat'))
        return chat.users.filter(id=request.user.id).exists()

    @authenticated_users
    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        """ Allow only chat members and staff to access the message's details. """
        return self.chat.users.filter(id=request.user.id).exists()

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

    image = models.ImageField(upload_to=upload_to_friend_chat_message, blank=True)

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

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_list_permission(request):
        """ Allow only channel members and staff to access the message list. """
        from communities.models import Channel
        channel = get_object_or_404(Channel, id=request.query_params.get('channel'))
        return channel.memberships.filter(user=request.user).exists()

    @authenticated_users
    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        """ Allow only channel members and staff to access the message's details. """
        return self.channel.memberships.filter(user=request.user).exists()

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

    image = models.ImageField(upload_to=upload_to_channel_chat_message, blank=True)

    class Meta:
        ordering = ['-timestamp']
