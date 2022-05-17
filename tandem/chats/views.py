from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from chats.filters import ChannelChatMessageFilter, FriendChatMessageFilter, FriendChatFilter
from chats.models import FriendChat, FriendChatMessage, ChannelChatMessage
from chats.serializers import FriendChatSerializer, ChannelChatMessageSerializer, \
    FriendChatMessageSerializer


@extend_schema_view(
    list=extend_schema(
        description="Returns a list of user chats.",
        parameters=[
            OpenApiParameter('users', type=OpenApiTypes.UUID, required=True,
                             description="The ID of a user to filter by. The session's user must be the same as the "
                                         "specified user, unless they're a superuser.", )
        ]
    ),
    retrieve=extend_schema(
        description="Returns the details of the specified user chat.",
    ))
class FriendChatViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    Allow users to view the list of friend chats and create new ones.
    """

    class Meta:
        model = FriendChat

    queryset = FriendChat.objects.all()
    serializer_class = FriendChatSerializer
    filterset_class = FriendChatFilter

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """ Creates a friend chat, adding the creator and the other specified user to the related users list, and adds a
         'Chat created' message to use as the chat's first message. """

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
                             description="The ID of the chat that the messages belong to. The session's user must be "
                                         "one of the chat's users, unless they're a superuser.", )
        ]))
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
                             description="The ID of the channel that the messages belong to. The session's user must"
                                         "have a membership in the specified channel, unless they're a superuser.", )
        ]))
class ChannelChatMessageViewSet(mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """
    Returns the list of chat messages that belong to a channel.
    """

    class Meta:
        model = ChannelChatMessage

    queryset = ChannelChatMessage.objects.all()
    serializer_class = ChannelChatMessageSerializer
    filterset_class = ChannelChatMessageFilter
