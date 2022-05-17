from django_filters import rest_framework as filters

from chats.models import ChannelChatMessage, FriendChatMessage


class ChannelChatMessageFilter(filters.FilterSet):
    """
    Filter class for ChannelChatMessageViewSet. Requires a 'channel' parameter to filter by.
    """

    channel = filters.UUIDFilter(required=True)

    class Meta:
        model = ChannelChatMessage
        fields = ('channel',)


class FriendChatMessageFilter(filters.FilterSet):
    """
    Filter class for FriendChatMessageViewSet. Requires a 'chat' parameter to filter by.
    """

    chat = filters.UUIDFilter(required=True)

    class Meta:
        model = FriendChatMessage
        fields = ('chat',)
