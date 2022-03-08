from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from channels.models import Channel, Membership
from channels.serializers import ChannelSerializer, ChannelChatMessageSerializer, ChannelMembershipSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Disable PUT method, as it's not currently supported due to nested serializer fields
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

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


class MembershipViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allow channel memberships to be viewed or edited.
    """

    class Meta:
        model = Membership

    queryset = Membership.objects.all()
    serializer_class = ChannelMembershipSerializer

    # Disable unused views
    # http_method_names = ['get', 'post', 'patch', 'delete', 'head']
