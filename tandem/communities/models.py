import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import authenticated_users, allow_staff_or_superuser

from chats.models import AbstractChatMessage
from common.models import AvailableLanguage, ProficiencyLevel


def upload_to(instance, filename):
    return f'channels/{instance.id}.{filename.split(".")[-1]}'


class Channel(models.Model):

    @staticmethod
    @authenticated_users
    def has_read_permission(request):
        """ Allow all authenticated users to view all channels. """
        return True

    @authenticated_users
    def has_object_read_permission(self, request):
        """ Allow all authenticated users to view all channels. """
        return True

    @staticmethod
    @authenticated_users
    def has_create_permission(request):
        """ Allow all authenticated users to create channels. """
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):
        """ Leave handling of update and delete permissions to has_object_update_permission() and
        has_object_destroy_permission(). """
        return True

    @authenticated_users
    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        """ Allow only staff and channel admins/moderators to update a channel. """
        return self.memberships.filter(user=request.user, role__in=[ChannelRole.MOD, ChannelRole.ADMIN]).exists()

    @authenticated_users
    @allow_staff_or_superuser
    def has_object_destroy_permission(self, request):
        """ Allow only staff and channel admins to delete a channel. """
        return self.memberships.filter(user=request.user, role=ChannelRole.ADMIN).exists()

    def __str__(self):
        return self.name

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(
        blank=True,
        max_length=2000,
    )
    language = models.CharField(
        max_length=2,
        choices=AvailableLanguage.choices
    )
    level = models.CharField(
        max_length=2,
        choices=ProficiencyLevel.choices
    )
    image = models.ImageField(upload_to=upload_to, blank=True)


class ChannelRole(models.TextChoices):
    USER = 'U', _('User')
    MOD = 'M', _('Moderator')
    ADMIN = 'A', _('Administrator')


class Membership(models.Model):

    @staticmethod
    @authenticated_users
    def has_read_permission(request):
        """ Allow all authenticated users to view all memberships. """
        return True

    @authenticated_users
    def has_object_read_permission(self, request):
        """ Allow all authenticated users to view all memberships. """
        return True

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_create_permission(request):
        """ Allow users to create memberships only for themselves (except for staff, who can create memberships for any
        user). """
        from users.serializers import UserSerializer
        serializer = UserSerializer(request.user, context={'request': request})
        return request.data.get('user') == serializer.data.get('url')

    @staticmethod
    @authenticated_users
    def has_write_permission(request):
        """ Leave handling of update and delete permissions to has_object_update_permission() and
        has_object_destroy_permission(). """
        return True

    @authenticated_users
    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        """ Allow only staff and channel admins/moderators to update a membership. """
        return self.channel.memberships.filter(user=request.user,
                                               role__in=[ChannelRole.MOD, ChannelRole.ADMIN]).exists()

    @authenticated_users
    @allow_staff_or_superuser
    def has_object_destroy_permission(self, request):
        """ Allow only staff, channel admins/moderators and a user to delete a membership for that user. """
        return request.user == self.user or self.channel.memberships.filter(
            user=request.user, role__in=[ChannelRole.MOD, ChannelRole.ADMIN]).exists()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    channel = models.ForeignKey(
        to='Channel',
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.CharField(
        max_length=1,
        choices=ChannelRole.choices,
        default=ChannelRole.USER
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(name='unique_user_channel', fields=['user', 'channel'])
        ]
