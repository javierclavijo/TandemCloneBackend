from rest_framework import permissions, viewsets

from chats.models import UserChat, UserChatMessage, ChannelChatMessage
from chats.serializers import UserChatSerializer, ChannelChatMessageSerializer, \
    UserChatMessageSerializer


class UserChatViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view chats, send messages and edit them, etc.
    Restricts data to the request's user's chats, unless they are staff.
    """

    class Meta:
        model = UserChat

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserChat.objects.all()
        return self.request.user.chats.all()

    queryset = UserChat.objects.all()
    serializer_class = UserChatSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserChatMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view user chat messages, etc.
    """

    class Meta:
        model = UserChatMessage

    queryset = UserChatMessage.objects.all()
    serializer_class = UserChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChannelChatMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view channel chat messages, etc.
    """

    class Meta:
        model = ChannelChatMessage

    queryset = ChannelChatMessage.objects.all()
    serializer_class = ChannelChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
