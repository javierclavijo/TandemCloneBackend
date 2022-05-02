from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import permissions, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

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
        return self.request.user.friend_chats.all()

    queryset = FriendChat.objects.all()
    serializer_class = FriendChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('users',)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """ After creating a friend chat, adds the request's user and the other user (specified in the 'users' array in
        the request) to the related users list. Additionally, create the first message of the chat. """

        if not len(request.data['users']):
            return Response(data={"error": "No users were specified."},
                            status=status.HTTP_400_BAD_REQUEST)

        other_user = get_object_or_404(get_user_model(), id=request.data['users'][0])

        # Check that a chat with the two users doesn't exist already
        if FriendChat.objects.filter(users=request.user).filter(users=other_user).exists():
            return Response(data={"error": "A chat for this pair of users already exists."},
                            status=status.HTTP_400_BAD_REQUEST)

        response = super(FriendChatViewSet, self).create(request, *args, **kwargs)
        chat = FriendChat.objects.get(id=response.data['id'])
        chat.users.add(request.user)
        chat.users.add(other_user)
        chat.save()

        first_message = FriendChatMessage(
            author=request.user,
            chat=chat,
            content="Chat created"
        )
        first_message.save()

        serialized_chat = FriendChatSerializer(chat, context={"request": request})
        response.data = serialized_chat.data
        return response


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
