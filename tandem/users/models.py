from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    friends = models.ManyToManyField(
        to="self",
    )
    description = models.TextField(
        blank=True,
        max_length=2000,
    )
