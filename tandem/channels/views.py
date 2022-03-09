from django.db import transaction
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response

from channels.models import Channel, Membership, ChannelInterest
from channels.serializers import ChannelSerializer, ChannelChatMessageSerializer, ChannelMembershipSerializer, \
    MembershipSerializer, ChannelInterestSerializer
from common.models import Interest


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

    @action(
        detail=True,
        methods=['patch']
    )
    @transaction.atomic()
    def set_interests(self, request, *args, **kwargs):
        """
        Update the channel's interest list. Must receive a list of interest values (from the Interest enum).
        Mostly identical to UserViewSet.set_interests.
        """
        instance = self.get_object()
        try:
            interests = request.data["interests"]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        new_interest_objects = []
        interest_choices = dict(Interest.choices)
        for interest in interests:
            try:
                interest_choices[interest]
            except KeyError:
                # If any interest is not a valid interest, return 400 status code
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # First, find the object for the interest if there's already one for this channel. This way, integrity errors
            # are avoided.
            try:
                # If an object is found, add it to the new list of interests.
                interest_object = ChannelInterest.objects.get(channel=instance, interest=interest)
                new_interest_objects.append(interest_object)
            except ChannelInterest.DoesNotExist:
                # If no object is found, create and save a new one
                data = {
                    'channel': instance.id,
                    'interest': interest
                }
                serializer = ChannelInterestSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                new_interest_objects.append(serializer.instance)

        # Delete other interests from the channel's language list
        instance.interests.exclude(id__in=[interest.id for interest in new_interest_objects]).delete()

        # The channel object is not modified at all. Instead, it's used to get the data for the response.
        serializer = self.get_serializer(instance=instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    class Meta:
        model = Channel


class MembershipViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allow channel memberships to be viewed or edited.
    """

    class Meta:
        model = Membership

    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
