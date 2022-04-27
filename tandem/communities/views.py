from rest_framework import viewsets, permissions, parsers

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

    # Disable PUT method, as it's not currently supported due to nested serializer fields
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

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
