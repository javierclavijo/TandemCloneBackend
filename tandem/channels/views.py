from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from channels.models import Channel
from channels.serializers import ChannelSerializer, ChannelChatMessageSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def chat(self, *args, **kwargs):
        """
        Fetches the channel's chat.
        """
        message_serializer = ChannelChatMessageSerializer(
            self.get_object().messages.all(),
            context={'request': self.request},
            many=True
        )
        return Response(message_serializer.data)

    class Meta:
        model = Channel
