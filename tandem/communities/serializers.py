from rest_framework import serializers

from common.serializers import MembershipSerializer
from communities.models import Channel, Membership
from users.serializers import UserSerializer


class ChannelMembershipSerializer(MembershipSerializer):
    """
    Membership serializer to use in channel serializer, for representational purposes. Excludes channel field from
    representation.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = [
            'url',
            'user',
            'role'
        ]


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    """
    Channel serializer class.
    """
    memberships = ChannelMembershipSerializer(many=True, read_only=True)

    class Meta:
        model = Channel
        fields = [
            'url',
            'id',
            'name',
            'description',
            'language',
            'level',
            'memberships',
        ]
