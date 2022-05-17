from django_filters import rest_framework as filters

from chats.models import ChannelChatMessage


class ChannelChatMessageFilter(filters.FilterSet):
    """
    Filter class for ChannelMessageViewSet. Requires a 'channel' parameter to filter by
    """

    channel = filters.UUIDFilter(required=True)

    class Meta:
        model = ChannelChatMessage
        fields = ('channel',)
