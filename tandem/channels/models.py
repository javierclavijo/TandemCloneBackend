from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import AvailableLanguage, ProficiencyLevel, Interest, AbstractChatMessage, \
    AbstractChatMessageTranslation, AbstractChatMessageCorrection


class Channel(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=64, )
    description = models.TextField(
        blank=True,
        max_length=2000,
    )
    language = models.CharField(
        max_length=2,
        choices=AvailableLanguage.choices
    )
    start_proficiency_level = models.CharField(
        max_length=2,
        choices=ProficiencyLevel.choices
    )
    end_proficiency_level = models.CharField(
        max_length=2,
        choices=ProficiencyLevel.choices
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='start_proficiency_level_gte_end_proficiency_level',
                check=models.Q(end_proficiency_level__gte=models.F('start_proficiency_level'))
            )
        ]


class Membership(models.Model):
    class ChannelRole(models.TextChoices):
        USER = 'U', _('User')
        MOD = 'M', _('Moderator')
        ADMIN = 'A', _('Administrator')

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


class ChannelInterest(models.Model):
    channel = models.ForeignKey(
        to='Channel',
        on_delete=models.CASCADE,
        related_name='interests'
    )
    interest = models.PositiveIntegerField(
        choices=Interest.choices
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_channel_interest',
                fields=['channel', 'interest']
            )
        ]


class ChannelChatMessage(AbstractChatMessage):
    channel = models.ForeignKey(
        to='Channel',
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
