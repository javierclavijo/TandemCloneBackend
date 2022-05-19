import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import authenticated_users, allow_staff_or_superuser
from rest_framework.authtoken.models import Token

from common.models import AvailableLanguage, ProficiencyLevel


def upload_to(instance, filename):
    return f'users/{instance.id}.{filename.split(".")[-1]}'


class CustomUser(AbstractUser):

    @staticmethod
    @authenticated_users
    def has_read_permission(request):
        """ Allow all authenticated users to view all users. """
        return True

    @authenticated_users
    def has_object_read_permission(self, request):
        """ Allow all authenticated users to view all users. """
        return True

    @staticmethod
    def has_create_permission(request):
        """ Always allow user creation. """
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):
        """ Leave handling of update permissions to has_object_update_permission(). """
        return True

    @authenticated_users
    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        """ Allow users to update only their own profile (except for staff, who edit any user). """
        return self == request.user

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), blank=False, unique=True)
    description = models.TextField(
        blank=True,
        max_length=2000,
    )
    image = models.ImageField(upload_to=upload_to, blank=True)


class UserLanguage(models.Model):

    @staticmethod
    @authenticated_users
    def has_read_permission(request):
        """ Allow all authenticated users to view all user languages. """
        return True

    @authenticated_users
    def has_object_read_permission(self, request):
        """ Allow all authenticated users to view all user languages. """
        return True

    @staticmethod
    @authenticated_users
    def has_create_permission(request):
        """ Allow users to add languages only for themselves (except for staff, who add languages to any user). """
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
        """ Allow users to update only their own languages (except for staff, who add languages to any user). """
        return self.user == request.user

    @authenticated_users
    @allow_staff_or_superuser
    def has_object_destroy_permission(self, request):
        """ Allow users to delete only their own languages (except for staff, who delete any user's languages). """
        return self.user == request.user

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.TextField(
        max_length=2,
        choices=AvailableLanguage.choices
    )
    level = models.TextField(
        max_length=2,
        choices=ProficiencyLevel.choices
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
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


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Generates an authentication token whenever a user object is created."""
    if created:
        Token.objects.create(user=instance)
