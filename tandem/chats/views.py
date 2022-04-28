from rest_framework import permissions, viewsets

from chats.models import FriendChat, FriendChatMessage, ChannelChatMessage
from chats.serializers import FriendChatSerializer, ChannelChatMessageSerializer, \
    FriendChatMessageSerializer


class FriendChatViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view chats, send messages and edit them, etc.
    Restricts data to the request's user's chats, unless they are staff.
    """

    class Meta:
        model = FriendChat

    def get_queryset(self):
        if self.request.user.is_staff:
            return FriendChat.objects.all()
        return self.request.user.chats.all()

    queryset = FriendChat.objects.all()
    serializer_class = FriendChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('users',)


class FriendChatMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view user chat messages, etc.
    """

    class Meta:
        model = FriendChatMessage

    queryset = FriendChatMessage.objects.all()
    serializer_class = FriendChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('chat',)


class ChannelChatMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view channel chat messages, etc.
    """

    class Meta:
        model = ChannelChatMessage

    queryset = ChannelChatMessage.objects.all()
    serializer_class = ChannelChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('channel',)
