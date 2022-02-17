from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import AvailableLanguage, ProficiencyLevel


class CustomUser(AbstractUser):
    friends = models.ManyToManyField(
        to="self",
        related_name='friends'
    )
    description = models.TextField(
        blank=True,
        max_length=2000,
    )


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
        to='CustomUser',
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
