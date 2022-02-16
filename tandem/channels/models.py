from django.db import models
from django.utils.translation import gettext_lazy as _


class Channel(models.Model):
    name = models.CharField(max_length=64, )
    description = models.TextField(
        blank=True,
        max_length=2000,
    )


class Membership(models.Model):
    class Role(models.TextChoices):
        USER = 'U', _('User')
        MOD = 'M', _('Moderator')
        ADMIN = 'A', _('Administrator')

    user = models.ForeignKey(
        to='users.CustomUser',
        on_delete=models.CASCADE
    )
    channel = models.ForeignKey(
        to='Channel',
        on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=1,
        choices=Role.choices,
        default=Role.USER
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(name='unique_user_channel', fields=['user', 'channel'])
        ]
