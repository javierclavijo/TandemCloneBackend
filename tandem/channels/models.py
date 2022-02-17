from django.db import models
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _

from common.models import AvailableLanguage, ProficiencyLevel


class Channel(models.Model):
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
                check=Q(end_proficiency_level__gte=F('start_proficiency_level'))
            )
        ]


class Membership(models.Model):
    class ChannelRole(models.TextChoices):
        USER = 'U', _('User')
        MOD = 'M', _('Moderator')
        ADMIN = 'A', _('Administrator')

    user = models.ForeignKey(
        to='users.CustomUser',
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
