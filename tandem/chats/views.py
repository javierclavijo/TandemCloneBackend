from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from chats.filters import ChannelChatMessageFilter, FriendChatMessageFilter
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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('chat', type=OpenApiTypes.UUID, required=True,
                             description='The ID of the chat that the messages belong to.', )
        ]
    ),
)
class FriendChatMessageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Returns the list of chat messages that belong to a user chat.
    """

    class Meta:
        model = FriendChatMessage

    queryset = FriendChatMessage.objects.all()
    serializer_class = FriendChatMessageSerializer
    filterset_class = FriendChatMessageFilter


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('channel', type=OpenApiTypes.UUID, required=True,
                             description='The ID of the channel that the messages belong to.', )
        ]
    ),
)
class ChannelChatMessageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Returns the list of chat messages that belong to a channel.
    """

    class Meta:
        model = ChannelChatMessage

    queryset = ChannelChatMessage.objects.all()
    serializer_class = ChannelChatMessageSerializer
    filterset_class = ChannelChatMessageFilter
