from rest_framework import permissions, viewsets

from chats.models import UserChat
from chats.serializers import UserChatSerializer


class UserChatViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view chats, send messages, edit them, etc.
    """

    class Meta:
        model = UserChat

    queryset = UserChat.objects.all()
    serializer_class = UserChatSerializer
    permission_classes = [permissions.IsAuthenticated]
