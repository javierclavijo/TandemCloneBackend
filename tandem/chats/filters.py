from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from chats.models import ChannelChatMessage, FriendChatMessage, FriendChat


class ChannelChatMessageFilter(filters.FilterSet):
    """
    Filter class for ChannelChatMessageViewSet. Requires a 'channel' parameter to filter by.
    """

    channel = filters.UUIDFilter(required=True)

    class Meta:
        model = ChannelChatMessage
        fields = ('channel',)


class FriendChatFilter(filters.FilterSet):
    """
    Filter class for FriendChatMessageViewSet. Requires a 'chat' parameter to filter by.
    """

    users = filters.ModelMultipleChoiceFilter(required=True, queryset=get_user_model().objects.all())

    class Meta:
        model = FriendChat
        fields = ('users',)


class FriendChatMessageFilter(filters.FilterSet):
    """
    Filter class for FriendChatMessageViewSet. Requires a 'chat' parameter to filter by.
    """

    chat = filters.UUIDFilter(required=True)

    class Meta:
        model = FriendChatMessage
        fields = ('chat',)
