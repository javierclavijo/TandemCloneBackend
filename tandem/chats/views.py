from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, inline_serializer, \
    OpenApiResponse
from rest_framework import viewsets, status, mixins, fields
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from chats.filters import ChannelChatMessageFilter, FriendChatMessageFilter, FriendChatFilter
from chats.models import FriendChat, FriendChatMessage, ChannelChatMessage
from chats.permissions import IsAdminUserOrChannelMember, FriendChatMessageIsAdminOrChatUser
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
    ),
    create=extend_schema(
        request=inline_serializer(name="friend_chat_create_request", fields={
            "users": fields.ListField(child=fields.UUIDField())
        }),
        responses={
            400: OpenApiResponse(description="No user was specified, the specified user is the same as the session's "
                                             "user or a chat for this pair of users already exists.",
                                 response=inline_serializer(name="friend_chat_create_bad_request", fields={
                                     "error": fields.CharField()
                                 })),
            404: OpenApiResponse(description="The user specified in the 'users' field was not found.",
                                 response=inline_serializer(name="friend_chat_create_not_found", fields={
                                     "detail": fields.CharField()
                                 }))
        })
)
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
        """ Creates a friend chat, adding the creator and the user specified in the 'users' array to the related users
        list, and adds a 'Chat created' message as the chat's first message. """

        if not len(request.data['users']):
            return Response(data={"error": "No users were specified."},
                            status=status.HTTP_400_BAD_REQUEST)

        other_user = get_object_or_404(get_user_model(), id=request.data['users'][0])

        # Check that the other user is not the same user as the session's user
        if other_user.id == request.user.id:
            return Response(data={"error": "The user specified in the request cannot be the same as the session's "
                                           "user."},
                            status=status.HTTP_400_BAD_REQUEST)

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
        ]),
    retrieve=extend_schema(
        description="Returns the details of the specified user chat message."
    ))
class FriendChatMessageViewSet(mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    """
    Returns the list of chat messages that belong to a user chat.
    """

    class Meta:
        model = FriendChatMessage

    queryset = FriendChatMessage.objects.all()
    serializer_class = FriendChatMessageSerializer
    filterset_class = FriendChatMessageFilter
    permission_classes = [FriendChatMessageIsAdminOrChatUser]


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('channel', type=OpenApiTypes.UUID, required=True,
                             description="The ID of the channel that the messages belong to. The session's user must "
                                         "have a membership in the specified channel, unless they're a superuser.", )
        ]),
    retrieve=extend_schema(
        description="Returns the details of the specified channel chat message."
    ))
class ChannelChatMessageViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """
    Returns the list of chat messages that belong to a channel.
    """

    class Meta:
        model = ChannelChatMessage

    queryset = ChannelChatMessage.objects.all()
    serializer_class = ChannelChatMessageSerializer
    filterset_class = ChannelChatMessageFilter
    permission_classes = [IsAdminUserOrChannelMember]
