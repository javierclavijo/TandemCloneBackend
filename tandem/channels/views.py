from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from channels.models import Channel, Membership, ChannelInterest
from channels.serializers import ChannelSerializer, MembershipSerializer, ChannelInterestSerializer
from chats.serializers import ChannelChatMessageSerializer
from common.models import Interest


class ChannelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    class Meta:
        model = Channel

    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Disable PUT method, as it's not currently supported due to nested serializer fields
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def get_queryset(self):
        """
        Optionally restricts the returned channels, by filtering against `name`, `language`, `levels` and `interests`
        query parameters in the URL.
        """
        queryset = Channel.objects.all()
        name = self.request.query_params.get('name')
        language = self.request.query_params.get('language')
        levels = self.request.query_params.get('levels')
        interests = self.request.query_params.get('interests')

        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        if language is not None:
            queryset = queryset.filter(language=language)

        if levels is not None:
            # Create an OR query object to filter by, including a query object level for each level, filtering by the
            # channel's level range.
            # Start creating a query object from the last level in the list, then add the rest of the queried levels.
            levels_parts = levels.split(',')
            first_level = levels_parts.pop()
            level_queryset = Q(start_proficiency_level__lte=first_level, end_proficiency_level__gte=first_level)
            for level in levels_parts:
                level_queryset |= Q(start_proficiency_level__lte=level, end_proficiency_level__gte=level)
            queryset = queryset.filter(level_queryset)

        if interests is not None:
            queryset = queryset.filter(interests__interest__in=interests.split(','))

        return queryset

    @action(detail=True, methods=['patch'])
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
                return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            # First, find the object for the interest if there's already one for this channel. This way, integrity
            # errors are avoided.
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


class MembershipViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allow channel memberships to be viewed or edited.
    """

    class Meta:
        model = Membership

    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
