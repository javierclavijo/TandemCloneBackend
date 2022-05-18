from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from chats.models import FriendChat
from communities.models import Channel


class IsAdminUserOrChannelMember(permissions.BasePermission):
    """
    Object and model-level permissions to only allow staff and the members of a channel to view its messages. Used in channel chat
    message views.
    """

    def has_permission(self, request, view):
        # Allow all requests by admin users
        if request.user.is_staff:
            return True
        # Allow GET requests only if there exists a membership for the user in the message's channel.
        if request.method == 'GET':
            channel = get_object_or_404(Channel, id=request.query_params['channel'])
            return channel.memberships.filter(user=request.user).exists()
        # Always allow HEAD and OPTIONS requests.
        elif request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Allow all requests by admin users
        if request.user.is_staff:
            return True
        # Allow GET requests only if there exists a membership for the user in the message's channel.
        if request.method == 'GET':
            return obj.channel.memberships.filter(user=request.user).exists()
        # Always allow HEAD and OPTIONS requests.
        elif request.method in permissions.SAFE_METHODS:
            return True
        return False


class FriendChatMessageIsAdminOrChatUser(permissions.BasePermission):
    """
    Object and model-level permissions to only allow staff and the users of a friend chat to view its messages. Used in
    friend chat message views.
    """

    def has_permission(self, request, view):
        # Allow all requests by admin users
        if request.user.is_staff:
            return True
        # Allow GET requests only if the request's user is one of the chat's users
        if request.method == 'GET':
            chat = get_object_or_404(FriendChat, id=request.query_params['chat'])
            return chat.users.filter(id=request.user.id).exists()
        # Always allow HEAD and OPTIONS requests.
        elif request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Allow all requests by admin users
        if request.user.is_staff:
            return True
        # Allow GET requests only if the request's user is one of the chat's users
        if request.method == 'GET':
            return obj.users.filter(id=request.user.id).exists()
        # Always allow HEAD and OPTIONS requests.
        elif request.method in permissions.SAFE_METHODS:
            return True
        return False
