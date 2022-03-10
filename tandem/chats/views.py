from rest_framework import permissions, viewsets

from channels.models import Channel
from chats.models import UserChat
from chats.serializers import UserChatSerializer, ChannelChatSerializer


class UserChatViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view chats, send messages and edit them, etc.
    """

    class Meta:
        model = UserChat

    queryset = UserChat.objects.all()
    serializer_class = UserChatSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChannelChatViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view channel chats, send messages and edit them, etc.
    """

    class Meta:
        model = Channel

    queryset = Channel.objects.all()
    serializer_class = ChannelChatSerializer
    permission_classes = [permissions.IsAuthenticated]
