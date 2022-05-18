from rest_framework import permissions

from communities.models import ChannelRole


class IsAdminOrChannelStaffUser(permissions.BasePermission):
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
