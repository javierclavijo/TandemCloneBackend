from rest_framework import viewsets, permissions, parsers

from chats.models import ChannelChatMessage
from chats.serializers import ChannelChatMessageSerializer
from common.serializers import MembershipSerializer
from communities.models import Channel, Membership
from communities.serializers import ChannelSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    class Meta:
        model = Channel

    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    filterset_fields = ('memberships__user',)

    # Disable PUT method, as it's not currently supported due to nested serializer fields
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def create(self, request, *args, **kwargs):
        """ After creating a channel, creates a membership for it with the request's user and 'Admin' role. """
        response = super(ChannelViewSet, self).create(request, *args, **kwargs)
        channel_id = response.data['id']

        membership = Membership(
            user=request.user,
            channel_id=channel_id,
            role='A'
        )
        membership.save()
        serialized_membership = MembershipSerializer(membership, context={'request': request})
        response.data['memberships'].append(serialized_membership.data)

        message = ChannelChatMessage(
            author=request.user,
            channel_id=channel_id,
            content='Created channel'
        )
        message.save()
        serialized_message = ChannelChatMessageSerializer(message, context={'request': request})
        response.data['messages'].append(serialized_message.data)
        return response

    def get_queryset(self):
        """
        Optionally restricts the returned channels, by filtering against `name`, `language` and `levels`
        query parameters in the URL.
        """
        queryset = Channel.objects.all()
        name = self.request.query_params.get('name')
        language = self.request.query_params.get('language')
        levels = self.request.query_params.get('levels')

        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        if language is not None:
            queryset = queryset.filter(language=language)

        if levels is not None:
            queryset = queryset.filter(level__in=levels)

        return queryset


class MembershipViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allow channel memberships to be viewed or edited.
    """

    class Meta:
        model = Membership

    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
