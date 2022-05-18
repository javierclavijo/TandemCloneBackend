from rest_framework import permissions, exceptions

from communities.models import ChannelRole
from users.serializers import UserSerializer


class CanEditChannel(permissions.BasePermission):
    """
    Object-level permissions to only allow a channel's staff to edit its info.
    """

    def has_object_permission(self, request, view, obj):
        # Allow all requests by admin users
        if request.user.is_staff:
            return True
        # Allow PATCH requests only if the user has a staff role (i.e. admin or moderator)
        if request.method == 'PATCH':
            return obj.memberships.filter(user=request.user, role__in=[ChannelRole.MOD, ChannelRole.ADMIN]).exists()
        # Always allow POST, GET, HEAD and OPTIONS requests.
        elif request.method in [*permissions.SAFE_METHODS, 'POST']:
            return True
        return False


class CanCreateEditOrDeleteMembership(permissions.BasePermission):
    """
    Object-level permissions which restrict creation, edition and deletion of user memberships:
    - Creation: allows the site's staff and a user to create a membership for that particular user.
    - Edition: allows a channel's staff and the site's staff to edit the membership.
    - Deletion: allows the site's and the channel's staff, and the membership's user to delete the membership.
    """

    def has_permission(self, request, view):
        # Allow all requests by admin users.
        if request.user.is_staff:
            return True
        # Allow a user to create a membership for themselves.
        elif request.method == 'POST':
            try:
                serializer = UserSerializer(request.user, context={'request': request})
                return request.data['user'] == serializer.data['url']
            except ValueError:
                raise exceptions.NotFound
        # Allow all PATCH requests to make has_object_permission() handle them.
        elif request.method == 'PATCH':
            return True
        # Always allow GET, HEAD and OPTIONS requests.
        elif request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Allow all requests by admin users.
        if request.user.is_staff:
            return True
        # Allow PATCH requests only if the user has a staff role (i.e. admin or moderator)
        elif request.method == 'PATCH':
            return obj.channel.memberships.filter(user=request.user,
                                                  role__in=[ChannelRole.MOD, ChannelRole.ADMIN]).exists()
        # Always allow GET, HEAD and OPTIONS requests.
        elif request.method in permissions.SAFE_METHODS:
            return True
        return False
