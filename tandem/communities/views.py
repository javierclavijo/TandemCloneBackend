from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets, parsers, mixins
from rest_framework.decorators import action

from chats.models import ChannelChatMessage
from chats.serializers import ChannelChatMessageSerializer
from common.serializers import MembershipSerializer
from communities.filters import ChannelFilter
from communities.models import Channel, Membership
from communities.serializers import ChannelSerializer


@extend_schema_view(
    list=extend_schema(
        description="Returns a list of channels.",
        parameters=[
            OpenApiParameter('memberships__user', type=OpenApiTypes.UUID, required=True,
                             description="The ID of a user to filter the list by. Used to fetch the chat list for "
                                         "the session's user.", )
        ]
    ),
    retrieve=extend_schema(
        description="Returns the details of the specified channel.",
    ),
    partial_update=extend_schema(
        description="Modifies the details of the specified channel.",
    ),
    destroy=extend_schema(
        description="Deletes the specified channel."
    ),
    discover=extend_schema(
        parameters=[
            OpenApiParameter('language', type=OpenApiTypes.UUID, many=True,
                             description="One or multiple languages to filter channels by.  Available values : "
                                         "DE, EN, ES, FR, IT", )
        ]
    )
)
class ChannelViewSet(viewsets.ModelViewSet):
    """
    Allows channels to be viewed, edited or deleted.
    """

    class Meta:
        model = Channel

    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    filterset_class = ChannelFilter
    permission_classes = [DRYPermissions]

    # Disable PUT method, as it's not currently supported due to nested serializer fields
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def create(self, request, *args, **kwargs):
        """ Creates a channel and an associated admin membership for the session's user. """
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

    @action(detail=False, methods=['get'])
    def discover(self, request):
        """ Returns a list of random channels which the user is not a member of. """
        # Exclude channels that the session's user is a member of from the queryset and order it randomly.
        self.queryset = self.Meta.model.objects.exclude(memberships__user=request.user).order_by('?')
        return self.list(self, request)


@extend_schema_view(
    retrieve=extend_schema(
        description="Returns the details of the specified membership.",
    ),
    create=extend_schema(
        description="Creates a membership."
    ),
    partial_update=extend_schema(
        description="Modifies the details of the specified membership.",
    ),
    destroy=extend_schema(
        description="Deletes the specified membership."
    )
)
class MembershipViewSet(mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    Allows channel memberships to be viewed, created or edited.
    """

    class Meta:
        model = Membership

    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']
    permission_classes = [DRYPermissions]
